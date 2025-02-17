from football_data_manager.common.repositories.players.player_entity import PlayerEntity
from football_data_manager.common.repositories.players.player_repository import (
    PlayerRepository,
)
from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_datetime,
)
from tests.common.repositories.sample_data.abstract_sample_data import (
    AbstractSampleData,
)
from tests.common.repositories.sample_data.team_sample_data import TeamSampleData
from tests.common.utils.random import random_string


class PlayerSampleData(AbstractSampleData[PlayerRepository, PlayerEntity, str]):
    """
    Player sample data.
    """

    @property
    def prerequisites(self) -> list[type[AbstractSampleData]]:
        return [TeamSampleData]

    @property
    def entity_list(self) -> list[PlayerEntity]:
        return [
            PlayerEntity(
                id="PULSELIVE_PLAYER_92622",
                birth_country="Netherlands",
                birth_date=create_utc_datetime(1991, 7, 8),
                birth_place="Breda",
                current_team_id="PULSELIVE_TEAM_10",
                display_name_en="Virgil van Dijk",
                display_name_kr="버질 반 다이크",
                full_name="Virgil van Dijk",
                height=195,
                loan=False,
                national_team="Netherlands",
                number=4,
                photo_url="https://resources.premierleague.com/premierleague"
                + "/photos/players/40x40/p97032.png",
                position="D",
                position_info_en="Centre Central Defender",
                position_info_kr="중앙 수비수",
                weight=92,
            ),
            PlayerEntity(
                id="PULSELIVE_PLAYER_180060",
                birth_country="Portugal",
                birth_date=create_utc_datetime(1994, 9, 8),
                birth_place="Maia",
                current_team_id="PULSELIVE_TEAM_12",
                display_name_en="Bruno Fernandes",
                display_name_kr="브루노 페르난데스",
                full_name="Bruno Miguel Borges Fernandes",
                height=179,
                loan=False,
                national_team="Portugal",
                number=18,
                photo_url="https://resources.premierleague.com/premierleague"
                + "/photos/players/40x40/p141746.png",
                position="M",
                position_info_en="Left/Centre/Right Attacking Midfielder",
                position_info_kr="왼쪽/중앙/오른쪽 공격형 미드필더",
                weight=66,
            ),
            PlayerEntity(
                id="PULSELIVE_PLAYER_288147",
                birth_country="Norway",
                birth_date=create_utc_datetime(1998, 12, 17),
                birth_place="Drammen",
                current_team_id="PULSELIVE_TEAM_1",
                display_name_en="Martin Ødegaard",
                display_name_kr="마르틴 외데고르",
                full_name="Martin Ødegaard",
                height=178,
                loan=False,
                national_team="Norway",
                number=8,
                photo_url="https://resources.premierleague.com/premierleague"
                + "/photos/players/40x40/p184029.png",
                position="M",
                position_info_en="Left/Centre/Right Attacking Midfielder",
                position_info_kr="왼쪽/중앙/오른쪽 공격형 미드필더",
                weight=68,
            ),
        ]

    @staticmethod
    def repository_instance(db_service) -> PlayerRepository:
        return PlayerRepository(db_service)

    @staticmethod
    def random_id() -> str:
        return random_string(20)
