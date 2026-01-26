# Football Data Puller - Database Schema Documentation

## Overview

이 문서는 Football Data Puller 프로젝트의 데이터베이스 스키마를 정의합니다.
모든 엔티티는 SQLAlchemy ORM을 기반으로 구현되어 있습니다.

## Entity Relationship Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Competition   │────<│     Season      │────<│    Fixture      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │                        │
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐     ┌─────────────────┐
                       │   TeamStat      │     │     Match       │
                       └─────────────────┘     └─────────────────┘
                              │                   │    │    │
                              │                   │    │    │
                              ▼                   │    │    │
                       ┌─────────────────┐       │    │    └──────<MatchStat
                       │ TeamStatMatch   │       │    │
                       │  Association    │       │    └──────<Lineup/Card/Goal/Substitution
                       └─────────────────┘       │
                                                 │
┌─────────────────┐     ┌─────────────────┐     │
│      Team       │────<│   PlayerStat    │<────┘
└─────────────────┘     └─────────────────┘
        │                      │
        │                      ▼
        │               ┌─────────────────┐
        │               │ PlayerStatAward │
        │               │   Association   │
        │               └─────────────────┘
        │                      │
        ▼                      ▼
┌─────────────────┐     ┌─────────────────┐
│     Player      │     │     Award       │
└─────────────────┘     └─────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Official     │     │     Staff       │────<│ StaffAwardAssoc │
└─────────────────┘     └─────────────────┘     └─────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Ground      │     │      News       │────<│ NewsTeamAssoc   │
└─────────────────┘     └─────────────────┘     └─────────────────┘

┌─────────────────┐
│   Analytics     │
└─────────────────┘
```

---

## Base Entities

### BaseEntity

모든 엔티티의 기본 클래스입니다.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID (String)` | Primary Key, auto-generated |
| `created_at` | `DateTime` | 생성 시간 (UTC) |
| `updated_at` | `DateTime` | 수정 시간 (UTC) |
| `source` | `SourceEnum` | 데이터 소스 |
| `source_id` | `String` | 소스 시스템의 고유 식별자 |

### PulseliveEntity (extends BaseEntity)

Pulselive 데이터 소스 전용 엔티티의 기본 클래스입니다.
- `source`가 자동으로 `SourceEnum.PULSELIVE`로 설정됩니다.

---

## Core Entities

### CompetitionEntity

대회/리그 정보를 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `abbreviation` | `String` | No | 대회 약어 (예: 'PL', 'UCL') |
| `name_en` | `String` | No | 대회명 (영문) |
| `name_kr` | `String` | No | 대회명 (한글) |
| `icon_url` | `String` | Yes | 대회 아이콘/로고 URL |
| `description_en` | `String` | Yes | 대회 설명 (영문) |
| `description_kr` | `String` | Yes | 대회 설명 (한글) |

**Relationships:**
- `Season` (1:N) - 대회에 속한 시즌들

---

### SeasonEntity

시즌 정보를 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `abbreviation` | `String` | No | 시즌 약어 (예: '23/24') |
| `competition_id` | `UUID` | No | FK → Competition |
| `date_start` | `DateTime` | No | 시즌 시작일 |
| `date_end` | `DateTime` | No | 시즌 종료일 |
| `year_start` | `Integer` | No | 시작 연도 |
| `year_end` | `Integer` | No | 종료 연도 |

**Relationships:**
- `Competition` (N:1)
- `Fixture` (1:N)
- `TeamStat` (1:N)
- `PlayerStat` (1:N)
- `Analytics` (1:N)

---

### TeamEntity

팀 정보를 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `abbreviation` | `String` | No | 팀 약어 (예: 'MCI', 'LIV') |
| `name_en` | `String` | No | 팀명 (영문) |
| `name_kr` | `String` | No | 팀명 (한글) |
| `short_name_en` | `String` | No | 짧은 팀명 (영문) |
| `short_name_kr` | `String` | No | 짧은 팀명 (한글) |
| `icon_url` | `String` | Yes | 팀 아이콘/로고 URL |
| `championship_season_associations` | `List` | No | 시즌 참가 연결 |

