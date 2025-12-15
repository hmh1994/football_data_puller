# 엔티티별 필드 갱신 분석

이 문서는 각 엔티티의 필드가 어떤 Puller에 의해 갱신되는지 분석합니다.
`puller-analysis.md`를 기반으로 엔티티 중심의 관점에서 재구성한 문서입니다.

---

## 요약 테이블

| 엔티티               | 갱신하는 Puller                    | 필드 수 | 작업 유형        |
|-------------------|--------------------------------|------|--------------|
| CompetitionEntity | CompetitionPuller              | 4    | 생성           |
| SeasonEntity      | SeasonPuller                   | 7    | 생성           |
| TeamEntity        | TeamPuller                     | 7    | 생성, 갱신       |
| GroundEntity      | TeamPuller                     | 5    | 생성           |
| PlayerEntity      | PlayerPuller, MatchPuller      | 14   | 생성, 갱신       |
| FixtureEntity     | FixturePuller                  | 7    | 생성           |
| MatchEntity       | MatchPuller                    | 19+  | 생성, 갱신       |
| OfficialEntity    | MatchPuller                    | 3    | 생성           |
| StaffEntity       | MatchPuller, AwardPuller       | 4    | 생성           |
| MatchStatEntity   | MatchStatPuller                | 35+  | 생성           |
| PlayerStatEntity  | PlayerStatsPuller, AwardPuller | 55+  | Upsert, 연관추가 |
| TeamStatEntity    | TeamStatsPuller                | 32+  | 생성, 갱신       |
| AwardEntity       | AwardPuller                    | 2    | 생성           |

---

## 상세 엔티티별 분석

### 1. CompetitionEntity

**갱신 Puller**: `PulseliveNewCompetitionPuller`

| 필드             | Puller            | 작업 | 비고          |
|----------------|-------------------|----|-------------|
| `abbreviation` | CompetitionPuller | 생성 | `item.code` |
| `name_en`      | CompetitionPuller | 생성 | `item.name` |
| `name_kr`      | CompetitionPuller | 생성 | 번역 처리       |
| `source_id`    | CompetitionPuller | 생성 | `item.id`   |

**특이사항**: 단일 Puller에서만 갱신, 생성 후 변경 없음

---

### 2. SeasonEntity

**갱신 Puller**: `PulseliveNewSeasonPuller`

| 필드                 | Puller       | 작업 | 비고          |
|--------------------|--------------|----|-------------|
| `abbreviation`     | SeasonPuller | 생성 | "24/25" 형식  |
| `competition`      | SeasonPuller | 생성 | FK 참조       |
| `date_end`         | SeasonPuller | 생성 | 마지막 매치위크 기준 |
| `date_start`       | SeasonPuller | 생성 | 첫 매치위크 기준   |
| `season_source_id` | SeasonPuller | 생성 | `item.id`   |
| `year_end`         | SeasonPuller | 생성 | 시즌명 파싱      |
| `year_start`       | SeasonPuller | 생성 | 시즌명 파싱      |

**특이사항**: 단일 Puller에서만 갱신, 생성 후 변경 없음

---

### 3. TeamEntity

**갱신 Puller**: `PulseliveNewTeamPuller`

| 필드              | Puller     | 작업         | 비고                     |
|-----------------|------------|------------|------------------------|
| `abbreviation`  | TeamPuller | 생성         | `team_item.abbr`       |
| `icon_url`      | TeamPuller | 생성, **갱신** | 비어있으면 갱신               |
| `name_en`       | TeamPuller | 생성         | `team_item.name`       |
| `name_kr`       | TeamPuller | 생성         | 번역 처리                  |
| `short_name_en` | TeamPuller | 생성         | `team_item.short_name` |
| `short_name_kr` | TeamPuller | 생성         | 번역 처리                  |
| `source_id`     | TeamPuller | 생성         | `team_item.id`         |

**특이사항**: `icon_url`만 조건부 갱신 (비어있는 경우)

---

### 4. GroundEntity

**갱신 Puller**: `PulseliveNewTeamPuller`

