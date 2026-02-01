from pydantic import BaseModel

from football_data_manager.puller.services.the_athletic.models.responses.the_athletic_league_feed_mulligan_layout_content_author_response import (
    TheAthleticLeagueFeedMulliganLayoutContentAuthorResponse,
)


class TheAthleticLeagueFeedMulliganLayoutContentResponse(BaseModel):
    __typename: str
    title: str | None = None
    consumable_id: str | None = None
    author: TheAthleticLeagueFeedMulliganLayoutContentAuthorResponse | None = None
    excerpt: str | None = None
    image_uri: str | None = None
    permalink: str | None = None