**Relationships:**
- `TeamChampionshipAssociation` (1:N)
- `Fixture` (as home/away team)
- `PlayerStat` (1:N)
- `TeamStat` (1:N)

---

### PlayerEntity

선수 정보를 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `display_name_en` | `String` | No | 표시명 (영문) |
| `display_name_kr` | `String` | No | 표시명 (한글) |
| `full_name` | `String` | No | 전체 이름 |
| `birth_country` | `String` | Yes | 출생 국가 |
| `birth_date` | `DateTime` | Yes | 생년월일 |
| `nationality_en` | `String` | No | 국적 (영문) |
| `nationality_kr` | `String` | No | 국적 (한글) |
| `nationality_flag_icon_url` | `String` | Yes | 국기 아이콘 URL |
| `position` | `PositionEnum` | No | 포지션 |
| `preferred_foot` | `SideEnum` | No | 주발 |
| `height` | `Integer` | Yes | 키 (cm) |
| `weight` | `Integer` | Yes | 몸무게 (kg) |
| `photo_url` | `String` | Yes | 선수 사진 URL |
| `championship_season_associations` | `List` | No | 시즌 참가 연결 |

**Relationships:**
- `PlayerChampionshipAssociation` (1:N)
- `PlayerStat` (1:N)
- `MatchLineupAssociation` (1:N)
- `MatchGoalAssociation` (1:N)
- `MatchCardAssociation` (1:N)
- `MatchSubstitutionAssociation` (1:N)

---

### GroundEntity

경기장 정보를 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `name_en` | `String` | No | 경기장명 (영문) |
| `name_kr` | `String` | No | 경기장명 (한글) |
| `city_name_en` | `String` | No | 도시명 (영문) |
| `city_name_kr` | `String` | No | 도시명 (한글) |
| `capacity` | `Integer` | Yes | 수용 인원 |
| `location_latitude` | `Float` | Yes | 위도 |
| `location_longitude` | `Float` | Yes | 경도 |

**Relationships:**
- `Fixture` (1:N)
- `TeamStat` (1:N)

---

### FixtureEntity

경기 일정 정보를 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `season_id` | `UUID` | No | FK → Season |
| `home_team_id` | `UUID` | No | FK → Team (홈팀) |
| `away_team_id` | `UUID` | No | FK → Team (원정팀) |
| `ground_id` | `UUID` | Yes | FK → Ground |
| `game_week` | `Integer` | No | 라운드/게임위크 |
| `kickoff_time` | `DateTime` | No | 킥오프 시간 |

**Relationships:**
- `Season` (N:1)
- `Team` (N:1, home)
- `Team` (N:1, away)
- `Ground` (N:1)
- `Match` (1:1)

---

### MatchEntity

경기 결과 정보를 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `fixture_id` | `UUID` | No | FK → Fixture |
| `attendance` | `Integer` | No | 관중 수 |
| `clock` | `Integer` | No | 경기 시간 (분) |
| `period` | `PeriodEnum` | No | 경기 상태 |
| **Home Team** |
| `home_team_id` | `UUID` | No | FK → Team |
| `home_team_captain_id` | `UUID` | Yes | FK → Player |
| `home_team_manager` | `UUID` | Yes | FK → Staff |
| `home_team_formation` | `List[int]` | No | 포메이션 (예: [4,4,2]) |
| `home_team_score` | `Integer` | No | 홈팀 득점 |
| `home_team_half_time_score` | `Integer` | Yes | 전반 득점 |
| **Away Team** |
| `away_team_id` | `UUID` | No | FK → Team |
| `away_team_captain_id` | `UUID` | Yes | FK → Player |
| `away_team_manager` | `UUID` | Yes | FK → Staff |
| `away_team_formation` | `List[int]` | No | 포메이션 |
| `away_team_score` | `Integer` | No | 원정팀 득점 |
| `away_team_half_time_score` | `Integer` | Yes | 전반 득점 |
| **Officials** |
| `official_main_referee_id` | `UUID` | Yes | FK → Official |
| `official_assistant_1_referee_id` | `UUID` | Yes | FK → Official |
| `official_assistant_2_referee_id` | `UUID` | Yes | FK → Official |
| `official_fourth_referee_id` | `UUID` | Yes | FK → Official |
| `official_var_id` | `UUID` | Yes | FK → Official |
| `official_assistant_var_id` | `UUID` | Yes | FK → Official |