| 필드             | Puller     | 작업 | 비고                 |
|----------------|------------|----|--------------------|
| `capacity`     | TeamPuller | 생성 | `stadium.capacity` |
| `city_name_en` | TeamPuller | 생성 | `stadium.city`     |
| `city_name_kr` | TeamPuller | 생성 | 번역 처리              |
| `name_en`      | TeamPuller | 생성 | `stadium.name`     |
| `name_kr`      | TeamPuller | 생성 | 번역 처리              |

**특이사항**: TeamPuller에서 팀과 함께 생성, 생성 후 변경 없음

---

### 5. PlayerEntity

**갱신 Puller**: `PulseliveNewPlayerPuller`, `PulseliveNewMatchPuller` (간접)

| 필드                          | Puller       | 작업         | 비고                             |
|-----------------------------|--------------|------------|--------------------------------|
| `birth_country`             | PlayerPuller | 생성         | `player_item.country_of_birth` |
| `birth_date`                | PlayerPuller | 생성         | `player_item.dates.birth`      |
| `display_name_en`           | PlayerPuller | 생성         | `player_item.name.simple_name` |
| `display_name_kr`           | PlayerPuller | 생성         | 번역 처리                          |
| `full_name`                 | PlayerPuller | 생성         | `player_item.name.full_name`   |
| `height`                    | PlayerPuller | 생성         | `player_item.height`           |
| `nationality_en`            | PlayerPuller | 생성         | `player_item.country.country`  |
| `nationality_kr`            | PlayerPuller | 생성         | 번역 처리                          |
| `nationality_flag_icon_url` | PlayerPuller | 생성         | 검증된 URL                        |
| `photo_url`                 | PlayerPuller | 생성, **갱신** | 비어있으면 갱신                       |
| `position`                  | PlayerPuller | 생성         | PositionEnum 변환                |
| `preferred_foot`            | PlayerPuller | 생성         | SideEnum 변환                    |
| `source_id`                 | PlayerPuller | 생성         | `player_item.id.player_id`     |
| `weight`                    | PlayerPuller | 생성         | `player_item.weight`           |

**특이사항**:

- `photo_url`만 조건부 갱신 (비어있는 경우)
- MatchPuller에서 누락된 선수 발견 시 `PlayerPuller.process_player()` 호출하여 간접 생성

---

### 6. FixtureEntity

**갱신 Puller**: `PulseliveNewFixturePuller`

| 필드             | Puller        | 작업 | 비고                   |
|----------------|---------------|----|----------------------|
| `away_team`    | FixturePuller | 생성 | FK 참조 (TeamEntity)   |
| `game_week`    | FixturePuller | 생성 | 매치위크 번호              |
| `ground`       | FixturePuller | 생성 | FK 참조 (GroundEntity) |
| `home_team`    | FixturePuller | 생성 | FK 참조 (TeamEntity)   |
| `kickoff_time` | FixturePuller | 생성 | UTC 변환               |
| `season`       | FixturePuller | 생성 | FK 참조 (SeasonEntity) |
| `source_id`    | FixturePuller | 생성 | `match.match_id`     |

**특이사항**: 단일 Puller에서만 갱신, 생성 후 변경 없음

---

### 7. MatchEntity

**갱신 Puller**: `PulseliveNewMatchPuller`

#### 기본 필드

| 필드           | Puller      | 작업     | 비고    |
|--------------|-------------|--------|-------|
| `attendance` | MatchPuller | 생성, 갱신 | 관중 수  |
| `clock`      | MatchPuller | 생성, 갱신 | 경기 시간 |
| `period`     | MatchPuller | 생성, 갱신 | 경기 상태 |
| `fixture`    | MatchPuller | 생성     | FK 참조 |

#### 홈팀 필드 (home_team_*)

| 필드                          | Puller      | 작업     | 비고                   |
|-----------------------------|-------------|--------|----------------------|
| `home_team_captain`         | MatchPuller | 생성, 갱신 | FK 참조 (PlayerEntity) |
| `home_team_manager`         | MatchPuller | 생성, 갱신 | FK 참조 (StaffEntity)  |
| `home_team_formation`       | MatchPuller | 생성, 갱신 | 포메이션 문자열             |
| `home_team_score`           | MatchPuller | 생성, 갱신 | 최종 점수                |
| `home_team_half_time_score` | MatchPuller | 생성, 갱신 | 전반 점수                |

#### 원정팀 필드 (away_team_*)

