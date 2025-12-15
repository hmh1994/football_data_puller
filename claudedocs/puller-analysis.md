# Pulselive New Puller 서비스 분석

이 문서는 `football_data_manager/puller/services/pulselive_new/services` 디렉토리에 정의된 모든 Puller 서비스와 해당 레포지토리/필드 갱신 의존성을 분석합니다.

---

## 요약 테이블

| Puller                          | 사용하는 레포지토리                                                               | 작업 유형  |
|---------------------------------|--------------------------------------------------------------------------|--------|
| `PulseliveNewCompetitionPuller` | CompetitionRepository                                                    | 생성     |
| `PulseliveNewSeasonPuller`      | SeasonRepository, CompetitionRepository                                  | 생성     |
| `PulseliveNewTeamPuller`        | TeamRepository, GroundRepository                                         | 생성, 갱신 |
| `PulseliveNewPlayerPuller`      | PlayerRepository                                                         | 생성, 갱신 |
| `PulseliveNewFixturePuller`     | FixtureRepository, TeamRepository, GroundRepository                      | 생성     |
| `PulseliveNewMatchPuller`       | MatchRepository, OfficialRepository, PlayerRepository, StaffRepository   | 생성, 갱신 |
| `PulseliveNewMatchStatPuller`   | MatchStatRepository, TeamRepository                                      | 생성     |
| `PulseliveNewPlayerStatsPuller` | PlayerStatRepository, TeamRepository                                     | Upsert |
| `PulseliveNewTeamStatsPuller`   | TeamStatRepository, FixtureRepository, MatchRepository, GroundRepository | 생성, 갱신 |
| `PulseliveNewAwardPuller`       | AwardRepository, PlayerRepository, PlayerStatRepository, StaffRepository | 생성, 갱신 |

---

## 상세 Puller 분석

### 1. PulseliveNewCompetitionPuller

**파일**: `pulselive_new_competition_puller.py`

**레포지토리**:

- `CompetitionRepository` (쓰기)

**CompetitionEntity 갱신 필드**:
| 필드 | 데이터 소스 | 작업 |
|------|-------------|------|
| `abbreviation` | `item.code` | 생성 |
| `name_en` | `item.name` | 생성 |
| `name_kr` | `translator.translate_word(item.name)` | 생성 |
| `source_id` | `item.id` | 생성 |

**비고**:

- `id_filter`를 사용하여 특정 대회만 필터링 (FA컵, 리그컵, 챔피언스리그, 유로파리그, 프리미어리그 등)
- `_next` 파라미터를 통한 페이지네이션 지원

---

### 2. PulseliveNewSeasonPuller

**파일**: `pulselive_new_season_puller.py`

**레포지토리**:

- `SeasonRepository` (쓰기)
- `CompetitionRepository` (읽기 전용 참조)

**SeasonEntity 갱신 필드**:
| 필드 | 데이터 소스 | 작업 |
|------|-------------|------|
| `abbreviation` | `year_start/year_end`로부터 생성 (예: "24/25") | 생성 |
| `competition` | 입력 파라미터 | 생성 |
| `date_end` | 마지막 매치위크의 최신 킥오프 시간 | 생성 |
| `date_start` | 매치위크 1의 가장 이른 킥오프 시간 | 생성 |
| `season_source_id` | `item.id` | 생성 |
| `year_end` | 시즌명에서 추출 | 생성 |
| `year_start` | 시즌명에서 추출 | 생성 |

**비고**:

- 이진 탐색을 사용하여 경기가 있는 마지막 매치위크 탐색
- "Season 2024/2025"와 같은 시즌명을 파싱하여 연도 경계 추출

---

### 3. PulseliveNewTeamPuller

**파일**: `pulselive_new_team_puller.py`

**레포지토리**:

- `TeamRepository` (쓰기)
- `GroundRepository` (쓰기)

