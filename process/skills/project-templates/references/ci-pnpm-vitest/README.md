# ci-pnpm-vitest

**복사형.** `files/` 를 레포 루트에 복사하면 일단 돈다.

> **마지막 검증**: 2026-09-09 에 `mantle-kr-herald` 에서 뽑음. **2026-09-10 에 `jarvis` 에 PR 제목 검사만 적용해 CI 통과 확인** — PR #20, run `34436822886`, 스텝이 실제로 돌아 `PR title OK: ...` 를 찍었다 (`PR_TITLE` 이 비면 exit 1 이므로 배선까지 증명된다).
>
> **2026-09-10: `files/scripts/check-pr-title.js` 가 조각에 들어왔다.** jarvis 에서 이 스텝을 실제로 붙이려면 스크립트를 새로 써야 했고, 그 결과물을 되가져왔다. 그전까지 이 조각의 `ci.yml` 은 **존재하지 않는 스크립트를 부르고 있었다.**
>
> **단 `ci.yml` 파일을 복사한 게 아니다.** jarvis 에 이미 있던 `ci.yml` 에 스텝 하나를 손으로 옮겼고, `typecheck:web` 절반은 조건이 안 맞아 쓰지 않았다. **`files/` 를 통째로 복사해본 적은 아직 없다** — 액션 버전과 `node-version: 24` 는 여전히 검증 안 된 값이다 (jarvis 는 Node 22 를 쓴다).
>
> 썩는 값: `actions/checkout@v4`, `actions/setup-node@v4`, `pnpm/action-setup@v4`, `node-version: 24`. 액션 메이저 버전과 Node 버전은 시간이 지나면 틀려지고, **틀려도 조용히 경고만 뜬다.** 쓰기 전에 현재 버전을 확인한다.

pnpm + TypeScript + Vitest 레포의 GitHub Actions 워크플로. 스텝 두 개가 조각의 내용이고, 나머지는 그 둘을 돌리기 위한 골조다.

## 출처

`mantle-kr-herald` `.github/workflows/ci.yml`

