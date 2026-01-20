# Q1.

질문은 아래와 같습니다. 각 선수별로 `슈팅/패스/수비/드리블/규율` 각각의 항목에 대한 점수를 구하고 싶습니다.
그런데, 1시즌당 경기는 380 경기이고, 선수의 총 수는 약 600명에 달하니, 경기를 마칠 때마다 선수들의 전체 점수를 갱신하는 것은 매우 어려운 일입니다. 한 경기가 끝났을 때 해당 경기에 참가한 선수에
대해서만 점수를 갱신하는 방식으로 점수가 구해지면 좋겠습니다. 단, 경기 전후의 delta는 구하기 어렵습니다.
적절한 점수 계산 방식을 섹션 별로 의미하는 바에 대한 설명, latex 표현, 그리고 python code expression으로 표기해주세요.
이때 공용으로 사용할 함수들은 답변의 가장 상단에서 정의하고 진행합시다. 공용 함수들의 의미, latex 표기, python code expression 역시 표기해야합니다.

# A1.

아래 방식은 **시즌 누적 PlayerStat**만으로(= 경기 전/후 delta 없이) 점수를 계산하는 “재계산형 점수”입니다. 그래서 **경기 종료 후 그 경기 참가 선수들만**(라인업/교체 관련
association에 등장한 선수) 다시 계산해서 저장하면 됩니다.
PlayerStatEntity에는 슈팅/패스/수비/볼소유(드리블)/규율 관련 필드가 이미 정의돼 있습니다.
또한 질문에서 알려주신 것처럼 `minutes`(해당 시즌 현재까지 출전 시간)가 PlayerStatEntity에 **추가로 존재한다고 가정**합니다.

---

## 공용 함수 (모든 섹션에서 공통 사용)

### 1) Clamp (구간 자르기)

* 의미: 값을 ([a,b]) 범위로 제한
* LaTeX:
  [
  \mathrm{clamp}(x;a,b)=\min(\max(x,a),b)
  ]
* Python:

```python
def clamp(x: float, lo: float, hi: float) -> float:
    return min(max(x, lo), hi)
```

### 2) Safe division (0 나눗셈 방지)

* 의미: 분모가 0에 가까울 때 안정적으로 비율 계산
* LaTeX:
  [
  \mathrm{sdiv}(u,v;\epsilon)=\frac{u}{\max(v,\epsilon)}
  ]
* Python:

```python
def sdiv(u: float, v: float, eps: float = 1e-9) -> float:
    return u / max(v, eps)
```

### 3) Per-90 (90분 환산)

* 의미: “시즌 누적 카운트/가치”를 분당으로 나눠 90분 기준으로 환산
  (여기서 (m)=`minutes`)
* LaTeX:
  [
  \mathrm{per90}(c,m)=90\cdot\frac{c}{\max(m,1)}
  ]
* Python:

```python
def per90(count: float, minutes: float) -> float:
    return 90.0 * count / max(minutes, 1.0)
```

### 4) Shrinkage (표본 적을 때 사전값으로 수축)

* 의미: 출전시간/시도횟수(표본)가 적을수록 “초반 뽀록”을 줄이기 위해 사전 평균(prior)로 당김

    * (x): 관측 지표(예: per90, 성공률 등)
    * (x_0): prior(리그 평균/역사 평균 등 상수)
    * (n): 신뢰도 표본(예: minutes, 패스 시도, 드리블 시도, 경합 수 등)
    * (n_0): prior 강도(“몇 표본 정도면 관측을 믿을 것인가”)
* LaTeX:
  [
  \mathrm{shrink}(x;x_0,n,n_0)=\frac{nx+n_0x_0}{n+n_0}
  ]
* Python:

```python
def shrink(x: float, prior: float, n: float, n0: float) -> float:
    return (n * x + n0 * prior) / (n + n0)
```

### 5) Normalize to ([0,1])

* 의미: 지표를 미리 정한 “현실적인 범위” ([L,H])에 사상하여 0~1 점수로 만듦
  (리그 전체 분포를 매번 다시 계산하지 않기 위해 **상수 범위**를 사용)
