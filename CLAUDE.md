# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup

- **Virtual Environment**: `python3.12 -m venv venv && source venv/bin/activate`
- **Install Dependencies**: `pip install -e ".[all]"` (installs essential, dev, and test dependencies)
- **Database Setup**: Requires PostgreSQL database configuration via `.env` file in `configs/` directory

### Testing

- **Run All Tests**: `pytest -vv`
- **Test Configuration**: Uses pytest with `pythonpath = ["."]` and `testpaths = ["tests"]`

### Application Execution

- **Health Check**: `python app.py health`
- **Test Operation**: `python app.py test` (runs async test function)

## Project Architecture

### Core Structure

This is a **data pipeline application** for football data management using Python 3.12+ with async/await patterns
throughout.

**Main Components**:

- **Data Pullers**: Services that extract data from external sources (PulseLive API, The Athletic GraphQL)
- **Repository Layer**: SQLAlchemy-based ORM with generic repository pattern for database operations
- **Service Containers**: Dependency injection using `dependency-injector` library
- **Entity Models**: Database models representing football domain objects (teams, players, matches, etc.)

### Key Architectural Patterns

#### Repository Pattern

- **Base Repository** (`football_data_manager/common/repositories/base_repository.py`): Generic CRUD operations with
  async SQLAlchemy
- **Entity-specific repositories**: Each domain object has its own repository extending BaseRepository
- **Session Management**: Uses `@with_db_session` decorator for automatic session handling
- **Duplication Prevention**: Built-in deduplication logic based on ID and source_id

#### Dependency Injection

- **CommonServiceContainer**: Core services (config, database, translator)
- **PullerServiceContainer**: Data pulling services (PulseLive, The Athletic)
- **Configuration**: Environment-based config loading from `.env` files

#### Data Source Integration

- **PulseLive**: Football API integration with complex response models for matches, teams, competitions
- **The Athletic**: GraphQL news service with AI-powered translation (OpenAI integration)
- **Source Tracking**: All entities track their source (enum-based) and source_id for provenance

### Database Layer

- **SQLAlchemy 2.0+** with async support (`asyncpg` driver)
- **Base Entity**: All models inherit from BaseEntity with common fields (id, source, source_id, timestamps)
- **Complex Associations**: Many association tables for match lineups, goals, cards, substitutions
- **Migration Strategy**: Uses `Base.metadata.create_all()` for schema creation

### Domain Models

- **Core Entities**: Competition, Season, Team, Player, Match, Ground, Official
- **Statistics**: MatchStat, PlayerStat, TeamStat with detailed performance metrics
- **News**: News entities with team associations and AI translation capabilities
- **Complex Match Data**: Detailed match information including lineups, events, formations, officials

### Service Architecture

- **Client Services**: HTTP clients for external APIs (GraphQL, REST, Web scraping)
- **Puller Services**: Orchestrate data extraction and database persistence
- **Config Service**: Environment-based configuration management
- **Translator Service**: AI-powered text translation using OpenAI/Anthropic APIs

### Testing Structure

- **pytest-asyncio**: Async test support
- **Mock Services**: Located in `tests/common/services/mocks.py`
- **Sample Data**: Reusable test data generators in `tests/common/repositories/sample_data/`
- **Repository Tests**: Comprehensive test coverage for all repository operations

### External Dependencies

- **Core**: SQLAlchemy, asyncpg, dependency-injector, pydantic, httpx
- **AI Services**: OpenAI, Anthropic APIs for content translation
- **Web**: gql (GraphQL), beautifulsoup4 for scraping
- **Testing**: pytest, pytest-asyncio, aiosqlite

### Configuration

- Environment variables loaded from `configs/.env`
- API configurations for multiple external services
- Database connection settings for PostgreSQL
- Structured config models using Pydantic

## Development Notes

### Code Style

- **Async/Await**: All database and HTTP operations are async
- **Type Hints**: Comprehensive typing with generics for repository pattern
- **Pydantic Models**: Used for API response validation and configuration
- **Error Handling**: Database connection checks and session management built into repositories

### Data Flow

1. **Configuration Loading**: Environment variables → Config service
2. **Service Container Setup**: Dependency injection initialization
3. **Data Pulling**: External APIs → Response models → Entity conversion
4. **Database Operations**: Repository pattern → SQLAlchemy → PostgreSQL
5. **Content Enhancement**: AI translation for news content

