from pydantic import BaseModel

from football_data_manager.puller.services.the_athletic.models.responses.the_athletic_league_feed_mulligan_layout_response import (
    TheAthleticLeagueFeedMulliganLayoutResponse,
)


class TheAthleticLeagueFeedMulliganResponse(BaseModel):
    __typename: str
    layouts: list[TheAthleticLeagueFeedMulliganLayoutResponse]
