from pathlib import Path
import asyncio
from core.util.config import load_yaml
from core.component.llm.LLMService import LLM
from core.component.tts.TTSService import TTS
from core.component.translator.TranslatorService import Translator
from core.component.asr.ASRService import ASR


class BaseAmadeus:
    def __init__(self):
        config_path = Path("config.yaml")
        self.config = load_yaml(config_path)
        self.llm = LLM(self.config.get("llm", {}))
        self.tts = None
        self.tts_ready = False
        self.translator = Translator(self.config.get("translator", {}))
        self.asr = ASR(self.config.get("asr", {}))

        self.message_queue = asyncio.Queue()
        self.sentence_queue = asyncio.Queue()
        self.tts_lock = asyncio.Lock()
        self.audio_tasks = set()
        self.turn_id = 0
        self.user = {}
        self.context_window = []

        system_prompt = self.config.get("llm", {}).get("system_prompt", "")
        if system_prompt:
            self.context_window.append({"role": "system", "content": system_prompt})

        self.context_window_index = 0

    def get_tts(self):
        if self.tts is None:
            self.tts = TTS(self.config.get("tts", {}))
        self.tts_ready = True
        return self.tts
