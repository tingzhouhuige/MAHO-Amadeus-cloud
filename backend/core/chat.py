import asyncio
import base64
import json
import logging
import re
import uuid
from websockets.exceptions import WebSocketException

SENTENCE_ENDINGS = re.compile(r"(.+?[。！？!?\n]+)", re.S)
TTS_MAX_SENTENCES = 2
TEXT_SYNC_WAIT_SECONDS = 3
TTS_HARD_WAIT_SECONDS = 22
LLM_TIMEOUT_SECONDS = 10


class ChatFallbackError(Exception):
    pass


def _friendly_error(exc: Exception) -> str:
    text = str(exc).lower()
    blocked_markers = [
        "content",
        "sensitive",
        "policy",
        "moderation",
        "审核",
        "敏感",
        "违禁",
        "安全",
        "拒绝",
        "blocked",
    ]
    if any(marker in text for marker in blocked_markers):
        return "这个问题被接口拦住了，换个说法吧。"
    if isinstance(exc, ChatFallbackError):
        return "模型没回内容，换个说法吧。"
    return "模型出错了，换个问题吧。"


def split_complete_sentences(buffer: str):
    sentences = []
    rest = buffer
    while True:
        match = SENTENCE_ENDINGS.match(rest)
        if not match:
            break
        sentence = match.group(1).strip()
        if sentence:
            sentences.append(sentence)
        rest = rest[match.end():]
    return sentences, rest


def trim_for_tts(sentence: str) -> str:
    original = sentence
    sentence = re.sub(r"[（(][^）)]{0,40}[）)]", "", sentence)
    return re.sub(r"\s+", " ", sentence).strip() or re.sub(r"\s+", " ", original).strip()


async def send_text(websocket, text: str):
    for char in text:
        if char.strip():
            await websocket.send_text(json.dumps({"type": "text", "data": char}))


def _next_turn(Amadeus) -> int:
    Amadeus.turn_id += 1
    return Amadeus.turn_id


def _track_audio_task(Amadeus, task: asyncio.Task):
    Amadeus.audio_tasks.add(task)
    task.add_done_callback(lambda done: Amadeus.audio_tasks.discard(done))


async def notify_audio_done(websocket, Amadeus, turn_id: int, tasks: list[asyncio.Task]):
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
    if turn_id == Amadeus.turn_id:
        try:
            await websocket.send_text(json.dumps({"type": "audio_done"}))
        except WebSocketException:
            pass


async def cancel_audio_tasks(Amadeus):
    Amadeus.turn_id += 1
    stale_tasks = [task for task in Amadeus.audio_tasks if task.done()]
    for task in stale_tasks:
        Amadeus.audio_tasks.discard(task)


async def synthesize_and_send_audio(websocket, Amadeus, display_sentence: str, tts_sentence: str, audio_id: str, turn_id: int):
    try:
        if turn_id != Amadeus.turn_id:
            return

        async with Amadeus.tts_lock:
            if turn_id != Amadeus.turn_id:
                return

            logging.info("[TTS-PIPE] sentence: %s", tts_sentence)
            ja_sentence = await Amadeus.translator.atranslate(tts_sentence)
            logging.info("[TTS-PIPE] translated: %s", ja_sentence)

            if turn_id != Amadeus.turn_id:
                return

            text_sent = False
            try:
                if Amadeus.tts is None and turn_id == Amadeus.turn_id:
                    await send_text(websocket, "…")

                tts = Amadeus.get_tts()
                tts_task = asyncio.create_task(asyncio.to_thread(tts.generate_audio, ja_sentence))
                try:
                    audio_data = await asyncio.wait_for(
                        asyncio.shield(tts_task),
                        timeout=TEXT_SYNC_WAIT_SECONDS,
                    )
                except asyncio.TimeoutError:
                    if turn_id == Amadeus.turn_id:
                        await send_text(websocket, display_sentence)
                        text_sent = True
                    audio_data = await asyncio.wait_for(
                        asyncio.shield(tts_task),
                        timeout=TTS_HARD_WAIT_SECONDS,
                    )
                if audio_data and turn_id == Amadeus.turn_id:
                    if not text_sent:
                        await send_text(websocket, display_sentence)
                    await websocket.send_text(json.dumps({
                        "type": "audio",
                        "id": audio_id,
                        "data": base64.b64encode(audio_data).decode(),
                        "is_final": True,
                    }))
                    logging.info("[TTS-PIPE] sent full sentence audio for %s", audio_id)
                    return
            except asyncio.CancelledError:
                raise
            except asyncio.TimeoutError:
                logging.warning("[TTS-PIPE] TTS still slow; text was sent without audio: %s", display_sentence)
                return
            except Exception as exc:
                logging.error("TTS failed: %r", exc)
                Amadeus.tts = None

            if turn_id == Amadeus.turn_id and not text_sent:
                await send_text(websocket, display_sentence)
            logging.warning("[TTS-PIPE] no audio returned for %s", audio_id)
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        logging.error("audio pipeline failed: %r", exc)


