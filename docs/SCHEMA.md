# Database Schema Reference

This document describes the complete database schema for the Football Data Manager repository.
All tables are managed via SQLAlchemy ORM and versioned through Alembic migrations.

---

## Table of Contents

1. [Base Fields](#base-fields)
2. [Core Reference Tables](#core-reference-tables)
    - [competitions](#competitions)
    - [seasons](#seasons)
    - [teams](#teams)
    - [players](#players)
    - [staffs](#staffs)
    - [officials](#officials)
    - [grounds](#grounds)
    - [awards](#awards)
3. [Fixture & Match Tables](#fixture--match-tables)
    - [fixtures](#fixtures)
    - [matches](#matches)
    - [match_stats](#match_stats)
4. [Season Aggregate Tables](#season-aggregate-tables)
    - [player_stats](#player_stats)
    - [team_stats](#team_stats)
    - [analytics](#analytics)
5. [Content Tables](#content-tables)
    - [news](#news)
6. [Association Tables](#association-tables)
    - [match_goal_association](#match_goal_association)
    - [match_card_association](#match_card_association)
    - [match_lineup_association](#match_lineup_association)
    - [match_substitute_association](#match_substitute_association)
    - [match_substitution_association](#match_substitution_association)
    - [team_stat_match_association](#team_stat_match_association)
    - [player_championship_association](#player_championship_association)
    - [team_championship_association](#team_championship_association)
    - [player_stat_award_association](#player_stat_award_association)
    - [staff_award_association](#staff_award_association)
    - [news_team_association](#news_team_association)

---

## Base Fields

All primary entity tables (excluding pure association tables) inherit the following fields from `BaseEntity`:

| Column       | Type               | Nullable         | Description                                                            |
|--------------|--------------------|------------------|------------------------------------------------------------------------|
| `id`         | `String` (UUID)    | NOT NULL         | Globally unique identifier, auto-generated as UUID v4                  |
| `source`     | `Enum(SourceEnum)` | NOT NULL         | Data source identifier. Values: `pulselive`, `the_athletic`, `unknown` |
| `source_id`  | `String`           | NOT NULL, UNIQUE | Unique identifier within the originating data source                   |
| `created_at` | `DateTime`         | NOT NULL         | UTC timestamp of record creation                                       |
| `updated_at` | `DateTime`         | NOT NULL         | UTC timestamp of the last update                                       |

Most entities extend `PulseliveEntity`, which is a specialization of `BaseEntity` that automatically sets
`source = pulselive`.

---

## Core Reference Tables

### competitions

Stores football competitions (leagues and cups).

| Column           | Type       | Nullable         | Description                                        |
|------------------|------------|------------------|----------------------------------------------------|
| `id`             | `String`   | NOT NULL (PK)    | *Inherited from BaseEntity*                        |
| `source`         | `Enum`     | NOT NULL         | *Inherited — always `pulselive`*                   |
| `source_id`      | `String`   | NOT NULL, UNIQUE | *Inherited*                                        |
| `created_at`     | `DateTime` | NOT NULL         | *Inherited*                                        |
| `updated_at`     | `DateTime` | NOT NULL         | *Inherited*                                        |
| `abbreviation`   | `String`   | NOT NULL, UNIQUE | Short code for the competition (e.g., `PL`, `UCL`) |
| `name_en`        | `String`   | NOT NULL         | Competition name in English                        |
| `name_kr`        | `String`   | NOT NULL         | Competition name in Korean                         |
| `description_en` | `String`   | NULL             | Competition description in English                 |
| `description_kr` | `String`   | NULL             | Competition description in Korean                  |
| `icon_url`       | `String`   | NULL             | URL to the competition icon/logo image             |

---

### seasons

Stores individual seasons of a competition.

| Column           | Type          | Nullable         | Description                                                            |
|------------------|---------------|------------------|------------------------------------------------------------------------|
| `id`             | `String`      | NOT NULL (PK)    | *Inherited from BaseEntity*                                            |
| `source`         | `Enum`        | NOT NULL         | *Inherited — always `pulselive`*                                       |
| `source_id`      | `String`      | NOT NULL, UNIQUE | *Inherited — composed as `{competition.source_id}_{season_source_id}`* |
| `created_at`     | `DateTime`    | NOT NULL         | *Inherited*                                                            |
| `updated_at`     | `DateTime`    | NOT NULL         | *Inherited*                                                            |
| `abbreviation`   | `String`      | NOT NULL         | Human-readable season code (e.g., `23/24`)                             |
| `competition_id` | `String` (FK) | NOT NULL         | Foreign key → `competitions.id` (CASCADE DELETE)                       |
| `date_start`     | `DateTime`    | NOT NULL         | Official start date and time of the season                             |
| `date_end`       | `DateTime`    | NOT NULL         | Official end date and time of the season                               |
| `year_start`     | `Integer`     | NOT NULL         | Calendar year in which the season starts                               |
| `year_end`       | `Integer`     | NOT NULL         | Calendar year in which the season ends                                 |

---

### teams

Stores football clubs with localized names and branding information.

| Column            | Type       | Nullable         | Description                                 |
|-------------------|------------|------------------|---------------------------------------------|
| `id`              | `String`   | NOT NULL (PK)    | *Inherited from BaseEntity*                 |
| `source`          | `Enum`     | NOT NULL         | *Inherited — always `pulselive`*            |
| `source_id`       | `String`   | NOT NULL, UNIQUE | *Inherited*                                 |
| `created_at`      | `DateTime` | NOT NULL         | *Inherited*                                 |
| `updated_at`      | `DateTime` | NOT NULL         | *Inherited*                                 |
| `abbreviation`    | `String`   | NOT NULL, UNIQUE | Short team code (e.g., `MCI`, `LIV`, `ARS`) |
| `name_en`         | `String`   | NOT NULL         | Full team name in English                   |
| `name_kr`         | `String`   | NOT NULL         | Full team name in Korean                    |
| `short_name_en`   | `String`   | NOT NULL         | Abbreviated team name in English            |
| `short_name_kr`   | `String`   | NOT NULL         | Abbreviated team name in Korean             |
| `icon_url`        | `String`   | NOT NULL         | URL to the team icon/logo image             |
| `color_primary`   | `String`   | NULL             | Primary brand color (typically a hex code)  |
| `color_secondary` | `String`   | NULL             | Secondary brand color                       |
| `description_en`  | `String`   | NULL             | Team description in English                 |
| `description_kr`  | `String`   | NULL             | Team description in Korean                  |
| `founded_year`    | `Integer`  | NULL             | Year the club was founded                   |

---

### players

Stores player personal profiles.

| Column                      | Type                 | Nullable         | Description                                                                            |
|-----------------------------|----------------------|------------------|----------------------------------------------------------------------------------------|
| `id`                        | `String`             | NOT NULL (PK)    | *Inherited from BaseEntity*                                                            |
| `source`                    | `Enum`               | NOT NULL         | *Inherited — always `pulselive`*                                                       |
| `source_id`                 | `String`             | NOT NULL, UNIQUE | *Inherited*                                                                            |
| `created_at`                | `DateTime`           | NOT NULL         | *Inherited*                                                                            |
| `updated_at`                | `DateTime`           | NOT NULL         | *Inherited*                                                                            |
| `full_name`                 | `String`             | NOT NULL         | Player's full legal name                                                               |
| `display_name_en`           | `String`             | NOT NULL         | Display name in English                                                                |
| `display_name_kr`           | `String`             | NOT NULL         | Display name in Korean                                                                 |
| `birth_date`                | `DateTime`           | NULL             | Date of birth                                                                          |
| `birth_country`             | `String`             | NULL             | Country of birth (English name)                                                        |
| `nationality_en`            | `String`             | NOT NULL         | Nationality in English                                                                 |
| `nationality_kr`            | `String`             | NOT NULL         | Nationality in Korean                                                                  |
| `nationality_flag_icon_url` | `String`             | NULL             | URL to the nationality flag icon                                                       |
| `photo_url`                 | `String`             | NULL             | URL to the player's photo                                                              |
| `position`                  | `Enum(PositionEnum)` | NOT NULL         | Playing position. Values: `goalkeeper`, `defender`, `midfielder`, `forward`, `unknown` |
| `preferred_foot`            | `Enum(SideEnum)`     | NOT NULL         | Preferred foot. Values: `right`, `left`, `both`, `unknown`                             |
| `height`                    | `Integer`            | NULL             | Player height in centimeters                                                           |
| `weight`                    | `Integer`            | NULL             | Player weight in kilograms                                                             |

---

### staffs

Stores coaching staff and management personnel.

| Column            | Type       | Nullable         | Description                      |
|-------------------|------------|------------------|----------------------------------|
| `id`              | `String`   | NOT NULL (PK)    | *Inherited from BaseEntity*      |
| `source`          | `Enum`     | NOT NULL         | *Inherited — always `pulselive`* |
| `source_id`       | `String`   | NOT NULL, UNIQUE | *Inherited*                      |
| `created_at`      | `DateTime` | NOT NULL         | *Inherited*                      |
| `updated_at`      | `DateTime` | NOT NULL         | *Inherited*                      |
| `full_name`       | `String`   | NOT NULL         | Full legal name                  |
| `display_name_en` | `String`   | NOT NULL, UNIQUE | Display name in English          |
| `display_name_kr` | `String`   | NOT NULL         | Display name in Korean           |

---

### officials

Stores match officials (referees, assistants, VAR officials).

| Column            | Type       | Nullable         | Description                                              |
|-------------------|------------|------------------|----------------------------------------------------------|
| `id`              | `String`   | NOT NULL (PK)    | *Inherited from BaseEntity*                              |
| `source`          | `Enum`     | NOT NULL         | *Inherited — always `pulselive`*                         |
| `source_id`       | `String`   | NOT NULL, UNIQUE | *Inherited — MD5 hash of `display_name_en`, modulo 2^16* |
| `created_at`      | `DateTime` | NOT NULL         | *Inherited*                                              |
| `updated_at`      | `DateTime` | NOT NULL         | *Inherited*                                              |
| `full_name`       | `String`   | NOT NULL         | Official's full legal name                               |
| `display_name_en` | `String`   | NOT NULL, UNIQUE | Display name in English                                  |
| `display_name_kr` | `String`   | NOT NULL         | Display name in Korean                                   |

---

### grounds

Stores stadium and venue information.

| Column               | Type       | Nullable         | Description                                                 |
|----------------------|------------|------------------|-------------------------------------------------------------|
| `id`                 | `String`   | NOT NULL (PK)    | *Inherited from BaseEntity*                                 |
| `source`             | `Enum`     | NOT NULL         | *Inherited — always `pulselive`*                            |
| `source_id`          | `String`   | NOT NULL, UNIQUE | *Inherited — MD5 hash of normalized `name_en`, modulo 2^16* |
| `created_at`         | `DateTime` | NOT NULL         | *Inherited*                                                 |
| `updated_at`         | `DateTime` | NOT NULL         | *Inherited*                                                 |
| `name_en`            | `String`   | NOT NULL, UNIQUE | Ground name in English                                      |
| `name_kr`            | `String`   | NOT NULL         | Ground name in Korean                                       |
| `city_name_en`       | `String`   | NOT NULL         | City name in English                                        |
| `city_name_kr`       | `String`   | NOT NULL         | City name in Korean                                         |
| `capacity`           | `Integer`  | NULL             | Maximum spectator capacity                                  |
| `location_latitude`  | `Double`   | NULL             | Geographic latitude coordinate (decimal degrees)            |
| `location_longitude` | `Double`   | NULL             | Geographic longitude coordinate (decimal degrees)           |

---

### awards

Stores award types that can be assigned to players or staff.

| Column           | Type                  | Nullable         | Description                                                                                                                                |
|------------------|-----------------------|------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| `id`             | `String`              | NOT NULL (PK)    | *Inherited from BaseEntity*                                                                                                                |
| `source`         | `Enum`                | NOT NULL         | *Inherited — always `pulselive`*                                                                                                           |
| `source_id`      | `String`              | NOT NULL, UNIQUE | *Inherited — MD5 hash of the award type value, modulo 2^16*                                                                                |
| `created_at`     | `DateTime`            | NOT NULL         | *Inherited*                                                                                                                                |
| `updated_at`     | `DateTime`            | NOT NULL         | *Inherited*                                                                                                                                |
| `type`           | `Enum(AwardTypeEnum)` | NOT NULL         | Award type. Values: `POTM`, `GOTM`, `SOTM`, `POTS`, `YPOTS`, `PM`, `GOTS`, `MPGOTS`, `SOTS`, `GB`, `GG`, `MICOTS`, `GCOTS`, `MOTM`, `MOTS` |
| `name_en`        | `String`              | NULL             | Award name in English                                                                                                                      |
| `name_kr`        | `String`              | NULL             | Award name in Korean                                                                                                                       |
| `description_en` | `String`              | NULL             | Award description in English                                                                                                               |
| `description_kr` | `String`              | NULL             | Award description in Korean                                                                                                                |
| `icon_url`       | `String`              | NULL             | URL to the award icon image                                                                                                                |

---

## Fixture & Match Tables

### fixtures

Stores scheduled match information (pre-match scheduling data).

| Column         | Type          | Nullable         | Description                                     |
|----------------|---------------|------------------|-------------------------------------------------|
| `id`           | `String`      | NOT NULL (PK)    | *Inherited from BaseEntity*                     |
| `source`       | `Enum`        | NOT NULL         | *Inherited — always `pulselive`*                |
| `source_id`    | `String`      | NOT NULL, UNIQUE | *Inherited — from source system fixture ID*     |
| `created_at`   | `DateTime`    | NOT NULL         | *Inherited*                                     |
| `updated_at`   | `DateTime`    | NOT NULL         | *Inherited*                                     |
| `season_id`    | `String` (FK) | NOT NULL         | Foreign key → `seasons.id` (CASCADE DELETE)     |
| `home_team_id` | `String` (FK) | NOT NULL         | Foreign key → `teams.id` (CASCADE DELETE)       |
| `away_team_id` | `String` (FK) | NOT NULL         | Foreign key → `teams.id` (CASCADE DELETE)       |
| `ground_id`    | `String` (FK) | NULL             | Foreign key → `grounds.id` (SET NULL on DELETE) |
| `game_week`    | `Integer`     | NOT NULL         | Game week (round) number within the season      |
| `kickoff_time` | `DateTime`    | NOT NULL         | Scheduled kickoff date and time (UTC)           |

**Indexes:** `ix_fixtures_home_team`, `ix_fixtures_away_team`, `ix_fixtures_home_team_season`,
`ix_fixtures_away_team_season`, `ix_fixtures_kickoff_time_desc`

---

### matches

Stores completed match data including scores, formations, and officials.

| Column                            | Type               | Nullable         | Description                                                                                |
|-----------------------------------|--------------------|------------------|--------------------------------------------------------------------------------------------|
| `id`                              | `String`           | NOT NULL (PK)    | *Inherited from BaseEntity*                                                                |
| `source`                          | `Enum`             | NOT NULL         | *Inherited — always `pulselive`*                                                           |
| `source_id`                       | `String`           | NOT NULL, UNIQUE | *Inherited — same as the associated fixture's `source_id`*                                 |
| `created_at`                      | `DateTime`         | NOT NULL         | *Inherited*                                                                                |
| `updated_at`                      | `DateTime`         | NOT NULL         | *Inherited*                                                                                |
| `fixture_id`                      | `String` (FK)      | NOT NULL         | Foreign key → `fixtures.id` (CASCADE DELETE)                                               |
| `home_team_id`                    | `String` (FK)      | NOT NULL         | Foreign key → `teams.id` (CASCADE DELETE)                                                  |
| `away_team_id`                    | `String` (FK)      | NOT NULL         | Foreign key → `teams.id` (CASCADE DELETE)                                                  |
| `home_team_score`                 | `Integer`          | NOT NULL         | Final score of the home team                                                               |
| `away_team_score`                 | `Integer`          | NOT NULL         | Final score of the away team                                                               |
| `home_team_half_time_score`       | `Integer`          | NULL             | Home team score at half-time                                                               |
| `away_team_half_time_score`       | `Integer`          | NULL             | Away team score at half-time                                                               |
| `home_team_formation`             | `ARRAY(Integer)`   | NOT NULL         | Home team formation as an ordered array of player counts per row (e.g., `[4, 3, 3]`)       |
| `away_team_formation`             | `ARRAY(Integer)`   | NOT NULL         | Away team formation as an ordered array of player counts per row                           |
| `home_team_captain_id`            | `String` (FK)      | NULL             | Foreign key → `players.id` (SET NULL on DELETE)                                            |
| `away_team_captain_id`            | `String` (FK)      | NULL             | Foreign key → `players.id` (SET NULL on DELETE)                                            |
| `home_team_manager`               | `String` (FK)      | NULL             | Foreign key → `staffs.id` (SET NULL on DELETE)                                             |
| `away_team_manager`               | `String` (FK)      | NULL             | Foreign key → `staffs.id` (SET NULL on DELETE)                                             |
| `official_main_referee_id`        | `String` (FK)      | NULL             | Foreign key → `officials.id` (SET NULL on DELETE)                                          |
| `official_assistant_1_referee_id` | `String` (FK)      | NULL             | Foreign key → `officials.id` (SET NULL on DELETE)                                          |
| `official_assistant_2_referee_id` | `String` (FK)      | NULL             | Foreign key → `officials.id` (SET NULL on DELETE)                                          |
| `official_fourth_referee_id`      | `String` (FK)      | NULL             | Foreign key → `officials.id` (SET NULL on DELETE)                                          |
| `official_var_id`                 | `String` (FK)      | NULL             | Foreign key → `officials.id` (SET NULL on DELETE)                                          |
| `official_assistant_var_id`       | `String` (FK)      | NULL             | Foreign key → `officials.id` (SET NULL on DELETE)                                          |
| `attendance`                      | `Integer`          | NULL             | Number of spectators at the match                                                          |
| `clock`                           | `Integer`          | NOT NULL         | Match time elapsed in minutes at the time of last update (0 when not started)              |
| `period`                          | `Enum(PeriodEnum)` | NOT NULL         | Current match period. Values: `prematch`, `firsthalf`, `secondhalf`, `fulltime`, `unknown` |

---

### match_stats

Stores per-team per-match statistics. Each completed match produces two rows — one per team.

| Column                             | Type          | Nullable         | Description                                                    |
|------------------------------------|---------------|------------------|----------------------------------------------------------------|
| `id`                               | `String`      | NOT NULL (PK)    | *Inherited from BaseEntity*                                    |
| `source`                           | `Enum`        | NOT NULL         | *Inherited — always `pulselive`*                               |
| `source_id`                        | `String`      | NOT NULL, UNIQUE | *Inherited — composed as `{match.source_id}_{team.source_id}`* |
| `created_at`                       | `DateTime`    | NOT NULL         | *Inherited*                                                    |
| `updated_at`                       | `DateTime`    | NOT NULL         | *Inherited*                                                    |
| `match_id`                         | `String` (FK) | NOT NULL         | Foreign key → `matches.id` (CASCADE DELETE)                    |
| `team_id`                          | `String` (FK) | NOT NULL         | Foreign key → `teams.id` (CASCADE DELETE)                      |
| `big_chances`                      | `Integer`     | NOT NULL         | Total big chances created                                      |
| `big_chances_missed`               | `Integer`     | NOT NULL         | Big chances that were missed                                   |
| `corners`                          | `Integer`     | NOT NULL         | Number of corner kicks taken                                   |
| `expected_goals`                   | `Double`      | NOT NULL         | Expected goals (xG)                                            |
| `expected_goals_non_penalty`       | `Double`      | NOT NULL         | Non-penalty expected goals (npxG)                              |
| `expected_goals_on_target`         | `Double`      | NOT NULL         | Expected goals from shots on target (xGOT)                     |
| `fouls_committed`                  | `Integer`     | NOT NULL         | Total fouls committed                                          |
| `possession`                       | `Double`      | NOT NULL         | Ball possession percentage (0.0–100.0)                         |
| `shots_total`                      | `Integer`     | NOT NULL         | Total shots attempted                                          |
| `shots_on_target`                  | `Integer`     | NOT NULL         | Shots on target (including goals)                              |
| `shots_off_target`                 | `Integer`     | NOT NULL         | Shots off target                                               |
| `shots_blocked`                    | `Integer`     | NOT NULL         | Shots blocked by opponents                                     |
| `shots_inside_box`                 | `Integer`     | NOT NULL         | Shots taken from inside the penalty box                        |
| `shots_outside_box`                | `Integer`     | NOT NULL         | Shots taken from outside the penalty box                       |
| `shots_hit_woodwork`               | `Integer`     | NOT NULL         | Shots that hit the post or crossbar                            |
| `passes_total`                     | `Integer`     | NOT NULL         | Total passes attempted                                         |
| `passes_accurate`                  | `Integer`     | NOT NULL         | Accurate passes                                                |
| `passes_own_half`                  | `Integer`     | NOT NULL         | Passes completed in the team's own half                        |
| `passes_opposition_half`           | `Integer`     | NOT NULL         | Passes completed in the opposition's half                      |
| `passes_offsides`                  | `Integer`     | NOT NULL         | Passes that resulted in offside                                |
| `passes_throws`                    | `Integer`     | NOT NULL         | Throw-ins taken                                                |
| `passes_total_crosses`             | `Integer`     | NOT NULL         | Total crosses attempted                                        |
| `passes_accurate_crosses`          | `Integer`     | NOT NULL         | Accurate crosses                                               |
| `passes_total_long_balls`          | `Integer`     | NOT NULL         | Total long balls attempted                                     |
| `passes_accurate_long_balls`       | `Integer`     | NOT NULL         | Accurate long balls                                            |
| `passes_touches_in_opposition_box` | `Integer`     | NOT NULL         | Ball touches inside the opposition penalty box                 |
| `duels_total`                      | `Integer`     | NOT NULL         | Total duels contested                                          |
| `duels_won`                        | `Integer`     | NOT NULL         | Duels won                                                      |
| `duels_ground_total`               | `Integer`     | NOT NULL         | Total ground duels contested                                   |
| `duels_ground_won`                 | `Integer`     | NOT NULL         | Ground duels won                                               |
| `duels_aerial_total`               | `Integer`     | NOT NULL         | Total aerial duels contested                                   |
| `duels_aerial_won`                 | `Integer`     | NOT NULL         | Aerial duels won                                               |
| `duels_dribbles_total`             | `Integer`     | NOT NULL         | Total dribble attempts                                         |
| `duels_dribbles_successful`        | `Integer`     | NOT NULL         | Successful dribbles                                            |
| `defense_tackles_total`            | `Integer`     | NOT NULL         | Total tackle attempts                                          |
| `defense_tackles_won`              | `Integer`     | NOT NULL         | Tackles won                                                    |
| `defense_interceptions`            | `Integer`     | NOT NULL         | Interceptions made                                             |
| `defense_blocks`                   | `Integer`     | NOT NULL         | Shots blocked by defenders                                     |
| `defense_clearances`               | `Integer`     | NOT NULL         | Defensive clearances made                                      |
| `defense_keeper_saves`             | `Integer`     | NOT NULL         | Saves made by the goalkeeper                                   |
| `discipline_yellow_cards`          | `Integer`     | NOT NULL         | Yellow cards received                                          |
| `discipline_red_cards`             | `Integer`     | NOT NULL         | Red cards received (including second yellows and direct reds)  |

---

## Season Aggregate Tables

### player_stats

Stores cumulative per-player per-season statistics. Each row represents one player's statistics for a single season at a
single club.

#### Identifiers & Foreign Keys

| Column           | Type          | Nullable         | Description                                                       |
|------------------|---------------|------------------|-------------------------------------------------------------------|
| `id`             | `String`      | NOT NULL (PK)    | *Inherited from BaseEntity*                                       |
| `source`         | `Enum`        | NOT NULL         | *Inherited — always `pulselive`*                                  |
| `source_id`      | `String`      | NOT NULL, UNIQUE | *Inherited — composed as `{season.source_id}_{player.source_id}`* |
| `created_at`     | `DateTime`    | NOT NULL         | *Inherited*                                                       |
| `updated_at`     | `DateTime`    | NOT NULL         | *Inherited*                                                       |
| `player_id`      | `String` (FK) | NOT NULL         | Foreign key → `players.id` (CASCADE DELETE)                       |
| `season_id`      | `String` (FK) | NOT NULL         | Foreign key → `seasons.id` (CASCADE DELETE)                       |
| `team_id`        | `String` (FK) | NOT NULL         | Foreign key → `teams.id` (CASCADE DELETE)                         |
| `number`         | `Integer`     | NOT NULL         | Player's jersey number for the season                             |
| `appearances`    | `Integer`     | NOT NULL         | Number of match appearances                                       |
| `minutes_played` | `Integer`     | NOT NULL         | Total minutes played (default: 0)                                 |

#### Shooting

| Column                                | Type      | Nullable | Description                       |
|---------------------------------------|-----------|----------|-----------------------------------|
| `shooting_goals`                      | `Integer` | NULL     | Total goals scored                |
| `shooting_goals_penalty`              | `Integer` | NULL     | Goals scored from penalties       |
| `shooting_shots`                      | `Integer` | NULL     | Total shots attempted             |
| `shooting_shots_on_target`            | `Integer` | NULL     | Shots on target                   |
| `shooting_penalties_taken`            | `Integer` | NULL     | Total penalty kicks taken         |
| `shooting_expected_goals`             | `Double`  | NULL     | Expected goals (xG)               |
| `shooting_expected_goals_non_penalty` | `Double`  | NULL     | Non-penalty expected goals (npxG) |
| `shooting_expected_goals_on_target`   | `Double`  | NULL     | Expected goals on target (xGOT)   |

#### Passing

| Column                        | Type      | Nullable | Description                  |
|-------------------------------|-----------|----------|------------------------------|
| `passing_assists`             | `Integer` | NULL     | Total assists                |
| `passing_chances_created`     | `Integer` | NULL     | Key passes (chances created) |
| `passing_passes_total`        | `Integer` | NULL     | Total passes attempted       |
| `passing_passes_successful`   | `Integer` | NULL     | Successful (accurate) passes |
| `passing_crosses_total`       | `Integer` | NULL     | Total crosses attempted      |
| `passing_crosses_successful`  | `Integer` | NULL     | Successful crosses           |
| `passing_long_balls_total`    | `Integer` | NULL     | Total long balls attempted   |
| `passing_long_balls_accurate` | `Integer` | NULL     | Accurate long balls          |
| `passing_expected_assists`    | `Double`  | NULL     | Expected assists (xA)        |

#### Defending

| Column                                 | Type      | Nullable | Description                                   |
|----------------------------------------|-----------|----------|-----------------------------------------------|
| `defending_tackles_total`              | `Integer` | NULL     | Total tackle attempts                         |
| `defending_tackles_won`                | `Integer` | NULL     | Tackles won                                   |
| `defending_interceptions`              | `Integer` | NULL     | Interceptions made                            |
| `defending_blocked`                    | `Integer` | NULL     | Shots blocked                                 |
| `defending_recoveries`                 | `Integer` | NULL     | Ball recoveries                               |
| `defending_fouls_committed`            | `Integer` | NULL     | Fouls committed                               |
| `defending_duels_total`                | `Integer` | NULL     | Total duels contested                         |
| `defending_duels_won`                  | `Integer` | NULL     | Duels won                                     |
| `defending_duels_aerial_total`         | `Integer` | NULL     | Total aerial duels contested                  |
| `defending_duels_aerial_won`           | `Integer` | NULL     | Aerial duels won                              |
| `defending_duels_ground_total`         | `Integer` | NULL     | Total ground duels contested                  |
| `defending_duels_ground_won`           | `Integer` | NULL     | Ground duels won                              |
| `defending_possession_won_final_third` | `Integer` | NULL     | Possessions won in the opponent's final third |

#### Possession & Dribbling

| Column                                 | Type      | Nullable | Description                                    |
|----------------------------------------|-----------|----------|------------------------------------------------|
| `possession_touches`                   | `Integer` | NULL     | Total ball touches                             |
| `possession_touches_in_opposition_box` | `Integer` | NULL     | Ball touches inside the opponent's penalty box |
| `possession_dribble_total`             | `Integer` | NULL     | Total dribble attempts                         |
| `possession_dribble_successful`        | `Integer` | NULL     | Successful dribbles                            |
| `possession_fouls_won`                 | `Integer` | NULL     | Fouls won (drawn)                              |

#### Goalkeeping

| Column                               | Type      | Nullable | Description                             |
|--------------------------------------|-----------|----------|-----------------------------------------|
| `goalkeeping_saves`                  | `Integer` | NULL     | Total saves made                        |
| `goalkeeping_clean_sheets`           | `Integer` | NULL     | Clean sheets kept                       |
| `goalkeeping_goals_conceded`         | `Integer` | NULL     | Goals conceded                          |
| `goalkeeping_goals_prevented`        | `Double`  | NULL     | Goals prevented (PSxG – Goals Conceded) |
| `goalkeeping_penalties_faced`        | `Integer` | NULL     | Penalties faced                         |
| `goalkeeping_penalty_saved`          | `Integer` | NULL     | Penalties saved                         |
| `goalkeeping_penalty_goals_conceded` | `Integer` | NULL     | Penalties conceded as goals             |
| `goalkeeping_high_claim`             | `Integer` | NULL     | High ball claims                        |

#### Discipline

| Column                        | Type      | Nullable | Description                                          |
|-------------------------------|-----------|----------|------------------------------------------------------|
| `discipline_yellow_cards`     | `Integer` | NULL     | Yellow cards received                                |
| `discipline_red_cards`        | `Integer` | NULL     | Red cards received (total, including second yellows) |
| `discipline_red_cards_direct` | `Integer` | NULL     | Direct red cards received                            |

#### Computed Score Fields

The following score fields are computed by `PlayerStatScorer` using a Bayesian shrinkage model. All scores are on a *
*0–100 scale** (higher is better).

| Column             | Type     | Nullable               | Description                                   |
|--------------------|----------|------------------------|-----------------------------------------------|
| `score_shooting`   | `Double` | NOT NULL (default 0.0) | Shooting quality score                        |
| `score_passing`    | `Double` | NOT NULL (default 0.0) | Passing quality score                         |
| `score_defending`  | `Double` | NOT NULL (default 0.0) | Defending quality score                       |
| `score_dribbling`  | `Double` | NOT NULL (default 0.0) | Dribbling quality score                       |
| `score_discipline` | `Double` | NOT NULL (default 0.0) | Discipline score (higher = fewer cards/fouls) |
| `score_overall`    | `Double` | NOT NULL (default 0.0) | Overall performance score                     |

##### score_shooting

Raw components normalized to [0, 1]:

```
f_npxg_90   = norm(npxG / minutes * 90,  lo=0.00, hi=0.60)
f_goals_90  = norm(npGoals / minutes * 90, lo=0.00, hi=0.60)
f_sot_rate  = norm(shots_on_target / shots, lo=0.20, hi=0.60)
f_gxg_ratio = norm(npGoals / npxG,        lo=0.60, hi=1.40)

raw = 0.40 * f_npxg_90 + 0.30 * f_goals_90 + 0.20 * f_sot_rate + 0.10 * f_gxg_ratio
score_shooting = 100 * shrink(raw, prior=0.5, minutes, prior_minutes=450)
```

##### score_passing

```
f_xa_90          = norm(xA / minutes * 90,               lo=0.00, hi=0.30)
f_chances_90     = norm(chances_created / minutes * 90,  lo=0.00, hi=1.50)
f_assists_90     = norm(assists / minutes * 90,           lo=0.00, hi=0.60)
f_pass_accuracy  = norm(passes_successful / passes_total, lo=0.60, hi=0.95)
f_cross_long_acc = norm(0.5 * (crosses_successful/crosses_total) + 0.5 * (long_balls_accurate/long_balls_total), lo=0.20, hi=0.75)

raw = 0.30 * f_xa_90 + 0.20 * f_chances_90 + 0.15 * f_assists_90 + 0.25 * f_pass_accuracy + 0.10 * f_cross_long_acc
score_passing = 100 * shrink(raw, prior=0.5, minutes, prior_minutes=450)
```

##### score_defending

*For outfield players:*

```
f_tackles_won_90    = norm(tackles_won / minutes * 90,           lo=0.0, hi=3.0)
f_interceptions_90  = norm(interceptions / minutes * 90,         lo=0.0, hi=3.0)
f_blocked_90        = norm(blocked / minutes * 90,               lo=0.0, hi=2.5)
f_recoveries_90     = norm(recoveries / minutes * 90,            lo=0.0, hi=12.0)
f_duel_win_rate     = norm(duels_won / duels_total,              lo=0.40, hi=0.75)
f_aerial_win_rate   = norm(aerial_won / aerial_total,            lo=0.35, hi=0.80)
f_fouls_penalty     = 1.0 - norm(fouls_committed / minutes * 90, lo=0.3, hi=2.5)

raw = 0.20 * f_tackles_won_90 + 0.20 * f_interceptions_90 + 0.10 * f_blocked_90
    + 0.15 * f_recoveries_90 + 0.15 * f_duel_win_rate + 0.10 * f_aerial_win_rate + 0.10 * f_fouls_penalty
score_defending = 100 * shrink(raw, prior=0.5, minutes, prior_minutes=450)
```

*For goalkeepers:*

```
f_saves_90       = norm(saves / minutes * 90,          lo=0.0, hi=5.0)
f_prevented_90   = norm(goals_prevented / minutes * 90, lo=-1.0, hi=1.0)
f_clean_sheet_90 = norm(clean_sheets / minutes * 90,   lo=0.0, hi=0.5)

raw = 0.55 * f_saves_90 + 0.25 * f_prevented_90 + 0.20 * f_clean_sheet_90
score_defending = 100 * shrink(raw, prior=0.5, minutes, prior_minutes=450)
```

##### score_dribbling

```
f_success_rate   = norm(dribble_successful / dribble_total,             lo=0.30, hi=0.75)
f_volume_90      = norm(dribble_total / minutes * 90,                   lo=0.0,  hi=6.0)
f_fouls_won_90   = norm(fouls_won / minutes * 90,                       lo=0.0,  hi=3.0)
f_box_touches_90 = norm(touches_in_opposition_box / minutes * 90,       lo=0.0,  hi=10.0)

raw = 0.35 * f_success_rate + 0.30 * f_volume_90 + 0.20 * f_fouls_won_90 + 0.15 * f_box_touches_90
score_dribbling = 100 * shrink(raw, prior=0.5, minutes, prior_minutes=450)
```

##### score_discipline

```
weighted_cards = yellow_cards + 2 * (red_cards - direct_red_cards) + 3 * direct_red_cards
f_cards_90 = norm(weighted_cards / minutes * 90, lo=0.0, hi=2.0)
f_fouls_90 = norm(fouls_committed / minutes * 90, lo=0.0, hi=3.0)

penalty = 0.7 * f_cards_90 + 0.3 * f_fouls_90
raw = 1.0 - clamp(penalty, 0.0, 1.0)
score_discipline = 100 * shrink(raw, prior=0.5, minutes, prior_minutes=450)
```

##### score_overall

Position-weighted blend of category scores using position-specific weights:

| Position   | Shooting | Passing | Defending | Dribbling | Discipline |
|------------|----------|---------|-----------|-----------|------------|
| Forward    | 0.35     | 0.20    | 0.05      | 0.30      | 0.10       |
| Midfielder | 0.20     | 0.35    | 0.15      | 0.20      | 0.10       |
| Defender   | 0.05     | 0.20    | 0.45      | 0.10      | 0.20       |
| Goalkeeper | 0.00     | 0.10    | 0.80      | 0.00      | 0.10       |
| Unknown    | 0.20     | 0.25    | 0.25      | 0.15      | 0.15       |

```
arithmetic_mean = Σ (weight_i * score_i / 100)
geometric_mean  = exp(Σ (weight_i * log(max(score_i / 100, 1e-6))))
blended         = 0.70 * arithmetic_mean + 0.30 * geometric_mean

score_overall = 100 * shrink(blended, prior=0.5, minutes, prior_minutes=225)
```

*Bayesian shrinkage formula used throughout:*

```
shrink(raw, prior, sample_minutes, prior_minutes) =
    (sample_minutes * raw + prior_minutes * prior) / (sample_minutes + prior_minutes)
```

---

### team_stats

Stores cumulative per-team per-season statistics. Each row represents one team's season record for a given competition
season.

#### Identifiers & Foreign Keys

| Column       | Type          | Nullable         | Description                                                          |
|--------------|---------------|------------------|----------------------------------------------------------------------|
| `id`         | `String`      | NOT NULL (PK)    | *Inherited from BaseEntity*                                          |
| `source`     | `Enum`        | NOT NULL         | *Inherited — always `pulselive`*                                     |
| `source_id`  | `String`      | NOT NULL, UNIQUE | *Inherited — composed as `{season.source_id}_{team.source_id}`*      |
| `created_at` | `DateTime`    | NOT NULL         | *Inherited*                                                          |
| `updated_at` | `DateTime`    | NOT NULL         | *Inherited*                                                          |
| `team_id`    | `String` (FK) | NOT NULL         | Foreign key → `teams.id` (CASCADE DELETE)                            |
| `season_id`  | `String` (FK) | NOT NULL         | Foreign key → `seasons.id` (CASCADE DELETE)                          |
| `ground_id`  | `String` (FK) | NULL             | Foreign key → `grounds.id` (SET NULL on DELETE) — team's home ground |
| `manager_id` | `String` (FK) | NULL             | Foreign key → `staffs.id` — current manager                          |

#### Overall Season Record

Aggregated from all completed (`FULLTIME`) matches in the season.

| Column                      | Type             | Nullable | Description                                                               |
|-----------------------------|------------------|----------|---------------------------------------------------------------------------|
| `overall_matches`           | `Integer`        | NOT NULL | Total matches played                                                      |
| `overall_matches_won`       | `Integer`        | NOT NULL | Matches won                                                               |
| `overall_matches_drawn`     | `Integer`        | NOT NULL | Matches drawn                                                             |
| `overall_matches_lost`      | `Integer`        | NOT NULL | Matches lost                                                              |
| `overall_goals_for`         | `Integer`        | NOT NULL | Total goals scored                                                        |
| `overall_goals_against`     | `Integer`        | NOT NULL | Total goals conceded                                                      |
| `overall_goals_difference`  | `Integer`        | NOT NULL | Goal difference                                                           |
| `overall_points`            | `Integer`        | NOT NULL | Total league points                                                       |
| `overall_position`          | `Integer`        | NULL     | Current league standing (1 = top)                                         |
| `overall_cumulative_points` | `ARRAY(Integer)` | NOT NULL | Running array of cumulative points after each match (chronological order) |

**Calculated fields:**

```
overall_goals_difference = overall_goals_for - overall_goals_against

overall_points += 3  (if goals_for > goals_against)
overall_points += 1  (if goals_for == goals_against)
overall_points += 0  (if goals_for < goals_against)

overall_cumulative_points[i] = overall_points after the (i+1)-th match
```

#### Home Season Record

Aggregated from home matches only.

| Column                   | Type             | Nullable | Description                                |
|--------------------------|------------------|----------|--------------------------------------------|
| `home_matches`           | `Integer`        | NOT NULL | Home matches played                        |
| `home_matches_won`       | `Integer`        | NOT NULL | Home matches won                           |
| `home_matches_drawn`     | `Integer`        | NOT NULL | Home matches drawn                         |
| `home_matches_lost`      | `Integer`        | NOT NULL | Home matches lost                          |
| `home_goals_for`         | `Integer`        | NOT NULL | Goals scored at home                       |
| `home_goals_against`     | `Integer`        | NOT NULL | Goals conceded at home                     |
| `home_goals_difference`  | `Integer`        | NOT NULL | Home goal difference                       |
| `home_points`            | `Integer`        | NOT NULL | Points earned at home                      |
| `home_position`          | `Integer`        | NULL     | Home-only league standing                  |
| `home_cumulative_points` | `ARRAY(Integer)` | NOT NULL | Running cumulative points for home matches |

**Calculated fields:**

```
home_goals_difference = home_goals_for - home_goals_against
home_cumulative_points[i] = home_points after the (i+1)-th home match
```

#### Away Season Record

Aggregated from away matches only.

| Column                   | Type             | Nullable | Description                                |
|--------------------------|------------------|----------|--------------------------------------------|
| `away_matches`           | `Integer`        | NOT NULL | Away matches played                        |
| `away_matches_won`       | `Integer`        | NOT NULL | Away matches won                           |
| `away_matches_drawn`     | `Integer`        | NOT NULL | Away matches drawn                         |
| `away_matches_lost`      | `Integer`        | NOT NULL | Away matches lost                          |
| `away_goals_for`         | `Integer`        | NOT NULL | Goals scored away                          |
| `away_goals_against`     | `Integer`        | NOT NULL | Goals conceded away                        |
| `away_goals_difference`  | `Integer`        | NOT NULL | Away goal difference                       |
| `away_points`            | `Integer`        | NOT NULL | Points earned away                         |
| `away_position`          | `Integer`        | NULL     | Away-only league standing                  |
| `away_cumulative_points` | `ARRAY(Integer)` | NOT NULL | Running cumulative points for away matches |

**Calculated fields:**

```
away_goals_difference = away_goals_for - away_goals_against
away_cumulative_points[i] = away_points after the (i+1)-th away match
```

#### Overall Season Advanced Statistics

Sourced from the Pulselive API (not derived from individual match records in DB).

| Column                                          | Type      | Nullable | Description                                   |
|-------------------------------------------------|-----------|----------|-----------------------------------------------|
| `overall_stat_attack_total_shots`               | `Integer` | NULL     | Total shots attempted across the season       |
| `overall_stat_attack_shots_on_target`           | `Integer` | NULL     | Shots on target across the season             |
| `overall_stat_attack_expected_goals`            | `Double`  | NULL     | Total expected goals (xG) across the season   |
| `overall_stat_attack_expected_assists`          | `Double`  | NULL     | Total expected assists (xA) across the season |
| `overall_stat_attack_corners`                   | `Integer` | NULL     | Total corner kicks taken                      |
| `overall_stat_attack_crosses`                   | `Integer` | NULL     | Total crosses attempted                       |
| `overall_stat_attack_crosses_successful`        | `Integer` | NULL     | Successful crosses                            |
| `overall_stat_attack_long_balls`                | `Integer` | NULL     | Total long balls attempted                    |
| `overall_stat_attack_long_balls_successful`     | `Integer` | NULL     | Accurate long balls                           |
| `overall_stat_attack_passes`                    | `Integer` | NULL     | Total passes attempted                        |
| `overall_stat_attack_passes_successful`         | `Integer` | NULL     | Accurate passes                               |
| `overall_stat_attack_touches_in_opposition_box` | `Integer` | NULL     | Touches inside the opponent's penalty box     |
| `overall_stat_average_possession`               | `Double`  | NULL     | Average ball possession percentage            |
| `overall_stat_defense_blocks`                   | `Integer` | NULL     | Shots blocked by defenders                    |
| `overall_stat_defense_clearances`               | `Integer` | NULL     | Total defensive clearances                    |
| `overall_stat_defense_interceptions`            | `Integer` | NULL     | Interceptions made                            |
| `overall_stat_defense_tackles`                  | `Integer` | NULL     | Total tackles attempted                       |
| `overall_stat_defense_tackles_successful`       | `Integer` | NULL     | Tackles won                                   |
| `overall_stat_defense_saves`                    | `Integer` | NULL     | Goalkeeper saves                              |
| `overall_stat_defense_saves_penalty`            | `Integer` | NULL     | Penalties saved by the goalkeeper             |
| `overall_stat_defense_clean_sheets`             | `Integer` | NULL     | Clean sheets kept                             |
| `overall_stat_defense_duels_total`              | `Integer` | NULL     | Total duels contested                         |
| `overall_stat_defense_duels_won`                | `Integer` | NULL     | Duels won                                     |
| `overall_stat_defense_duels_aerial_total`       | `Integer` | NULL     | Total aerial duels                            |
| `overall_stat_defense_duels_aerial_won`         | `Integer` | NULL     | Aerial duels won                              |
| `overall_stat_defense_duels_ground_total`       | `Integer` | NULL     | Total ground duels                            |
| `overall_stat_defense_duels_ground_won`         | `Integer` | NULL     | Ground duels won                              |
| `overall_stat_discipline_fouls`                 | `Integer` | NULL     | Total fouls committed                         |
| `overall_stat_discipline_yellow_cards`          | `Integer` | NULL     | Yellow cards received                         |
| `overall_stat_discipline_red_cards`             | `Integer` | NULL     | Red cards received (total)                    |
| `overall_stat_discipline_red_cards_direct`      | `Integer` | NULL     | Direct red cards received                     |

**Calculated fields:**

```
overall_stat_attack_crosses           = successful_crosses + unsuccessful_crosses
overall_stat_attack_long_balls        = successful_long_passes + unsuccessful_long_passes
overall_stat_attack_passes_successful = successful_long_passes + successful_short_passes
overall_stat_defense_saves            = shots_conceded_inside_box + shots_conceded_outside_box
                                       - goals_conceded + penalties_saved
```

#### Momentum

| Column     | Type     | Nullable | Description                                                                                                             |
|------------|----------|----------|-------------------------------------------------------------------------------------------------------------------------|
| `momentum` | `Double` | NULL     | Team Momentum Index — a normalized measure of recent form relative to season average. Range: approximately −100 to +100 |

**Calculated field:**

```
N = last N matches (default N=5)

ΔPPM = PPM(N) - PPM(season)
     = (cumulative_points[-1] - cumulative_points[-(N+1)]) / N  -  overall_points / overall_matches

ΔxG  = average(team_xG - opponent_xG) over the N most recent matches

z(ΔPPM) = (ΔPPM - μ_ΔPPM) / σ_ΔPPM    # z-score across all teams in the season
z(ΔxG)  = (ΔxG  - μ_ΔxG)  / σ_ΔxG

momentum = 100 * tanh(0.5 * (0.6 * z(ΔPPM) + 0.4 * z(ΔxG)))
```

`NULL` when fewer than 2 teams have sufficient data for z-score normalization.

---

### analytics

Stores pre-computed aggregate analytics metrics for a season (e.g., league-wide per-match averages).

| Column           | Type                     | Nullable         | Description                                                                                                                                                                    |
|------------------|--------------------------|------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `id`             | `String`                 | NOT NULL (PK)    | *Inherited from BaseEntity*                                                                                                                                                    |
| `source`         | `Enum`                   | NOT NULL         | *Inherited*                                                                                                                                                                    |
| `source_id`      | `String`                 | NOT NULL, UNIQUE | *Inherited*                                                                                                                                                                    |
| `created_at`     | `DateTime`               | NOT NULL         | *Inherited*                                                                                                                                                                    |
| `updated_at`     | `DateTime`               | NOT NULL         | *Inherited*                                                                                                                                                                    |
| `season_id`      | `String` (FK)            | NOT NULL         | Foreign key → `seasons.id` (CASCADE DELETE)                                                                                                                                    |
| `key`            | `Enum(AnalyticsKeyEnum)` | NOT NULL         | Metric identifier. Values: `per_match_goals`, `per_match_pass_accuracy`, `per_match_substitutions`, `per_match_xg`, `per_match_yellow_cards`, `total_goals`, `total_red_cards` |
| `title_en`       | `String`                 | NOT NULL         | Display title in English                                                                                                                                                       |
| `title_kr`       | `String`                 | NOT NULL         | Display title in Korean                                                                                                                                                        |
| `value`          | `Float`                  | NOT NULL         | Current metric value                                                                                                                                                           |
| `delta`          | `Float`                  | NULL             | Change in value compared to the previous reporting period                                                                                                                      |
| `description_en` | `String`                 | NULL             | Optional description in English                                                                                                                                                |
| `description_kr` | `String`                 | NULL             | Optional description in Korean                                                                                                                                                 |

---

## Content Tables

### news

Stores news articles with bilingual content.

| Column          | Type                 | Nullable         | Description                                                      |
|-----------------|----------------------|------------------|------------------------------------------------------------------|
| `id`            | `String`             | NOT NULL (PK)    | *Inherited from BaseEntity*                                      |
| `source`        | `Enum`               | NOT NULL         | *Inherited — e.g., `the_athletic`*                               |
| `source_id`     | `String`             | NOT NULL, UNIQUE | *Inherited*                                                      |
| `created_at`    | `DateTime`           | NOT NULL         | *Inherited*                                                      |
| `updated_at`    | `DateTime`           | NOT NULL         | *Inherited*                                                      |
| `title_en`      | `String`             | NOT NULL         | Article title in English                                         |
| `title_kr`      | `String`             | NOT NULL         | Article title in Korean                                          |
| `content_en`    | `String`             | NOT NULL         | Full article content in English                                  |
| `content_kr`    | `String`             | NOT NULL         | Full article content in Korean                                   |
| `author_en`     | `ARRAY(String)`      | NOT NULL         | List of author names in English                                  |
| `author_kr`     | `ARRAY(String)`      | NOT NULL         | List of author names in Korean                                   |
| `publish_date`  | `DateTime`           | NOT NULL         | Publication date and time (UTC)                                  |
| `url`           | `String`             | NOT NULL         | Original article URL                                             |
| `thumbnail_url` | `String`             | NOT NULL         | URL to the article thumbnail image                               |
| `type`          | `Enum(NewsTypeEnum)` | NOT NULL         | Article type. Values: `full_article`, `tweet_summary`, `unknown` |

---

## Association Tables

### match_goal_association

Records individual goal events within a match.

| Column             | Type          | Nullable | PK | Description                                                        |
|--------------------|---------------|----------|----|--------------------------------------------------------------------|
| `match_id`         | `String` (FK) | NOT NULL | ✓  | Foreign key → `matches.id` (CASCADE DELETE)                        |
| `player_id`        | `String` (FK) | NOT NULL | ✓  | Foreign key → `players.id` (CASCADE DELETE) — player who scored    |
| `index`            | `Integer`     | NOT NULL | ✓  | Sequential index of this goal event within the match               |
| `is_home`          | `Boolean`     | NOT NULL | ✓  | `true` if the goal was scored for the home team                    |
| `assist_player_id` | `String` (FK) | NULL     | —  | Foreign key → `players.id` (SET NULL on DELETE) — assisting player |
| `clock`            | `Integer`     | NOT NULL | —  | Match minute when the goal was scored                              |
| `is_penalty`       | `Boolean`     | NOT NULL | —  | `true` if the goal was scored from a penalty kick                  |
| `is_own_goal`      | `Boolean`     | NOT NULL | —  | `true` if the goal was an own goal                                 |

**Composite PK:** `(match_id, player_id, index, is_home)`

---

### match_card_association

Records individual disciplinary card events within a match.

| Column      | Type                 | Nullable | PK | Description                                                                |
|-------------|----------------------|----------|----|----------------------------------------------------------------------------|
| `match_id`  | `String` (FK)        | NOT NULL | ✓  | Foreign key → `matches.id` (CASCADE DELETE)                                |
| `player_id` | `String` (FK)        | NOT NULL | ✓  | Foreign key → `players.id` (CASCADE DELETE) — player who received the card |
| `index`     | `Integer`            | NOT NULL | ✓  | Sequential index of this card event within the match                       |
| `card_type` | `Enum(CardTypeEnum)` | NOT NULL | ✓  | Card type. Values: `yellow`, `secondyellow`, `straightred`                 |
| `is_home`   | `Boolean`            | NOT NULL | ✓  | `true` if the card was for a home team player                              |
| `clock`     | `Integer`            | NOT NULL | —  | Match minute when the card was issued                                      |

**Composite PK:** `(match_id, player_id, index, card_type, is_home)`

---

### match_lineup_association

Records the starting lineup formation for each team in a match.

| Column         | Type                 | Nullable | PK | Description                                              |
|----------------|----------------------|----------|----|----------------------------------------------------------|
| `match_id`     | `String` (FK)        | NOT NULL | ✓  | Foreign key → `matches.id` (CASCADE DELETE)              |
| `player_id`    | `String` (FK)        | NOT NULL | ✓  | Foreign key → `players.id` (CASCADE DELETE)              |
| `is_home`      | `Boolean`            | NOT NULL | ✓  | `true` if the player is in the home team's lineup        |
| `position`     | `Enum(PositionEnum)` | NOT NULL | —  | Player's position in the formation                       |
| `shirt_number` | `Integer`            | NOT NULL | —  | Player's shirt number                                    |
| `row`          | `Integer`            | NOT NULL | —  | Formation row index (e.g., 0=goalkeeper, 1=defense, ...) |
| `column`       | `Integer`            | NOT NULL | —  | Position column within the row                           |

**Composite PK:** `(match_id, player_id, is_home)`

---

### match_substitute_association

Records players on the substitutes' bench for each team in a match.

| Column         | Type                 | Nullable | PK | Description                                      |
|----------------|----------------------|----------|----|--------------------------------------------------|
| `match_id`     | `String` (FK)        | NOT NULL | ✓  | Foreign key → `matches.id` (CASCADE DELETE)      |
| `player_id`    | `String` (FK)        | NOT NULL | ✓  | Foreign key → `players.id` (CASCADE DELETE)      |
| `is_home`      | `Boolean`            | NOT NULL | ✓  | `true` if the player is on the home team's bench |
| `position`     | `Enum(PositionEnum)` | NOT NULL | —  | Player's position                                |
| `shirt_number` | `Integer`            | NOT NULL | —  | Player's shirt number                            |

**Composite PK:** `(match_id, player_id, is_home)`

---

### match_substitution_association

Records substitution events (player swaps) during a match.

| Column          | Type          | Nullable | PK | Description                                                             |
|-----------------|---------------|----------|----|-------------------------------------------------------------------------|
| `match_id`      | `String` (FK) | NOT NULL | ✓  | Foreign key → `matches.id` (CASCADE DELETE)                             |
| `in_player_id`  | `String` (FK) | NOT NULL | ✓  | Foreign key → `players.id` (CASCADE DELETE) — player entering the pitch |
| `out_player_id` | `String` (FK) | NOT NULL | ✓  | Foreign key → `players.id` (CASCADE DELETE) — player leaving the pitch  |
| `is_home`       | `Boolean`     | NOT NULL | ✓  | `true` if the substitution is for the home team                         |
| `clock`         | `Integer`     | NOT NULL | —  | Match minute when the substitution occurred                             |

**Composite PK:** `(match_id, in_player_id, out_player_id, is_home)`

---

### team_stat_match_association

Links a `team_stats` record to the individual `matches` that contributed to it. Used to reconstruct per-match history
and for momentum calculation.

| Column         | Type          | Nullable | PK | Description                                              |
|----------------|---------------|----------|----|----------------------------------------------------------|
| `team_stat_id` | `String` (FK) | NOT NULL | ✓  | Foreign key → `team_stats.id` (CASCADE DELETE)           |
| `match_id`     | `String` (FK) | NOT NULL | ✓  | Foreign key → `matches.id` (CASCADE DELETE)              |
| `kickoff_time` | `DateTime`    | NOT NULL | —  | Scheduled kickoff time (used for chronological ordering) |
| `is_home`      | `Boolean`     | NOT NULL | —  | `true` if the team was the home side in this match       |

**Composite PK:** `(team_stat_id, match_id)`

---

### player_championship_association

Records which seasons a player participated in (championship memberships).

| Column      | Type          | Nullable | PK | Description                                                        |
|-------------|---------------|----------|----|--------------------------------------------------------------------|
| `player_id` | `String` (FK) | NOT NULL | ✓  | Foreign key → `players.id` (CASCADE DELETE)                        |
| `season_id` | `String` (FK) | NOT NULL | ✓  | Foreign key → `seasons.id` (CASCADE DELETE)                        |
| `date_end`  | `DateTime`    | NOT NULL | —  | End date of the player's participation in this championship season |

**Composite PK:** `(player_id, season_id)`

---

### team_championship_association

Records which seasons a team participated in (championship memberships).

| Column      | Type          | Nullable | PK | Description                                                      |
|-------------|---------------|----------|----|------------------------------------------------------------------|
| `team_id`   | `String` (FK) | NOT NULL | ✓  | Foreign key → `teams.id` (CASCADE DELETE)                        |
| `season_id` | `String` (FK) | NOT NULL | ✓  | Foreign key → `seasons.id` (CASCADE DELETE)                      |
| `date_end`  | `DateTime`    | NOT NULL | —  | End date of the team's participation in this championship season |

**Composite PK:** `(team_id, season_id)`

---

### player_stat_award_association

Links player season statistics to awards received during that season.

| Column           | Type          | Nullable | PK | Description                                      |
|------------------|---------------|----------|----|--------------------------------------------------|
| `player_stat_id` | `String` (FK) | NOT NULL | ✓  | Foreign key → `player_stats.id` (CASCADE DELETE) |
| `award_id`       | `String` (FK) | NOT NULL | ✓  | Foreign key → `awards.id` (CASCADE DELETE)       |
| `date`           | `DateTime`    | NOT NULL | ✓  | Date when the award was presented                |

**Composite PK:** `(player_stat_id, award_id, date)`

---

### staff_award_association

Links staff members to awards received.

| Column     | Type          | Nullable | PK | Description                                |
|------------|---------------|----------|----|--------------------------------------------|
| `staff_id` | `String` (FK) | NOT NULL | ✓  | Foreign key → `staffs.id` (CASCADE DELETE) |
| `award_id` | `String` (FK) | NOT NULL | ✓  | Foreign key → `awards.id` (CASCADE DELETE) |
| `date`     | `DateTime`    | NOT NULL | ✓  | Date when the award was presented          |

**Composite PK:** `(staff_id, award_id, date)`

---

### news_team_association

Links news articles to the teams mentioned in them.

| Column    | Type          | Nullable | PK | Description                               |
|-----------|---------------|----------|----|-------------------------------------------|
| `news_id` | `String` (FK) | NOT NULL | ✓  | Foreign key → `news.id` (CASCADE DELETE)  |
| `team_id` | `String` (FK) | NOT NULL | ✓  | Foreign key → `teams.id` (CASCADE DELETE) |

**Composite PK:** `(news_id, team_id)`
