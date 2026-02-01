from asyncio import sleep
from json import loads
from typing import TypeVar

from black.lines import Callable
from pydantic import BaseModel
from regex import compile

from football_data_manager.common.services.client.anthropic_client_service import (
    AnthropicClientService,
)
from football_data_manager.common.services.client.openai_client_service import (
    OpenAiClientService,
)
from football_data_manager.common.services.config.config_service import ConfigService
from football_data_manager.common.services.translator.models.word_response import (
    WordResponse,
)

T = TypeVar("T", bound=BaseModel)


class TranslatorService:

    __anthropic_client: AnthropicClientService
    __openai_client: OpenAiClientService

    def __init__(self, config_service: ConfigService):
        self.__anthropic_client = AnthropicClientService(
            api_key=config_service.api_list.anthropic.key
        )
        self.__openai_client = OpenAiClientService(
            api_key=config_service.api_list.open_ai.key
        )

    async def translate_word(self, word: str) -> str:
        """
        Translates text using the OpenAI client.
        :return: Translated text.
        """
        result = await self.__translate_from_anthropic(
            system_messages=[
                (
                    True,
                    "You are a professional translator specializing in translating English place names, stadium names, and similar proper nouns into Korean.",
                ),
                (
                    True,
                    """## Instructions:
1. Translate the given English term into its commonly used Korean equivalent
2. For place names and stadium names, use the standard Korean transliteration or the widely accepted Korean name
3. If there's an official Korean name, use that; otherwise, use phonetic transliteration following Korean transliteration rules
4. Return the result in the exact JSON format specified below""",
                ),
                (
                    True,
                    """## Output Format:
```json
{
    "original": "[original English term]",
    "translated": "[Korean translation]"
}
```""",
                ),
                (
                    True,
                    """## Examples:
- "Premier League" → "프리미어 리그"
- "Wembley Stadium" → "웸블리 스타디움"
- "Manchester United" → "맨체스터 유나이티드"
- "New York" → "뉴욕"
""",
                ),
                (False, "Now translate the following term:"),
            ],
            user_messages=[f'"{word}"'],
            decoder=lambda x: WordResponse.model_validate(x),
        )
        return result.translated

    async def __translate_from_anthropic(
        self,
        system_messages: list[tuple[bool, str]],
        user_messages: list[str],
        decoder: Callable[[str], T],
    ) -> T | None:
        """
        Translates text using the Anthropic client.
        :return: Translated text.
        """
        try_count = 0
        while try_count < 5:
            try:
                responses = await self.__anthropic_client.request(
                    system_messages=system_messages,
                    user_messages=user_messages,
                )
                jsons = [
                    obj
                    for resp in responses
                    for obj in compile(r"\{(?:[^{}]|(?R))*\}").findall(resp)
                ]
                return decoder(loads(str(max(jsons, key=len))))
            except Exception as e:
                print(f"Translation error: {e}")
                await sleep(1)
                try_count += 1
        return None