| 필드                          | Puller      | 작업     | 비고                   |
|-----------------------------|-------------|--------|----------------------|
| `away_team_captain`         | MatchPuller | 생성, 갱신 | FK 참조 (PlayerEntity) |
| `away_team_manager`         | MatchPuller | 생성, 갱신 | FK 참조 (StaffEntity)  |
| `away_team_formation`       | MatchPuller | 생성, 갱신 | 포메이션 문자열             |
| `away_team_score`           | MatchPuller | 생성, 갱신 | 최종 점수                |
| `away_team_half_time_score` | MatchPuller | 생성, 갱신 | 전반 점수                |

#### 심판진 필드 (official_*)

| 필드                             | Puller      | 작업     | 비고                     |
|--------------------------------|-------------|--------|------------------------|
| `official_main_referee`        | MatchPuller | 생성, 갱신 | FK 참조 (OfficialEntity) |
| `official_assistant_1_referee` | MatchPuller | 생성, 갱신 | FK 참조 (OfficialEntity) |
| `official_assistant_2_referee` | MatchPuller | 생성, 갱신 | FK 참조 (OfficialEntity) |
| `official_fourth_referee`      | MatchPuller | 생성, 갱신 | FK 참조 (OfficialEntity) |
| `official_var`                 | MatchPuller | 생성, 갱신 | FK 참조 (OfficialEntity) |
| `official_assistant_var`       | MatchPuller | 생성, 갱신 | FK 참조 (OfficialEntity) |

#### 연관 테이블 (Association)

| 연관 관계  | Puller      | 메서드                     | 필드                                                              |
|--------|-------------|-------------------------|-----------------------------------------------------------------|
| 선발 라인업 | MatchPuller | `append_lineup()`       | `player`, `position`, `shirt_number`, `row`, `column`           |
| 교체 명단  | MatchPuller | `append_substitute()`   | `player`, `position`, `shirt_number`                            |
| 카드     | MatchPuller | `append_card()`         | `player`, `card_type`, `clock`                                  |
| 득점     | MatchPuller | `append_goal()`         | `player`, `assist_player`, `is_penalty`, `is_own_goal`, `clock` |
| 교체     | MatchPuller | `append_substitution()` | `in_player`, `out_player`, `clock`                              |

**특이사항**: FULLTIME 상태가 아닌 경기는 갱신, 연관 테이블도 함께 처리

---

### 8. OfficialEntity

**갱신 Puller**: `PulseliveNewMatchPuller`

| 필드                | Puller      | 작업 | 비고                          |
|-------------------|-------------|----|-----------------------------|
| `display_name_en` | MatchPuller | 생성 | `official_info.simple_name` |
| `display_name_kr` | MatchPuller | 생성 | 번역 처리                       |
| `full_name`       | MatchPuller | 생성 | `official_info.full_name`   |

**특이사항**: MatchPuller에서 경기 처리 시 함께 생성, 생성 후 변경 없음

---

### 9. StaffEntity

**갱신 Puller**: `PulseliveNewMatchPuller`, `PulseliveNewAwardPuller`

| 필드                | Puller                   | 작업 | 비고                       |
|-------------------|--------------------------|----|--------------------------|
| `display_name_en` | MatchPuller, AwardPuller | 생성 | `staff_info.simple_name` |
| `display_name_kr` | MatchPuller, AwardPuller | 생성 | 번역 처리                    |
| `full_name`       | MatchPuller, AwardPuller | 생성 | `staff_info.full_name`   |
| `source_id`       | MatchPuller, AwardPuller | 생성 | `staff_info.id`          |

#### 연관 테이블 (Association)

| 연관 관계 | Puller      | 메서드                          | 필드              |
|-------|-------------|------------------------------|-----------------|
| 수상    | AwardPuller | `append_award_association()` | `award`, `date` |

**특이사항**:

- MatchPuller: 감독 정보 생성
- AwardPuller: 감독 수상 시 스태프 생성 및 수상 연관 추가

---

### 10. MatchStatEntity

**갱신 Puller**: `PulseliveNewMatchStatPuller`

#### 빅찬스 필드 (big_chances_*)

| 필드                   | Puller          | 작업 |
|----------------------|-----------------|----|
| `big_chances`        | MatchStatPuller | 생성 |
| `big_chances_missed` | MatchStatPuller | 생성 |

