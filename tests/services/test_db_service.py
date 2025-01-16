from sqlite3 import OperationalError

from pytest import fixture, raises
from sqlalchemy import text

from football_data_puller.services.db.db_service import DbService
from tests.services.mocks import gen_config_service_mock


class TestDbService:
    """
    Test cases for DbService class.
    :ivar config_service_mock: ConfigService mock.
    """

    config_service_mock = gen_config_service_mock(
        db_database_name=":memory:",
        db_driver_name="sqlite",
    )

    @fixture
    def db_service(self) -> DbService:
        """
        Creates a DbService instance.
        :return: DbService instance for config service mock.
        """
        return DbService(self.config_service_mock)

    def test_check_connection_success(self, db_service: DbService):
        """
        Tests the check_connection is working on normal conditions.
        """
        assert db_service.check_connection(), "Connection failed."

    def test_check_connection_failure(self, monkeypatch, db_service: DbService):
        """
        Tests the check_connection is working on connection failure.
        """
        # noinspection PyUnresolvedReferences
        monkeypatch.setattr(db_service._DbService__engine, "connect",
                            lambda: (_ for _ in ()).throw(OperationalError("Fake connection error", {}, None)))
        assert not db_service.check_connection(), "Connection succeeded."

    def test_create_db_session_commit(self, db_service: DbService):
        """
        Tests the create_db_session is working on normal conditions.
        """
        with db_service.create_db_session() as session:
            result = session.execute(text("SELECT 1")).scalar()
            assert result == 1, "Session commit did not work."

    def test_create_db_session_exception(self, monkeypatch, db_service: DbService):
        """
        Tests the create_db_session is working on exception.
        """
        commit_msg = "Commit failed."

        class FakeSession:
            def __init__(self):
                self.closed = False
                self.committed = False
                self.rolled_back = False
                self.tried_to_commit = False

            def commit(self):
                self.tried_to_commit = True
                raise Exception(commit_msg)
                # noinspection PyUnreachableCode
                self.committed = True

            def rollback(self):
                self.rolled_back = True

            def close(self):
                self.closed = True

        # noinspection PyUnresolvedReferences
        monkeypatch.setattr(db_service, "_DbService__session", lambda: FakeSession())
        with raises(Exception) as exc_info:
            with db_service.create_db_session() as session:
                pass
        assert commit_msg in str(exc_info.value)
        assert session.tried_to_commit, "Session not tried to commit."
        assert session.rolled_back, "Session not rolled back."
        assert session.closed, "Session not closed."
        assert not session.committed, "Session committed."
