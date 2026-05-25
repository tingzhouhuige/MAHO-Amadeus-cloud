from pathlib import Path
import asyncio
import copy
import os
from core.util.config import load_yaml
from core.component.llm.LLMService import LLM
from core.component.tts.TTSService import TTS
from core.component.translator.TranslatorService import Translator
from core.component.asr.ASRService import ASR

_BACKEND_DIR = Path(__file__).resolve().parents[1]


def _deep_merge(base, override):
    result = copy.deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _apply_role_profile(config):
    role_config = config.get("role", {}) or {}
    profiles = role_config.get("profiles", {}) or {}
    selected = (os.getenv("MAHO_ROLE") or role_config.get("select") or "maho").strip().lower()
    profile = profiles.get(selected)
    if not profile:
        selected = "maho"
        profile = profiles.get(selected, {})

    merged = _deep_merge(config, profile)
    _apply_tts_fallback(merged, profiles)
    merged["active_role"] = {
        "key": selected,
        "name": profile.get("name", selected),
        "display_name": profile.get("display_name", selected),
    }
    return merged


def _apply_tts_fallback(config, profiles):
    tts_config = config.get("tts", {}) or {}
    if tts_config.get("select") != "genie_tts_service":
        return

    genie_config = tts_config.get("genie_tts_service", {}) or {}
    model_dir = genie_config.get("onnx_model_dir", "")
    if not model_dir:
        return

    model_path = _resolve_config_path(model_dir)
    if model_path.is_dir():
        reference_path = genie_config.get("reference_audio_path", "")
        if reference_path:
            ref_path = _resolve_config_path(reference_path)
            if not ref_path.is_file():
                genie_config["reference_audio_path"] = ""
                genie_config["reference_audio_text"] = ""
        return

    fallback = (
        profiles.get("maho", {})
        .get("tts", {})
        .get("genie_tts_service")
    )
    if fallback:
        tts_config["genie_tts_service"] = copy.deepcopy(fallback)


def _resolve_config_path(path_value):
    path = Path(path_value)
    if path.is_absolute():
        return path

    repo_root = Path(__file__).resolve().parents[2]
    backend_root = Path(__file__).resolve().parents[1]
    parts = path.parts
    if parts and parts[0].lower() == "backend":
        return repo_root / path
    return backend_root / path


class BaseAmadeus:
    def __init__(self):
        config_path = _BACKEND_DIR / "config.yaml"
        self.config = _apply_role_profile(load_yaml(config_path))
        self.active_role = self.config.get("active_role", {})
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
