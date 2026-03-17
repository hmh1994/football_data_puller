# Validation Log 분석 요약

## 전체 현황

| Entity | Total | PASS | FAIL | WARNING | Status |
|--------|-------|------|------|---------|--------|
| competition | 28 | 28 | 0 | 0 | OK |
| season | 675 | 527 | 73 | 75 | FAIL |
| player | 9,351 | 8,884 | 461 | 6 | FAIL |
| fixture | 9,120 | 8,398 | 722 | 0 | FAIL |
| match | 68,338 | 67,972 | 366 | 0 | FAIL |
| match-stat | 84,320 | 84,238 | 82 | 0 | FAIL |
| team-stat | 4,588 | 4,294 | 294 | 0 | FAIL |
| player-stat | 45,583 | 44,209 | 1,374 | 0 | FAIL |
| analytics | 77 | 69 | 8 | 0 | FAIL |
| news | 5,570 | 5,570 | 0 | 0 | OK |
| award | 154 | 154 | 0 | 0 | OK |
| cross-dataset | 27 | 25 | 2 | 0 | FAIL |
| **Total** | **227,831** | **224,368** | **3,382** | **81** | **FAIL** |

## 분류 원칙

> **Pull되지 않은 데이터로 인해 FAIL이 발생하면, 그것은 Validator 문제이다.**
> Validator는 데이터 존재 여부를 먼저 확인하고, 없으면 PASS 또는 SKIP해야 한다.

## 분류 결과

| 분류 | FAIL 건수 | WARNING 건수 | 비율 |
|------|-----------|-------------|------|
| Validator 문제 | ~2,877건 | ~82건 | ~85.1% |
| Data 문제 (소스 데이터 결함) | ~350건 | 0건 | ~10.4% |

상세 분석은 아래 문서 참조:
- [01_validator_issues.md](./01_validator_issues.md) - Validator 문제 (미pull 데이터 미처리 + 로직 버그)
- [02_data_issues.md](./02_data_issues.md) - 소스 데이터 문제 (양쪽 데이터 존재하나 불일치)
