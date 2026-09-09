# 에이전트 설정 운영 기준

이 레포의 스킬을 어떤 전제 위에서 운영하는지 적어둔 문서다. 선택지를 늘어놓은 비교표가 아니라 **이미 내린 결정과 그 근거**의 기록이다. 새 스킬이나 플러그인을 추가할지 판단할 때 여기 적힌 기준을 먼저 통과시킨다.

측정 기준일 2026-09-09 · 하네스 Claude Code

---

## 1. 제약: 컨텍스트 예산

모든 결정이 여기서 나온다.

**스킬 설명문은 전부 컨텍스트에 상주한다.** 모델은 매 턴 "지금 쓸 스킬이 있나"를 판단하려고 등록된 **모든** 스킬의 `description`을 훑는다. 그래서 스킬이 늘어나면 두 가지가 동시에 나빠진다.

1. 고정 컨텍스트가 커져 실제 작업에 쓸 예산이 줄고
2. 후보가 많아져 **맞는 스킬을 못 고르는 구간**이 온다

두 번째가 본질이다. 스킬을 20개 깔면 20배 똑똑해지는 게 아니라, 20개 중에 헷갈리기 시작한다. 스킬은 자산이 아니라 **비용을 치르고 사는 것**이고, 값을 못 하면 마이너스다.

### 측정값

`/reload-plugins` 기준 스킬 70개.

| 구분 | 개수 | 성격 |
|---|---:|---|
| 하네스 내장 | 16 | 제거 불가 |
| vercel | 36 | 플러그인 스킬의 67% |
| superpowers | 14 | 작업 절차 전체 |
| 그 외 | 4 | 단일 스킬 플러그인 |

플러그인 스킬 54개 중 **vercel 하나가 36개**다. `playwright`와 `context7`은 MCP 전용이라 스킬 카운트에 잡히지 않는다.

> 열거로 확인한 건 53개(vercel 36 · superpowers 14 · 단일 스킬 플러그인 3). 보고값 54와의 차이 1개는 미확인으로 남긴다.

---

## 2. 결정: vercel은 프로젝트 스코프다

**`vercel`은 유저 스코프에서 내린다. Next.js/Vercel 레포에서만 켠다.**

권장이 아니라 확정된 운영 방식이다. 근거는 셋이다.

**부피.** 스킬 36개는 플러그인 스킬 전체의 3분의 2다. 이걸 유저 스코프에 두면 Vercel과 아무 상관 없는 모든 세션에서 36개가 상주한다.

**적중률.** 상주하는 36개는 대부분 특정 스택 전용이다. `next-cache-components`, `turbopack`, `microfrontends`, `vercel-firewall` 같은 것들이다. 블록체인 레포에서 작업할 때 이것들이 후보에 섞이는 건 순수한 손해다. 노이즈가 늘면 정작 맞는 스킬의 상대적 신호가 약해진다.

**잃는 게 없다.** 프로젝트 스코프로 내려도 Vercel 작업에서 손해가 없다. 해당 레포에서는 그대로 36개를 다 쓴다.

### 판단 기준으로 일반화하면

**플러그인을 유저 스코프에 둘 조건은 "언제 쓸지 모른다"가 아니라 "어느 레포에서든 쓴다"다.** vercel은 후자가 아니다. 같은 기준을 DB·클라우드·프레임워크 플러그인에 그대로 적용한다.

### 적용

```bash
# 유저 스코프에서 내린다
# ~/.claude/settings.json 의 enabledPlugins 에서 제거

# Vercel 을 쓰는 레포에서만 켠다
cd <next.js 레포>
claude plugin install vercel@claude-plugins-official   # scope: project
```

---

## 3. 결정: 유저 스코프는 10개까지

어디서나 쓰는 것만 유저 스코프에 둔다. 언어·스택 중립이어야 한다.

```
superpowers            작업 절차
skill-creator          스킬 제작
claude-code-setup      레포별 자동화 진단
claude-md-management   프로젝트 규약 관리
serena                 시맨틱 코드 분석
context7               최신 라이브러리 문서 조회
github                 이슈·PR·CI
sentry                 에러·스택 트레이스
```