#### 수비 필드 (defense_*)

| 필드                      | Puller          | 작업 |
|-------------------------|-----------------|----|
| `defense_blocks`        | MatchStatPuller | 생성 |
| `defense_clearances`    | MatchStatPuller | 생성 |
| `defense_interceptions` | MatchStatPuller | 생성 |
| `defense_keeper_saves`  | MatchStatPuller | 생성 |
| `defense_tackles_total` | MatchStatPuller | 생성 |
| `defense_tackles_won`   | MatchStatPuller | 생성 |

#### 징계 필드 (discipline_*)

| 필드                        | Puller          | 작업 |
|---------------------------|-----------------|----|
| `discipline_red_cards`    | MatchStatPuller | 생성 |
| `discipline_yellow_cards` | MatchStatPuller | 생성 |

#### 듀얼 필드 (duels_*)

| 필드                          | Puller          | 작업 |
|-----------------------------|-----------------|----|
| `duels_aerial_total`        | MatchStatPuller | 생성 |
| `duels_aerial_won`          | MatchStatPuller | 생성 |
| `duels_dribbles_successful` | MatchStatPuller | 생성 |
| `duels_dribbles_total`      | MatchStatPuller | 생성 |
| `duels_ground_total`        | MatchStatPuller | 생성 |
| `duels_ground_won`          | MatchStatPuller | 생성 |
| `duels_total`               | MatchStatPuller | 생성 |
| `duels_won`                 | MatchStatPuller | 생성 |

#### 기대골 필드 (expected_goals_*)

| 필드                           | Puller          | 작업 |
|------------------------------|-----------------|----|
| `expected_goals`             | MatchStatPuller | 생성 |
| `expected_goals_non_penalty` | MatchStatPuller | 생성 |
| `expected_goals_on_target`   | MatchStatPuller | 생성 |

#### 파울 필드 (fouls_*)

| 필드                | Puller          | 작업 |
|-------------------|-----------------|----|
| `fouls_committed` | MatchStatPuller | 생성 |

#### 패스 필드 (passes_*)

| 필드                                 | Puller          | 작업 |
|------------------------------------|-----------------|----|
| `passes_accurate`                  | MatchStatPuller | 생성 |
| `passes_accurate_crosses`          | MatchStatPuller | 생성 |
| `passes_accurate_long_balls`       | MatchStatPuller | 생성 |
| `passes_offsides`                  | MatchStatPuller | 생성 |
| `passes_opposition_half`           | MatchStatPuller | 생성 |
| `passes_own_half`                  | MatchStatPuller | 생성 |
| `passes_throws`                    | MatchStatPuller | 생성 |
| `passes_total`                     | MatchStatPuller | 생성 |
| `passes_total_crosses`             | MatchStatPuller | 생성 |
| `passes_total_long_balls`          | MatchStatPuller | 생성 |
| `passes_touches_in_opposition_box` | MatchStatPuller | 생성 |

#### 슛 필드 (shots_*)

| 필드                   | Puller          | 작업 |
|----------------------|-----------------|----|
| `shots_blocked`      | MatchStatPuller | 생성 |
| `shots_hit_woodwork` | MatchStatPuller | 생성 |
| `shots_inside_box`   | MatchStatPuller | 생성 |
| `shots_off_target`   | MatchStatPuller | 생성 |
| `shots_on_target`    | MatchStatPuller | 생성 |
| `shots_outside_box`  | MatchStatPuller | 생성 |
| `shots_total`        | MatchStatPuller | 생성 |

#### 기타 필드

| 필드           | Puller          | 작업 |
|--------------|-----------------|----|
| `corners`    | MatchStatPuller | 생성 |
| `possession` | MatchStatPuller | 생성 |
| `match`      | MatchStatPuller | 생성 |
| `team`       | MatchStatPuller | 생성 |

**특이사항**: 경기당 2개 생성 (홈/원정), 생성 후 변경 없음

---

### 11. PlayerStatEntity

**갱신 Puller**: `PulseliveNewPlayerStatsPuller`, `PulseliveNewAwardPuller`

#### 핵심 필드 (Core)

