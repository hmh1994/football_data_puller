from anthropic import AsyncAnthropic
from anthropic.types import MessageParam, TextBlockParam, CacheControlEphemeralParam


class AnthropicClientService:
    """
    Client service for Anthropic API.
    :param api_key: API key for Anthropic.
    :param default_model: Default model to use for requests (default is "claude-3-5-haiku-latest").
    :param timeout: Timeout in seconds for API requests (default is 900.0).
    :ivar __client: Instance of AsyncAnthropic client.
    """

    default_model: str
    __client: AsyncAnthropic

    def __init__(
        self,
        api_key: str,
        default_model: str = "claude-3-5-haiku-latest",
        timeout: float = 900.0,
    ):
        self.default_model = default_model
        self.__client = AsyncAnthropic(api_key=api_key, timeout=timeout)

    async def request(
        self,
        system_messages: list[tuple[bool, str]],
        user_messages: list[str],
        max_tokens: int = 1000,
        model: str | None = None,
    ) -> list[str]:
        """
        Create a response using Anthropic API.
        :param system_messages: List of tuples where each tuple contains a boolean indicating if the message is cached and the message itself.
        :param user_messages: List of user messages.
        :param max_tokens: Maximum number of tokens to generate in the response (default is 1000).
        :param model: Model to use for the request (default is None, which uses the default model).
        :return: List of response messages from the API.
        """
        model_to_use = model or self.default_model
        system_messages = [
            TextBlockParam(
                text=msg,
                type="text",
                cache_control=(
                    CacheControlEphemeralParam(type="ephemeral") if is_cached else None
                ),
            )
            for is_cached, msg in system_messages
        ]
        response = await self.__client.messages.create(
            max_tokens=max_tokens,
            messages=[MessageParam(content=msg, role="user") for msg in user_messages],
            model=model_to_use,
            system=system_messages,
        )
        return [content.text for content in response.content]