**Associations:**
- `card_associations` - 경고/퇴장 카드
- `goal_associations` - 득점
- `lineup_associations` - 선발 라인업
- `substitute_associations` - 교체 명단
- `substitution_associations` - 실제 교체

**Computed Properties:**
- `is_home_won`, `is_away_won`, `is_drawn`
- `home_point`, `away_point`

---

### OfficialEntity

심판 정보를 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `display_name_en` | `String` | No | 표시명 (영문) |
| `display_name_kr` | `String` | No | 표시명 (한글) |
| `full_name` | `String` | No | 전체 이름 |

---

### StaffEntity

감독/코치 등 스태프 정보를 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `display_name_en` | `String` | No | 표시명 (영문) |
| `display_name_kr` | `String` | No | 표시명 (한글) |
| `full_name` | `String` | No | 전체 이름 |
| `award_associations` | `List` | No | 수상 연결 |

**Relationships:**
- `StaffAwardAssociation` (1:N)

---

### AwardEntity

수상 정보를 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `type` | `AwardTypeEnum` | No | 수상 타입 |
| `name_en` | `String` | Yes | 수상명 (영문) |
| `name_kr` | `String` | Yes | 수상명 (한글) |
| `description_en` | `String` | Yes | 설명 (영문) |
| `description_kr` | `String` | Yes | 설명 (한글) |
| `icon_url` | `String` | Yes | 수상 아이콘 URL |

---

### NewsEntity

뉴스 정보를 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `title_en` | `String` | No | 제목 (영문) |
| `title_kr` | `String` | No | 제목 (한글) |
| `content_en` | `String` | No | 내용 (영문) |
| `content_kr` | `String` | No | 내용 (한글) |
| `author_en` | `List[String]` | No | 작성자 (영문) |
| `author_kr` | `List[String]` | No | 작성자 (한글) |
| `publish_date` | `DateTime` | No | 발행일 |
| `url` | `String` | No | 원본 URL |
| `thumbnail_url` | `String` | No | 썸네일 URL |
| `type` | `NewsTypeEnum` | No | 뉴스 타입 |
| `team_associations` | `List` | No | 관련 팀 연결 |

---

### AnalyticsEntity

분석 지표 정보를 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `key` | `AnalyticsKeyEnum` | No | 지표 키 |
| `title_en` | `String` | No | 제목 (영문) |
| `title_kr` | `String` | No | 제목 (한글) |
| `value` | `Float` | No | 값 |
| `delta` | `Float` | Yes | 변화량 |
| `description_en` | `String` | Yes | 설명 (영문) |
| `description_kr` | `String` | Yes | 설명 (한글) |
| `season_id` | `UUID` | No | FK → Season |

---

## Statistics Entities

### PlayerStatEntity

선수 시즌 통계를 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `player_id` | `UUID` | No | FK → Player |
| `season_id` | `UUID` | No | FK → Season |
| `team_id` | `UUID` | No | FK → Team |
| `number` | `Integer` | No | 등번호 |
| `appearances` | `Integer` | No | 출전 횟수 |
| `award_associations` | `List` | No | 수상 연결 |