| 커밋 | 무엇 |
|---|---|
| `0ef41b1` | 최초 워크플로 (install, typecheck, test) |
| `7e916a6` | `typecheck:web` 추가 |
| `f2486e0` | PR 제목 검사 추가 (#180) |

## 왜 있는가

### PR 제목 검사

squash merge 를 쓰면 **PR 제목이 그대로 main 의 커밋 제목이 된다.** 브랜치 안의 커밋은 리뷰도 받고 훅도 거치지만 제목은 아무 관문도 안 거친다. 이 레포에서 아무도 안 보는 유일한 텍스트가 된다.

2026-08-11 에 영어 커밋 제목 400개 사이로 한국어 제목 두 개가 이 경로로 들어왔다. **해당 브랜치의 커밋은 전부 영어였다.** 제목만 아니었다.

두 가지가 이 스텝의 모양을 정했다.

- **별도 job 이 아니라 `test` job 안에 둔다.** main 의 required status check 가 `test` 하나뿐이었다. 새 job 을 만들면 통과 여부가 표시는 되지만 강제되지 않는다. 누군가 required 목록에 손으로 추가하기 전까지는 그냥 초록색 장식이다
- **제목을 env 로 넘긴다.** `run:` 안에 `${{ }}` 로 보간하면 백틱이나 `$(...)` 가 든 제목이 러너에서 실행된다. 제목은 외부 입력이다

#### 규칙은 "ASCII 만" 이 아니다

`jarvis` 에 붙이면서 드러났다. 그 레포의 영어 제목들은 `—` (U+2014) 와 `→` (U+2192) 를 쓴다 (`feat: Phase 2 execution — jarvis do → draft PR`). ASCII 로 잡으면 **자기 히스토리 20개 중 3개가 떨어진다.** herald 가 당한 것은 한글이었으므로 검사 대상도 한글/CJK 여야 한다. 잡으려는 것이 "비-ASCII" 가 아니라 "영어가 아닌 것" 이라는 게 요점이다.

#### 검사기가 조용히 고장 나는 경우

규칙이 정규식 한 줄이라 깨지면 **전부 통과시키면서 초록색으로 보인다** — 이 스텝이 막으려는 바로 그 종류의 실패가 검사기 자신에게 생긴다. 그래서 스크립트가 자기 픽스처를 매 실행마다 검사하고, 어긋나면 exit 2 로 죽는다.

### `typecheck:web`

두 사실이 겹칠 때만 생기는 구멍이다.

1. 별도 `tsconfig.json` 을 가진 하위 디렉터리는 루트 `tsc` 에 안 잡힌다
2. Vitest 는 esbuild 를 통해 도는데, esbuild 는 타입을 **검사하지 않고 지운다**

그래서 그 디렉터리의 타입 오류는 typecheck 도 test 도 안 걸리고 main 에 들어간다. herald 에서는 `web/` 이 그 디렉터리였고 `web/tests/OutletCard.test.tsx` 가 이걸 드러냈다.

## 바꿔야 할 것

| 위치 | 무엇 |
|---|---|
| `pnpm/action-setup@v4` 의 버전 출처 | **둘 중 하나는 있어야 한다.** 조각의 파일은 `package.json` 의 `packageManager` 필드에서 읽는 쪽을 쓴다 (파일 주석 참조). 대상 레포에 그 필드가 없으면 액션에 `version:` 을 직접 박는다 — `jarvis` 가 `version: 11` 로 그렇게 한다 (2026-09-10 관찰) |
| `node-version: 24` | 대상 레포의 Node 버전. **pnpm 메이저가 요구하는 최소 Node 를 먼저 확인한다** — `jarvis` 는 `ci: use Node 22 (required by pnpm 11)` 로 이 이유 때문에 한 번 올렸다 (커밋 `f8aee63`) |
| `scripts/check-pr-title.js` 의 **규칙** | 스크립트 자체는 이제 조각에 들어 있다 (`files/scripts/`). 바꿀 것은 `CJK` 와 `CONVENTIONAL` 두 줄 — jarvis/herald 의 규칙(영어 + Conventional Commits)이다. **`FIXTURES` 도 같이 고친다**, 안 그러면 스크립트가 자기 자신을 떨어뜨린다 |
| `package.json` 의 `scripts` | `"check:pr-title": "node scripts/check-pr-title.js"` 를 추가해야 워크플로의 `pnpm check:pr-title` 이 붙는다. 이 한 줄이 빠지면 CI 는 조각 탓이 아니라 그 이유로 깨진다 |
| `pnpm typecheck:web` | `web` 을 실제 하위 디렉터리 이름으로. tsconfig 가 여러 개면 스텝을 그만큼 늘린다 |
| `branches: [main]` | 기본 브랜치 이름이 다르면 |

## 안 써도 되는 조건

**PR 제목 검사를 뺀다:**

- squash merge 를 안 쓴다. 그러면 제목은 커밋 제목이 되지 않고 검사할 이유가 사라진다
- 검사할 규칙이 없다. 커밋 제목 언어나 형식에 대한 합의가 없으면 검사도 없다
- required status check 가 여러 개다. 이 경우 별도 job 으로 빼는 쪽이 낫다. `test` 안에 둘 이유가 사라진다

**확인은 두 군데를 봐야 한다.** `repos/{owner}/{repo}/branches/main/protection` 은 레거시 branch protection 만 본다. ruleset 으로 걸어둔 레포는 여기서 `Branch not protected` 404 가 나오고, 보호가 없다고 잘못 읽게 된다 (`jarvis`, 2026-09-10). `repos/{owner}/{repo}/rulesets` 를 같이 본다.

**`typecheck:web` 을 뺀다:**

- tsconfig 가 하나다. 루트 typecheck 가 전부 덮는다
- 하위 디렉터리 tsconfig 가 있어도 루트 tsconfig 의 `references` 나 `include` 로 이미 잡힌다. 확인하고 뺀다

둘 다 빼면 남는 건 평범한 pnpm CI 이고, 이 조각을 쓸 이유도 없다.