* LaTeX:
  [
  \mathrm{norm01}(x;L,H)=\mathrm{clamp}\left(\frac{x-L}{H-L};0,1\right)
  ]
* Python:

```python
def norm01(x: float, lo: float, hi: float) -> float:
    return clamp((x - lo) / max(hi - lo, 1e-9), 0.0, 1.0)
```

### 6) Weighted sum → 0~100

* 의미: 여러 하위지표를 가중합(0~1)으로 만들고 100점 환산
* LaTeX:
  [
  \mathrm{score100}(\mathbf{f},\mathbf{w})=100\cdot \mathrm{clamp}\left(\sum_i w_i f_i;0,1\right)
  ]
* Python:

```python
def score100(features: list[float], weights: list[float]) -> float:
    s = sum(w * f for w, f in zip(weights, features))
    return 100.0 * clamp(s, 0.0, 1.0)
```

---

## 점수 업데이트 전략 (요구사항 충족 방식)

* 한 경기 종료 후 “그 경기 참가 선수”는 `MatchLineupAssociation.player_id`, `MatchSubstituteAssociation.player_id`, 그리고 실제 교체
  `MatchSubstitutionAssociation`의 `in_player_id/out_player_id`로 식별 가능합니다.
* 그 선수들의 PlayerStat(시즌 누적치)와 `minutes`가 업데이트된 뒤, 아래 점수 함수를 **그 선수들만** 호출해 저장하면 됩니다.
* 이 방식은 **경기 전후 delta를 몰라도** “현재 누적치”로만 점수를 재계산합니다.

---

## (1) 슈팅 점수 (S_{\text{shot}})

### 의미

* 득점/기대득점(xG) 기반 “위협도(볼륨+질)” + 유효슈팅 비율(정확도) + 결정력(득점/xG)을 반영
* PlayerStatEntity 슈팅 필드: `shooting_goals`, `shooting_goals_penalty`, `shooting_shots`, `shooting_shots_on_target`,
  `shooting_expected_goals_non_penalty` 등

### LaTeX

비(페널티) 득점/기대득점:
[
g_{\text{np}}=g-g_{\text{pen}},\quad xg_{\text{np}}=\text{npxG}
]
하위지표(수축+정규화):
[
f_1=\mathrm{norm01}\Big(\mathrm{shrink}(\mathrm{per90}(xg_{\text{np}},m);x_0, m, m_0);,0,0.60\Big)
]
[
f_2=\mathrm{norm01}\Big(\mathrm{shrink}(\mathrm{per90}(g_{\text{np}},m);g_0, m, m_0);,0,0.60\Big)
]
[
f_3=\mathrm{norm01}\Big(\mathrm{shrink}(\mathrm{sdiv}(\text{SOT},\text{Shots});a_0, \text{Shots}, n_{a0});,0.20,0.60\Big)
]
[
f_4=\mathrm{norm01}\Big(\mathrm{shrink}(\mathrm{sdiv}(g_{\text{np}},xg_{\text{np}});r_0, xg_{\text{np}}, n_{r0});,0.60,1.40\Big)
]
최종 점수:
[
S_{\text{shot}}=100\cdot \mathrm{clamp}(0.40f_1+0.30f_2+0.20f_3+0.10f_4;0,1)
]

### Python code expression

```python
def shooting_score(ps) -> float:
    m = float(ps.minutes)  # (추가된 필드라고 가정)
    g = float(ps.shooting_goals)
    g_pen = float(ps.shooting_goals_penalty)
    g_np = max(g - g_pen, 0.0)

    xg_np = float(ps.shooting_expected_goals_non_penalty)
    shots = float(ps.shooting_shots)
    sot = float(ps.shooting_shots_on_target)

    # priors (예시: 리그 역사 평균으로 튜닝)
    x0, g0 = 0.12, 0.10  # npxG90, non-penalty goals90 prior
    a0 = 0.33  # SOT/shots prior
    r0 = 1.00  # goals/xG prior
    m0 = 900.0  # minutes prior strength (약 10경기)
    na0 = 30.0  # attempts prior strength (shots)
    nr0 = 1.5  # xG prior strength

    f1 = norm01(shrink(per90(xg_np, m), x0, m, m0), 0.0, 0.60)
    f2 = norm01(shrink(per90(g_np, m), g0, m, m0), 0.0, 0.60)
    f3 = norm01(shrink(sdiv(sot, shots), a0, shots, na0), 0.20, 0.60)
    f4 = norm01(shrink(sdiv(g_np, xg_np), r0, xg_np, nr0), 0.60, 1.40)

    return score100([f1, f2, f3, f4], [0.40, 0.30, 0.20, 0.10])
```

