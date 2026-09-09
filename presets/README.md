# presets

복사해서 쓰는 설정 원본. 도메인이 아니라 **스택** 단위로 잘랐다.

## 왜 도메인별이 아닌가

레포 하나에는 `.claude/settings.json`이 하나다. Next.js + Postgres 앱이면 frontend·backend·infra 세 도메인에서 끌어와야 하는데, 도메인별 조각으로 흩어두면 쓸 때마다 손으로 합쳐야 한다. 설정이 실제로 적용되는 단위가 스택이므로 그 축으로 자른다.

도메인 폴더(`../backend` 등)는 그 자체가 **플러그인**이다. `.claude-plugin/plugin.json`과 `skills/`로 이뤄지고, 설치되면 하네스가 통째로 가져간다. 거기에 설정 JSON을 두면 플러그인 페이로드에 딸려 들어가 아무 의미 없는 파일이 된다.

## 세 스코프의 역할

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

## user/

유저 스코프 원본. 플러그인 10개. 공식 8개와 내 도메인 플러그인 2개다.

**여기 둘 조건은 "언제 쓸지 모른다"가 아니라 "어느 레포에서든 쓴다"다.** 스킬 30개를 넘기지 않는다 (현재 25개). 근거는 [`../docs/SETUP-GUIDE.md`](../docs/SETUP-GUIDE.md) §1, §3.

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

**내 도메인 플러그인도 똑같이 센다.** 지금은 스킬 25개라 여유가 있지만, 도메인에 스킬을 채우면 금방 찬다. `skill-authoring@kyle-skills`는 스킬을 쓰는 자리가 이 레포뿐이라 여기 넣지 않고 `skills` 레포의 프로젝트 스코프로 뒀다.

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

오른쪽 열은 함께 켜지는 내 도메인 플러그인이다. 프리셋 JSON에 `@kyle-skills`로 들어가 있으므로 [마켓플레이스를 먼저 등록](../README.md#쓰는-법)해야 설치된다.

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
