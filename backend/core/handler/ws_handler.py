import asyncio
import json
import logging
from pathlib import Path
import sys

from core.auth.login import AuthManager
from core.chat import cancel_audio_tasks, handle_chat
from starlette.websockets import WebSocketDisconnect

sys.path.append(str(Path(__file__).parent.parent.parent))


class WSHandler:
    def __init__(self):
        self.auth_manager = AuthManager()
        self.current_chat_task = None

    async def _clear_queues(self, Amadeus):
        for queue in (Amadeus.message_queue, Amadeus.sentence_queue):
            while not queue.empty():
                try:
                    queue.get_nowait()
                    queue.task_done()
                except asyncio.QueueEmpty:
                    break

    async def interrupt_chat(self, websocket, Amadeus, notify: bool = True):
        if self.current_chat_task and not self.current_chat_task.done():
            self.current_chat_task.cancel()
            try:
                await self.current_chat_task
            except asyncio.CancelledError:
                logging.info("current chat task cancelled")
            except Exception as exc:
                logging.error("cancel chat task failed: %r", exc)
            finally:
                self.current_chat_task = None

        await cancel_audio_tasks(Amadeus)
        await self._clear_queues(Amadeus)

        if notify:
            await websocket.send_text(json.dumps({"type": "end"}))
        logging.info("chat/audio queues cleared")

    async def handle_ws(self, websocket, Amadeus):
        await websocket.accept()
        logging.info("WebSocket accepted")
        if not getattr(Amadeus, "tts_ready", False):
            await websocket.send_text(json.dumps({"type": "tts_loading"}))
            asyncio.create_task(self.notify_tts_ready(websocket, Amadeus))
        else:
            await websocket.send_text(json.dumps({"type": "tts_ready"}))

        try:
            while True:
                data = await websocket.receive_text()
                msg = json.loads(data)
                msg_type = msg.get("type")

                if msg_type == "chat":
                    token = msg.get("token")
                    if not token or not self.auth_manager.verify_token(token):
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "msg": "未授权，请先登录",
                        }))
                        continue

                    if self.current_chat_task and not self.current_chat_task.done():
                        await self.interrupt_chat(websocket, Amadeus, notify=False)

                    text = (msg.get("data") or "").strip()
                    if not text:
                        await websocket.send_text(json.dumps({"type": "end"}))
                        continue

                    self.current_chat_task = asyncio.create_task(
                        handle_chat(websocket, Amadeus, text)
                    )

                elif msg_type == "interrupt":
                    await self.interrupt_chat(websocket, Amadeus)

                elif msg_type == "audio":
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "msg": "语音输入已关闭，请使用文字提问",
                    }))
        except WebSocketDisconnect:
            logging.info("WebSocket disconnected")
        except Exception as exc:
            logging.error("WebSocket handler failed: %r", exc)
        finally:
            await self.interrupt_chat(websocket, Amadeus, notify=False)

    async def notify_tts_ready(self, websocket, Amadeus):
        try:
            while not getattr(Amadeus, "tts_ready", False):
                await asyncio.sleep(0.2)
            await websocket.send_text(json.dumps({"type": "tts_ready"}))
        except Exception:
            pass