---

## (2) 패스 점수 (S_{\text{pass}})

### 의미

* 창의성(xA/찬스 생성/어시스트) + 볼 순환 기여(패스 시도량) + 정확도(성공률, 크로스/롱볼 성공률)
* PlayerStatEntity 패스 필드: `passing_assists`, `passing_chances_created`, `passing_expected_assists`,
  `passing_passes_total`, `passing_passes_successful`, `passing_crosses_*`, `passing_long_balls_*`

### LaTeX

[
p_{\text{acc}}=\frac{p_s}{p_t},\quad c_{\text{acc}}=\frac{c_s}{c_t},\quad l_{\text{acc}}=\frac{l_s}{l_t}
]
[
f_1=\mathrm{norm01}(\mathrm{shrink}(\mathrm{per90}(xA,m);xA_0,m,m_0);0,0.45)
]
[
f_2=\mathrm{norm01}(\mathrm{shrink}(\mathrm{per90}(\text{Chances},m);cc_0,m,m_0);0,3.0)
]
[
f_3=\mathrm{norm01}(\mathrm{shrink}(\mathrm{per90}(\text{Assists},m);as_0,m,m_0);0,0.35)
]
[
f_4=\mathrm{norm01}(\mathrm{shrink}(p_{\text{acc}};p_0,p_t,n_{p0});0.70,0.93)
]
[
f_5=\tfrac12\mathrm{norm01}(\mathrm{shrink}(c_{\text{acc}};c_0,c_t,n_{c0});0.10,0.35)
+\tfrac12\mathrm{norm01}(\mathrm{shrink}(l_{\text{acc}};l_0,l_t,n_{l0});0.30,0.70)
]
[
S_{\text{pass}}=100\cdot\mathrm{clamp}(0.30f_1+0.20f_2+0.15f_3+0.25f_4+0.10f_5;0,1)
]

### Python

```python
def passing_score(ps) -> float:
    m = float(ps.minutes)

    assists = float(ps.passing_assists)
    chances = float(ps.passing_chances_created)
    xa = float(ps.passing_expected_assists)

    pt = float(ps.passing_passes_total)
    psucc = float(ps.passing_passes_successful)
    ct = float(ps.passing_crosses_total)
    cs = float(ps.passing_crosses_successful)
    lt = float(ps.passing_long_balls_total)
    ls = float(ps.passing_long_balls_accurate)

    # priors (예시)
    xa0, cc0, as0 = 0.10, 1.2, 0.08
    p0, c0, l0 = 0.82, 0.22, 0.50
    m0 = 900.0
    np0, nc0, nl0 = 400.0, 30.0, 25.0

    f1 = norm01(shrink(per90(xa, m), xa0, m, m0), 0.0, 0.45)
    f2 = norm01(shrink(per90(chances, m), cc0, m, m0), 0.0, 3.0)
    f3 = norm01(shrink(per90(assists, m), as0, m, m0), 0.0, 0.35)

    pass_acc = sdiv(psucc, pt)
    cross_acc = sdiv(cs, ct)
    long_acc = sdiv(ls, lt)

    f4 = norm01(shrink(pass_acc, p0, pt, np0), 0.70, 0.93)
    f5 = 0.5 * norm01(shrink(cross_acc, c0, ct, nc0), 0.10, 0.35) +
    0.5 * norm01(shrink(long_acc, l0, lt, nl0), 0.30, 0.70)


return score100([f1, f2, f3, f4, f5], [0.30, 0.20, 0.15, 0.25, 0.10])
```

---

## (3) 수비 점수 (S_{\text{def}})

### 의미

