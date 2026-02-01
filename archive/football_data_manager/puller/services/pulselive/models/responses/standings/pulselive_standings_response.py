from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive.models.responses.standings.pulselive_standings_comp_season_response import (
    PulseliveStandingsCompSeasonResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.standings.pulselive_standings_table_response import (
    PulseliveStandingsTableResponse,
)


class PulseliveStandingsResponse(CamelCaseModel):
    comp_season: PulseliveStandingsCompSeasonResponse
    live: bool
    dynamically_generated: bool
    tables: list[PulseliveStandingsTableResponse]