DB·클라우드·프레임워크·BI는 **전부 프로젝트 스코프**다. 예외를 두기 시작하면 기준이 무너지고, 무너진 다음에는 다시 세우기 어렵다.

같은 기준을 적용하면 `frontend-design`과 `playwright`도 유저 스코프에서 내려간다. 둘 다 프론트엔드 작업 전용이라 "어느 레포에서든 쓴다"를 통과하지 못한다. `vercel`과 함께 `presets/project/nextjs-vercel`로 옮겼다.

**추가는 한 번에 3~4개까지.** 며칠 써보고 다음 묶음으로 간다. 한꺼번에 20개를 켜면 어느 게 효과였는지 영영 알 수 없다.

복사해서 쓸 설정 원본은 [`presets/`](../presets)에 있다.

---

## 4. 이미 갖고 있는 것

새 플러그인을 고르기 전에 이 두 계층에 있는지부터 확인한다. 이것만으로 설치 후보의 절반이 걸러진다.

```
① 내장 16개         하네스 기본기, 손댈 것 없음
② superpowers 14개  작업 절차 ("어떻게 일할지")
③ 도메인 플러그인    ← 여기만 비어 있다 ("무엇을 아는지")
```

### ① 내장 스킬 16개

플러그인 접두사(`superpowers:`, `vercel:`)가 **안 붙은** 것들이 내장이다. 설치 대상이 아니다.

**아티팩트 · 시각화**

- `dataviz`: 차트·그래프·대시보드 작성 **전에** 자동 로드. 팔레트 공식, 축 규칙, 접근성 검증기 포함
- `artifact-design`: 아티팩트 작성 전 디자인 강도 캘리브레이션
- `artifact-diagramming`: 양쪽 테마에서 읽히는 인라인 SVG 다이어그램
- `artifact-capabilities`: 페이지에 상태 저장·라이브 데이터·파일 처리 능력 부여
- `design`: 다중 아트보드 디자인 캔버스

**코드 품질**

- `code-review`: diff·PR·브랜치를 low에서 ultra까지 강도를 골라 리뷰
- `simplify`: 재사용·단순화·효율 정리를 찾아 바로 적용 (버그는 안 봄)
- `security-review`: 브랜치 변경분 보안 리뷰

**환경 · 설정**

- `init`: CLAUDE.md 생성
- `update-config`: settings.json의 훅·권한·환경변수 작성
- `fewer-permission-prompts`: 자주 쓰는 읽기 전용 명령의 허용목록 자동 생성
- `keybindings-help`: 키바인딩 커스터마이즈

**실행 · 자동화**

- `run`: 앱을 실제로 띄워 변경 확인
- `loop`: 프롬프트·슬래시 명령 주기 반복
- `schedule`: cron 기반 클라우드 에이전트

**레퍼런스**

- `claude-api`: 모델 ID·가격·파라미터·툴 유즈·캐싱

### 겹쳐서 설치하지 않는 것

| 후보 | 이미 있는 것 | 판단 |
|---|---|---|
| 차트·대시보드 생성 플러그인 | `dataviz` | 설치 안 함 |
| `code-simplifier` | `simplify` | 설치 안 함 |
| 범용 코드 리뷰 플러그인 | `code-review` | 설치 안 함 |

**단, `code-review`(내장)와 `superpowers:requesting-code-review`는 겹치지 않는다.** 전자는 diff를 직접 훑는 *실행 도구*, 후자는 리뷰어 서브에이전트를 *디스패치하는 절차*다. 둘 다 쓴다.

### ② superpowers 14개는 전부 절차다

| 단계 | 스킬 |
|---|---|
| 설계 | `brainstorming` · `writing-plans` · `using-git-worktrees` · `using-superpowers` |
| 실행 | `executing-plans` · `subagent-driven-development` · `dispatching-parallel-agents` · `test-driven-development` |
| 검증 | `systematic-debugging` · `requesting-code-review` · `receiving-code-review` · `verification-before-completion` |
| 마무리·메타 | `finishing-a-development-branch` · `writing-skills` |

