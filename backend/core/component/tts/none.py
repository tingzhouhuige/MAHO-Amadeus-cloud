import logging


class Client:
    def generate_audio(self, text: str, **kwargs) -> bytes | None:
        logging.info("TTS 已禁用，跳过音频生成。")
        return None
