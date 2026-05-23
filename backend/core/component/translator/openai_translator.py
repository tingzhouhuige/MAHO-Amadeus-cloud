import asyncio
from core.component.llm.openai_api import Client as OpenAIClient


class Client:
    def __init__(self, api_key: str, base_url: str, model: str, **kwargs):
        self.openai_client = OpenAIClient(api_key=api_key, base_url=base_url, model=model)

    def translate(self, text: str, from_lang: str = "auto", to_lang: str = "ja") -> str:
        try:
            return asyncio.run(self.atranslate(text, from_lang, to_lang))
        except RuntimeError:
            return text
        except Exception as e:
            return f"翻译错误: {str(e)}"

    async def atranslate(self, text: str, from_lang: str = "auto", to_lang: str = "ja") -> str:
        lang_map = {
            "ja": "日语",
            "zh": "中文",
            "en": "英语",
        }
        target_lang = lang_map.get(to_lang, to_lang)
        prompt = (
            f"把下面文本翻译成适合TTS朗读的{target_lang}。"
            "只输出译文，不要解释。必须和原文逐句对应，不能增加新内容，不能省略核心含义。"
            "尽量短，避免括号和舞台动作。\n\n"
            f"{text}"
        )
        response = ""
        async for token in self.openai_client.generate(prompt, max_tokens=80, temperature=0.1):
            response += token
        return response.strip() or text
