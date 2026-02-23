from asyncio import sleep
from datetime import UTC, datetime
from json import JSONDecodeError, dumps, loads

import anthropic
import httpx
from bs4 import BeautifulSoup
from pydantic import ValidationError
from regex import compile

from football_data_manager.common.enums.news_type_enum import NewsTypeEnum
from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.common.services.config.config_service import ConfigService
from football_data_manager.puller.interfaces.the_athletic.news import (
    ArticleResponse,
    NewsTranslateResponse,
)
from football_data_manager.puller.pullers.the_athletic.news import NewsPuller
from football_data_manager.repository.entities.news import NewsEntity
from football_data_manager.repository.entities.teams import TeamEntity
from football_data_manager.repository.repositories.news import NewsRepository
from football_data_manager.repository.repositories.teams import TeamRepository


class NewsMerger:
    """Merge The Athletic feed content into news entities."""

    def __init__(
        self,
        news_repo: NewsRepository,
        team_repo: TeamRepository,
        news_puller: NewsPuller,
        config_service: ConfigService,
    ):
        self._news_repo = news_repo
        self._team_repo = team_repo
        self._news_puller = news_puller

        api_key = config_service.api_list.anthropic.key or ""
        self._anthropic_client = anthropic.AsyncAnthropic(api_key=api_key)
        self._http_client = httpx.AsyncClient(
            timeout=20,
            follow_redirects=True,
            headers={"User-Agent": "FootballDataManager/1.0"},
        )

    async def merge_league_feed(
        self,
        league_abbr: str = "EN_PR",
        max_pages: int = 5,
    ) -> list[NewsEntity]:
        """Pull league feed pages, scrape, translate, and persist news rows."""
        short_name_map = await self._get_team_short_name_map()

        created_news: list[NewsEntity] = []
        seen_consumable_ids: set[str] = set()

        for page in range(max_pages):
            feed = await self._news_puller.pull_league_feed(league_abbr=league_abbr, page=page)
            layouts = feed.feedMulligan.get("layouts", [])

            page_contents = [
                content
                for layout in layouts
                for content in layout.get("contents", [])
                if content.get("consumable_id")
            ]

            if not page_contents:
                break

            should_stop = False
            for content in page_contents:
                consumable_id = str(content["consumable_id"])
                if consumable_id in seen_consumable_ids:
                    continue
                seen_consumable_ids.add(consumable_id)

                existing = await self._news_repo.get_by_source(
                    SourceEnum.THE_ATHLETIC,
                    consumable_id,
                )
                if existing is not None:
                    should_stop = True
                    continue

                news_entity = await self._merge_one_content(content, short_name_map)
                if news_entity is not None:
                    created_news.append(news_entity)

            if should_stop:
                break

        return created_news

    async def _merge_one_content(
        self,
        content: dict,
        team_short_name_map: dict[str, str],
    ) -> NewsEntity | None:
        permalink = content.get("permalink")
        consumable_id = content.get("consumable_id")
        if not permalink or not consumable_id:
            return None

        article = await self._scrape_article(permalink)
        if article is None or not article.articleBody:
            return None

        translated = await self._translate_article(article, team_short_name_map)
        if translated is None:
            return None

        publish_date = self._parse_publish_date(article.datePublished)
        if publish_date is None:
            return None

        news = NewsEntity(
            author_en=[author["en"] for author in translated.authors],
            author_kr=[author["ko"] for author in translated.authors],
            content_en=" ".join(translated.summary["en"]),
            content_kr=" ".join(translated.summary["ko"]),
            publish_date=publish_date,
            url=permalink,
            source=SourceEnum.THE_ATHLETIC,
            source_id=str(consumable_id),
            thumbnail_url=article.thumbnailUrl,
            title_en=translated.title["en"],
            title_kr=translated.title["ko"],
            typ=NewsTypeEnum.FULL_ARTICLE,
        )

        teams = await self._resolve_teams(translated.teams)
        news = await self._news_repo.append_teams(news, teams)

        created = await self._news_repo.create(news)
        return created

    async def _scrape_article(self, permalink: str) -> ArticleResponse | None:
        try:
            response = await self._http_client.get(permalink)
            response.raise_for_status()
        except httpx.HTTPError:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        article_body = None
        next_data_tag = soup.find("script", id="__NEXT_DATA__")
        if next_data_tag and next_data_tag.string:
            try:
                next_data = loads(next_data_tag.string.strip())
                article_body = (
                    next_data.get("props", {})
                    .get("pageProps", {})
                    .get("article", {})
                    .get("article_body")
                )
            except JSONDecodeError:
                article_body = None

        ld_json_candidates = soup.find_all("script", type="application/ld+json")
        for script_tag in ld_json_candidates:
            if not script_tag.string:
                continue
            try:
                parsed = loads(script_tag.string.strip())
            except JSONDecodeError:
                continue

            candidate = None
            if isinstance(parsed, dict):
                candidate = parsed
            elif isinstance(parsed, list):
                candidate = next(
                    (
                        item
                        for item in parsed
                        if isinstance(item, dict) and item.get("headline")
                    ),
                    None,
                )

            if not candidate:
                continue

            if isinstance(candidate.get("author"), dict):
                candidate["author"] = [candidate["author"]]

            try:
                article = ArticleResponse.model_validate(candidate)
            except ValidationError:
                continue

            article.articleBody = article_body
            return article

        return None

    async def _translate_article(
        self,
        article: ArticleResponse,
        team_short_name_map: dict[str, str],
    ) -> NewsTranslateResponse | None:
        if not article.articleBody:
            return None

        body = {
            "authors": [author["name"] for author in article.author],
            "title": article.headline,
            "article": article.articleBody[:45000],
        }

        instruction = self._build_translation_instruction(team_short_name_map)
        user_prompt = dumps(body, ensure_ascii=False)

        retry = 0
        while retry < 5:
            try:
                response = await self._anthropic_client.messages.create(
                    model="claude-3-5-haiku-latest",
                    max_tokens=2000,
                    temperature=0.0,
                    system=instruction,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                text = "".join(
                    block.text for block in response.content if hasattr(block, "text")
                )
                return self._parse_translation_response(text)
            except (anthropic.AnthropicError, ValidationError, JSONDecodeError, ValueError):
                retry += 1
                await sleep(1)

        return None

    @staticmethod
    def _build_translation_instruction(team_short_name_map: dict[str, str]) -> str:
        return (
            "You are a sports-news translator and summarizer. "
            "Given JSON with authors/title/article in English, return one JSON object with keys: "
            "article, authors, title, summary, teams.\n"
            "Rules:\n"
            "- Translate title and author names to Korean.\n"
            "- Summarize article into 3-5 bullets for both English and Korean.\n"
            "- Detect only closely related teams and return team abbreviations.\n"
            "- Leave football acronyms in English.\n"
            "Team short-name to abbreviation map:\n"
            f"{dumps(team_short_name_map, ensure_ascii=False)}"
        )

    @staticmethod
    def _parse_translation_response(text: str) -> NewsTranslateResponse:
        json_candidates = compile(r"\{(?:[^{}]|(?R))*\}").findall(text)
        if not json_candidates:
            raise ValueError("No JSON object found in translation response")

        payload = loads(max(json_candidates, key=len))
        return NewsTranslateResponse.model_validate(payload)

    async def _resolve_teams(self, team_abbreviations: list[str]) -> list[TeamEntity]:
        teams: list[TeamEntity] = []
        seen: set[str] = set()

        for abbreviation in team_abbreviations:
            if abbreviation in seen:
                continue
            seen.add(abbreviation)

            team = await self._team_repo.get_by_abbreviation(abbreviation)
            if team is not None:
                teams.append(team)

        return teams

    async def _get_team_short_name_map(self) -> dict[str, str]:
        teams = await self._team_repo.get_all()
        return {
            team.short_name_en: team.abbreviation
            for team in teams
            if team.short_name_en and team.abbreviation
        }

    @staticmethod
    def _parse_publish_date(date_string: str) -> datetime | None:
        try:
            return (
                datetime.fromisoformat(date_string.replace("Z", "+00:00"))
                .astimezone(UTC)
                .replace(tzinfo=None)
            )
        except ValueError:
            return None

    async def close(self) -> None:
        """Release network resources used by NewsMerger."""
        await self._http_client.aclose()
        if hasattr(self._anthropic_client, "close"):
            maybe_awaitable = self._anthropic_client.close()
            if hasattr(maybe_awaitable, "__await__"):
                await maybe_awaitable
