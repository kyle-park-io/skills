# AGENTS.md

이 레포에서 작업하는 에이전트를 위한 지침. 사람이 읽어도 된다.

이곳은 도메인별로 나눈 에이전트 스킬 모음이자 플러그인 마켓플레이스다. Claude Code 와 Codex 양쪽을 지원한다.

## 하기 전에 알아야 할 것

### 매니페스트는 생성물이다

`plugin.json` 과 `marketplace.json` 을 직접 고치지 않는다. 전부 `domains.json` 에서 생성된다.

```bash
python3 scripts/gen-manifests.py           # 생성
python3 scripts/gen-manifests.py --check   # 최신 여부만 확인
```

도메인을 추가하거나 버전을 올릴 때는 `domains.json` 만 고치고 생성기를 돌린 뒤 결과를 함께 커밋한다. 도메인 7개에 하네스 2개라 매니페스트가 16개다. 손으로 맞추면 반드시 갈라진다.

### 스킬은 툴이 아니라 동작을 부른다

스킬 본문에 하네스의 툴 이름을 쓰지 않는다. 이것이 같은 파일이 Claude Code 와 Codex 양쪽에서 그대로 도는 유일한 이유다.

| 이렇게 | 이렇게 말고 |
|---|---|
| 파일을 읽는다 | `Read` 툴로 읽는다 |
| 서브에이전트를 띄운다 | `Task` 를 호출한다 / `spawn_agent` 를 쓴다 |
| 웹을 검색한다 | `WebSearch` 를 부른다 |

`git`, `npm`, `terraform` 같은 셸 명령은 하네스가 아니라 시스템에 속하므로 그대로 쓴다.

하네스별로 스킬을 갈라 쓰고 싶어지면 그건 스킬이 잘못 쓰인 신호다. 본문을 동작 수준으로 끌어올린다.

### 새 스킬의 자리

```
<도메인>/skills/<스킬-이름>/SKILL.md
```

도메인 폴더 바로 밑이 아니다. `<도메인>/skills/` 아래여야 플러그인 페이로드로 잡힌다.

`_template/SKILL.md` 를 복사해서 시작한다. 프론트매터 `name` 은 폴더명과 일치시킨다.

## 스킬을 추가하기 전에 통과할 것

1. **내장·기존 스킬과 겹치는가.** 현재 하네스에 내장되었거나 설치된 스킬이 이미 상당 부분을 덮는다. 겹치면 만들지 않는다. Claude Code에서 측정한 기준 목록은 [`docs/SETUP-GUIDE.md`](docs/SETUP-GUIDE.md) §4에 있다. Codex에서는 현재 세션의 스킬 목록도 따로 확인한다.
2. **어느 도메인인가.** 도메인 선택이 곧 스코프 결정이다. 유저 스코프 도메인에 넣으면 그 스킬은 모든 세션에 상주한다.
3. **`description` 이 기존 스킬과 구별되는가.** 트리거 상황이 겹치면 둘 다 안 뽑힌다.

세 번째가 실패의 주된 원인이다. 먼저 `description` 에 **"이럴 때는 쓰지 않는다"** 를 명시적으로 쓴다. 겹치는 이웃 스킬을 이름으로 떠올리고 그쪽으로 가야 할 상황을 적는 것이 트리거 정확도를 만드는 주된 수단이다.

그래도 안 뜨거나 엉뚱하게 뜨면 그때 측정한다. `scripts/real-trigger-eval.py` 를
`--harness claude` 또는 `--harness codex`로 쓴다. `skill-creator` 의 Claude
eval 은 스킬을 설치하지 않고 `.claude/commands/` 에 흉내 파일을 심어 재기
때문에 실물과 다른 숫자가 나온다 (`a29fa11`: 프록시 recall 11%, 실물 100%).

쿼리 셋은 [`evals/`](evals) 아래 스킬 이름으로 둔다. 형식과 지금까지의 측정 기록은 [`evals/README.md`](evals/README.md).

**측정은 비싸다.** 쿼리 수 x 반복 횟수만큼 독립 세션이 뜬다. 14 쿼리를 3회씩 Opus 로 돌린 실측이 에이전트 작업 113분이었고, 그것이 하루치 사용량 한도를 태웠다. Claude Code에서는 `fanout-cost-gate` 훅이 그 수를 계산해 막는다. Codex에는 그 Claude 훅이 적용되지 않으므로 실행자가 같은 계산을 먼저 확인한다 ([`presets/README.md`](presets/README.md#병렬-실행-비용-훅)). 모델 선택 기준은 스크립트의 docstring 에 있다.

## 문체

- **엠대쉬(U+2014)를 쓰지 않는다.** 콜론, 마침표, 괄호로 대체한다. 엔대쉬(U+2013)도 마찬가지다.
- 문서는 한국어, 커밋 메시지는 영어.
- 커밋은 컨벤셔널 커밋을 따른다. `feat:` `fix:` `docs:` `chore:` `refactor:` `test:` 에 필요하면 스코프를 붙인다.

## 커밋 전 확인

```bash
python3 scripts/gen-manifests.py --check          # 매니페스트 최신
grep -rnP '[\x{2013}\x{2014}]' --include='*.md' .   # 엠대쉬·엔대쉬 없음
find . -name '*.json' -not -path './.git/*' \
  -exec python3 -c 'import json,sys;json.load(open(sys.argv[1]))' {} \;   # JSON 유효
```
