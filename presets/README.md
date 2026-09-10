# presets

Claude Code에 복사해서 쓰는 설정 원본. 도메인이 아니라 **스택** 단위로 잘랐다. 이 디렉터리의 `.claude` 파일은 Codex 설정 파일이 아니다.

Codex에서 사용자 전체에 쓸 도메인은 `codex plugin add <도메인>@kyle-skills`로 설치한다. 특정 레포에만 쓸 자체 스킬은 대상 레포의 `.agents/skills/`에 필요한 스킬 폴더만 둔다. Claude Code 공식 플러그인 이름은 Codex 마켓플레이스와 일대일로 대응하지 않으므로, 아래 프리셋의 외부 플러그인 목록을 Codex 설정으로 그대로 옮기지 않는다.

## 왜 도메인별이 아닌가

레포 하나에는 `.claude/settings.json`이 하나다. Next.js + Postgres 앱이면 frontend·backend·infra 세 도메인에서 끌어와야 하는데, 도메인별 조각으로 흩어두면 쓸 때마다 손으로 합쳐야 한다. 설정이 실제로 적용되는 단위가 스택이므로 그 축으로 자른다.

도메인 폴더(`../backend` 등)는 그 자체가 **플러그인**이다. `.claude-plugin/plugin.json`과 `skills/`로 이뤄지고, 설치되면 하네스가 통째로 가져간다. 거기에 설정 JSON을 두면 플러그인 페이로드에 딸려 들어가 아무 의미 없는 파일이 된다.

## Claude Code 세 스코프의 역할

| 스코프 | 파일 | 담는 것 | 커밋 |
|---|---|---|---|
| 유저 | `~/.claude/settings.json` | 어디서나 쓰는 플러그인, `env` | 해당 없음 |
| 프로젝트 | `<repo>/.claude/settings.json` | 그 스택 전용 플러그인 | **한다** |
| 로컬 | `<repo>/.claude/settings.local.json` | `permissions.allow` | **안 한다** |

프로젝트 스코프는 공유 대상이다. 그 레포를 여는 사람이면 누구나 같은 플러그인을 켜야 하므로 커밋한다. 로컬 스코프는 내 머신에서 내가 승인한 명령 허용목록이라 공유 대상이 아니다. `.gitignore`에 넣는다.

```gitignore
.claude/settings.local.json
```

---

## 새 머신 셋업

### Claude Code

노트북을 새로 사면 **이 레포를 클론해도 아무것도 켜지지 않는다.** 프로젝트 스코프는 각 작업 레포에 커밋돼 있어 클론하면 따라오지만, 유저 스코프는 `~/.claude/settings.json`에 있고 그 파일은 어느 레포에도 들어 있지 않다.

순서는 이렇다.

**1. 유저 스코프 설정을 병합한다.**

[`user/settings.json`](user/settings.json)의 `extraKnownMarketplaces`와 `enabledPlugins`를 `~/.claude/settings.json`에 넣는다. **덮어쓰지 않는다.** `model`, `theme`, `effortLevel` 같은 개인 설정이 그 파일에 같이 살기 때문이다.

`extraKnownMarketplaces`가 마켓플레이스 등록을 대신하므로 `claude plugin marketplace add`를 따로 칠 필요가 없다. 이 한 블록이 없으면 `enabledPlugins`의 `@kyle-skills` 항목이 어느 마켓플레이스인지 몰라 해석되지 않는다.

**source는 `github`로 고정한다.** 커밋되는 프리셋에 로컬 절대경로를 넣으면 그 머신 하나를 빼고 전부 틀린 설정이 된다. 이 레포를 직접 고치는 머신만 손으로 `{"source": "directory", "path": "..."}`로 바꿔 푸시 전 스킬을 확인한다. 그건 머신 하나에 대한 예외지 프리셋에 담을 값이 아니다.

공식 플러그인이 안 잡히면 한 번만 등록한다.

```bash
claude plugin marketplace add anthropics/claude-plugins-official
```

**2. 훅 스크립트를 복사한다.**

`settings.json`의 `hooks` 블록이 `~/.claude/hooks/fanout-cost-gate.sh`를 부른다. **파일이 없으면 모든 Bash 호출이 없는 스크립트를 실행하려 든다.**

```bash
mkdir -p ~/.claude/hooks
cp presets/user/hooks/fanout-cost-gate.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/fanout-cost-gate.sh
```