* 태클/인터셉트/블로킹/볼회수/경합 승률(지상+공중) 기반 “수비 기여도”
* 파울(수비 쪽)은 감점
* PlayerStatEntity 수비/경합/파울 필드: `defending_tackles_*`, `defending_interceptions`, `defending_blocked`,
  `defending_recoveries`, `defending_duels_*`, `defending_fouls_committed` 등

> 참고: 골키퍼는 PlayerStatEntity에 `goalkeeping_*`가 따로 있으니, GK의 “수비”는 별도 분기로 계산하는 것을 권장합니다.

### LaTeX (필드 플레이어 기본)

[
t=\mathrm{per90}(\text{TacklesWon},m),;
i=\mathrm{per90}(\text{Interceptions},m),;
b=\mathrm{per90}(\text{Blocked},m),;
r=\mathrm{per90}(\text{Recoveries},m)
]
[
d=\frac{\text{DuelsWon}}{\text{DuelsTotal}},\quad
a=\frac{\text{AerialWon}}{\text{AerialTotal}},\quad
f=\mathrm{per90}(\text{Fouls},m)
]
정규화 후:
[
S_{\text{def}}=100\cdot\mathrm{clamp}\big(0.22f_t+0.18f_i+0.12f_b+0.18f_r+0.20f_d+0.10f_a-0.10f_f;0,1\big)
]

### Python

```python
def defending_score_outfield(ps) -> float:
    m = float(ps.minutes)

    tw = float(ps.defending_tackles_won)
    inter = float(ps.defending_interceptions)
    blk = float(ps.defending_blocked)
    rec = float(ps.defending_recoveries)

    dt = float(ps.defending_duels_total)
    dw = float(ps.defending_duels_won)
    at = float(ps.defending_duels_aerial_total)
    aw = float(ps.defending_duels_aerial_won)

    fouls = float(ps.defending_fouls_committed)

    # priors (예시)
    t0, i0, b0, r0 = 1.2, 0.9, 0.4, 4.5
    d0, a0 = 0.55, 0.55
    f0 = 1.0
    m0 = 900.0
    nd0, na0 = 80.0, 40.0  # duels trials

    ft = norm01(shrink(per90(tw, m), t0, m, m0), 0.0, 3.0)
    fi = norm01(shrink(per90(inter, m), i0, m, m0), 0.0, 2.5)
    fb = norm01(shrink(per90(blk, m), b0, m, m0), 0.0, 1.8)
    fr = norm01(shrink(per90(rec, m), r0, m, m0), 0.0, 8.0)

    duel_win = sdiv(dw, dt)
    aerial_win = sdiv(aw, at)
    fd = norm01(shrink(duel_win, d0, dt, nd0), 0.40, 0.70)
    fa = norm01(shrink(aerial_win, a0, at, na0), 0.40, 0.75)

    ff = norm01(shrink(per90(fouls, m), f0, m, m0), 0.0, 2.5)

    s = 0.22 * ft + 0.18 * fi + 0.12 * fb + 0.18 * fr + 0.20 * fd + 0.10 * fa - 0.10 * ff
    return 100.0 * clamp(s, 0.0, 1.0)


def defending_score_goalkeeper(ps) -> float:
    m = float(ps.minutes)
    saves = float(ps.goalkeeping_saves)
    prevented = float(ps.goalkeeping_goals_prevented)
    cs = float(ps.goalkeeping_clean_sheets)

    # priors (예시)
    sv0, gp0, cs0 = 2.6, 0.0, 0.25
    m0 = 900.0

    f1 = norm01(shrink(per90(saves, m), sv0, m, m0), 0.0, 5.5)
    f2 = norm01(shrink(per90(prevented, m), gp0, m, m0), -0.3, 0.6)
    f3 = norm01(shrink(per90(cs, m), cs0, m, m0), 0.0, 0.50)

    return score100([f1, f2, f3], [0.55, 0.25, 0.20])
```

---

## (4) 드리블 점수 (S_{\text{drb}})

### 의미

* 드리블 “성공률 + 볼륨” + 파울 유도(상대를 제낀 효과) + 박스 터치(위협 지역 진입)
* PlayerStatEntity 볼소유(드리블) 필드: `possession_dribble_total`, `possession_dribble_successful`, `possession_fouls_won`,
  `possession_touches_in_opposition_box`

