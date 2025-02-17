from football_data_puller.repositories.grounds.ground_entity import GroundEntity
from football_data_puller.repositories.grounds.ground_repository import GroundRepository
from football_data_puller.services.db.db_service import DbService
from tests.repositories.sample_data.abstract_sample_data import AbstractSampleData
from tests.utils.random import random_string


class GroundSampleData(AbstractSampleData[GroundRepository, GroundEntity, str]):
    """
    Ground sample data.
    """

    @property
    def prerequisites(self) -> list[type[AbstractSampleData]]:
        return []

    @property
    def entity_list(self) -> list[GroundEntity]:
        return [
            GroundEntity(
                id="PULSELIVE_GROUND_42",
                capacity=75635,
                city_name_en="Manchester",
                city_name_kr="맨체스터",
                location_latitude=53.4626,
                location_longitude=-2.29103,
                name_en="Old Trafford",
                name_kr="올드 트래포드",
            ),
            GroundEntity(
                id="PULSELIVE_GROUND_52",
                capacity=60272,
                city_name_en="London",
                city_name_kr="런던",
                location_latitude=51.5548,
                location_longitude=-0.108533,
                name_en="Emirates Stadium",
                name_kr="에미레이츠 스타디움",
            ),
            GroundEntity(
                id="PULSELIVE_GROUND_7305",
                capacity=61276,
                city_name_en="Liverpool",
                city_name_kr="리버풀",
                location_latitude=53.4313,
                location_longitude=-2.96158,
                name_en="Anfield",
                name_kr="안필드",
            ),
        ]

    @staticmethod
    def repository_instance(db_service: DbService) -> GroundRepository:
        return GroundRepository(db_service)

    @staticmethod
    def random_id() -> str:
        return random_string(20)
