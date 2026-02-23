from asyncio import sleep
from inspect import isawaitable
from json import JSONDecodeError, loads

import anthropic
from pydantic import BaseModel, ValidationError
from regex import compile

from football_data_manager.common.services.config.config_service import ConfigService


class _TranslateWordResponse(BaseModel):
    """Structured translation output from Claude."""

    original: str
    translated: str


class TranslatorService:
    """English-to-Korean translator backed by Anthropic Claude."""

    def __init__(self, config_service: ConfigService):
        self._api_key = config_service.api_list.anthropic.key
        self._client = anthropic.AsyncAnthropic(api_key=self._api_key or "")

    async def translate_word(self, word: str) -> str:
        """Translate a term to Korean. Returns original text on failure."""
        if not word:
            return word

        if not self._api_key:
            return word

        system_prompt = (
            "You are a professional football-domain translator from English to Korean.\n"
            "Return only JSON in this shape: "
            '{"original":"<english>","translated":"<korean>"}.\n'
            "Examples:\n"
            '- "Premier League" -> "프리미어 리그"\n'
            '- "Manchester United" -> "맨체스터 유나이티드"\n'
            '- "Erling Haaland" -> "엘링 홀란드"'
        )
        user_prompt = f'Translate this term: "{word}"'

        retry_count = 0
        while retry_count < 5:
            try:
                response = await self._client.messages.create(
                    model="claude-haiku-4-5",
                    max_tokens=200,
                    temperature=0.0,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                text = "".join(
                    block.text for block in response.content if hasattr(block, "text")
                )
                parsed = self._parse_json(text)
                translated = parsed.translated.strip()
                return translated or word
            except (
                anthropic.AnthropicError,
                JSONDecodeError,
                ValidationError,
                ValueError,
            ):
                retry_count += 1
                await sleep(1)

        return word

    async def close(self) -> None:
        """Close underlying HTTP resources."""
        if hasattr(self._client, "close"):
            maybe_awaitable = self._client.close()
            if isawaitable(maybe_awaitable):
                await maybe_awaitable

    @staticmethod
    def _parse_json(raw_text: str) -> _TranslateWordResponse:
        json_candidates = compile(r"\{(?:[^{}]|(?R))*\}").findall(raw_text)
        if not json_candidates:
            raise ValueError("No JSON payload found in translator response")
        payload = loads(max(json_candidates, key=len))
        return _TranslateWordResponse.model_validate(payload)
