from football_data_manager.common.old_repositories.teams.team_entity import TeamEntity
from football_data_manager.common.old_repositories.teams.team_repository import (
    TeamRepository,
)
from football_data_manager.common.services.db.db_service import DbService
from tests.common.repositories.sample_data.abstract_sample_data import (
    AbstractSampleData,
)
from tests.common.repositories.sample_data.ground_sample_data import GroundSampleData
from tests.common.utils.random import random_string


class TeamSampleData(AbstractSampleData[TeamRepository, TeamEntity, str]):
    """
    Team sample data.
    """

    @property
    def prerequisites(self) -> list[type[AbstractSampleData]]:
        return [GroundSampleData]

    @property
    def entity_list(self) -> list[TeamEntity]:
        return [
            TeamEntity(
                id="PULSELIVE_TEAM_1",
                abbreviation="ARS",
                ground_id="PULSELIVE_GROUND_52",
                name_en="Arsenal",
                name_kr="아스널",
                icon_url="https://resources.premierleague.com/premierleague"
                + "/badges/50/t3@x2.png",
                short_name_en="Arsenal",
                short_name_kr="아스널",
            ),
            TeamEntity(
                id="PULSELIVE_TEAM_10",
                abbreviation="LIV",
                ground_id="PULSELIVE_GROUND_7305",
                name_en="Liverpool",
                name_kr="리버풀",
                icon_url="https://resources.premierleague.com/premierleague"
                + "/badges/50/t14@x2.png",
                short_name_en="Liverpool",
                short_name_kr="리버풀",
            ),
            TeamEntity(
                id="PULSELIVE_TEAM_12",
                abbreviation="MUN",
                ground_id="PULSELIVE_GROUND_42",
                name_en="Manchester United",
                name_kr="맨체스터 유나이티드",
                icon_url="https://resources.premierleague.com/premierleague"
                + "/badges/50/t1@x2.png",
                short_name_en="Man Utd",
                short_name_kr="맨유",
            ),
        ]

    @staticmethod
    def repository_instance(db_service: DbService) -> TeamRepository:
        return TeamRepository(db_service)

    @staticmethod
    def random_id() -> str:
        return random_string(20)
