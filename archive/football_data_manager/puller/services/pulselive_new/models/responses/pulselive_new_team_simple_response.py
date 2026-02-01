from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveNewTeamSimpleResponse(CamelCaseModel):
    """
    Simple team information from PulseLive API.
    
    Contains basic team details typically used in statistics responses.
    
    :ivar id: Team ID
    :ivar name: Full team name
    :ivar short_name: Shortened team name
    :ivar abbr: Team abbreviation
    """
    
    id: str
    name: str
    short_name: str
    abbr: str