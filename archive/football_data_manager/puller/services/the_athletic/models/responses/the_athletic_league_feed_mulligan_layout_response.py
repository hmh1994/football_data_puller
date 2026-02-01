from pydantic import BaseModel

from football_data_manager.puller.services.the_athletic.models.responses.the_athletic_league_feed_mulligan_layout_content_response import (
    TheAthleticLeagueFeedMulliganLayoutContentResponse,
)


class TheAthleticLeagueFeedMulliganLayoutResponse(BaseModel):
    __typename: str
    type: str
    typename: str
    contents: list[TheAthleticLeagueFeedMulliganLayoutContentResponse]
