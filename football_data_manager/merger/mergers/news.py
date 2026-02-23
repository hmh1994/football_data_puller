import asyncio
import logging
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

logger = logging.getLogger(__name__)


class NewsMerger:
    """Merge The Athletic feed content into news entities."""

    _CONCURRENCY = 5

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
        self._semaphore = asyncio.Semaphore(self._CONCURRENCY)

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
        logger.info("Loading team short-name map")
        short_name_map = await self._get_team_short_name_map()
        logger.info("Loaded %d team short-names", len(short_name_map))

        created_news: list[NewsEntity] = []
        seen_consumable_ids: set[str] = set()

        for page in range(max_pages):
            logger.info("Pulling feed page %d/%d", page + 1, max_pages)
            feed = await self._news_puller.pull_league_feed(
                league_abbr=league_abbr, page=page
            )
            layouts = feed.feedMulligan.get("layouts", [])

            page_contents = [
                content
                for layout in layouts
                for content in layout.get("contents", [])
                if content.get("consumable_id")
            ]

            if not page_contents:
                logger.info("No articles on page %d, stopping", page + 1)
                break

            # Phase 1: filter new articles (sequential DB lookups)
            should_stop = False
            new_contents: list[dict] = []
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
                    logger.debug(
                        "Article %s already exists, marking stop", consumable_id
                    )
                    should_stop = True
                    continue

                new_contents.append(content)

            # Phase 2: scrape, translate, persist in parallel
            if new_contents:
                logger.info(
                    "Processing %d new articles on page %d (concurrency=%d)",
                    len(new_contents),
                    page + 1,
                    self._CONCURRENCY,
                )
                tasks = [
                    self._merge_one_content(content, short_name_map)
                    for content in new_contents
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, Exception):
                        logger.warning("Article processing failed: %s", result)
                    elif result is not None:
                        created_news.append(result)

            if should_stop:
                logger.info("Found existing article, stopping feed crawl")
                break

        return created_news

    async def _merge_one_content(
        self,
        content: dict,
        team_short_name_map: dict[str, str],
    ) -> NewsEntity | None:
        async with self._semaphore:
            return await self._process_one_content(content, team_short_name_map)

    async def _process_one_content(
        self,
        content: dict,
        team_short_name_map: dict[str, str],
    ) -> NewsEntity | None:
        permalink = content.get("permalink")
        consumable_id = content.get("consumable_id")
        if not permalink or not consumable_id:
            return None

        logger.info("Scraping article %s", consumable_id)
        article = await self._scrape_article(permalink)
        if article is None:
            return None
        if not article.articleBody:
            logger.warning("Article %s: no body content found", consumable_id)
            return None

        logger.info("Translating article %s", consumable_id)
        translated = await self._translate_article(
            article, team_short_name_map, int(consumable_id),
        )
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
        if created is not None:
            logger.info("Created news: %s", translated.title.get("en", "")[:80])
        return created

    async def _scrape_article(self, permalink: str) -> ArticleResponse | None:
        try:
            response = await self._http_client.get(permalink)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Scrape failed for %s: %s", permalink, exc)
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
        consumable_id: int,
    ) -> NewsTranslateResponse | None:
        if not article.articleBody:
            return None

        body = {
            "consumable_id": consumable_id,
            "authors": [author["name"] for author in article.author],
            "title": article.headline,
            "article": article.articleBody[:45000],
        }

        instruction = self._build_translation_instruction(team_short_name_map)
        user_prompt = dumps(body, ensure_ascii=False)

        last_error: Exception | None = None
        for attempt in range(1, 4):
            try:
                response = await self._anthropic_client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=2000,
                    temperature=0.0,
                    system=instruction,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                text = "".join(
                    block.text for block in response.content if hasattr(block, "text")
                )
                return self._parse_translation_response(text)
            except (
                anthropic.AnthropicError,
                ValidationError,
                JSONDecodeError,
                ValueError,
            ) as exc:
                last_error = exc
                logger.debug("Translation attempt %d/3: %s", attempt, exc)
                await asyncio.sleep(1)

        logger.warning(
            "Translation failed after 3 attempts: %s: %s",
            type(last_error).__name__, last_error,
        )
        return None

    @staticmethod
    def _build_translation_instruction(team_short_name_map: dict[str, str]) -> str:
        example = dumps(
            {
                "article": 12345,
                "authors": [{"en": "John Smith", "ko": "존 스미스"}],
                "title": {"en": "Original Title", "ko": "번역된 제목"},
                "summary": {
                    "en": ["bullet 1", "bullet 2"],
                    "ko": ["요약 1", "요약 2"],
                },
                "teams": ["ARS", "TOT"],
            },
            ensure_ascii=False,
        )
        return (
            "You are a sports-news translator and summarizer. "
            "Given JSON with authors/title/article in English, "
            "return ONLY one JSON object matching this exact schema:\n"
            f"{example}\n\n"
            "Field rules:\n"
            "- article: copy the consumable_id number from input as integer.\n"
            "- authors: list of objects, each with 'en' (original) and 'ko' (Korean) keys.\n"
            "- title: object with 'en' (original) and 'ko' (Korean translated) keys.\n"
            "- summary: object with 'en' (3-5 English bullets) and 'ko' (3-5 Korean bullets) keys.\n"
            "- teams: list of team abbreviations closely related to the article.\n"
            "- Leave football acronyms (e.g. VAR, XG) in English.\n\n"
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