**TeamEntity 갱신 필드**:
| 필드 | 데이터 소스 | 작업 |
|------|-------------|------|
| `abbreviation` | `team_item.abbr` | 생성 |
| `icon_url` | 검증된 프리미어리그 배지 URL | 생성, 갱신 |
| `name_en` | `team_item.name` | 생성 |
| `name_kr` | `translator.translate_word(team_item.name)` | 생성 |
| `short_name_en` | `team_item.short_name` 또는 `team_item.name` | 생성 |
| `short_name_kr` | `translator.translate_word(short_name)` | 생성 |
| `source_id` | `team_item.id` | 생성 |

**GroundEntity 갱신 필드**:
| 필드 | 데이터 소스 | 작업 |
|------|-------------|------|
| `capacity` | `stadium.capacity` | 생성 |
| `city_name_en` | `stadium.city` | 생성 |
| `city_name_kr` | `translator.translate_word(stadium.city)` | 생성 |
| `name_en` | `stadium.name` | 생성 |
| `name_kr` | `translator.translate_word(stadium.name)` | 생성 |

**비고**:

- 기존 팀의 `icon_url`이 비어있으면 갱신
- 배지 URL 설정 전 존재 여부 검증

---

### 4. PulseliveNewPlayerPuller

**파일**: `pulselive_new_player_puller.py`

**레포지토리**:

- `PlayerRepository` (쓰기)

**PlayerEntity 갱신 필드**:
| 필드 | 데이터 소스 | 작업 |
|------|-------------|------|
| `birth_country` | `player_item.country_of_birth` | 생성 |
| `birth_date` | `player_item.dates.birth` | 생성 |
| `display_name_en` | `player_item.name.simple_name` | 생성 |
| `display_name_kr` | `translator.translate_word(simple_name)` | 생성 |
| `full_name` | `player_item.name.full_name` | 생성 |
| `height` | `player_item.height` | 생성 |
| `nationality_en` | `player_item.country.country` | 생성 |
| `nationality_kr` | `translator.translate_word(country)` | 생성 |
| `nationality_flag_icon_url` | 검증된 국기 아이콘 URL | 생성 |
| `photo_url` | 검증된 선수 사진 URL | 생성, 갱신 |
| `position` | `PositionEnum.from_string(player_item.position)` | 생성 |
| `preferred_foot` | `SideEnum.from_string(player_item.preferred_foot)` | 생성 |
| `source_id` | `player_item.id.player_id` | 생성 |
| `weight` | `player_item.weight` | 생성 |

**비고**:

- 기존 선수의 `photo_url`이 비어있으면 갱신
- 반복 API 호출 방지를 위한 국가 번역 캐싱 사용

---

### 5. PulseliveNewFixturePuller

**파일**: `pulselive_new_fixture_puller.py`

**레포지토리**:

- `FixtureRepository` (쓰기)
- `TeamRepository` (읽기 전용 조회)
- `GroundRepository` (읽기 전용 조회)

**FixtureEntity 갱신 필드**:
| 필드 | 데이터 소스 | 작업 |
|------|-------------|------|
| `away_team` | `match.away_team.id`로 조회 | 생성 |
| `game_week` | `matchweek_number` 파라미터 | 생성 |
| `ground` | 경기장 이름으로 조회 | 생성 |
| `home_team` | `match.home_team.id`로 조회 | 생성 |
| `kickoff_time` | `create_utc_from_string(match.kickoff, match.kickoff_timezone)` | 생성 |
| `season` | 입력 파라미터 | 생성 |
| `source_id` | `match.match_id` | 생성 |

**비고**:

- 실행 전 팀 존재 필수 (없으면 ValueError 발생)
- 경기장 조회 시 이름의 첫 부분(쉼표 이전) 사용

---

### 6. PulseliveNewMatchPuller

**파일**: `pulselive_new_match_puller.py`

**레포지토리**:

- `MatchRepository` (쓰기)
- `OfficialRepository` (쓰기)
- `PlayerRepository` (읽기 전용 조회, 누락 시 PlayerPuller 트리거)
- `StaffRepository` (쓰기)

