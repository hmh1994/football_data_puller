from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.new_repositories import Base
from football_data_manager.common.new_repositories.constants import (
    TEAM_STATS_TABLE_NAME,
    FIXTURES_TABLE_NAME,
    TEAM_STAT_OVERALL_FIXTURE_ASSOCIATION_TABLE_NAME,
)


class TeamStatOverallFixtureAssociation(Base):
    __tablename__ = TEAM_STAT_OVERALL_FIXTURE_ASSOCIATION_TABLE_NAME

    TEAM_STAT_COLLECTION_NAME = "team_stat_overall_fixtures_association"
    FIXTURE_COLLECTION_NAME = "overall_fixture_associations"
    FIXTURE_ATTRIBUTE_NAME = "fixture"

    team_stat_id = Column(
        String, ForeignKey(f"{TEAM_STATS_TABLE_NAME}.id"), primary_key=True
    )
    fixture_id = Column(
        String, ForeignKey(f"{FIXTURES_TABLE_NAME}.id"), primary_key=True
    )
    # TODO: remove primary key constraint and add unique and non-null constraint from the `fixture_id`
    kickoff_time = Column(DateTime, nullable=False)

    team_stat = relationship(
        "TeamStatEntity",
        backref=backref(
            name=FIXTURE_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by="TeamStatOverallFixtureAssociation.kickoff_time",
        ),
    )
    fixture = relationship(
        "FixtureEntity", backref=backref(name=TEAM_STAT_COLLECTION_NAME, lazy="noload")
    )