### Database Considerations

- **Async Sessions**: All database operations use async sessions
- **Connection Management**: Automatic connection checking and session cleanup
- **Deduplication**: Built-in logic to prevent duplicate records based on source tracking
- **Relationship Loading**: Lazy loading with explicit refresh patterns for associations

## Repository Design Patterns & Standards

### Core Design Philosophy

The Football Data Manager follows a **Unified Repository Pattern** based on the successful match repository
implementation. All repositories must adhere to these standards for consistency, maintainability, and performance.

### Pattern Hierarchy

#### 1. Base Layer Architecture

```
BaseEntity (id, source, source_id, timestamps)
├── PulseliveEntity (source=PULSELIVE)
└── [Domain]Entity (domain-specific fields)

BaseRepository[TEntity] (generic CRUD with async)
├── PulseliveRepository[TEntity] (Pulselive-specific operations)
└── [Domain]Repository (domain-specific business logic)
```

#### 2. Entity Design Standards

**Required Patterns**:

- **Inheritance**: All entities extend `BaseEntity` or `PulseliveEntity`
- **Type Safety**: Full generic typing with `TEntity` bounds
- **Relationship Consistency**: String references for forward declarations
- **Association Abstraction**: Abstract base classes for complex associations
- **Property Methods**: Computed properties for business logic

#### 3. Association Pattern Standards

**Abstract Association Classes**:

```python
class AbstractMatchCardAssociation(Base):
    """
    Abstract base class for match card associations.

    Provides common functionality for associating cards (yellow/red) with players
    during a match. Used as a base for home and away team card associations.

    :ivar player_id: Foreign key to the player who received the card
    :ivar card_type: Type of card (yellow or red)
    :ivar clock: Time in minutes when the card was issued
    """

    __abstract__ = True

    player_id = Column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    card_type = Column(Enum(CardTypeEnum), primary_key=True)
    clock = Column(Integer, nullable=False)

    @property
    def card_info(self):
        """
        Get card information as a tuple.

        :returns: Tuple containing player ID, card type, and time
        """
        return self.player_id, self.card_type, self.clock
```

**Concrete Implementation**:

```python
class MatchHomeTeamCardAssociation(AbstractMatchCardAssociation):
    __tablename__ = MATCH_HOME_TEAM_CARD_ASSOCIATION_TABLE_NAME

    CARD_INFO_COLLECTION_NAME = "home_team_card_associations"

    match_id = Column(String, ForeignKey(MatchEntity.id), primary_key=True)
    match = relationship(
        MatchEntity,
        backref=backref(
            CARD_INFO_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by="MatchHomeTeamCardAssociation.clock",
        ),
    )

    def __init__(
            self,
            match: MatchEntity,
            player: PlayerEntity,
            card_type: CardTypeEnum,
            clock: int,
    ):
        """
        Initialize association with entities instead of IDs.

        :param match: Match entity where the event occurred
        :param player: Player entity who received the card
        :param card_type: Type of card issued
        :param clock: Time when the event occurred
        """
        super().__init__(player_id=player.id, card_type=card_type, clock=clock)
        self.match_id = match.id
```

**Entity-Based Constructor Pattern Requirements**:

- **Accept Entity Objects**: Pass entity instances instead of raw ID strings
- **Automatic ID Extraction**: Extract IDs using `entity.id` within the constructor
- **Super Initialization**: Call `super().__init__()` with extracted abstract class parameters
- **Match ID Assignment**: Set concrete `match_id` after parent initialization
- **Optional Entity Handling**: Use conditional extraction for optional relationships
- **Complete Documentation**: Document all parameters with clear descriptions

**Constructor Benefits**:

- **Type Safety**: Full compile-time type checking for entity relationships
- **API Consistency**: Unified interface across all association classes
- **Error Prevention**: Eliminates manual ID extraction and potential mistakes
- **Code Clarity**: More intuitive and object-oriented interface

#### 4. Repository Method Standards

**Performance-Optimized Duplicate Checking**:

