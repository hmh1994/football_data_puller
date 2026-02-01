from pydantic import BaseModel

from football_data_manager.puller.services.the_athletic.models.responses.the_athletic_league_feed_mulligan_response import (
    TheAthleticLeagueFeedMulliganResponse,
)


class TheAthleticLeagueFeedResponse(BaseModel):
    feedMulligan: TheAthleticLeagueFeedMulliganResponse