무엇을 하는 훅인지는 아래 [병렬 실행 비용 훅](#병렬-실행-비용-훅).

**3. `env`를 채운다.**

`CONTEXT7_API_KEY`는 레포에 빈 값으로 두었다. [context7.com/dashboard](https://context7.com/dashboard)에서 발급해 넣는다. 비워두면 401이 난다.

**토큰이 든 `settings.json`을 머신 간에 그대로 복사하지 않는다.** 레포의 프리셋을 병합하고 값은 새로 발급하는 쪽이 맞다.

**4. 작업 레포를 클론한다.**

프로젝트 스코프는 여기서 자동으로 붙는다. 커밋된 `<repo>/.claude/settings.json`이 `backend@kyle-skills` 같은 항목을 이미 들고 있고, 1번에서 마켓플레이스를 알려줬으므로 해석된다.

### Codex

Codex 플러그인 설치 상태는 사용자 스코프에 있으므로 레포를 클론하는 것만으로
복구되지 않는다. [`codex/bootstrap.sh`](codex/bootstrap.sh)를 한 번 실행한다.

```bash
bash presets/codex/bootstrap.sh
```

이 스크립트는 `kyle-skills` 마켓플레이스와 공통 작업 절차인
`superpowers@openai-curated-remote`, 실제 스킬이 들어 있는
`process@kyle-skills`만 멱등하게 설치한다. 아직 비어 있는 `architecture`는
스킬이 생긴 뒤 목록에 추가한다.

특정 레포에만 둘 자체 스킬은 플러그인으로 전역 설치하지 않고 그 레포의
`.agents/skills/` 아래에 링크한다. Codex는 이 경로를 상위 디렉터리부터 레포
루트까지 읽고 심볼릭 링크도 따라간다.

```bash
mkdir -p <대상 레포>/.agents/skills
ln -s <이 레포>/backend/skills/schema-review \
  <대상 레포>/.agents/skills/schema-review
```

설치 뒤에는 새 대화를 열어 스킬 목록을 다시 적재한다. 확인 명령:

```bash
codex plugin marketplace list
codex plugin list
```

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

유저 스코프 원본. 플러그인 10개. 공식 8개와 내 도메인 플러그인 2개다.

이 디렉터리의 JSON과 훅은 Claude Code 전용이다. Codex의 공통 설치 목록은
[`codex/bootstrap.sh`](codex/bootstrap.sh)가 맡는다.

**여기 둘 조건은 "언제 쓸지 모른다"가 아니라 "어느 레포에서든 쓴다"다.** 스킬 30개를 넘기지 않는다 (현재 26개). 근거는 [`../docs/SETUP-GUIDE.md`](../docs/SETUP-GUIDE.md) §1, §3.

| 플러그인 | 역할 |
|---|---|
| `superpowers` | 작업 절차 |
| `skill-creator` | 스킬 제작 |
| `claude-code-setup` | 레포별 자동화 진단 |
| `claude-md-management` | 프로젝트 규약 관리 |
| `serena` | 시맨틱 코드 분석 |
| `context7` | 최신 라이브러리 문서 조회 |
| `github` | 이슈·PR·CI |
| `sentry` | 에러·스택 트레이스 |
| `architecture@kyle-skills` | 내 아키텍처 스킬 |
| `process@kyle-skills` | 내 작업 절차 스킬 |

**내 도메인 플러그인도 똑같이 센다.** 지금은 스킬 26개라 여유가 있지만, 도메인에 스킬을 채우면 금방 찬다. `skill-authoring@kyle-skills`는 스킬을 쓰는 자리가 이 레포뿐이라 여기 넣지 않고 `skills` 레포의 프로젝트 스코프로 뒀다.

`env.CONTEXT7_API_KEY`는 빈 값으로 두었다. [context7.com/dashboard](https://context7.com/dashboard)에서 발급해 채운다. 비워두면 401이 난다. 이유는 SETUP-GUIDE §7.

**여기 없는 것.** `vercel`, `frontend-design`, `playwright`는 유저 스코프에서 내렸다. 셋 다 특정 스택 전용이라 위 조건을 통과하지 못한다. `project/nextjs-vercel`로 옮겼다.

```bash
# 적용: 기존 설정과 병합할 것. 덮어쓰면 model·theme 같은 개인 설정이 날아간다
$EDITOR ~/.claude/settings.json
```

---

## project/

레포 루트에 `.claude/` 통째로 복사한다.

```bash
cp -r presets/project/nextjs-vercel/.claude <대상 레포>/
```

| 프리셋 | 공식 플러그인 | 내 도메인 |
|---|---|---|
| `nextjs-vercel` | vercel · frontend-design · playwright · chrome-devtools-mcp · modern-web-guidance · typescript-lsp | `frontend` · `infra` |
| `backend-postgres` | prisma · postman · typescript-lsp | `backend` |
| `data-analytics` | duckdb-skills · grafana-mcp · pyright-lsp | `dashboard` |
| `infra-terraform` | terraform · aws-core · semgrep | `infra` |

오른쪽 열은 함께 켜지는 내 도메인 플러그인이다. 프리셋 JSON에 `@kyle-skills`로 들어가 있으므로 [유저 스코프 설정을 먼저 넣어야](#새-머신-셋업) 해석된다.

### 바꿔 끼우는 자리

프리셋은 시작점이지 정답이 아니다. 스택이 다르면 같은 자리를 갈아 끼운다.

- **DB**: `prisma` 자리에 `supabase` / `neon` / `mongodb` / `convex`. **하나만** 켠다
- **클라우드**: `aws-core` 자리에 `azure` / `cloudflare` / `railway` / `render`. **하나만** 켠다
- **언어 서버**: `typescript-lsp` 자리에 `pyright-lsp` / `gopls-lsp` / `rust-analyzer-lsp`

여러 프리셋을 합칠 때는 `enabledPlugins` 객체를 병합한다. 겹치는 키는 그냥 하나로 둔다.

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
