from openai import AsyncOpenAI


class OpenAIClientService:
    """
    OpenAI client services using the openAI package.

    :param api_key: OpenAI API key.
    :param organization: OpenAI organization ID (optional).
    :param default_model: Default model to use (default is "gpt-4o-mini").
    :param timeout: Timeout in seconds for API requests (default is 900.0).
    """

    default_model: str
    timeout: float
    __client: AsyncOpenAI

    def __init__(
        self,
        api_key: str,
        organization: str | None = None,
        default_model: str = "gpt-4o-mini",
        timeout: float = 900.0,
    ):
        self.default_model = default_model
        self.timeout = timeout
        self.__client = AsyncOpenAI(
            api_key=api_key,
            organization=organization,
            timeout=timeout,
        )

    async def request(
        self,
        system_messages: list[str],
        user_messages: list[str],
        model: str | None = None,
    ) -> list[str]:
        """
        Create a response using OpenAI API.
        :param system_messages:
        :param user_messages:
        :param model:
        :return:
        """
        model_to_use = model or self.default_model
        response = await self.__client.with_options(
            timeout=self.timeout
        ).chat.completions.create(
            model=model_to_use,
            messages=[
                {"role": "system", "content": message} for message in system_messages
            ]
            + [{"role": "user", "content": message} for message in user_messages],
        )
        return [
            choice.message.content
            for choice in response.choices
            if choice.message.content is not None
        ]

    async def request_by_flex_processing(
        self,
        instructions: str,
        message: str,
        model: str | None = None,
    ) -> str:
        """
        Create a response using OpenAI API.

        :param instructions: Instructions for the model.
        :param message: Input data for the model.
        :param model: Name of the model to use (default is the default model).
        :return: Response from the OpenAI API.
        """
        model_to_use = model or self.default_model
        response = await self.__client.with_options(
            timeout=self.timeout
        ).responses.create(
            model=model_to_use,
            instructions=instructions,
            input=message,
            service_tier="flex",
        )
        return response.output_text