| 필드            | Puller            | 작업     |
|---------------|-------------------|--------|
| `number`      | PlayerStatsPuller | Upsert |
| `player`      | PlayerStatsPuller | Upsert |
| `season`      | PlayerStatsPuller | Upsert |
| `team`        | PlayerStatsPuller | Upsert |
| `appearances` | PlayerStatsPuller | Upsert |

#### 수비 필드 (defending_*)

| 필드                                     | Puller            | 작업     |
|----------------------------------------|-------------------|--------|
| `defending_blocked`                    | PlayerStatsPuller | Upsert |
| `defending_duels_aerial_total`         | PlayerStatsPuller | Upsert |
| `defending_duels_aerial_won`           | PlayerStatsPuller | Upsert |
| `defending_duels_ground_total`         | PlayerStatsPuller | Upsert |
| `defending_duels_ground_won`           | PlayerStatsPuller | Upsert |
| `defending_duels_total`                | PlayerStatsPuller | Upsert |
| `defending_duels_won`                  | PlayerStatsPuller | Upsert |
| `defending_fouls_committed`            | PlayerStatsPuller | Upsert |
| `defending_interceptions`              | PlayerStatsPuller | Upsert |
| `defending_possession_won_final_third` | PlayerStatsPuller | Upsert |
| `defending_recoveries`                 | PlayerStatsPuller | Upsert |
| `defending_tackles_total`              | PlayerStatsPuller | Upsert |
| `defending_tackles_won`                | PlayerStatsPuller | Upsert |

#### 징계 필드 (discipline_*)

| 필드                            | Puller            | 작업     |
|-------------------------------|-------------------|--------|
| `discipline_red_cards`        | PlayerStatsPuller | Upsert |
| `discipline_red_cards_direct` | PlayerStatsPuller | Upsert |
| `discipline_yellow_cards`     | PlayerStatsPuller | Upsert |

#### 골키퍼 필드 (goalkeeping_*)

| 필드                                   | Puller            | 작업     |
|--------------------------------------|-------------------|--------|
| `goalkeeping_clean_sheets`           | PlayerStatsPuller | Upsert |
| `goalkeeping_goals_conceded`         | PlayerStatsPuller | Upsert |
| `goalkeeping_goals_prevented`        | PlayerStatsPuller | Upsert |
| `goalkeeping_high_claim`             | PlayerStatsPuller | Upsert |
| `goalkeeping_penalties_faced`        | PlayerStatsPuller | Upsert |
| `goalkeeping_penalty_goals_conceded` | PlayerStatsPuller | Upsert |
| `goalkeeping_penalty_saved`          | PlayerStatsPuller | Upsert |
| `goalkeeping_saves`                  | PlayerStatsPuller | Upsert |

#### 패스 필드 (passing_*)

| 필드                            | Puller            | 작업     |
|-------------------------------|-------------------|--------|
| `passing_assists`             | PlayerStatsPuller | Upsert |
| `passing_chances_created`     | PlayerStatsPuller | Upsert |
| `passing_crosses_successful`  | PlayerStatsPuller | Upsert |
| `passing_crosses_total`       | PlayerStatsPuller | Upsert |
| `passing_expected_assists`    | PlayerStatsPuller | Upsert |
| `passing_long_balls_accurate` | PlayerStatsPuller | Upsert |
| `passing_long_balls_total`    | PlayerStatsPuller | Upsert |
| `passing_passes_successful`   | PlayerStatsPuller | Upsert |
| `passing_passes_total`        | PlayerStatsPuller | Upsert |

#### 점유 필드 (possession_*)

| 필드                                     | Puller            | 작업     |
|----------------------------------------|-------------------|--------|
| `possession_dribble_successful`        | PlayerStatsPuller | Upsert |
| `possession_dribble_total`             | PlayerStatsPuller | Upsert |
| `possession_fouls_won`                 | PlayerStatsPuller | Upsert |
| `possession_touches`                   | PlayerStatsPuller | Upsert |
| `possession_touches_in_opposition_box` | PlayerStatsPuller | Upsert |

#### 슈팅 필드 (shooting_*)