async def handle_chat(websocket, Amadeus, user_text):
    try:
        await websocket.send_text(json.dumps({"type": "start"}))
    except WebSocketException:
        return

    turn_id = _next_turn(Amadeus)
    logging.info("chat turn %s received: %s", turn_id, user_text)

    try:
        Amadeus.context_window.append({"role": "user", "content": user_text})

        full_response = ""
        sentence_buffer = ""
        tts_sentence_count = 0
        turn_audio_tasks = []

        llm_stream = Amadeus.llm.generate(Amadeus.context_window)
        while True:
            try:
                response = await asyncio.wait_for(anext(llm_stream), timeout=LLM_TIMEOUT_SECONDS)
            except StopAsyncIteration:
                break
            except asyncio.TimeoutError as exc:
                raise ChatFallbackError("模型首包超时，可能被接口拦截或网络卡住。") from exc

            if turn_id != Amadeus.turn_id:
                return

            clean = response.replace("<think>", "").replace("</think>", "")
            if not clean:
                continue

            full_response += clean

            sentence_buffer += clean
            sentences, sentence_buffer = split_complete_sentences(sentence_buffer)
            for sentence in sentences:
                if tts_sentence_count >= TTS_MAX_SENTENCES:
                    continue
                audio_id = uuid.uuid4().hex
                task = asyncio.create_task(synthesize_and_send_audio(
                    websocket,
                    Amadeus,
                    sentence,
                    trim_for_tts(sentence),
                    audio_id,
                    turn_id,
                ))
                _track_audio_task(Amadeus, task)
                turn_audio_tasks.append(task)
                tts_sentence_count += 1

        if sentence_buffer.strip() and tts_sentence_count < TTS_MAX_SENTENCES:
            audio_id = uuid.uuid4().hex
            task = asyncio.create_task(synthesize_and_send_audio(
                websocket,
                Amadeus,
                sentence_buffer,
                trim_for_tts(sentence_buffer),
                audio_id,
                turn_id,
            ))
            _track_audio_task(Amadeus, task)
            turn_audio_tasks.append(task)

        if not full_response.strip():
            raise ChatFallbackError("模型没有返回内容，可能被接口拦截。")

        Amadeus.context_window.append({"role": "assistant", "content": full_response})
        asyncio.create_task(notify_audio_done(websocket, Amadeus, turn_id, turn_audio_tasks))
    except asyncio.CancelledError:
        await cancel_audio_tasks(Amadeus)
        raise
    except Exception as exc:
        logging.error("chat failed: %r", exc)
        try:
            fallback = _friendly_error(exc)
            await send_text(websocket, fallback)
            Amadeus.context_window.append({"role": "assistant", "content": fallback})
            await websocket.send_text(json.dumps({
                "type": "error",
                "msg": f"模型请求失败：{exc}",
            }))
            await websocket.send_text(json.dumps({"type": "audio_done"}))
        except WebSocketException:
            pass

    try:
        await websocket.send_text(json.dumps({"type": "end"}))
    except WebSocketException:
        pass


async def process_char_queue(Amadeus, websocket):
    while True:
        await asyncio.sleep(3600)


async def process_sentence_queue(Amadeus, websocket):
    while True:
        await asyncio.sleep(3600)