**MatchEntity 갱신 필드**:
| 필드 그룹 | 필드 | 작업 |
|-----------|------|------|
| **기본 정보** | `attendance`, `clock`, `period` | 생성, 갱신 |
| **홈팀** | `home_team_captain`, `home_team_manager`, `home_team_formation`, `home_team_score`,
`home_team_half_time_score` | 생성, 갱신 |
| **원정팀** | `away_team_captain`, `away_team_manager`, `away_team_formation`, `away_team_score`,
`away_team_half_time_score` | 생성, 갱신 |
| **심판진** | `official_main_referee`, `official_assistant_1_referee`, `official_assistant_2_referee`,
`official_fourth_referee`, `official_var`, `official_assistant_var` | 생성, 갱신 |
| **경기 일정** | `fixture` | 생성 |

**연관 필드 (MatchRepository 메서드)**:
| 연관 관계 | 메서드 | 필드 |
|-----------|--------|------|
| **선발 라인업** | `append_lineup()` | `player`, `position`, `shirt_number`, `row`, `column` |
| **교체 명단** | `append_substitute()` | `player`, `position`, `shirt_number` |
| **카드** | `append_card()` | `player`, `card_type`, `clock` |
| **득점** | `append_goal()` | `player`, `assist_player`, `is_penalty`, `is_own_goal`, `clock` |
| **교체** | `append_substitution()` | `in_player`, `out_player`, `clock` |

**OfficialEntity 갱신 필드**:
| 필드 | 데이터 소스 | 작업 |
|------|-------------|------|
| `display_name_en` | `official_info.simple_name` | 생성 |
| `display_name_kr` | `translator.translate_word(simple_name)` | 생성 |
| `full_name` | `official_info.full_name` | 생성 |

**StaffEntity 갱신 필드**:
| 필드 | 데이터 소스 | 작업 |
|------|-------------|------|
| `display_name_en` | `staff_info.simple_name` | 생성 |
| `display_name_kr` | `translator.translate_word(simple_name)` | 생성 |
| `full_name` | `staff_info.full_name` | 생성 |
| `source_id` | `staff_info.id` | 생성 |

**비고**:

- FULLTIME 상태가 아닌 기존 경기는 갱신
- `PulseliveNewPlayerPuller.process_player()`를 통해 누락된 선수 생성
- 감독에 대한 누락된 스태프 엔티티 생성

---

### 7. PulseliveNewMatchStatPuller

**파일**: `pulselive_new_match_stat_puller.py`

**레포지토리**:

- `MatchStatRepository` (쓰기)
- `TeamRepository` (읽기 전용 조회)

**MatchStatEntity 갱신 필드 (접두사 그룹)**:
| 필드 접두사 | 필드 |
|-------------|------|
| **big_chances_** | `big_chances`, `big_chances_missed` |
| **corners** | `corners` |
| **defense_** | `defense_blocks`, `defense_clearances`, `defense_interceptions`, `defense_keeper_saves`,
`defense_tackles_total`, `defense_tackles_won` |
| **discipline_** | `discipline_red_cards`, `discipline_yellow_cards` |
| **duels_** | `duels_aerial_total`, `duels_aerial_won`, `duels_dribbles_successful`, `duels_dribbles_total`,
`duels_ground_total`, `duels_ground_won`, `duels_total`, `duels_won` |
| **expected_goals_** | `expected_goals`, `expected_goals_non_penalty`, `expected_goals_on_target` |
| **fouls_** | `fouls_committed` |
| **passes_** | `passes_accurate`, `passes_accurate_crosses`, `passes_accurate_long_balls`, `passes_offsides`,
`passes_opposition_half`, `passes_own_half`, `passes_throws`, `passes_total`, `passes_total_crosses`,
`passes_total_long_balls`, `passes_touches_in_opposition_box` |
| **possession** | `possession` |
| **shots_** | `shots_blocked`, `shots_hit_woodwork`, `shots_inside_box`, `shots_off_target`, `shots_on_target`,
`shots_outside_box`, `shots_total` |
| **관계** | `match`, `team` |

**비고**:

- 경기당 2개의 MatchStatEntity 생성 (홈, 원정)
- `expected_goals_non_penalty` = `expected_goals - (penalties * 0.79)`로 계산