### LaTeX

[
s=\frac{\text{DrbSucc}}{\text{DrbTot}},\quad v=\mathrm{per90}(\text{DrbTot},m),\quad
w=\mathrm{per90}(\text{FoulsWon},m),\quad
b=\mathrm{per90}(\text{BoxTouches},m)
]
[
S_{\text{drb}}=100\cdot \mathrm{clamp}(0.35f_s+0.30f_v+0.20f_w+0.15f_b;0,1)
]

### Python

```python
def dribbling_score(ps) -> float:
    m = float(ps.minutes)

    dt = float(ps.possession_dribble_total)
    ds = float(ps.possession_dribble_successful)
    fw = float(ps.possession_fouls_won)
    box = float(ps.possession_touches_in_opposition_box)

    # priors (예시)
    s0 = 0.55
    v0, w0, b0 = 2.0, 0.9, 1.2
    m0 = 900.0
    nd0 = 40.0

    succ_rate = sdiv(ds, dt)
    fs = norm01(shrink(succ_rate, s0, dt, nd0), 0.35, 0.75)
    fv = norm01(shrink(per90(dt, m), v0, m, m0), 0.0, 7.0)
    fw_ = norm01(shrink(per90(fw, m), w0, m, m0), 0.0, 2.5)
    fb = norm01(shrink(per90(box, m), b0, m, m0), 0.0, 6.0)

    return score100([fs, fv, fw_, fb], [0.35, 0.30, 0.20, 0.15])
```

---

## (5) 규율 점수 (S_{\text{disc}})

### 의미

* 경고/퇴장(특히 직접퇴장) + 파울 빈도를 “페널티”로 보고, **적을수록 점수 높게**
* PlayerStatEntity 규율 필드: `discipline_yellow_cards`, `discipline_red_cards`, `discipline_red_cards_direct`
* 파울은 `defending_fouls_committed` 사용

### LaTeX

가중 카드 페널티(예: 경고 1, 간접퇴장 2, 직접퇴장 3):
[
C = Y + 2(R-R_d) + 3R_d
]
[
c_{90}=\mathrm{per90}(C,m),\quad f_{90}=\mathrm{per90}(\text{Fouls},m)
]
규율 점수(감점 후 반전):
[
P = 0.7,\mathrm{norm01}(c_{90};0,1.2) + 0.3,\mathrm{norm01}(f_{90};0,3.0)
]
[
S_{\text{disc}} = 100\cdot(1-\mathrm{clamp}(P;0,1))
]

### Python

```python
def discipline_score(ps) -> float:
    m = float(ps.minutes)

    y = float(ps.discipline_yellow_cards)
    r = float(ps.discipline_red_cards)
    rd = float(ps.discipline_red_cards_direct)
    fouls = float(ps.defending_fouls_committed)

    # weighted card events
    c = y + 2.0 * max(r - rd, 0.0) + 3.0 * rd

    # priors (예시)
    c0 = 0.25  # cards90 prior
    f0 = 1.0  # fouls90 prior
    m0 = 900.0

    c90 = shrink(per90(c, m), c0, m, m0)
    f90 = shrink(per90(fouls, m), f0, m, m0)

    p = 0.7 * norm01(c90, 0.0, 1.2) + 0.3 * norm01(f90, 0.0, 3.0)
    return 100.0 * (1.0 - clamp(p, 0.0, 1.0))
```

---

## 마무리: “경기 참가 선수만 갱신” 구현 포인트

1. 경기 종료 → 해당 match의 참가 선수 목록을 association에서 수집
2. 그 선수들의 PlayerStat(시즌 누적치) 및 `minutes` 업데이트 완료 후
3. 위 5개 함수를 호출해 **그 선수들만** 점수 컬럼(또는 별도 테이블)에 저장

원하시면, 위 점수 5개를 하나의 `compute_player_scores(ps, position)`로 묶고(골키퍼 분기 포함), DB 업데이트를 “참가 선수 id 리스트 입력 → 벌크 upsert” 형태로 정리한
예시 코드까지 이어서 적어드릴게요.