**Shooting Stats:**
| Field | Type | Description |
|-------|------|-------------|
| `shooting_goals` | `Integer` | 득점 수 |
| `shooting_goals_penalty` | `Integer` | PK 득점 |
| `shooting_penalties_taken` | `Integer` | PK 시도 |
| `shooting_shots` | `Integer` | 총 슈팅 |
| `shooting_shots_on_target` | `Integer` | 유효 슈팅 |
| `shooting_expected_goals` | `Float` | xG |
| `shooting_expected_goals_non_penalty` | `Float` | npxG |
| `shooting_expected_goals_on_target` | `Float` | xGOT |

**Passing Stats:**
| Field | Type | Description |
|-------|------|-------------|
| `passing_assists` | `Integer` | 어시스트 |
| `passing_chances_created` | `Integer` | 찬스 생성 |
| `passing_expected_assists` | `Float` | xA |
| `passing_passes_total` | `Integer` | 총 패스 |
| `passing_passes_successful` | `Integer` | 성공 패스 |
| `passing_crosses_total` | `Integer` | 크로스 시도 |
| `passing_crosses_successful` | `Integer` | 크로스 성공 |
| `passing_long_balls_total` | `Integer` | 롱볼 시도 |
| `passing_long_balls_accurate` | `Integer` | 롱볼 성공 |

**Defending Stats:**
| Field | Type | Description |
|-------|------|-------------|
| `defending_tackles_total` | `Integer` | 태클 시도 |
| `defending_tackles_won` | `Integer` | 태클 성공 |
| `defending_interceptions` | `Integer` | 인터셉트 |
| `defending_blocked` | `Integer` | 블로킹 |
| `defending_recoveries` | `Integer` | 볼 회수 |
| `defending_duels_total` | `Integer` | 총 경합 |
| `defending_duels_won` | `Integer` | 경합 승리 |
| `defending_duels_aerial_total` | `Integer` | 공중볼 경합 |
| `defending_duels_aerial_won` | `Integer` | 공중볼 승리 |
| `defending_duels_ground_total` | `Integer` | 지상 경합 |
| `defending_duels_ground_won` | `Integer` | 지상 승리 |
| `defending_fouls_committed` | `Integer` | 파울 |
| `defending_possession_won_final_third` | `Integer` | 최종 1/3 볼 탈취 |

**Possession Stats:**
| Field | Type | Description |
|-------|------|-------------|
| `possession_touches` | `Integer` | 볼 터치 |
| `possession_touches_in_opposition_box` | `Integer` | 상대 박스 내 터치 |
| `possession_dribble_total` | `Integer` | 드리블 시도 |
| `possession_dribble_successful` | `Integer` | 드리블 성공 |
| `possession_fouls_won` | `Integer` | 파울 유도 |

**Goalkeeping Stats:**
| Field | Type | Description |
|-------|------|-------------|
| `goalkeeping_saves` | `Integer` | 선방 |
| `goalkeeping_clean_sheets` | `Integer` | 클린시트 |
| `goalkeeping_goals_conceded` | `Integer` | 실점 |
| `goalkeeping_goals_prevented` | `Float` | 막은 골 |
| `goalkeeping_high_claim` | `Integer` | 하이 클레임 |
| `goalkeeping_penalties_faced` | `Integer` | PK 대면 |
| `goalkeeping_penalty_saved` | `Integer` | PK 선방 |
| `goalkeeping_penalty_goals_conceded` | `Integer` | PK 실점 |

**Discipline Stats:**
| Field | Type | Description |
|-------|------|-------------|
| `discipline_yellow_cards` | `Integer` | 경고 |
| `discipline_red_cards` | `Integer` | 퇴장 |
| `discipline_red_cards_direct` | `Integer` | 직접 퇴장 |

---

### TeamStatEntity

팀 시즌 통계를 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `team_id` | `UUID` | No | FK → Team |
| `season_id` | `UUID` | No | FK → Season |
| `ground_id` | `UUID` | No | FK → Ground |
| `match_associations` | `List` | No | 경기 연결 |

