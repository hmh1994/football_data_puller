from asyncio import sleep, gather
from datetime import datetime, UTC
from json import loads, dumps

from aiohttp import request
from bs4 import BeautifulSoup
from regex import compile

from football_data_manager.common.repositories.news.news_entity import NewsEntity
from football_data_manager.common.repositories.news.news_repository import (
    NewsRepository,
)
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
from football_data_manager.common.repositories.teams.team_repository import (
    TeamRepository,
)
from football_data_manager.common.services.client.openai_client_service import (
    OpenAIClientService,
)
from football_data_manager.common.services.config.models.api_config import ApiConfig
from football_data_manager.common.services.db.db_service import DbService
from football_data_manager.common.utils.type_helper.list_helper import remove_duplicates
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
    __graphql_service: TheAthleticGraphQLService
    __openai_service: OpenAIClientService
    __news_repository: NewsRepository
    __team_repository: TeamRepository

    target_competition_abbr = ["EN_PR"]
    teams: list[TeamEntity]
    translate_instruction: str

    def __init__(
        self,
        openai_config: ApiConfig,
        the_athletic_config: ApiConfig,
        db_service: DbService,
    ):
        self.__news_repository = NewsRepository(db_service)
        self.__team_repository = TeamRepository(db_service)
        self.__graphql_service = TheAthleticGraphQLService(the_athletic_config)
        self.__openai_service = OpenAIClientService(
            api_key=openai_config.key, default_model="o4-mini"
        )

    async def pull_news(self):
        self.teams = await self.__team_repository.read_all()
        self.translate_instruction = await self.__get_openai_instruction()
        news_list = await gather(
            *[
                self.__pull_league_news_list(abbr)
                for abbr in self.target_competition_abbr
            ]
        )
        news_list = remove_duplicates(
            [n for sublist in news_list for n in sublist],
            lambda x: x.id,
        )
        print(f"News entities count: {len(news_list)}")
        await self.__news_repository.create_all(news_list, primary_key=lambda x: x.id)

    async def __pull_league_news_list(self, league_abbr: str) -> list[NewsEntity]:
        """
        Pulls league news list from The Athletic API.
        :param league_abbr: League abbreviation.
        :return: List of news items.
        """
        print(f"Pulling league news list for {league_abbr}")
        contents = await self.__pull_news_list(league_abbr)
        print(f"News pulled from The Athletic: {len(contents)}")
        news: list[list[NewsEntity]] = await gather(
            *[self.__pull_news_entity(c) for c in contents]
        )
        return [n for sublist in news for n in sublist]

    async def __pull_news_entity(
        self, content: TheAthleticLeagueFeedMulliganLayoutContentResponse
    ) -> list[NewsEntity]:
        """
        Pulls news entity from The Athletic API.
        :param content: The content object.
        :return: The news entity.
        """
        article = await self.__pull_news_body(content)
        if article is None:
            return []
        print(f"News entity pulled: [{content.consumable_id}] {article.headline}")
        translate_response = await self.__translate_article(article)
        if translate_response is None:
            return []
        print(
            f"News entity translated: [{content.consumable_id}] {article.headline} - {len(translate_response.summaries)} summaries"
        )
        return self.__process_news(content, article, translate_response)

    async def __pull_news_list(
        self, league_abbr: str
    ) -> list[TheAthleticLeagueFeedMulliganLayoutContentResponse]:
        """
        Pulls news list from The Athletic API.
        :param league_abbr: League abbreviation.
        :return: List of news items.
        """
        contents = []
        page = 0
        while page < 5:
            response = await self.__graphql_service.get_league_feed(league_abbr, page)
            new_contents = [
                c
                for r in response.feedMulligan.layouts
                for c in r.contents
                if c.consumable_id is not None
            ]
            filtered_contents = [
                c
                for c in new_contents
                if not (await self.__check_if_news_exists(c.consumable_id))
            ]
            print(f"League feed response from page {page}: {len(filtered_contents)}")
            contents.extend(filtered_contents)
            if len(new_contents) != len(filtered_contents):
                break
            page += 1
        return contents

    @staticmethod
    async def __pull_news_body(
        content: TheAthleticLeagueFeedMulliganLayoutContentResponse,
    ) -> TheAthleticArticleResponse | None:
        """
        Pulls the body of a news item from The Athletic API.
        :param content: The content object.
        :return: The article response.
        """
        async with request("GET", content.permalink) as resp:
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
                response = await self.__openai_service.request_by_flex_processing(
                    instructions=self.translate_instruction,
                    message=f"Here is the article to process. Please apply the above rules and return the JSON-formatted summaries only:\n```\n{dumps(body)}\n```",
                    model="o4-mini",
                )
                return NewsTranslateResponse.model_validate(
                    loads(
                        max(compile(r"\{(?:[^{}]|(?R))*\}").findall(response), key=len)
                    )
                )
            except Exception as e:
                print(f"Translation error: {e}")
                await sleep(1)
                try_count += 1
        return None

    def __process_news(
        self,
        content: TheAthleticLeagueFeedMulliganLayoutContentResponse,
        article: TheAthleticArticleResponse,
        translate_response: NewsTranslateResponse,
    ) -> list[NewsEntity]:
        """
        Processes the news item and creates a NewsEntity object.
        :param content: The content object.
        :param article: The article response.
        :param translate_response: The translation response.
        :return: The NewsEntity object.
        """
        news_list = []
        author_en = [a.en for a in translate_response.authors]
        author_kr = [a.ko for a in translate_response.authors]
        publish_date = (
            datetime.fromisoformat(article.datePublished)
            .astimezone(UTC)
            .replace(tzinfo=None)
        )
        url = content.permalink
        source = "The Athletic"
        thumbnail_url = article.thumbnailUrl
        title_en = translate_response.title.en
        title_kr = translate_response.title.ko
        typ = "FULL_ARTICLE"
        for idx, summary in enumerate(translate_response.summaries):
            teams = [
                team.id for team in self.teams if team.abbreviation in summary.teams
            ]
            news_list.append(
                NewsEntity(
                    id=NewsEntity.get_the_athletic_id(content.consumable_id, idx),
                    author_en=author_en,
                    author_kr=author_kr,
                    content_en=" ".join(summary.en),
                    content_kr=" ".join(summary.ko),
                    publish_date=publish_date,
                    url=url,
                    source=source,
                    teams=teams,
                    thumbnail_url=thumbnail_url,
                    title_en=title_en,
                    title_kr=title_kr,
                    type=typ,
                )
            )
        return news_list

    async def __check_if_news_exists(self, news_id: str) -> bool:
        """
        Checks if the news already exists in the database.
        :param news_id: News ID.
        :return: True if exists, False otherwise.
        """
        return (
            await self.__news_repository.read_by_id(
                NewsEntity.get_the_athletic_id(news_id, 1)
            )
        ) is not None

    async def __get_openai_instruction(self) -> str:
        """
        Gets the OpenAI instruction for the news item.
        :return: The instruction.
        """
        abbrs = {team.short_name_en: team.abbreviation for team in self.teams}
        return f"""You are an expert sports‐news summarization assistant.
When given one or more JSON objects each containing an article, a title and an authors, you will:
- Read each object’s author array and translate each "name" from English into Korean.
- Read the articleBody text.
- Produce 3–5 concise bullet summaries of the article’s main points.
- For each bullet, provide both the original English sentence and its Korean translation.
- Identify any team names mentioned and include their official three‐letter abbreviations only for teams very closely related to the article’s content in a "teams" list.
  Below is the list of teams and their abbreviations:
  ```
{dumps(abbrs)}
  ```
- If the article covers multiple distinct topics, break your summaries into separate sections accordingly.
- Do not create multiple sections with very similar content; group related points into a single section.
- Provide all summaries in a concise, to-the-point tone.
- Whenever monetary amounts appear, normalize them to ￡00m or €00m notation.
- Do not translate English acronyms (e.g., FA, PSR)—leave those as-is.
- Output a single JSON object with this structure:
  ```
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
    "summaries": [
      {{
        "summary": <section_index>,
        "en": [ "<English summary point 1>", ... ],
        "ko": [ "<Korean translation 1>", ... ],
        "teams": [ "<Team 1>", ... ]
      }},
      ...
    ]
  }}
  ```"""
