from json import loads

from football_data_manager.common.services.client.anthropic_client_service import (
    AnthropicClientService,
)
from football_data_manager.common.services.client.openai_client_service import (
    OpenAiClientService,
)


class TranslatorService:

    __anthropic_client: AnthropicClientService
    __openai_client: OpenAiClientService

    async def translate_word(self, word: str) -> str:
        """
        Translates text using the OpenAI client.
        :return: Translated text.
        """
        result = await self.__anthropic_client.request(
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
        )
        return loads(result[0])["translated"]