**Overall Statistics:**
| Field | Type | Description |
|-------|------|-------------|
| `overall_matches` | `Integer` | 총 경기 수 |
| `overall_matches_won` | `Integer` | 승리 |
| `overall_matches_drawn` | `Integer` | 무승부 |
| `overall_matches_lost` | `Integer` | 패배 |
| `overall_points` | `Integer` | 승점 |
| `overall_goals_for` | `Integer` | 득점 |
| `overall_goals_against` | `Integer` | 실점 |
| `overall_goals_difference` | `Integer` | 득실차 |
| `overall_cumulative_points` | `List[int]` | 누적 승점 |

**Home Statistics:**
| Field | Type | Description |
|-------|------|-------------|
| `home_matches` | `Integer` | 홈 경기 수 |
| `home_matches_won` | `Integer` | 홈 승리 |
| `home_matches_drawn` | `Integer` | 홈 무승부 |
| `home_matches_lost` | `Integer` | 홈 패배 |
| `home_points` | `Integer` | 홈 승점 |
| `home_goals_for` | `Integer` | 홈 득점 |
| `home_goals_against` | `Integer` | 홈 실점 |
| `home_goals_difference` | `Integer` | 홈 득실차 |
| `home_cumulative_points` | `List[int]` | 홈 누적 승점 |

**Away Statistics:**
| Field | Type | Description |
|-------|------|-------------|
| `away_matches` | `Integer` | 원정 경기 수 |
| `away_matches_won` | `Integer` | 원정 승리 |
| `away_matches_drawn` | `Integer` | 원정 무승부 |
| `away_matches_lost` | `Integer` | 원정 패배 |
| `away_points` | `Integer` | 원정 승점 |
| `away_goals_for` | `Integer` | 원정 득점 |
| `away_goals_against` | `Integer` | 원정 실점 |
| `away_goals_difference` | `Integer` | 원정 득실차 |
| `away_cumulative_points` | `List[int]` | 원정 누적 승점 |

**Advanced Attack Stats:**
| Field | Type | Description |
|-------|------|-------------|
| `overall_stat_attack_corners` | `Integer` | 코너킥 |
| `overall_stat_attack_crosses` | `Integer` | 크로스 |
| `overall_stat_attack_crosses_successful` | `Integer` | 크로스 성공 |
| `overall_stat_attack_expected_assists` | `Float` | xA |
| `overall_stat_attack_expected_goals` | `Float` | xG |
| `overall_stat_attack_long_balls` | `Integer` | 롱볼 |
| `overall_stat_attack_long_balls_successful` | `Integer` | 롱볼 성공 |
| `overall_stat_attack_passes` | `Integer` | 패스 |
| `overall_stat_attack_passes_successful` | `Integer` | 패스 성공 |
| `overall_stat_attack_shots_on_target` | `Integer` | 유효 슈팅 |
| `overall_stat_attack_total_shots` | `Integer` | 총 슈팅 |
| `overall_stat_attack_touches_in_opposition_box` | `Integer` | 상대 박스 터치 |

**Advanced Defense Stats:**
| Field | Type | Description |
|-------|------|-------------|
| `overall_stat_average_possession` | `Float` | 평균 점유율 |
| `overall_stat_defense_blocks` | `Integer` | 블로킹 |
| `overall_stat_defense_clean_sheets` | `Integer` | 클린시트 |
| `overall_stat_defense_clearances` | `Integer` | 클리어런스 |
| `overall_stat_defense_duels_*` | `Integer` | 경합 통계 |
| `overall_stat_defense_interceptions` | `Integer` | 인터셉트 |
| `overall_stat_defense_saves` | `Integer` | 선방 |
| `overall_stat_defense_saves_penalty` | `Integer` | PK 선방 |
| `overall_stat_defense_tackles` | `Integer` | 태클 |
| `overall_stat_defense_tackles_successful` | `Integer` | 태클 성공 |

