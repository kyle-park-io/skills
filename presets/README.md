# presets

Claude Code와 Codex에 복사해서 쓰는 설정 원본. 도메인이 아니라 **스택** 단위로
잘랐다. `.claude/settings.json`과 `.codex/config.toml`은 서로 다른 하네스의
프로젝트 설정이다.

Codex 로컬 마켓플레이스 플러그인은 사용자 캐시에 설치한 뒤 기본 비활성화하고,
각 프리셋의 `.codex/config.toml`에서 그 스택에 필요한 도메인만 활성화한다.
Claude Code 공식 플러그인 이름은 Codex 카탈로그와 일대일로 대응하지 않으므로,
`.claude`의 외부 플러그인 목록을 `.codex`에 그대로 옮기지 않는다.

## 왜 도메인별이 아닌가

레포 하나에는 하네스별 프로젝트 설정이 하나씩 있다. Next.js + Postgres 앱이면
frontend, backend, infra 세 도메인에서 끌어와야 하는데, 도메인별 조각으로
흩어두면 쓸 때마다 손으로 합쳐야 한다. 설정이 실제로 적용되는 단위가 스택이므로
그 축으로 자른다.

도메인 폴더(`../backend` 등)는 그 자체가 **플러그인**이다. `.claude-plugin/plugin.json`과 `skills/`로 이뤄지고, 설치되면 하네스가 통째로 가져간다. 거기에 설정 JSON을 두면 플러그인 페이로드에 딸려 들어가 아무 의미 없는 파일이 된다.

## 설정 스코프의 역할

| 하네스와 스코프 | 파일 | 담는 것 | 커밋 |
|---|---|---|---|
| Claude 유저 | `~/.claude/settings.json` | 어디서나 쓰는 플러그인, `env` | 해당 없음 |
| Claude 프로젝트 | `<repo>/.claude/settings.json` | 그 스택 전용 플러그인 | **한다** |
| Claude 로컬 | `<repo>/.claude/settings.local.json` | `permissions.allow` | **안 한다** |
| Codex 유저 | `~/.codex/config.toml` | 캐시된 플러그인의 기본 상태 | 해당 없음 |
| Codex 프로젝트 | `<repo>/.codex/config.toml` | 자체 도메인 활성화, 프로젝트 MCP | **한다** |
| Codex 독립 스킬 | `<repo>/.agents/skills/` | 플러그인 밖의 프로젝트 스킬 | **한다** |

프로젝트 스코프는 공유 대상이다. 그 레포를 여는 사람이면 누구나 같은 플러그인을 켜야 하므로 커밋한다. 로컬 스코프는 내 머신에서 내가 승인한 명령 허용목록이라 공유 대상이 아니다. `.gitignore`에 넣는다.

```gitignore
.claude/settings.local.json
```

---

## 새 머신 셋업

### Claude Code

노트북을 새로 사면 **이 레포를 클론해도 아무것도 켜지지 않는다.** 프로젝트 스코프는 각 작업 레포에 커밋돼 있어 클론하면 따라오지만, 유저 스코프는 `~/.claude/settings.json`에 있고 그 파일은 어느 레포에도 들어 있지 않다.

**1. 부트스트랩을 돌린다.**

```bash
bash presets/claude/bootstrap.sh
```

[`claude/bootstrap.sh`](claude/bootstrap.sh)가 유저 스코프 병합과 훅 설치를 멱등하게 처리하고, 마지막에 게이트가 실제로 서는지 확인한다. `CLAUDE_CONFIG_DIR`을 존중하므로 임시 디렉터리를 가리켜 먼저 시험해 볼 수 있다.

**손으로 하지 않는다.** 선언적인 것은 `extraKnownMarketplaces`와 `enabledPlugins`뿐이고, 훅 복사는 파일 시스템 작업이라 JSON 병합으로 대신할 수 없다. 그 한 단계가 빠진 채 설정만 병합되면 `settings.json`이 없는 스크립트를 가리키게 되고, 그때부터 **모든 Bash 호출이 그것을 실행하려 든다.** 부분 적용이 아무것도 안 한 것보다 나쁜 유일한 지점이라 순서를 스크립트에 고정했다. 훅 파일을 먼저 놓고 설정을 나중에 병합한다.

