from sqlite3 import OperationalError

from pytest import fixture, raises, mark
from sqlalchemy import text

from football_data_manager.common.services.db.db_service import DbService
from tests.common.services.mocks import gen_db_service_mock


class TestDbService:
    """
    Test cases for DbService class.
    """

    @fixture
    def db_service(self) -> DbService:
        """
        Creates a DbService instance.
        :return: DbService instance for config service mock.
        """
        return gen_db_service_mock()

    @mark.asyncio
    async def test_check_connection_success(self, db_service: DbService):
        """
        Tests the check_connection is working on normal conditions.
        :param db_service: Pytest database service fixture.
        """
        assert await db_service.check_connection(), "Connection failed."

    @mark.asyncio
    async def test_check_connection_failure(self, monkeypatch, db_service: DbService):
        """
        Tests the check_connection is working on connection failure.
        :param monkeypatch: Pytest monkeypatch fixture.
        :param db_service: Pytest database service fixture.
        """

        class FakeEngine:
            async def connect(self):
                raise OperationalError("Fake connection error", {}, None)

        monkeypatch.setattr(db_service, "engine", lambda: FakeEngine())
        assert (
            not await db_service.check_connection()
        ), "Connection succeeded unexpectedly."

    @mark.asyncio
    async def test_create_db_session_commit(self, db_service: DbService):
        """
        Tests the create_db_session is working on normal conditions.
        :param db_service: Pytest database service fixture.
        """
        async with db_service.create_db_session() as session:
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1, "Session commit did not work."

    @mark.asyncio
    async def test_create_db_session_exception(
        self, monkeypatch, db_service: DbService
    ):
        """
        Tests the create_db_session is working on exception.
        :param monkeypatch: Pytest monkeypatch fixture.
        :param db_service: Pytest database service fixture.
        """
        commit_msg = "Commit failed."

        class FakeAsyncSession:
            def __init__(self):
                self.closed = False
                self.committed = False
                self.rolled_back = False
                self.tried_to_commit = False

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_value, traceback):
                pass

            async def commit(self):
                self.tried_to_commit = True
                raise Exception(commit_msg)
                # noinspection PyUnreachableCode
                self.committed = True

            async def rollback(self):
                self.rolled_back = True

            async def close(self):
                self.closed = True

        monkeypatch.setattr(
            db_service, "_DbService__session_maker", lambda: FakeAsyncSession()
        )

        with raises(Exception) as exc_info:
            async with db_service.create_db_session() as fake_session:
                pass

        assert commit_msg in str(exc_info.value), "Exception message is incorrect."
        assert (
            fake_session.tried_to_commit
        ), "Session was not attempted to be committed."
        assert fake_session.rolled_back, "Session did not roll back."
        assert fake_session.closed, "Session did not close."
        assert not fake_session.committed, "Session was incorrectly committed."