**Discipline Stats:**
| Field | Type | Description |
|-------|------|-------------|
| `overall_stat_discipline_fouls` | `Integer` | 파울 |
| `overall_stat_discipline_yellow_cards` | `Integer` | 경고 |
| `overall_stat_discipline_red_cards` | `Integer` | 퇴장 |
| `overall_stat_discipline_red_cards_direct` | `Integer` | 직접 퇴장 |

---

### MatchStatEntity

경기별 팀 통계를 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `match_id` | `UUID` | No | FK → Match |
| `team_id` | `UUID` | No | FK → Team |

**Shooting Stats:**
| Field | Type | Description |
|-------|------|-------------|
| `shots_total` | `Integer` | 총 슈팅 |
| `shots_on_target` | `Integer` | 유효 슈팅 |
| `shots_off_target` | `Integer` | 빗나간 슈팅 |
| `shots_blocked` | `Integer` | 막힌 슈팅 |
| `shots_inside_box` | `Integer` | 박스 내 슈팅 |
| `shots_outside_box` | `Integer` | 박스 외 슈팅 |
| `shots_hit_woodwork` | `Integer` | 골대 맞춘 슈팅 |
| `big_chances` | `Integer` | 빅찬스 |
| `big_chances_missed` | `Integer` | 놓친 빅찬스 |
| `expected_goals` | `Float` | xG |
| `expected_goals_non_penalty` | `Float` | npxG |
| `expected_goals_on_target` | `Float` | xGOT |

**Passing Stats:**
| Field | Type | Description |
|-------|------|-------------|
| `passes_total` | `Integer` | 총 패스 |
| `passes_accurate` | `Integer` | 성공 패스 |
| `passes_own_half` | `Integer` | 자진영 패스 |
| `passes_opposition_half` | `Integer` | 상대 진영 패스 |
| `passes_total_crosses` | `Integer` | 크로스 시도 |
| `passes_accurate_crosses` | `Integer` | 크로스 성공 |
| `passes_total_long_balls` | `Integer` | 롱볼 시도 |
| `passes_accurate_long_balls` | `Integer` | 롱볼 성공 |
| `passes_throws` | `Integer` | 스로인 |
| `passes_offsides` | `Integer` | 오프사이드 |
| `passes_touches_in_opposition_box` | `Integer` | 상대 박스 터치 |

**Defense Stats:**
| Field | Type | Description |
|-------|------|-------------|
| `defense_tackles_total` | `Integer` | 태클 시도 |
| `defense_tackles_won` | `Integer` | 태클 성공 |
| `defense_interceptions` | `Integer` | 인터셉트 |
| `defense_blocks` | `Integer` | 블로킹 |
| `defense_clearances` | `Integer` | 클리어런스 |
| `defense_keeper_saves` | `Integer` | GK 선방 |
| `corners` | `Integer` | 코너킥 |

**Duels Stats:**
| Field | Type | Description |
|-------|------|-------------|
| `duels_total` | `Integer` | 총 경합 |
| `duels_won` | `Integer` | 경합 승리 |
| `duels_aerial_total` | `Integer` | 공중볼 경합 |
| `duels_aerial_won` | `Integer` | 공중볼 승리 |
| `duels_ground_total` | `Integer` | 지상 경합 |
| `duels_ground_won` | `Integer` | 지상 승리 |
| `duels_dribbles_total` | `Integer` | 드리블 시도 |
| `duels_dribbles_successful` | `Integer` | 드리블 성공 |

**Other Stats:**
| Field | Type | Description |
|-------|------|-------------|
| `possession` | `Float` | 점유율 (%) |
| `fouls_committed` | `Integer` | 파울 |
| `discipline_yellow_cards` | `Integer` | 경고 |
| `discipline_red_cards` | `Integer` | 퇴장 |

---

## Association Entities

### MatchGoalAssociation

