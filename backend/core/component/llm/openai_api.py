from openai import AsyncOpenAI
import os
from httpx import Timeout


def _read_env(name: str) -> str | None:
    value = os.getenv(name)
    if value:
        return value

    if os.name == "nt":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                value, _ = winreg.QueryValueEx(key, name)
                return value
        except OSError:
            return None
    return None


class Client:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        timeout: int = 60,
        max_tokens: int = 384,
        temperature: float = 0.7,
        **kwargs
    ):
        if not api_key:
            api_key = (
                _read_env("DEEPSEEK_API_KEY")
                or _read_env("OPENROUTER_API_KEY")
                or _read_env("OPENAI_API_KEY")
                or "EMPTY"
            )

        default_headers = {}
        if "openrouter.ai" in base_url:
            default_headers = {
                "HTTP-Referer": _read_env("OPENROUTER_SITE_URL") or "http://localhost",
                "X-Title": _read_env("OPENROUTER_APP_NAME") or "MAHO-Amadeus",
            }
            
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=Timeout(timeout),
            default_headers=default_headers,
        )
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    async def generate(self, prompt: str | list, max_tokens: int | None = None, temperature: float | None = None):
        messages = []
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = prompt

        max_tokens = self.max_tokens if max_tokens is None else max_tokens
        temperature = self.temperature if temperature is None else temperature

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise RuntimeError(f"云端模型请求失败: {e}") from e