14개 **전부** "어떻게 일할지"다. 언어·프레임워크·인프라 지식은 한 줄도 없다. 그래서 도메인 스킬과 충돌하지 않고 위에 얹힌다. 그리고 그게 지금 공백의 정체다. superpowers는 "TDD로 짜라"고는 말하지만 "이 Postgres 스키마엔 부분 인덱스가 필요하다"고는 말해주지 않는다.

이 계층은 더 채울 게 없다. **③만 남았다.**

---

## 5. 도메인별 배치

이 레포의 폴더 구성과 1:1로 대응한다. 각 도메인의 상세 카탈로그는 해당 폴더의 `README.md`에 있다.

표기: **[있음]** 보유 · **[코어]** 먼저 · **[선택]** 스택 맞을 때 · **[OSS]** 마켓플레이스 밖

### [architecture](../architecture) · 공백, 최우선

에이전트는 grep으로 훑은 결과를 구조 이해라고 착각한다. 필요한 건 **심볼 단위로 정확히 읽는 능력**이다.

- **[코어]** `serena`: 시맨틱 코드 분석 MCP (oraios/serena, 29K)
- **[코어]** `typescript-lsp` / `pyright-lsp` / `gopls-lsp`: 언어 서버 직결
- **[OSS]** `tt-a1i/archify`: 아키텍처·시퀀스·데이터플로우 다이어그램
- **[선택]** `code-modernization` · `sourcegraph`

### [backend](../backend) · 공백

스키마를 모르는 채 쿼리를 쓰는 게 주된 실패다. DB 플러그인은 스키마를 직접 읽으므로 이 실패 모드 자체를 없앤다.

- **[코어]** `prisma` / `supabase` / `neon` / `mongodb` / `convex` 중 **하나만**
- **[코어]** `postman`
- **[선택]** `mcp-server-dev` · `agent-sdk-dev` · `auth0` / `workos` · `redis-development`

### [frontend](../frontend) · 부분

`playwright`는 "동작하나"를, `chrome-devtools-mcp`는 "왜 느린가"를 본다. 대체재가 아니다.

- **[프로젝트 스코프]** `frontend-design` · `playwright` (§3)
- **[코어]** `chrome-devtools-mcp` · `modern-web-guidance`
- **[선택]** `figma` · `superdesign`

### [dashboard](../dashboard) · 부분

차트를 **그리는** 능력은 내장 `dataviz`가 이미 갖고 있다. 비는 건 **데이터에 닿는 경로**다.

- **[있음]** `dataviz` (내장)
- **[코어]** `duckdb-skills`: 셋업 비용 0, 가장 범용적
- **[코어]** `grafana-mcp`: 대시보드를 직접 만들고 고침
- **[선택]** `clickhouse` + `clickhouse-best-practices` · `posthog` / `amplitude`

### [infra](../infra) · 부분

관측 도구를 붙이면 디버깅이 추측에서 조회로 바뀐다.

- **[코어]** `sentry` · `github`
- **[선택]** `terraform` · `aws-core` / `azure` / `cloudflare` 중 클라우드는 **하나만**
- **[프로젝트 스코프]** `vercel` (§2)

### [process](../process) · 기반 있음

- **[있음]** `superpowers` · `claude-code-setup`
- **[코어]** `claude-md-management` · `mattpocock-skills`

### [skill-authoring](../skill-authoring) · 기반 있음

- **[있음]** `skill-creator` · `superpowers:writing-skills`
- **[코어]** `plugin-dev`

---

## 6. 외부 스킬 반입 절차

마켓플레이스 밖 OSS 스킬은 검증 없이 넣지 않는다. 스킬은 프롬프트 주입 표면이고, 컨텍스트에 상주하며, 도구 호출을 유도할 수 있다.

