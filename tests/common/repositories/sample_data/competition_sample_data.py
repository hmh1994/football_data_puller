from football_data_manager.common.repositories.competitions.competition_repository import (
    CompetitionEntity,
    CompetitionRepository,
)
from football_data_manager.common.services.db.db_service import DbService
from tests.common.repositories.sample_data.abstract_sample_data import (
    AbstractSampleData,
)
from tests.common.utils.random import random_string


class CompetitionSampleData(
    AbstractSampleData[CompetitionRepository, CompetitionEntity, str]
):
    """
    Sample data for CompetitionRepository.
    """

    @property
    def prerequisites(self) -> list[type[AbstractSampleData]]:
        return []

    @property
    def entity_list(self) -> list[CompetitionEntity]:
        return [
            CompetitionEntity(
                id="PULSELIVE_COMPETITION_1",
                abbreviation="EN_PR",
                description_en="The Premier League is a professional "
                + "association football league in England and the highest level "
                + "of the English football league system.",
                description_kr="프리미어리그 또는 잉글랜드 외의 지역에서 구분을 위해 잉글리쉬 "
                + "프리미어리그는 1992년에 시작한 잉글랜드의 최상위 축구 리그이다.",
                icon_url="https://resources.premierleague.com/premierleague"
                + "/competitions/competition_1_small.png",
                name_en="Premier League",
                name_kr="프리미어리그",
            ),
            CompetitionEntity(
                id="PULSELIVE_COMPETITION_2",
                abbreviation="EU_CL",
                description_en="The UEFA Champions League is an annual club "
                + "association football competition organised by the Union of "
                + "European Football Associations (UEFA) that is contested by "
                + "top-division European clubs.",
                description_kr="UEFA 챔피언스리그(UEFA Champions League)는 유럽 최상위 "
                + "축구 리그의 가장 우수한 축구 클럽들을 대상으로 유럽 축구 연맹이 주관하는 클럽 "
                + "축구 대회이다.",
                icon_url="https://resources.premierleague.com/premierleague"
                + "/competitions/competition_2_small.png",
                name_en="UEFA Champions League",
                name_kr="UEFA 챔피언스리그",
            ),
            CompetitionEntity(
                id="PULSELIVE_COMPETITION_3",
                abbreviation="EU_UC",
                description_en="The UEFA Europa League is an annual football "
                + "club competition organised since 1971 by the Union of "
                + "European Football Associations (UEFA) for eligible European "
                + "football clubs.",
                description_kr="UEFA 유로파리그는 1971년부터 UEFA가 주관하는 유럽 축구 "
                + "클럽들을 위한 대회이다.",
                icon_url="https://resources.premierleague.com/premierleague"
                + "/competitions/competition_3_small.png",
                name_en="UEFA Europa League",
                name_kr="UEFA 유로파리그",
            ),
            CompetitionEntity(
                id="PULSELIVE_COMPETITION_4",
                abbreviation="EN_FA",
                description_en="The Football Association Challenge Cup is an "
                + "annual knockout football competition in domestic English "
                + "football.",
                description_kr="FA컵은 잉글랜드 축구 협회에서 주관하는 토너먼트 축구 대회이다.",
                icon_url="https://resources.premierleague.com/premierleague"
                + "/competitions/competition_4_small.png",
                name_en="FA Cup",
                name_kr="FA컵",
            ),
            CompetitionEntity(
                id="PULSELIVE_COMPETITION_5",
                abbreviation="EN_LC",
                description_en="The English Football League Cup is an annual "
                + "knockout competition in men's domestic football in England.",
                description_kr="EFL컵, 일반적으로 리그컵이라고 알려진 이 대회는 잉글랜드의 축구 대회이다.",
                icon_url="https://resources.premierleague.com/premierleague"
                + "/competitions/competition_5_small.png",
                name_en="EFL Cup",
                name_kr="EFL컵",
            ),
            CompetitionEntity(
                id="PULSELIVE_COMPETITION_2247",
                abbreviation="EU_CF",
                description_en="The UEFA Conference League is an annual "
                + "football competition organised since 2021 by the Union of "
                + "European Football Associations (UEFA) for eligible European "
                + "football clubs.",
                description_kr="UEFA 컨퍼런스리그는 2021년에 출범한 유럽 축구 연맹(UEFA)의 "
                + "축구 클럽 대회이다.",
                icon_url="https://resources.premierleague.com/premierleague"
                + "/competitions/competition_2247_small.png",
                name_en="UEFA Conference League",
                name_kr="UEFA 컨퍼런스리그",
            ),
        ]

    @staticmethod
    def repository_instance(db_service: DbService) -> CompetitionRepository:
        return CompetitionRepository(db_service)

    @staticmethod
    def random_id() -> str:
        return random_string(20)