```python
# ✅ CORRECT - Efficient set-based checking
existing_cards = {(c.player_id, c.card_type, c.clock) for c in target_list}
card_key = (player.id, card_type, clock)
if card_key not in existing_cards:
# Add new association

# ❌ INCORRECT - Inefficient property-based checking
card_id_list = [c.card_info for c in target_list]  # O(n) property calls
if (player.id, card_type, clock) not in card_id_list:
# Add new association
```

**Comprehensive Docstrings (reStructuredText format)**:

```python
async def append_card(
        self,
        match: MatchEntity,
        is_home: bool,
        player: PlayerEntity,
        card_type: CardTypeEnum,
        clock: int,
) -> MatchEntity:
    """
    Append a card to the match if it doesn't already exist.

    :param match: The match entity
    :param is_home: Whether the card is for the home team
    :param player: The player who received the card
    :param card_type: The type of card (yellow/red)
    :param clock: The time when the card was given
    :returns: The updated match entity with the card added
    """
```

#### 5. Type Safety Standards

**Import Organization**:

```python
from typing import TYPE_CHECKING

from football_data_manager.common.enums.card_type_enum import CardTypeEnum

# ... other imports

if TYPE_CHECKING:
    pass  # Forward declaration space
```

**Generic Repository Typing**:

```python
TEntity = TypeVar("TEntity", bound=BaseEntity)


class BaseRepository(Generic[TEntity]):
    def __init__(self, db_service: DbService, model: Type[TEntity]):
        self.__db_service = db_service
        self.model = model
```

### Mandatory Implementation Checklist

#### Entity Requirements

- [ ] Extends `BaseEntity` or `PulseliveEntity`
- [ ] Uses string relationship references
- [ ] Implements proper `__init__` with type hints
- [ ] Has comprehensive reStructuredText docstrings (no type annotations)
- [ ] Uses consistent table naming via constants
- [ ] Documents all class attributes with `:ivar:` in class docstring
- [ ] Documents constructor parameters with `:param:` in `__init__` docstring
- [ ] Separates entity attributes (`:ivar:`) from initialization parameters (`:param:`)

#### Association Requirements

- [ ] Abstract base class for reusable patterns
- [ ] Concrete implementations for each relationship
- [ ] Entity-based `__init__` constructors (accept entities, not IDs)
- [ ] Proper `super().__init__()` calling with extracted IDs
- [ ] Property methods for convenient data access
- [ ] Proper backref configuration with class names
- [ ] Collection name constants for reference
- [ ] Complete reStructuredText documentation for constructors

#### Repository Requirements

- [ ] Extends appropriate base repository
- [ ] Implements domain-specific business methods
- [ ] Uses efficient duplicate checking (set-based)
- [ ] Has comprehensive reStructuredText method documentation
- [ ] Includes proper type hints and imports
- [ ] Documents parameters with `:param:` and `:returns:` (no type annotations)
- [ ] Includes usage examples for complex methods

### Performance Standards

- **Duplicate Checking**: Use set-based O(1) lookups instead of O(n) property calls
- **Relationship Loading**: Lazy loading with explicit `load_items()` method
- **Memory Management**: Direct attribute access for performance-critical operations
- **Query Optimization**: Minimize database round-trips through batch operations

### Documentation Standards

**reStructuredText Docstring Format**:
All methods, classes, and modules must use reStructuredText format for consistency with Sphinx documentation generation.

**Required Elements**:

- **Brief Description**: One-line summary of functionality
- **Detailed Description**: Multi-line explanation when needed
- **Parameters**: `:param name:` description for each parameter (no type annotations)
- **Returns**: `:returns:` description (no type annotations)
- **Raises**: `:raises ExceptionType:` for documented exceptions
- **Examples**: Usage examples when helpful

**Documentation Structure Guidelines**:

- **`:ivar:` (Instance Variables)**: Use for all entity attributes/fields in the class docstring
    - Database columns (Column definitions)
    - Relationships (relationship, Mapped)
    - Computed properties
    - Inherited attributes worth documenting

- **`:param:` (Parameters)**: Use for constructor parameters in the `__init__` method docstring
    - Only document parameters that are passed to the constructor
    - Focus on the purpose and usage of each parameter
    - Explain any validation or transformation that occurs

**Note**: Type information is provided through Python type hints in function signatures, so `:type:` and `:rtype:`
annotations are not required in docstrings.