1. [`NVIDIA/SkillSpector`](https://github.com/NVIDIA/SkillSpector)로 스캔해 악성 페이로드·취약점을 확인한다
2. `SKILL.md`를 직접 읽어 `description`과 본문이 같은 말을 하는지 확인한다
3. 프로젝트 스코프로만 먼저 켠다
4. 며칠 써본 뒤 유저 스코프 승격을 판단한다. §3의 10개 한도 안에서다

---

## 7. 트러블슈팅

### context7 401은 플러그인 버그다

**증상**

```
plugin:context7:context7 - ✘ Failed to connect
Server rejected the configured Authorization header (HTTP 401)
```

**원인**

README에는 "API 키는 선택 사항, 없으면 익명 연결"이라 적혀 있다. 그런데 401이 난다. 엔드포인트를 직접 찔러본 결과다.

| 요청 | 응답 |
|---|---:|
| `/mcp` · Authorization 없음 | 200 |
| `/mcp?client=claude-code-plugin` · 없음 | **401** |
| `/mcp?client=claude-code-plugin` · 빈 값 | **401** |
| `/mcp?client=claude-code-plugin` · 아무 값이나 | 200 |

플러그인이 쓰는 URL에는 `?client=claude-code-plugin`이 붙어 있고, **이 경로는 Authorization 헤더가 존재하고 비어 있지 않기만 하면 통과한다.** 키 내용은 검증하지도 않는다.

그런데 플러그인 설정이 이렇다.

```json
{ "headers": { "Authorization": "${CONTEXT7_API_KEY:-}" } }
```

`:-`의 기본값이 빈 문자열이라, 변수가 unset이면 빈 헤더가 나가 정확히 401 조건에 걸린다. README의 "익명으로 동작"은 쿼리 파라미터 없는 맨 URL 기준이라 이 경로에선 성립하지 않는다.

**해결하는 자리는 `~/.bashrc`가 아니다**

bashrc는 **대화형 bash 셸에서만** 읽힌다. IDE 확장이나 데스크톱 앱에서 하네스를 띄우면 적용되지 않는다. `~/.claude/settings.json`의 `env` 블록은 실행 경로와 무관하게 먹는다.

```json
{
  "env": {
    "CONTEXT7_API_KEY": "<context7.com/dashboard 에서 발급>"
  }
}
```

내장 `update-config` 스킬로 편집해도 된다.

```bash
claude mcp list | grep context7   # 적용 확인
```

### playwright 연결 실패

```
Skipping connection (recent failure cached, retries automatically in 15 min)
```

일시적이다. 15분 후 자동 재시도되며 대개 스스로 복구된다. 손대지 않는다.

---

## 부록: 도메인 배치의 근거

§5의 선정은 두 데이터를 대조해서 나왔다.

- **star-history 랭킹 데이터셋 12,400건.** 올타임 스냅샷 2026-09-08, 주간 집계 2026-09-01에서 09-07. 에이전트·스킬 관련 315개를 추려 `api.star-history.com/repo/{owner}/{name}`로 설명·토픽·주간 활동을 보강했다
- **`anthropics/claude-plugins-official` 마켓플레이스 매니페스트 292건**

당시 주간 스타 증가 상위 20개 중 13개가 에이전트·스킬 저장소였고, 1위가 아키텍처 다이어그램 스킬(`tt-a1i/archify`)이었다. 사람들이 에이전트에게 시키는 일이 코드 생성에서 **구조 파악**으로 옮겨간 신호로 읽었고, 그래서 `architecture`를 최우선 공백으로 뒀다.

분류 축은 [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills)의 디렉터리 구성을 기준선으로 삼았다. `api-and-interface-design`, `frontend-ui-engineering`, `observability-and-instrumentation`, `ci-cd-and-automation`, `documentation-and-adrs` 같은 이름들이다.

superpowers 구성은 로컬 설치본 v6.3.0을 직접 열어 확인했다. context7 응답 코드는 엔드포인트에 직접 요청해 측정했다.