경기 득점 정보를 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `match_id` | `UUID` | No | FK → Match |
| `player_id` | `UUID` | No | FK → Player (득점자) |
| `assist_player_id` | `UUID` | Yes | FK → Player (어시스트) |
| `index` | `Integer` | No | 득점 순서 |
| `clock` | `Integer` | No | 득점 시간 (분) |
| `is_penalty` | `Boolean` | No | PK 여부 |
| `is_own_goal` | `Boolean` | No | 자책골 여부 |
| `is_home` | `Boolean` | No | 홈팀 득점 여부 |

---

### MatchCardAssociation

경기 카드 정보를 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `match_id` | `UUID` | No | FK → Match |
| `player_id` | `UUID` | No | FK → Player |
| `index` | `Integer` | No | 카드 순서 |
| `card_type` | `CardTypeEnum` | No | 카드 타입 |
| `clock` | `Integer` | No | 카드 시간 (분) |
| `is_home` | `Boolean` | No | 홈팀 선수 여부 |

---

### MatchLineupAssociation

경기 선발 라인업을 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `match_id` | `UUID` | No | FK → Match |
| `player_id` | `UUID` | No | FK → Player |
| `position` | `PositionEnum` | No | 포지션 |
| `shirt_number` | `Integer` | No | 등번호 |
| `row` | `Integer` | No | 포메이션 행 |
| `column` | `Integer` | No | 포메이션 열 |
| `is_home` | `Boolean` | No | 홈팀 선수 여부 |

---

### MatchSubstituteAssociation

경기 교체 명단을 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `match_id` | `UUID` | No | FK → Match |
| `player_id` | `UUID` | No | FK → Player |
| `position` | `PositionEnum` | No | 포지션 |
| `shirt_number` | `Integer` | No | 등번호 |
| `is_home` | `Boolean` | No | 홈팀 선수 여부 |

---

### MatchSubstitutionAssociation

실제 교체 정보를 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `match_id` | `UUID` | No | FK → Match |
| `in_player_id` | `UUID` | No | FK → Player (교체 투입) |
| `out_player_id` | `UUID` | No | FK → Player (교체 아웃) |
| `clock` | `Integer` | No | 교체 시간 (분) |
| `is_home` | `Boolean` | No | 홈팀 교체 여부 |

---

### TeamChampionshipAssociation

팀-시즌 참가 연결을 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `team_id` | `UUID` | No | FK → Team |
| `season_id` | `UUID` | No | FK → Season |
| `date_end` | `DateTime` | No | 참가 종료일 |

---

### PlayerChampionshipAssociation

선수-시즌 참가 연결을 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `player_id` | `UUID` | No | FK → Player |
| `season_id` | `UUID` | No | FK → Season |
| `date_end` | `DateTime` | No | 참가 종료일 |

---

### TeamStatMatchAssociation

팀 통계-경기 연결을 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `team_stat_id` | `UUID` | No | FK → TeamStat |
| `match_id` | `UUID` | No | FK → Match |
| `kickoff_time` | `DateTime` | No | 킥오프 시간 |
| `is_home` | `Boolean` | No | 홈 경기 여부 |

---

### PlayerStatAwardAssociation

선수 통계-수상 연결을 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `player_stat_id` | `UUID` | No | FK → PlayerStat |
| `award_id` | `UUID` | No | FK → Award |
| `date` | `DateTime` | No | 수상 날짜 |

---

### StaffAwardAssociation

스태프-수상 연결을 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `staff_id` | `UUID` | No | FK → Staff |
| `award_id` | `UUID` | No | FK → Award |
| `date` | `DateTime` | No | 수상 날짜 |

---

### NewsTeamAssociation

뉴스-팀 연결을 저장합니다.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `news_id` | `UUID` | No | FK → News |
| `team_id` | `UUID` | No | FK → Team |

---

## Enumerations

### SourceEnum

데이터 소스를 정의합니다.

| Value | Description |
|-------|-------------|
| `PULSELIVE` | Pulselive API |
| `THE_ATHLETIC` | The Athletic |
| `UNKNOWN` | 알 수 없음 |

---

### PositionEnum

선수 포지션을 정의합니다.

