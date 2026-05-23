import os
os.environ["ORT_DISABLE_ALL"] = "1"
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import asyncio
import colorlog
import logging
import uvicorn
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.Amadeus import BaseAmadeus
from core.auth.login import AuthManager
from core.handler.ws_handler import WSHandler

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s %(levelname)s [%(pathname)s] %(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    },
))

logging.basicConfig(level=logging.INFO, handlers=[handler])

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auth_manager = AuthManager()
ws_handler = WSHandler()
shared_amadeus = BaseAmadeus()


class LoginRequest(BaseModel):
    username: str
    password: str


class VerifyRequest(BaseModel):
    token: str


@app.on_event("startup")
async def warmup_tts():
    async def _warm():
        try:
            logging.info("warming up TTS")
            await asyncio.to_thread(shared_amadeus.get_tts)
            logging.info("TTS warmup complete")
        except Exception as exc:
            logging.error("TTS warmup failed: %r", exc)

    asyncio.create_task(_warm())


@app.post("/api/login")
async def login(request: LoginRequest):
    if auth_manager.verify_user(request.username, request.password):
        token = auth_manager.pack_token(request.username)
        logging.info("user %s logged in", request.username)
        return {"success": True, "token": token, "username": request.username}
    logging.warning("user %s login failed", request.username)
    raise HTTPException(status_code=401, detail="用户名或密码错误")


@app.post("/api/verify")
async def verify_token(request: VerifyRequest):
    user_info = auth_manager.verify_token(request.token)
    if user_info:
        return {"valid": True, "username": user_info.get("username")}
    raise HTTPException(status_code=401, detail="Token 无效")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_handler.handle_ws(websocket, shared_amadeus)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        ws_ping_interval=300,
        ws_ping_timeout=300,
    )
