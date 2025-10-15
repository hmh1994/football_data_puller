from asyncio import sleep, gather
from datetime import datetime, UTC
from json import loads, dumps

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from regex import compile

from football_data_manager.common.enums.news_type_enum import NewsTypeEnum
from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.common.repositories.news.news_entity import NewsEntity
from football_data_manager.common.repositories.news.news_repository import (
    NewsRepository,
)
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
from football_data_manager.common.repositories.teams.team_repository import (
    TeamRepository,
)
from football_data_manager.common.services.client.anthropic_client_service import (
    AnthropicClientService,
)
from football_data_manager.common.services.config.models.api_config import ApiConfig
from football_data_manager.common.services.db.db_service import DbService
from football_data_manager.puller.services.the_athletic.models.responses.news_translate_response import (
    NewsTranslateResponse,
)
from football_data_manager.puller.services.the_athletic.models.responses.the_athletic_article_response import (
    TheAthleticArticleResponse,
)
from football_data_manager.puller.services.the_athletic.models.responses.the_athletic_league_feed_mulligan_layout_content_response import (
    TheAthleticLeagueFeedMulliganLayoutContentResponse,
)
from football_data_manager.puller.services.the_athletic.services.the_athletic_graphql_service import (
    TheAthleticGraphQLService,
)