# Q2.

shirink에 들어갈 사전값은 어떻게 결정해야하나요? 처음계산할때는?

# A2.

사전값(prior)은 “출전시간/시도횟수가 적을 때 점수가 리그 평균 근처로 붙도록” 만드는 **기준점**입니다. 핵심은 **(1) 무엇을 prior로 둘지**, **(2) 그 prior를 얼마나 세게 믿을지(n0)
** 두 가지를 정하는 거예요. 아래는 실무적으로 가장 안전한 결정 방식입니다.

---

## 1) prior(사전값) 결정 방법 3가지

### A. 리그/시즌 전체 평균(권장, 가장 단순·안정)

* 예: `pass_acc_prior = 리그 전체 passes_successful / passes_total`
* 예: `npxG90_prior = 리그 전체 npxG / total_minutes * 90`
* 장점: 구현 간단, 매 시즌 자동 갱신 가능
* 단점: 포지션 차이를 못 반영하면 일부 포지션이 손해/이득

**처음 계산(시즌 시작)**: 전 시즌(또는 최근 2~3시즌) 같은 대회의 평균을 prior로 씁니다.

---

### B. 포지션별 평균(추천, 품질 ↑)

* FW/AM/CM/CB/FB/GK 등 포지션 그룹별로 prior를 다르게 둠
* 예: CB의 `tackles_won90` prior와 FW의 prior는 다름
* 장점: 공정성↑, 분산↓
* 단점: 포지션 그룹 정의 필요

**처음 계산**: 전 시즌 포지션별 평균(또는 최근 N시즌 풀링) 사용.

---

### C. “상수 범위 기반” 고정 prior (데이터 없을 때)

* 데이터 파이프라인이 아직 없거나, 시즌/대회가 자주 바뀌면
* 예: `pass_acc_prior=0.82`, `dribble_succ_prior=0.55` 같은 고정값
* 장점: 당장 가능
* 단점: 리그마다 스타일 차이 반영 못함 → 시즌 중에 A/B 튜닝 필요

**처음 계산**: 일단 고정 prior로 시작하고, 최소한 “리그 전체 분모/분자 집계”가 가능해지는 순간 A로 전환하는 게 베스트입니다.

---

## 2) “처음 계산할 때(prior 데이터가 없을 때)” 현실적인 방법

### 1순위: 전 시즌(또는 최근 2~3시즌) 같은 리그 데이터

* 시즌1 초기치로 가장 흔하게 씁니다.

### 2순위: 시즌 첫 라운드 데이터로 “리그 평균” 만든 뒤 적용

* 1~3라운드 정도 지나면 분모(분)와 시도횟수가 쌓이므로 prior를 업데이트
* 중요한 점: prior 업데이트는 **매 경기마다 할 필요 없음**
  예: 라운드당 1번 / 하루 1번 / 배치 작업

### 3순위: 고정 prior로 시작 → 일정 표본 이후부터 리그 평균 prior로 교체

* 예: 시즌 시작~2라운드는 고정 prior, 3라운드부터 리그 평균 prior 사용

---

## 3) n0(사전 강도) 어떻게 정하나?

shrink 식은:
[
\mathrm{shrink}(x;x_0,n,n_0)=\frac{nx+n_0x_0}{n+n_0}
]

여기서 `n0`는 “**이 지표는 표본이 몇 개쯤 되어야 믿을까?**”를 숫자로 넣는 겁니다.

* **minutes 기반 지표(per90 같은 것)**: `n = minutes`로 두고

    * `m0 = 600~1200` 권장 (약 6~13경기 분량)
* **성공률(패스성공률/드리블성공률)**: `n = attempts`로 두고

    * 패스 성공률: `n0 = 200~500` (패스는 표본 많음)
    * 드리블 성공률: `n0 = 30~60`
    * 슈팅 SOT 비율: `n0 = 20~40`
* **득점/xG 같은 비율**: `n = xG` 또는 `shots`(둘 중 더 안정적인 쪽)

    * 보통 `xG`를 표본으로 쓰면 합리적이고, `n0 = 1~3 (xG 단위)` 정도가 잘 작동합니다.

