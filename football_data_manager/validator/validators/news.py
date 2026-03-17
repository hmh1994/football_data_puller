from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from football_data_manager.common.enums.news_type_enum import NewsTypeEnum
from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_now,
)
from football_data_manager.repository.entities.news import NewsEntity
from football_data_manager.repository.entities.news_team_association import (
    NewsTeamAssociation,
)
from football_data_manager.repository.entities.teams import TeamEntity
from football_data_manager.validator.validators.base import (
    AbstractValidator,
    ValidationResult,
)


class NewsValidator(AbstractValidator):
    """News entity validation."""

    async def validate(
        self,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> ValidationResult:
        _ = season_id, competition_id
        result = ValidationResult(entity="news")
        now = create_utc_now()

        async with self._session_factory.session() as session:
            news_items = (
                await session.execute(
                    select(NewsEntity).options(
                        selectinload(NewsEntity.team_associations)
                    )
                )
            ).scalars().all()
            if not news_items:
                result.add_warning("data_exists", detail="No News records found")
                return result

            team_ids = await self._load_id_set(session, TeamEntity)

            for news in news_items:
                entity_id = news.id
                self.check_not_empty(result, "title_en not empty", news.title_en, entity_id)
                self.check_not_empty(result, "title_kr not empty", news.title_kr, entity_id)
                self.check_not_empty(
                    result,
                    "content_en not empty",
                    news.content_en,
                    entity_id,
                )
                self.check_not_empty(
                    result,
                    "content_kr not empty",
                    news.content_kr,
                    entity_id,
                )
                self.check_not_empty(
                    result,
                    "author_en non-empty",
                    news.author_en,
                    entity_id,
                )
                self.check_not_empty(
                    result,
                    "author_kr non-empty",
                    news.author_kr,
                    entity_id,
                )
                self.check_true(
                    result,
                    "author list lengths match",
                    len(news.author_en) == len(news.author_kr),
                    entity_id,
                    detail=(
                        f"len(author_en)={len(news.author_en)}, "
                        f"len(author_kr)={len(news.author_kr)}"
                    ),
                )
                self.check_not_empty(result, "url not empty", news.url, entity_id)
                self.check_not_empty(
                    result,
                    "thumbnail_url not empty",
                    news.thumbnail_url,
                    entity_id,
                )
                self.check_true(
                    result,
                    "publish_date <= now",
                    news.publish_date <= now,
                    entity_id,
                    detail=f"publish_date={news.publish_date}",
                )
                self.check_true(
                    result,
                    "type valid",
                    isinstance(news.type, NewsTypeEnum),
                    entity_id,
                    detail=f"type={news.type}",
                )
                self.check_true(
                    result,
                    "source valid",
                    isinstance(news.source, SourceEnum),
                    entity_id,
                    detail=f"source={news.source}",
                )

                for association in list(news.team_associations):
                    self.check_fk_exists(
                        result,
                        "team_association FK",
                        association.team_id,
                        team_ids,
                        entity_id,
                    )

        return result