| 필드                                    | Puller            | 작업     |
|---------------------------------------|-------------------|--------|
| `shooting_expected_goals`             | PlayerStatsPuller | Upsert |
| `shooting_expected_goals_non_penalty` | PlayerStatsPuller | Upsert |
| `shooting_expected_goals_on_target`   | PlayerStatsPuller | Upsert |
| `shooting_goals`                      | PlayerStatsPuller | Upsert |
| `shooting_goals_penalty`              | PlayerStatsPuller | Upsert |
| `shooting_penalties_taken`            | PlayerStatsPuller | Upsert |
| `shooting_shots`                      | PlayerStatsPuller | Upsert |
| `shooting_shots_on_target`            | PlayerStatsPuller | Upsert |

#### 연관 테이블 (Association)

| 연관 관계 | Puller      | 메서드                          | 필드              |
|-------|-------------|------------------------------|-----------------|
| 수상    | AwardPuller | `append_award_association()` | `award`, `date` |

**특이사항**: PlayerStatsPuller는 Upsert 방식, AwardPuller는 수상 연관만 추가

---

### 12. TeamStatEntity

**갱신 Puller**: `PulseliveNewTeamStatsPuller`

#### 핵심 필드 (Core)

| 필드       | Puller          | 작업 |
|----------|-----------------|----|
| `ground` | TeamStatsPuller | 생성 |
| `season` | TeamStatsPuller | 생성 |
| `team`   | TeamStatsPuller | 생성 |

#### 공격 필드 (attack_*)

| 필드                                 | Puller          | 작업     |
|------------------------------------|-----------------|--------|
| `attack_corners`                   | TeamStatsPuller | 생성, 갱신 |
| `attack_crosses`                   | TeamStatsPuller | 생성, 갱신 |
| `attack_crosses_successful`        | TeamStatsPuller | 생성, 갱신 |
| `attack_expected_assists`          | TeamStatsPuller | 생성, 갱신 |
| `attack_expected_goals`            | TeamStatsPuller | 생성, 갱신 |
| `attack_long_balls`                | TeamStatsPuller | 생성, 갱신 |
| `attack_long_balls_successful`     | TeamStatsPuller | 생성, 갱신 |
| `attack_passes`                    | TeamStatsPuller | 생성, 갱신 |
| `attack_passes_successful`         | TeamStatsPuller | 생성, 갱신 |
| `attack_shots_on_target`           | TeamStatsPuller | 생성, 갱신 |
| `attack_total_shots`               | TeamStatsPuller | 생성, 갱신 |
| `attack_touches_in_opposition_box` | TeamStatsPuller | 생성, 갱신 |

#### 평균 필드 (average_*)

| 필드                   | Puller          | 작업     |
|----------------------|-----------------|--------|
| `average_possession` | TeamStatsPuller | 생성, 갱신 |

#### 수비 필드 (defense_*)

| 필드                           | Puller          | 작업     |
|------------------------------|-----------------|--------|
| `defense_blocks`             | TeamStatsPuller | 생성, 갱신 |
| `defense_clean_sheets`       | TeamStatsPuller | 생성, 갱신 |
| `defense_clearances`         | TeamStatsPuller | 생성, 갱신 |
| `defense_duels_aerial_total` | TeamStatsPuller | 생성, 갱신 |
| `defense_duels_aerial_won`   | TeamStatsPuller | 생성, 갱신 |
| `defense_duels_ground_total` | TeamStatsPuller | 생성, 갱신 |
| `defense_duels_ground_won`   | TeamStatsPuller | 생성, 갱신 |
| `defense_duels_total`        | TeamStatsPuller | 생성, 갱신 |
| `defense_duels_won`          | TeamStatsPuller | 생성, 갱신 |
| `defense_interceptions`      | TeamStatsPuller | 생성, 갱신 |
| `defense_saves`              | TeamStatsPuller | 생성, 갱신 |
| `defense_saves_penalty`      | TeamStatsPuller | 생성, 갱신 |
| `defense_tackles`            | TeamStatsPuller | 생성, 갱신 |
| `defense_tackles_successful` | TeamStatsPuller | 생성, 갱신 |

#### 징계 필드 (discipline_*)

| 필드                            | Puller          | 작업     |
|-------------------------------|-----------------|--------|
| `discipline_fouls`            | TeamStatsPuller | 생성, 갱신 |
| `discipline_red_cards`        | TeamStatsPuller | 생성, 갱신 |
| `discipline_red_cards_direct` | TeamStatsPuller | 생성, 갱신 |
| `discipline_yellow_cards`     | TeamStatsPuller | 생성, 갱신 |

