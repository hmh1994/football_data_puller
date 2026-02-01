from typing import TypeVar, Generic, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.repository.entities.base import BaseEntity
from football_data_manager.repository.session import SessionFactory
from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_now,
)
from football_data_manager.common.utils.type_helper.list_helper import (
    remove_duplicates,
)

TEntity = TypeVar("TEntity", bound=BaseEntity)


class AsyncBaseRepository(Generic[TEntity]):
    """
    Async base repository with generic CRUD operations.

    Provides standard database operations for any entity type.
    All methods accept an optional session parameter; if not provided,
    a new session is created from the session factory.

    :param session_factory: Factory for creating database sessions
    :param model: SQLAlchemy model class for this repository
    """

    def __init__(self, session_factory: SessionFactory, model: type[TEntity]):
        self._session_factory = session_factory
        self._model = model

    # ── Create ──────────────────────────────────────────────

    async def create(
        self, entity: TEntity, session: AsyncSession | None = None
    ) -> TEntity | None:
        """
        Create an entity. Returns None if duplicate.

        :param entity: Entity to create
        :param session: Optional existing session
        :return: Created entity or None if duplicate
        """
        async def _do(s: AsyncSession) -> TEntity | None:
            if await self._sieve_duplication(s, entity) is None:
                return None
            s.add(entity)
            await s.flush()
            await s.refresh(entity)
            return entity

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    async def create_many(
        self, entities: Sequence[TEntity], session: AsyncSession | None = None
    ) -> list[TEntity]:
        """
        Create multiple entities with deduplication.

        :param entities: Entities to create
        :param session: Optional existing session
        :return: Successfully created entities
        """
        async def _do(s: AsyncSession) -> list[TEntity]:
            unique = remove_duplicates(
                remove_duplicates(list(entities), key=lambda e: e.id),
                key=lambda e: (e.source, e.source_id),
            )
            sieved = [await self._sieve_duplication(s, e) for e in unique]
            candidates = [e for e in sieved if e is not None]
            if candidates:
                s.add_all(candidates)
                await s.flush()
            return candidates

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    # ── Read ────────────────────────────────────────────────

    async def get_by_id(
        self, entity_id: str, session: AsyncSession | None = None
    ) -> TEntity | None:
        """
        Get entity by primary key.

        :param entity_id: Entity UUID
        :param session: Optional existing session
        :return: Entity or None
        """
        async def _do(s: AsyncSession) -> TEntity | None:
            return await s.get(self._model, entity_id)

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    async def get_by_source(
        self,
        source: SourceEnum,
        source_id: str,
        session: AsyncSession | None = None,
    ) -> TEntity | None:
        """
        Get entity by source and source_id.

        :param source: Data source enum
        :param source_id: Source-specific ID
        :param session: Optional existing session
        :return: Entity or None
        """
        async def _do(s: AsyncSession) -> TEntity | None:
            stmt = (
                select(self._model)
                .filter_by(
                    source=(
                        source.value.upper()
                        if isinstance(source, SourceEnum)
                        else source.upper()
                    )
                )
                .filter_by(source_id=str(source_id))
            )
            result = await s.execute(stmt)
            return result.scalars().first()

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    async def get_all(
        self,
        *,
        limit: int | None = None,
        offset: int = 0,
        session: AsyncSession | None = None,
    ) -> list[TEntity]:
        """
        Get all entities with optional pagination.

        :param limit: Maximum number of results
        :param offset: Number of results to skip
        :param session: Optional existing session
        :return: List of entities
        """
        async def _do(s: AsyncSession) -> list[TEntity]:
            stmt = select(self._model).offset(offset)
            if limit is not None:
                stmt = stmt.limit(limit)
            result = await s.execute(stmt)
            return list(result.unique().scalars().all())

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    async def count(
        self, *filters, session: AsyncSession | None = None
    ) -> int:
        """
        Count entities with optional filters.

        :param filters: SQLAlchemy filter expressions
        :param session: Optional existing session
        :return: Number of matching entities
        """
        async def _do(s: AsyncSession) -> int:
            stmt = select(func.count()).select_from(self._model)
            if filters:
                stmt = stmt.where(*filters)
            result = await s.execute(stmt)
            return result.scalar_one()

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    async def exists(
        self, entity_id: str, session: AsyncSession | None = None
    ) -> bool:
        """
        Check if entity exists by ID.

        :param entity_id: Entity UUID
        :param session: Optional existing session
        :return: True if exists
        """
        return await self.get_by_id(entity_id, session=session) is not None

    async def exists_by_source(
        self,
        source: SourceEnum,
        source_id: str,
        session: AsyncSession | None = None,
    ) -> bool:
        """
        Check if entity exists by source.

        :param source: Data source enum
        :param source_id: Source-specific ID
        :param session: Optional existing session
        :return: True if exists
        """
        return await self.get_by_source(source, source_id, session=session) is not None

    # ── Update ──────────────────────────────────────────────

    async def update(
        self, entity: TEntity, session: AsyncSession | None = None
    ) -> TEntity:
        """
        Update an entity. Sets updated_at to current UTC time.

        :param entity: Entity to update
        :param session: Optional existing session
        :return: Updated entity
        """
        async def _do(s: AsyncSession) -> TEntity:
            entity.updated_at = create_utc_now()
            merged = await s.merge(entity)
            await s.flush()
            await s.refresh(merged)
            return merged

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    # ── Delete ──────────────────────────────────────────────

    async def delete(
        self, entity: TEntity, session: AsyncSession | None = None
    ) -> None:
        """
        Delete an entity.

        :param entity: Entity to delete
        :param session: Optional existing session
        """
        async def _do(s: AsyncSession) -> None:
            real = await s.get(self._model, entity.id)
            if real is not None:
                await s.delete(real)
                await s.flush()

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    async def delete_by_id(
        self, entity_id: str, session: AsyncSession | None = None
    ) -> bool:
        """
        Delete an entity by ID.

        :param entity_id: Entity UUID
        :param session: Optional existing session
        :return: True if entity was deleted
        """
        async def _do(s: AsyncSession) -> bool:
            entity = await s.get(self._model, entity_id)
            if entity is not None:
                await s.delete(entity)
                await s.flush()
                return True
            return False

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    # ── Protected Helpers ───────────────────────────────────

    async def _get_by_field(
        self, session: AsyncSession, **kwargs
    ) -> list[TEntity]:
        """
        Get entities by field values.

        :param session: Database session
        :param kwargs: Field name-value pairs
        :return: Matching entities
        """
        stmt = select(self._model).filter_by(**kwargs)
        result = await session.execute(stmt)
        return list(result.unique().scalars().all())

    async def _get_one_by_field(self, **kwargs) -> TEntity | None:
        """
        Get single entity by field values.

        :param kwargs: Field name-value pairs
        :return: Entity or None
        """
        async with self._session_factory.session() as s:
            results = await self._get_by_field(s, **kwargs)
            return results[0] if results else None

    async def _load_lazy_fields(
        self,
        entity: TEntity,
        fields: list[str],
        session: AsyncSession | None = None,
    ) -> TEntity:
        """
        Load lazy-loaded relationship fields.

        :param entity: Entity to load fields for
        :param fields: Relationship attribute names
        :param session: Optional existing session
        :return: Entity with relationships loaded
        """
        async def _do(s: AsyncSession) -> TEntity:
            if await self.exists(entity.id, session=s):
                merged = await s.merge(entity)
                await s.refresh(merged, attribute_names=fields)
                return merged
            return entity

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    async def _sieve_duplication(
        self, session: AsyncSession, entity: TEntity
    ) -> TEntity | None:
        """
        Check for duplicate entity by ID and source.

        :param session: Database session
        :param entity: Entity to check
        :return: Entity if not duplicate, None otherwise
        """
        if await self.get_by_id(entity.id, session=session) is not None:
            return None
        if await self.get_by_source(
            entity.source, entity.source_id, session=session
        ) is not None:
            return None
        return entity
