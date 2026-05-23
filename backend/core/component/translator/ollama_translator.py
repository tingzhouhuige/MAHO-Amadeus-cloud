from core.component.llm.ollama_api import Client as OllamaClient


class Client:
    def __init__(self, model: str = "qwen2.5:0.5b", base_url: str = "http://localhost:11434", **kwargs):
        self.ollama_client = OllamaClient(model=model, base_url=base_url)
        self.model = model

    def translate(self, text: str, from_lang: str = "auto", to_lang: str = "ja") -> str:
        return text

    async def atranslate(self, text: str, from_lang: str = "auto", to_lang: str = "ja") -> str:
        target_lang = self._get_lang_name(to_lang)
        prompt = (
            f"Translate the following text into {target_lang} for Japanese TTS.\n"
            "Return only the translated sentence. Do not add explanations, quotes, labels, or extra text.\n\n"
            f"{text}"
        )
        response = ""
        async for token in self.ollama_client.generate(prompt, max_tokens=256, temperature=0.1):
            response += token
        return response.strip()

    def _get_lang_name(self, lang_code: str) -> str:
        lang_map = {
            "ja": "natural Japanese",
            "jp": "natural Japanese",
            "en": "English",
            "zh": "Chinese",
            "ko": "Korean",
            "fr": "French",
            "de": "German",
            "es": "Spanish",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
        }
        return lang_map.get(lang_code, lang_code)