#### 연관 테이블 (Association)

| 연관 관계 | Puller          | 메서드                 | 필드                      |
|-------|-----------------|---------------------|-------------------------|
| 경기 일정 | TeamStatsPuller | `append_fixtures()` | `kickoff_time`, `match` |

**특이사항**: `update_stats()` 메서드로 대량 필드 갱신, FULLTIME 경기만 연관 처리

---

### 13. AwardEntity

**갱신 Puller**: `PulseliveNewAwardPuller`

| 필드          | Puller      | 작업 | 비고               |
|-------------|-------------|----|------------------|
| `_type`     | AwardPuller | 생성 | AwardTypeEnum 변환 |
| `source_id` | AwardPuller | 생성 | 타입에서 자동 생성       |

**지원 수상 유형**:

- POTM: 이달의 선수 (Player of the Month)
- GOTM: 이달의 골 (Goal of the Month)
- SOTM: 이달의 세이브 (Save of the Month)
- MOTM: 이달의 감독 (Manager of the Month)
- MOTS: 시즌의 감독 (Manager of the Season)

**특이사항**: 단일 Puller에서만 갱신, 생성 후 변경 없음

---

## 필드 갱신 패턴 요약

### 단일 Puller 갱신 (생성 전용)

| 엔티티               | Puller            | 특징         |
|-------------------|-------------------|------------|
| CompetitionEntity | CompetitionPuller | 초기 생성 후 불변 |
| SeasonEntity      | SeasonPuller      | 초기 생성 후 불변 |
| GroundEntity      | TeamPuller        | 초기 생성 후 불변 |
| FixtureEntity     | FixturePuller     | 초기 생성 후 불변 |
| OfficialEntity    | MatchPuller       | 초기 생성 후 불변 |
| MatchStatEntity   | MatchStatPuller   | 초기 생성 후 불변 |
| AwardEntity       | AwardPuller       | 초기 생성 후 불변 |

### 단일 Puller 갱신 (조건부 갱신)

| 엔티티            | Puller          | 갱신 조건                   |
|----------------|-----------------|-------------------------|
| TeamEntity     | TeamPuller      | `icon_url` 비어있을 때       |
| PlayerEntity   | PlayerPuller    | `photo_url` 비어있을 때      |
| MatchEntity    | MatchPuller     | `period != FULLTIME`일 때 |
| TeamStatEntity | TeamStatsPuller | 통계 데이터 갱신 필요 시          |

### 다중 Puller 갱신

| 엔티티              | Pullers                        | 역할 분담                                 |
|------------------|--------------------------------|---------------------------------------|
| PlayerEntity     | PlayerPuller, MatchPuller      | PlayerPuller 직접, MatchPuller 간접(누락 시) |
| StaffEntity      | MatchPuller, AwardPuller       | 감독 정보(Match), 수상 정보(Award)            |
| PlayerStatEntity | PlayerStatsPuller, AwardPuller | 통계(Stats), 수상 연관(Award)               |

---

## 의존성 순서

엔티티 생성 의존성에 따른 Puller 실행 순서:

```
1. CompetitionPuller     → CompetitionEntity
2. SeasonPuller          → SeasonEntity (Competition 필요)
3. TeamPuller            → TeamEntity, GroundEntity
4. PlayerPuller          → PlayerEntity
5. FixturePuller         → FixtureEntity (Season, Team, Ground 필요)
6. MatchPuller           → MatchEntity, OfficialEntity, StaffEntity (Fixture, Player 필요)
7. MatchStatPuller       → MatchStatEntity (Match, Team 필요)
8. PlayerStatsPuller     → PlayerStatEntity (Player, Season, Team 필요)
9. TeamStatsPuller       → TeamStatEntity (Team, Season, Ground, Fixture, Match 필요)
10. AwardPuller          → AwardEntity + 연관 (PlayerStat, Staff 필요)
```

---

## 참고사항

- 모든 엔티티는 `source_id`를 통해 중복 방지
- 번역이 필요한 필드(`*_kr`)는 `TranslatorService` 사용
- FK 참조 필드는 해당 엔티티가 먼저 존재해야 함
- 연관 테이블은 `append_*()` 메서드를 통해 추가
- Upsert 패턴은 PlayerStatEntity에서만 사용