이 자동화가 없어서 이미 한 번 당했다. 2026-09-09 에 게이트를 레포에 만들어 두고, 게이트가 설치되지 않은 머신에서 Opus 세션 42개를 띄워 사용량 한도를 태웠다.

스크립트가 하는 일은 이렇다.

- [`user/settings.json`](user/settings.json)의 `extraKnownMarketplaces`, `enabledPlugins`, `hooks`를 `~/.claude/settings.json`에 병합한다. **덮어쓰지 않는다.** `model`, `theme`, `effortLevel` 같은 개인 설정이 그 파일에 같이 살기 때문이다. 실제로 값이 바뀔 때만 `~/.claude/backups/`에 이전 파일을 남긴다. 바뀐 항목은 **추가와 변경을 구분해** 찍는다. 플러그인을 내린 것이 켠 것처럼 보이면 적용 결과를 눈으로 확인할 방법이 없다.
- `env`는 **빈 값일 때만** 자리를 만든다. 프리셋의 `CONTEXT7_API_KEY`가 빈 문자열이라, 그대로 덮어쓰면 이미 발급해 넣은 키를 지운다.
- `hooks`는 `command` 기준으로 합친다. 이미 붙여 둔 다른 훅은 건드리지 않는다.
- [`user/hooks/fanout-cost-gate.sh`](user/hooks/fanout-cost-gate.sh)를 `~/.claude/hooks/`에 복사하고 실행 권한을 준다.
- 훅에 가짜 페이로드를 먹여 세션 42개짜리 명령이 차단되는지, `CLAUDE_FANOUT_ACK=42`가 통과되는지, 무관한 명령이 통과되는지 셋 다 확인한다. 하나라도 어긋나면 0이 아닌 값으로 죽는다.

마지막 항목이 있는 이유는 Codex 부트스트랩이 `plugin list`로 끝나는 것과 같다. 설치했다는 것과 동작한다는 것은 다르고, **이 훅은 동작하지 않아도 조용하다.**

`extraKnownMarketplaces`가 마켓플레이스 등록을 대신하므로 `claude plugin marketplace add`를 따로 칠 필요가 없다. 이 한 블록이 없으면 `enabledPlugins`의 `@kyle-skills` 항목이 어느 마켓플레이스인지 몰라 해석되지 않는다.

**source는 `github`로 고정한다.** 커밋되는 프리셋에 로컬 절대경로를 넣으면 그 머신 하나를 빼고 전부 틀린 설정이 된다. 이 레포를 직접 고치는 머신만 손으로 `{"source": "directory", "path": "..."}`로 바꿔 푸시 전 스킬을 확인한다. 그건 머신 하나에 대한 예외지 프리셋에 담을 값이 아니다.

공식 플러그인이 안 잡히면 한 번만 등록한다.

```bash
claude plugin marketplace add anthropics/claude-plugins-official
```