class TheAthleticPullerService:
    __http_client: ClientSession
    __graphql_service: TheAthleticGraphQLService
    __anthropic_service: AnthropicClientService
    __news_repository: NewsRepository
    __team_repository: TeamRepository

    target_competition_abbr = ["EN_PR"]
    teams: list[TeamEntity]
    translate_instruction: list[tuple[bool, str]]

    def __init__(
        self,
        anthropic_config: ApiConfig,
        the_athletic_graphql_config: ApiConfig,
        db_service: DbService,
    ):
        self.__http_client = ClientSession()
        self.__news_repository = NewsRepository(db_service)
        self.__team_repository = TeamRepository(db_service)
        self.__graphql_service = TheAthleticGraphQLService(the_athletic_graphql_config)
        self.__anthropic_service = AnthropicClientService(api_key=anthropic_config.key)

    async def close(self):
        """
        Closes the HTTP client session.
        """
        await self.__http_client.close()

    async def pull_news(self):
        self.teams = await self.__team_repository.read_all()
        self.translate_instruction = await self.__get_openai_instruction()
        news_list = await gather(
            *[
                self.__pull_league_news_list(abbr)
                for abbr in self.target_competition_abbr
            ]
        )
        news = [n for sublist in news_list for n in sublist]
        print(f"News entities count: {len(news)}")
        await self.__news_repository.create_all(news)

    async def __pull_league_news_list(self, league_abbr: str) -> list[NewsEntity]:
        """
        Pulls league news list from The Athletic API.
        :param league_abbr: League abbreviation.
        :return: List of news items.
        """
        print(f"Pulling league news list for {league_abbr}")
        contents = await self.__pull_news_list(league_abbr)
        print(f"News pulled from The Athletic: {len(contents)}")
        news: list[NewsEntity] = await gather(
            *[self.__pull_news_entity(c) for c in contents]
        )
        return list(filter(None, news))

    async def __pull_news_entity(
        self, content: TheAthleticLeagueFeedMulliganLayoutContentResponse
    ) -> NewsEntity | None:
        article = await self.__pull_news_body(content)
        if article is None:
            return None
        if article.articleBody is None:
            print(f"Skipping news (no articleBody): [{content.consumable_id}] {article.headline}")
            return None
        print(f"News entity pulled: [{content.consumable_id}] {article.headline}")
        translate_response = await self.__translate_article(article)
        if translate_response is None:
            return None
        print(f"News entity translated: [{content.consumable_id}] {article.headline}")
        return await self.__process_news(content, article, translate_response)

    async def __pull_news_list(
        self, league_abbr: str
    ) -> list[TheAthleticLeagueFeedMulliganLayoutContentResponse]:
        contents = []
        content_id = set()
        page = 0
        while page < 5:
            response = await self.__graphql_service.get_league_feed(league_abbr, page)
            new_contents = [
                c
                for r in response.feedMulligan.layouts
                for c in r.contents
                if c.consumable_id is not None
            ]
            filtered_contents = list()
            for c in new_contents:
                if (
                    await self.__check_if_news_exists(c.consumable_id)
                    or c.consumable_id in content_id
                ):
                    continue
                content_id.add(c.consumable_id)
                filtered_contents.append(c)
            print(f"League feed response from page {page}: {len(filtered_contents)}")
            contents.extend(filtered_contents)
            if len(new_contents) != len(filtered_contents):
                break
            page += 1
        return contents

    async def __pull_news_body(
        self,
        content: TheAthleticLeagueFeedMulliganLayoutContentResponse,
    ) -> TheAthleticArticleResponse | None:
        async with self.__http_client.get(content.permalink) as resp:
            if resp.status != 200:
                return None
            body = await resp.text()
            soup = BeautifulSoup(body, "html.parser")
            script = soup.find("script", type="application/ld+json")
            if not script:
                return None
            return TheAthleticArticleResponse.model_validate(
                loads(script.string.strip())
            )

    async def __translate_article(
        self,
        article: TheAthleticArticleResponse,
    ) -> NewsTranslateResponse | None:
        body = {
            "authors": [a.name for a in article.author],
            "title": article.headline,
            "article": article.articleBody,
        }
        try_count = 0
        while try_count < 5:
            try:
                responses = await self.__anthropic_service.request(
                    system_messages=self.translate_instruction,
                    user_messages=["", dumps(body)],
                )
                jsons = [
                    obj
                    for resp in responses
                    for obj in compile(r"\{(?:[^{}]|(?R))*\}").findall(resp)
                ]
                return NewsTranslateResponse.model_validate(
                    loads(str(max(jsons, key=len)))
                )
            except Exception as e:
                print(f"Translation error: {e}")
                await sleep(1)
                try_count += 1
        return None

    async def __process_news(
        self,
        content: TheAthleticLeagueFeedMulliganLayoutContentResponse,
        article: TheAthleticArticleResponse,
        translate_response: NewsTranslateResponse,
    ) -> NewsEntity:
        author_en = [a.en for a in translate_response.authors]
        author_kr = [a.ko for a in translate_response.authors]
        publish_date = (
            datetime.fromisoformat(article.datePublished)
            .astimezone(UTC)
            .replace(tzinfo=None)
        )
        url = content.permalink
        thumbnail_url = article.thumbnailUrl
        title_en = translate_response.title.en
        title_kr = translate_response.title.ko
        news = NewsEntity(
            author_en=author_en,
            author_kr=author_kr,
            content_en=" ".join(translate_response.summary.en),
            content_kr=" ".join(translate_response.summary.ko),
            publish_date=publish_date,
            url=url,
            source=SourceEnum.THE_ATHLETIC,
            source_id=content.consumable_id,
            thumbnail_url=thumbnail_url,
            title_en=title_en,
            title_kr=title_kr,
            typ=NewsTypeEnum.FULL_ARTICLE,
        )
        return await self.__news_repository.append_teams(
            news,
            [
                team
                for team in self.teams
                if team.abbreviation in translate_response.teams
            ],
        )

    async def __check_if_news_exists(self, news_id: str) -> bool:
        return (
            await self.__news_repository.read_by_source_id(
                SourceEnum.THE_ATHLETIC, news_id
            )
        ) is not None

    async def __get_openai_instruction(self) -> list[tuple[bool, str]]:
        """
        Gets the OpenAI instruction for the news item.
        :return: The instruction.
        """
        abbrs = {team.short_name_en: team.abbreviation for team in self.teams}
        return [
            (
                True,
                """You are an expert sports‐news translator. When given a JSON object containing an article, a title and an authors, you will:
- Read each object's author array and translate each 'name' from English into Korean.
- Read body of the article text and summarize it in 3–5 concise bullet points.
- For each bullet, provide both the original English sentence and its Korean translation.
- Identify any team names mentioned and include their official three‐letter abbreviations only for teams very closely related to the article’s content in a 'teams' list.
- Whenever monetary amounts appear, normalize them to ￡00m or €00m notation.
- Do not translate English acronyms (e.g., FA, PSR)—leave those as-is.""",
            ),
            (
                True,
                f"- Below is the list of teams and their abbreviations:\n```\n{dumps(abbrs)}\n```",
            ),
            (True, "- Output a single JSON object with this structure:"),
            (
                True,
                f"""```
{{
    "article": <article_index>,
    "authors": [
        {{ "en": "<Original English name>", "ko": "<Translated Korean name>" }},
        ...
    ],
    "title": {{
        "en": "<Original article title>",
        "ko": "<Translated Korean title>"
    }},
    "summary": {{
        "en": [ "<English summary point 1>", ... ],
        "ko": [ "<Korean translation 1>", ... ],
    }},
    "teams": [ "<Team 1>", ... ]
}}
```""",
            ),
        ]