**Entity Docstring Examples**:

**Class-Level Documentation** (use `:ivar:` for all entity attributes):

```python
class TeamEntity(PulseliveEntity):
    """
    Represents a football team with localized names, icons, and championship associations.

    Extends PulseliveEntity to inherit source tracking and base functionality.
    Contains multilingual team information and associations with championship seasons.

    :ivar id: Unique identifier for the entity
    :ivar abbreviation: Team abbreviation (e.g., 'MCI', 'LIV')
    :ivar name_en: Team name in English
    :ivar name_kr: Team name in Korean
    :ivar icon_url: URL to team icon/logo image
    :ivar championship_season_associations: List of championship season associations
    :ivar short_name_en: Abbreviated team name in English
    :ivar short_name_kr: Abbreviated team name in Korean
    :ivar source: Data source (inherited from PulseliveEntity)
    :ivar source_id: Unique identifier from source system
    :ivar created_at: Entity creation timestamp
    :ivar updated_at: Last modification timestamp
    """
```

**Constructor Documentation** (use `:param:` for initialization parameters):

```python
    def __init__(
        self,
        abbreviation: str,
        icon_url: str,
        name_en: str,
        name_kr: str,
        short_name_en: str,
        short_name_kr: str,
        source_id: str,
):


"""
Initialize a new team entity.

:param abbreviation: Short team abbreviation (e.g., 'MCI', 'LIV')
:param icon_url: URL to team icon/logo image
:param name_en: Full team name in English
:param name_kr: Full team name in Korean
:param short_name_en: Abbreviated team name in English
:param short_name_kr: Abbreviated team name in Korean
:param source_id: Unique identifier from the source system
"""
```

**Repository Method Example**:

```python
async def create_team(
        self,
        name_en: str,
        name_kr: str,
        abbreviation: str,
        source_id: str
) -> TeamEntity | None:
    """
    Create a new team entity in the database.

    Creates a team with the provided information and stores it in the database.
    Handles deduplication based on source_id to prevent duplicate entries.

    :param name_en: Team name in English
    :param name_kr: Team name in Korean
    :param abbreviation: Short team abbreviation
    :param source_id: Unique identifier from the source system
    :returns: Created team entity, or None if duplicate detected
    :raises ValueError: If required parameters are invalid
    :raises DatabaseError: If database operation fails

    Example:
        >>> team = await team_repo.create_team(
        ...     name_en="Manchester City",
        ...     name_kr="맨체스터 시티",
        ...     abbreviation="MCI",
        ...     source_id="team_12345"
        ... )
    """
```

### Quality Gates

1. **Syntax Validation**: All Python files must compile without errors
2. **Pattern Consistency**: All repositories follow the unified pattern
3. **Type Safety**: Comprehensive type hints and proper imports
4. **Documentation**: Complete reStructuredText docstrings for all public methods
5. **Performance**: Efficient algorithms for duplicate checking and data access

### Migration Strategy

When applying these patterns to existing repositories:

1. **Assessment**: Identify current pattern deviations
2. **Prioritization**: Fix critical runtime errors first (`__qualname__`, `argument=`)
3. **Standardization**: Apply consistent relationship patterns
4. **Optimization**: Implement performance improvements
5. **Validation**: Test all changes for functionality and performance

### Repository Domain Coverage

The following domains must implement these patterns:

- `awards` - Award entities and repositories
- `competitions` - Competition and season management
- `fixtures` - Match fixture information
- `grounds` - Stadium and venue data
- `match_stats` - Match-level statistics
- `matches` - **✅ REFERENCE IMPLEMENTATION**
- `news` - News articles with team associations
- `officials` - Referee and official information
- `player_stats` - Individual player statistics
- `players` - Player entities and associations
- `seasons` - Season and championship data
- `staffs` - Coaching staff and management
- `team_stats` - Team-level statistics
- `teams` - Team entities and associations

### Success Metrics

- **Consistency**: 100% pattern compliance across all repositories
- **Performance**: 40-60% improvement in duplicate checking operations
- **Maintainability**: Unified codebase with consistent patterns
- **Type Safety**: Zero runtime type-related errors
- **Documentation**: Complete API documentation for all methods