---

### 8. PulseliveNewPlayerStatsPuller

**파일**: `pulselive_new_player_stats_puller.py`

**레포지토리**:

- `PlayerStatRepository` (쓰기 - upsert)
- `TeamRepository` (읽기 전용 조회)

**PlayerStatEntity 갱신 필드 (접두사 그룹)**:
| 필드 접두사 | 필드 |
|-------------|------|
| **Core** | `number`, `player`, `season`, `team`, `appearances` |
| **defending_** | `defending_blocked`, `defending_duels_aerial_total`, `defending_duels_aerial_won`,
`defending_duels_ground_total`, `defending_duels_ground_won`, `defending_duels_total`, `defending_duels_won`,
`defending_fouls_committed`, `defending_interceptions`, `defending_possession_won_final_third`, `defending_recoveries`,
`defending_tackles_total`, `defending_tackles_won` |
| **discipline_** | `discipline_red_cards`, `discipline_red_cards_direct`, `discipline_yellow_cards` |
| **goalkeeping_** | `goalkeeping_clean_sheets`, `goalkeeping_goals_conceded`, `goalkeeping_goals_prevented`,
`goalkeeping_high_claim`, `goalkeeping_penalties_faced`, `goalkeeping_penalty_goals_conceded`,
`goalkeeping_penalty_saved`, `goalkeeping_saves` |
| **passing_** | `passing_assists`, `passing_chances_created`, `passing_crosses_successful`, `passing_crosses_total`,
`passing_expected_assists`, `passing_long_balls_accurate`, `passing_long_balls_total`, `passing_passes_successful`,
`passing_passes_total` |
| **possession_** | `possession_dribble_successful`, `possession_dribble_total`, `possession_fouls_won`,
`possession_touches`, `possession_touches_in_opposition_box` |
| **shooting_** | `shooting_expected_goals`, `shooting_expected_goals_non_penalty`, `shooting_expected_goals_on_target`,
`shooting_goals`, `shooting_goals_penalty`, `shooting_penalties_taken`, `shooting_shots`, `shooting_shots_on_target` |

**비고**:

- `upsert_player_stat()` 사용하여 생성 또는 갱신
- v1 선수 상세 API에서 등번호 조회
- 파생 필드 계산 (예: `goals_prevented`, `expected_goals_non_penalty`)

---

### 9. PulseliveNewTeamStatsPuller

**파일**: `pulselive_new_team_stats_puller.py`

**레포지토리**:

- `TeamStatRepository` (쓰기)
- `FixtureRepository` (읽기 전용 조회)
- `MatchRepository` (읽기 전용 조회)
- `GroundRepository` (읽기 전용 참조)

**TeamStatEntity 갱신 필드 (접두사 그룹)**:
| 필드 접두사 | 필드 |
|-------------|------|
| **Core** | `ground`, `season`, `team` |
| **attack_** | `attack_corners`, `attack_crosses`, `attack_crosses_successful`, `attack_expected_assists`,
`attack_expected_goals`, `attack_long_balls`, `attack_long_balls_successful`, `attack_passes`,
`attack_passes_successful`, `attack_shots_on_target`, `attack_total_shots`, `attack_touches_in_opposition_box` |
| **average_** | `average_possession` |
| **defense_** | `defense_blocks`, `defense_clean_sheets`, `defense_clearances`, `defense_duels_aerial_total`,
`defense_duels_aerial_won`, `defense_duels_ground_total`, `defense_duels_ground_won`, `defense_duels_total`,
`defense_duels_won`, `defense_interceptions`, `defense_saves`, `defense_saves_penalty`, `defense_tackles`,
`defense_tackles_successful` |
| **discipline_** | `discipline_fouls`, `discipline_red_cards`, `discipline_red_cards_direct`,
`discipline_yellow_cards` |

**연관 필드 (TeamStatRepository 메서드)**:
| 연관 관계 | 메서드 | 필드 |
|-----------|--------|------|
| **경기 일정** | `append_fixtures()` | `kickoff_time`, `match` |

**비고**:

- 존재하지 않으면 새 TeamStatEntity 생성
- `update_stats()` 메서드로 대량 필드 갱신
- 경기 일정 연관은 FULLTIME 경기만 처리

---

### 10. PulseliveNewAwardPuller

**파일**: `pulselive_new_award_puller.py`

**레포지토리**:

- `AwardRepository` (쓰기)
- `PlayerRepository` (읽기 전용 조회)
- `PlayerStatRepository` (쓰기 - 연관 추가)
- `StaffRepository` (쓰기)

**AwardEntity 갱신 필드**:
| 필드 | 데이터 소스 | 작업 |
|------|-------------|------|
| `_type` | `AwardTypeEnum.from_string(award_type_str)` | 생성 |
| `source_id` | 타입에서 자동 생성 | 생성 |

**PlayerStatEntity 연관 필드**:
| 연관 관계 | 메서드 | 필드 |
|-----------|--------|------|
| **수상** | `append_award_association()` | `award`, `date` |

**StaffEntity 갱신 필드**:
| 필드 | 데이터 소스 | 작업 |
|------|-------------|------|
| `display_name_en` | `manager_award.name.simple_name` | 생성 |
| `display_name_kr` | `translator.translate_word(simple_name)` | 생성 |
| `full_name` | `manager_award.name.full_name` | 생성 |
| `source_id` | `manager_award.id` | 생성 |

**StaffEntity 연관 필드**:
| 연관 관계 | 메서드 | 필드 |
|-----------|--------|------|
| **수상** | `append_award_association()` | `award`, `date` |

**비고**:

- 지원 수상 유형: POTM(이달의 선수), GOTM(이달의 골), SOTM(이달의 세이브), MOTM(이달의 감독), MOTS(시즌의 감독)
- 감독이 없으면 스태프 엔티티 생성
- 선수 수상에는 PlayerStat 및 Player 엔티티 존재 필수

---

## 의존성 그래프

```
Competition (대회)
    └── Season (시즌)
            ├── Team (팀) ────────────┬── Ground (경기장)
            │                         │
            ├── Player (선수) ────────┘
            │
            ├── Fixture (경기일정) ────── Team, Ground
            │       │
            │       └── Match (경기) ───── Official (심판), Staff (스태프), Player
            │               │
            │               ├── MatchStat (경기 통계)
            │               │
            │               └── (TeamStats에서 사용)
            │
            ├── PlayerStats (선수 통계) ─── Player, Team
            │       │
            │       └── Award (수상 연관)
            │
            ├── TeamStats (팀 통계) ────── Team, Ground, Fixture, Match
            │
            └── Award (수상) ───────────── PlayerStat (연관), Staff (연관)
```

---

## 권장 실행 순서

의존성에 따른 권장 실행 순서:

1. **PulseliveNewCompetitionPuller** - 기본 대회 데이터
2. **PulseliveNewSeasonPuller** - 각 대회의 시즌
3. **PulseliveNewTeamPuller** - 각 시즌의 팀 및 경기장
4. **PulseliveNewPlayerPuller** - 각 팀의 선수
5. **PulseliveNewFixturePuller** - 각 시즌/매치위크의 경기 일정
6. **PulseliveNewMatchPuller** - 각 경기 일정의 경기 상세
7. **PulseliveNewMatchStatPuller** - 각 경기의 경기 통계
8. **PulseliveNewPlayerStatsPuller** - 각 선수/시즌의 선수 통계
9. **PulseliveNewTeamStatsPuller** - 각 팀/시즌의 팀 통계
10. **PulseliveNewAwardPuller** - 각 시즌의 수상 (PlayerStats 필요)

---

## 참고사항

- 모든 Puller는 `PulseliveNewWebclient`를 사용하여 API 호출
- `TranslatorService`를 통해 한국어 번역 처리
- 중복 방지는 `source_id` (PulseLive ID) 기반
- 대부분의 Puller는 중복 방지를 위해 기존 엔티티 건너뜀
- 일부 Puller는 기존 엔티티의 특정 필드만 갱신 (icon_url, photo_url)