| Value | Description |
|-------|-------------|
| `GOALKEEPER` | 골키퍼 |
| `DEFENDER` | 수비수 |
| `MIDFIELDER` | 미드필더 |
| `FORWARD` | 공격수 |
| `UNKNOWN` | 알 수 없음 |

---

### SideEnum

발 선호도를 정의합니다.

| Value | Description |
|-------|-------------|
| `RIGHT` | 오른발 |
| `LEFT` | 왼발 |
| `BOTH` | 양발 |
| `UNKNOWN` | 알 수 없음 |

---

### CardTypeEnum

카드 타입을 정의합니다.

| Value | Description |
|-------|-------------|
| `FIRST_YELLOW` | 경고 |
| `SECOND_YELLOW` | 누적 경고 퇴장 |
| `DIRECT_RED` | 직접 퇴장 |

---

### PeriodEnum

경기 상태를 정의합니다.

| Value | Description |
|-------|-------------|
| `PREMATCH` | 경기 전 |
| `FIRSTHALF` | 전반전 |
| `SECONDHALF` | 후반전 |
| `FULLTIME` | 경기 종료 |
| `UNKNOWN` | 알 수 없음 |

---

### AwardTypeEnum

수상 타입을 정의합니다.

| Value | Code | Description |
|-------|------|-------------|
| `PLAYER_OF_THE_MONTH` | POTM | 이달의 선수 |
| `GOAL_OF_THE_MONTH` | GOTM | 이달의 골 |
| `SAVE_OF_THE_MONTH` | SOTM | 이달의 선방 |
| `MANAGER_OF_THE_MONTH` | MOTM | 이달의 감독 |
| `PLAYER_OF_THE_SEASON` | POTS | 시즌 MVP |
| `YOUNG_PLAYER_OF_THE_SEASON` | YPOTS | 시즌 영플레이어 |
| `PLAYMAKER_OF_THE_SEASON` | PM | 시즌 플레이메이커 |
| `GOAL_OF_THE_SEASON` | GOTS | 시즌 최고의 골 |
| `MOST_POWERFUL_GOAL_OF_THE_SEASON` | MPGOTS | 시즌 가장 강력한 골 |
| `SAVE_OF_THE_SEASON` | SOTS | 시즌 최고의 선방 |
| `GOLDEN_BOOT` | GB | 득점왕 |
| `GOLDEN_GLOVE` | GG | 골든 글러브 |
| `MOST_IMPROBABLE_COMEBACK_OF_THE_SEASON` | MICOTS | 시즌 대역전 |
| `GAMECHANGER_OF_THE_SEASON` | GCOTS | 시즌 게임체인저 |
| `MANAGER_OF_THE_SEASON` | MOTS | 시즌 최고의 감독 |

---

### NewsTypeEnum

뉴스 타입을 정의합니다.

| Value | Description |
|-------|-------------|
| `FULL_ARTICLE` | 전체 기사 |
| `TWEET_SUMMARY` | 트윗 요약 |
| `UNKNOWN` | 알 수 없음 |

---

### AnalyticsKeyEnum

분석 지표 키를 정의합니다.

| Value | Description |
|-------|-------------|
| `PER_MATCH_GOALS` | 경기당 득점 |
| `PER_MATCH_PASS_ACCURACY` | 경기당 패스 성공률 |
| `PER_MATCH_SUBSTITUTIONS` | 경기당 교체 |
| `PER_MATCH_XG` | 경기당 xG |
| `PER_MATCH_YELLOW_CARDS` | 경기당 경고 |
| `TOTAL_GOALS` | 총 득점 |
| `TOTAL_RED_CARDS` | 총 퇴장 |

---

## Data Sources

### Pulselive API
- Premier League 공식 데이터 제공
- 경기, 선수, 팀 통계 등 핵심 데이터

### The Athletic
- 뉴스 및 기사 데이터
- GraphQL API 사용

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2024-12 | Initial schema documentation |