무엇을 하는 훅인지는 아래 [병렬 실행 비용 훅](#병렬-실행-비용-훅).

**2. `env`를 채운다.**

레포에는 키 두 개를 빈 값으로 두었다. 비었을 때 벌어지는 일이 서로 다르다.

| 키 | 비워두면 | 발급처 |
|---|---|---|
| `CONTEXT7_API_KEY` | 익명으로 연결된다. rate limit 만 낮다 | [context7.com/dashboard](https://context7.com/dashboard) |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | 아무 일도 없다. `github` 이 `false` 라서 | [github.com/settings/tokens](https://github.com/settings/tokens) |

`GITHUB_PERSONAL_ACCESS_TOKEN` 은 지금 쓰이는 값이 아니라 **켤 때 채우는 자리**다. github 은 `Authorization: Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}` 을 그대로 보내므로, 변수를 비워둔 채 플러그인만 `true` 로 올리면 빈 Bearer 가 나가고 서버가 400 으로 끊는다. 둘 다 `settings.json` 에 있으니 **같이 고치고 세션을 다시 띄운다.** 자세한 것은 SETUP-GUIDE §7.

**토큰이 든 `settings.json`을 머신 간에 그대로 복사하지 않는다.** 레포의 프리셋을 병합하고 값은 새로 발급하는 쪽이 맞다.

**3. 작업 레포를 클론한다.**

프로젝트 스코프는 여기서 자동으로 붙는다. 커밋된 `<repo>/.claude/settings.json`이 `backend@kyle-skills` 같은 항목을 이미 들고 있고, 1번에서 마켓플레이스를 알려줬으므로 해석된다.

### Codex

Codex 플러그인 설치 상태는 사용자 스코프에 있으므로 레포를 클론하는 것만으로
복구되지 않는다. [`codex/bootstrap.sh`](codex/bootstrap.sh)를 한 번 실행한다.

```bash
bash presets/codex/bootstrap.sh
```

이 스크립트는 `kyle-skills` 마켓플레이스와 공통 작업 절차인
`superpowers@openai-curated-remote`, `process@kyle-skills`를 멱등하게 설치하고
이미 있으면 최신 마켓플레이스 버전으로 갱신한다.
프로젝트용 도메인도 로컬 캐시에 설치하지만 사용자 기본값은 `false`로 되돌린다.
각 레포의 `.codex/config.toml`이 필요한 도메인만 `true`로 덮어쓴다.

**캐시 목록의 기준은 "비어 있는가"가 아니라 "참조되는가"다.** 어느 프로젝트
설정에서든 `true`로 켜는 도메인은 전부 캐시에 있어야 한다. Codex는 사용자
캐시에 없는 플러그인을 프로젝트에서 켤 수 없기 때문이다. 지금 캐시에 드는 것은
`backend`, `dashboard`, `frontend`, `infra`, `skill-authoring` 다섯이고, 이 중
`dashboard`·`infra`·`skill-authoring`은 스킬이 0개다. **비어 있어도 참조되면
넣는다.** 스킬 0개짜리 플러그인은 컨텍스트를 늘리지 않으므로 비용이 없고, 첫
스킬이 들어온 날 배선을 다시 하지 않아도 된다.

`architecture`는 어느 프로젝트 설정도 참조하지 않아 빠져 있다. 비어서가 아니라
쓰는 자리가 아직 없어서다. 첫 프리셋이 참조하면 그때 캐시 목록에 넣는다.

플러그인으로 묶지 않은 프로젝트 전용 스킬은 `.agents/skills/`에 둔다. Codex는
이 경로를 현재 디렉터리부터 레포 루트까지 읽고 심볼릭 링크도 따라간다.

설치 뒤에는 새 대화를 열어 스킬 목록을 다시 적재한다. 확인 명령:

```bash
codex plugin marketplace list
codex plugin list
codex -C <대상 레포> debug prompt-input | rg '<도메인>:'
```

`plugin list`는 설치된 사용자 기본 상태를 보여 주므로 프로젝트 프리셋 안에서도
`disabled`로 보일 수 있다. 실제 모델 입력에는 프로젝트 오버라이드가 적용된다.
마지막 명령이나 새 대화 `/skills`에서 유효 상태를 확인한다.

Claude의 `fanout-cost-gate` 훅은 Codex 설정에 적용되지 않는다. Codex로 트리거
eval을 돌릴 때도 쿼리 수 x `--runs`를 먼저 계산하고 비용을 확인한다.

---

## 병렬 실행 비용 훅

`user/hooks/fanout-cost-gate.sh`. `PreToolUse`로 모든 Bash 호출을 스쳐 지나가되 **독립 Claude 세션을 3개 이상 띄우는 명령만** 가로챈다.

세션 수를 명령에서 직접 계산한다. `--eval-set`의 쿼리 수 곱하기 `--runs`, 또는 명령에 박힌 직접 호출 횟수 중 큰 쪽이다. 그 수를 화면에 띄우고 실행을 막는다. 열려면 `CLAUDE_FANOUT_ACK=<세션 수>`를 명령 앞에 붙인다. **숫자가 계산값과 일치해야 하므로 실행하려면 그 수를 먼저 알아야 한다.**

```bash
# 막힌다
python3 scripts/real-trigger-eval.py --eval-set eval.json --runs 3 ...
#   -> 독립 Claude 세션 42개를 띄웁니다 (쿼리 14 x 반복 3)

# 통과한다
CLAUDE_FANOUT_ACK=42 python3 scripts/real-trigger-eval.py --eval-set eval.json --runs 3 ...
```

**`ask`가 아니라 `deny`인 이유.** `permissionDecision: "ask"`는 권한 프롬프트를 거치는데 `bypassPermissions` 모드에서는 그 프롬프트가 건너뛰어질 수 있다. 이 규칙은 모드와 무관하게 서야 한다.

**오탐은 남겨뒀다.** 명령을 문서에 적거나 테스트를 짜는 것과 명령을 실행하는 것을 문자열만 보고 완전히 구분할 수는 없다. eval 쪽은 `--eval-set` 파일이 실제로 있을 때만 세어 대부분 걸러지지만, 직접 호출 문자열이 세 번 이상 든 글을 쓰면 걸린다. **fail-closed가 맞다.** 오탐은 ack 한 번이고, 놓치면 하루치 쿼터다.

**왜 있는가.** 2026-09-09에 트리거 eval을 14쿼리 x 3회로 백그라운드 실행했고, 그것이 Opus 세션 42개와 에이전트 작업 113분이 되어 사용량 한도를 태웠다. 대화 컨텍스트는 싸다 (그 세션 전체가 178k / 1M). 비싼 것은 **세션을 새로 여는 일**이고 각 세션이 자기 시스템 프롬프트를 새로 싣는다. 그리고 그 수는 명령을 읽으면 실행 전에 계산된다. 계산할 수 있는 것을 사고가 난 뒤에 알 이유가 없다.

## user/

유저 스코프 원본. 켜는 것 7개, 끄는 것 5개다.

이 디렉터리의 JSON과 훅은 Claude Code 전용이다. Codex의 공통 설치 목록은
[`codex/bootstrap.sh`](codex/bootstrap.sh)가 맡는다.

**여기 둘 조건은 "언제 쓸지 모른다"가 아니라 "어느 레포에서든 쓴다"다.** 스킬 30개를 넘기지 않는다 (현재 21개. `~/.claude/skills/`의 4개까지 세면 25개). 근거는 [`../docs/SETUP-GUIDE.md`](../docs/SETUP-GUIDE.md) §1, §3.

숫자는 `claude plugin details <플러그인>`으로 열거했다 (2026-09-10).

| 플러그인 | 스킬 | 상시 토큰 | 역할 |
|---|---:|---:|---|
| `superpowers` | 14 | ~688 | 작업 절차 |
| `commit-commands` | 3 | ~103 | 커밋·푸시·PR. 레포마다 있다 |
| `claude-md-management` | 2 | ~175 | 프로젝트 규약 관리 |
| `claude-code-setup` | 1 | ~139 | 레포별 자동화 진단 (제안만, 쓰지는 않음) |
| `process@kyle-skills` | 1 | ~242 | 내 작업 절차 스킬 |
| `serena` | 0 | ~0 | 시맨틱 코드 분석 (MCP) |
| `context7` | 0 | ~0 | 최신 라이브러리 문서 조회 (MCP) |
| `github` | 0 | ~0 | 이슈·PR·CI (MCP) |
| 합 | **21** | **~1,347** | |

**`commit-commands`를 프리셋에 적어 넣었다.** 이미 머신에 켜져 있었는데 프리셋에는 항목이 없었다. 아래 [지우지 않고 `false`로 적는다](#지우지-않고-false로-적는다)의 규칙이 그대로 적용되는 자리다. 적지 않으면 "관심 없음"이라 머신마다 상태가 갈린다.

**MCP 전용 셋은 상시 0이다.** 툴 스키마가 컨텍스트에 상주하지 않고 쓸 때 불려온다. 그래서 툴 개수로 유저 스코프를 판단하지 않는다. 근거는 SETUP-GUIDE §3.

**내 도메인 플러그인도 똑같이 센다.** 아직 비어 있는 `architecture@kyle-skills`는 첫 스킬이 들어온 뒤 추가한다. `skill-authoring@kyle-skills`는 스킬을 쓰는 자리가 이 레포뿐이라 여기 넣지 않고 `skills` 레포의 프로젝트 스코프로 뒀다.

`env`의 키 두 개는 빈 값으로 두었다. `CONTEXT7_API_KEY`는 비워도 익명으로 연결되고 rate limit 만 낮다. `GITHUB_PERSONAL_ACCESS_TOKEN`은 `github`을 켤 때 채우는 자리다. 비운 채로 켜면 400 으로 죽는다. 이유는 SETUP-GUIDE §7.

### 지우지 않고 `false`로 적는다

| 플러그인 | 스킬 | 왜 내렸나 |
|---|---:|---|
| `github` | 0 (MCP) | 토큰이 있어야 산다. 없으면 빈 `Bearer` 가 나가 400 으로 죽고, `gh` CLI가 인증돼 있으면 이슈·PR·CI는 그쪽으로 된다. 토큰을 넣고 `true`로 되돌린다 (§2) |
| `vercel` | 33 | 특정 스택 전용. `project/nextjs-vercel`이 다시 켠다 |
| `telegram` | 2 | 서버가 `bun run`으로 뜬다. bun 이 없는 머신에서는 서버가 죽은 채 스킬 2개만 매 세션 162토큰씩 실린다. 쓰려면 bun 을 먼저 깔고 `true`로 되돌린다 |
| `frontend-design` | 1 | 프론트엔드 전용. 같은 프로젝트 프리셋으로 |
| `sentry` | 8 | 특정 SaaS를 붙인 레포만. 프로젝트 스코프 |
| `playwright` | 0 | 프론트엔드 전용 (MCP) |
| `skill-creator` | 1 | `superpowers:writing-skills`와 겹치고, 차별점인 eval은 쓸 수 없다 (SETUP-GUIDE §4) |

**항목을 지우면 안 꺼진다.** 병합은 프리셋에 있는 키만 덮어쓰므로, 지운 항목은 이미 켜진 머신에서 그대로 살아 있다. 끄려면 `false`로 적어야 전파된다. 지우면 "관심 없음", `false`면 "꺼라"다.

Codex 쪽 [`codex/bootstrap.sh`](codex/bootstrap.sh)가 도메인 플러그인을 캐시에 깔고 사용자 기본값을 `false`로 되돌리는 것과 같은 패턴이다. 유저 스코프에서 끄고 각 레포의 프로젝트 설정이 필요한 것만 켠다.

```bash
# 적용. 병합이라 model·theme 같은 개인 설정은 남는다
bash presets/claude/bootstrap.sh
```

---

## project/

레포 루트에 사용하는 하네스의 설정 디렉터리를 복사한다. 둘 다 쓰면 둘 다
복사한다.

```bash
cp -r presets/project/nextjs-vercel/.claude <대상 레포>/
cp -r presets/project/nextjs-vercel/.codex <대상 레포>/
```

**Codex 쪽은 지금 도메인 활성화만 있다.** 위 표의 Claude 공식 플러그인에 대응하는
MCP 서버를 `.codex/config.toml`에 넣지 않았다. 카탈로그가 1:1로 대응하지 않아
각각을 직접 찾아 구성하고 실제로 붙는지 확인해야 하는데, 아직 재지 않았다.
**확인하지 않은 설정을 커밋된 프리셋에 넣지 않는다.** 세션 시작 때 깨지면 클론한
사람 전부가 같이 깨진다. 측정한 뒤 채운다.

| 프리셋 | Claude 공식 플러그인 | 자체 도메인, 양쪽 공통 |
|---|---|---|
| `nextjs-vercel` | vercel, frontend-design, playwright, chrome-devtools-mcp, modern-web-guidance, typescript-lsp | `frontend`, `infra` |
| `backend-postgres` | prisma, postman, typescript-lsp | `backend` |
| `data-analytics` | duckdb-skills, grafana-mcp, pyright-lsp | `dashboard` |
| `infra-terraform` | terraform, aws-core, semgrep | `infra` |

오른쪽 열은 `.claude`와 `.codex`에서 함께 켜지는 자체 도메인 플러그인이다.
Codex 프로젝트 설정은 신뢰한 레포에서만 읽힌다. 사용자 캐시를 먼저 준비해야
하므로 [새 머신 셋업](#새-머신-셋업)의 부트스트랩을 한 번 실행한다.

Codex 원격 카탈로그의 `frontend-design-premium`, `figma`, `superdesign`,
`vercel`은 현재 `GLOBAL` 항목이라 이 프로젝트 프리셋에 넣지 않는다. 실제로 여러
레포에서 쓸 때만 전역 설치한다. 프로젝트 격리가 필요하면 디자인 지침은
`.agents/skills/`, Figma와 Vercel 같은 외부 연결은 `.codex/config.toml`의 MCP,
Playwright는 프로젝트 의존성으로 둔다.

### 바꿔 끼우는 자리

프리셋은 시작점이지 정답이 아니다. 스택이 다르면 같은 자리를 갈아 끼운다.

- **DB**: `prisma` 자리에 `supabase` / `neon` / `mongodb` / `convex`. **하나만** 켠다
- **클라우드**: `aws-core` 자리에 `azure` / `cloudflare` / `railway` / `render`. **하나만** 켠다
- **언어 서버**: `typescript-lsp` 자리에 `pyright-lsp` / `gopls-lsp` / `rust-analyzer-lsp`

여러 프리셋을 합칠 때 Claude는 `enabledPlugins` 객체를 병합한다. Codex는
`marketplaces.kyle-skills`를 하나만 남기고 `plugins` 테이블을 합친다.

---

## local/

`settings.local.json.example`은 최소 골격이다. 그대로 쓰라고 둔 게 아니다.

**손으로 채우지 말고 내장 `fewer-permission-prompts` 스킬을 돌린다.** 트랜스크립트를 훑어 실제로 자주 쓴 읽기 전용 명령만 골라 허용목록을 만들어준다. 예상으로 적으면 안 쓰는 항목이 쌓이고, 정작 필요한 건 빠진다.

```bash
cp presets/local/settings.local.json.example <대상 레포>/.claude/settings.local.json
echo '.claude/settings.local.json' >> <대상 레포>/.gitignore
```

---

## MCP 서버를 직접 붙일 때

플러그인에 딸린 MCP 서버는 플러그인을 켜면 같이 올라온다. 별도 파일이 필요 없다.

레포 루트의 `.mcp.json`은 **플러그인 밖의 MCP 서버**를 붙일 때만 쓴다. 여기에는 예시를 두지 않았다. 실제로 붙일 서버가 정해지기 전에 만들어두면 틀린 설정이 굳어질 뿐이다. 필요해지면 그때 `claude mcp add`로 붙이고, 잘 도는 설정을 여기 프리셋으로 옮긴다.

토큰은 `.mcp.json`에 직접 쓰지 않는다. `${VAR}` 참조를 쓰고 값은 유저 스코프 `settings.json`의 `env`에 둔다. context7 사례가 이 패턴이다.