**직관**:

* `n0`가 클수록 초반엔 거의 prior로 고정
* `n0`가 작을수록 초반부터 개인 편차가 크게 튀어버림

---

## 4) 실무에서 prior를 계산하는 구체식 (추천)

### per90형 prior

예: npxG90 prior
[
x_0 = 90\cdot\frac{\sum_i xg_{i}}{\sum_i m_i}
]
Python(리그 집계값이 있을 때):

```python
x0 = 90.0 * league_sum_npxg / max(league_sum_minutes, 1.0)
```

### 성공률 prior

예: 패스 성공률 prior
[
p_0=\frac{\sum_i p_{s,i}}{\sum_i p_{t,i}}
]
Python:

```python
p0 = league_sum_pass_success / max(league_sum_pass_total, 1.0)
```

포지션별 prior도 똑같이 “포지션 그룹으로 필터링한 합계”로 계산하면 됩니다.

---

## 5) 추천 운영안 (600명/380경기 조건 최적화)

* 경기 종료 후: **참가 선수만** PlayerStat과 점수 재계산(이미 하려는 방식)
* 별도 배치(라운드당 1회 정도):

    * `league priors`(또는 position priors)만 재계산해서 테이블/캐시로 저장
* 점수 계산 함수는 그 prior를 읽어 shrink에 넣음

이러면 “매 경기 600명 전체 업데이트” 없이도 prior는 최신에 가깝게 유지됩니다.

---

원하시면, (1) 리그 prior를 저장할 `LeaguePriorEntity` 같은 스키마(혹은 key-value) 설계, (2) 포지션별 prior까지 포함한 계산 파이프라인(참가 선수만 점수 갱신 + 라운드 배치
prior 갱신)까지 코드 형태로 깔끔하게 정리해드릴게요.

# Q3.

5개 섹션의 스코어를 모두 고려해서 Overall score를 만들고싶은데, 어떻게 계산하면 좋을까요?

# A3.

아래는 **5개 섹션 점수(0~100)** 를 합쳐 **Overall(0~100)** 를 만드는, “경기 전/후 delta 없이 시즌 누적치만으로 재계산 가능한” 방식입니다.
핵심은 (a) 포지션별 가중치, (b) 한 항목만 튀는 원툴을 억제하는 **균형 페널티(기하평균)**, (c) 출전시간 적을 때 Overall도 흔들리지 않도록 **minutes 기반 shrink** 입니다.

---

## 공용 함수 (Overall에 공통 사용)

> 아래 함수들은 이전에 정의한 `clamp`, `shrink`를 사용합니다.

### 1) Weighted arithmetic mean

* 의미: 가중 산술평균 (주력/역할 반영에 직관적)
* LaTeX:
  [
  \mathrm{wmean}(\mathbf{z},\mathbf{w})=\sum_i w_i z_i,\quad \sum_i w_i=1
  ]
* Python:

```python
def wmean(z: list[float], w: list[float]) -> float:
    return sum(wi * zi for wi, zi in zip(w, z))
```

### 2) Weighted geometric mean (균형을 강제)

* 의미: 한 항목이 낮으면 전체가 같이 내려가도록(“구멍”을 페널티)
* LaTeX:
  [
  \mathrm{wgeom}(\mathbf{z},\mathbf{w};\epsilon)=\exp\Big(\sum_i w_i\log(\max(z_i,\epsilon))\Big)
  ]
* Python:

```python
import math


def wgeom(z: list[float], w: list[float], eps: float = 1e-6) -> float:
    return math.exp(sum(wi * math.log(max(zi, eps)) for wi, zi in zip(w, z)))
```

### 3) Blend (산술평균 + 기하평균 혼합)

* 의미: 산술평균의 직관 + 기하평균의 균형 페널티를 섞음
* LaTeX:
  [
  \mathrm{blend}(A,G;\lambda)=(1-\lambda)A+\lambda G,\quad \lambda\in[0,1]
  ]
* Python:

```python
def blend(a: float, g: float, lam: float = 0.5) -> float:
    return (1.0 - lam) * a + lam * g
```

---

## Overall score 정의

### 입력

* 5개 섹션 점수(이미 계산된 값):
  [
  S_{\text{shot}}, S_{\text{pass}}, S_{\text{def}}, S_{\text{drb}}, S_{\text{disc}} \in [0,100]
  ]
* 정규화:
  [
  z_i = \frac{S_i}{100} \in [0,1]
  ]
* 포지션별 가중치 (\mathbf{w}) (합 1)
* 출전시간 (m=\text{minutes})

### LaTeX

1. 코어 결합 점수(0~1):
   [
   A=\mathrm{wmean}(\mathbf{z},\mathbf{w}),\quad
   G=\mathrm{wgeom}(\mathbf{z},\mathbf{w})
   ]
   [
   R=\mathrm{blend}(A,G;\lambda)
   ]

2. minutes 기반 Overall shrink(초반 안정화):
   [
   O = 100 \cdot \mathrm{shrink}(R;R_0,m,m_0)
   ]

* (R_0): Overall의 사전값(리그 평균 or 포지션 평균, 0~1)
* (m_0): minutes prior 강도(예: 900분 = 약 10경기)

---

## Python code expression (Overall 계산)

```python
def overall_score_from_sections(
        s_shot: float,
        s_pass: float,
        s_def: float,
        s_drb: float,
        s_disc: float,
        minutes: float,
        weights: list[float],  # [w_shot, w_pass, w_def, w_drb, w_disc], sum=1
        prior_overall: float = 0.50,  # R0 in [0,1] (리그/포지션 평균 권장)
        m0: float = 900.0,  # minutes prior strength
        lam: float = 0.5  # blend weight between arithmetic and geometric
) -> float:
    # 0~1 normalize
    z = [s_shot / 100.0, s_pass / 100.0, s_def / 100.0, s_drb / 100.0, s_disc / 100.0]
    # core aggregation
    a = wmean(z, weights)
    g = wgeom(z, weights)
    r = blend(a, g, lam=lam)  # 0~1
    # minutes shrink (overall도 초반 흔들림 방지)
    r_shrunk = shrink(r, prior_overall, minutes, m0)  # 0~1
    return 100.0 * clamp(r_shrunk, 0.0, 1.0)
```

---

## 포지션별 가중치 추천 (실무용 기본값)

> 아래는 “전체적으로 납득 가능한” 시작점입니다. 이후 데이터/피드백으로 튜닝하세요.

* **FW/Winger(공격수)**: 슈팅·드리블 비중↑
  `w = [0.35, 0.20, 0.05, 0.30, 0.10]`
* **AM/CM(공격/중앙 미드)**: 패스 중심 + 드리블/슈팅도 반영
  `w = [0.20, 0.35, 0.15, 0.20, 0.10]`
* **DM/CB(수비/센터백)**: 수비·규율 비중↑
  `w = [0.05, 0.20, 0.45, 0.10, 0.20]`
* **FB/WB(풀백/윙백)**: 패스·수비·드리블 균형
  `w = [0.10, 0.25, 0.30, 0.20, 0.15]`
* **GK(골키퍼)**: (권장) GK는 별도 Overall(예: GK수비 80% + 규율 20%)

    * 이미 GK용 `defending_score_goalkeeper()`를 쓰고 있다면:
      `w = [0.00, 0.10, 0.80, 0.00, 0.10]` 처럼 운용(슈팅/드리블은 0)

---

## 왜 이 방식이 “참가 선수만 갱신”에 잘 맞나?

* Overall은 오직 **현재 저장된 5개 섹션 점수 + minutes + (포지션 가중치, prior)** 로만 계산됩니다.
* 따라서 경기 종료 후 **참가 선수들만** 5개 섹션 점수 재계산 → 이어서 Overall 재계산하면 끝입니다.
* `wgeom`을 섞어서 “패스만 95점, 나머지 20점” 같은 원툴을 자연스럽게 눌러줍니다.

원하시면, (1) prior_overall을 “리그 평균/포지션 평균”으로 자동 산출하는 공식(집계 테이블 설계 포함)과 (2) 포지션이 없거나 멀티포지션일 때 가중치 결정 규칙(혼합 가중치)까지 한 번에
정리해드릴게요.
