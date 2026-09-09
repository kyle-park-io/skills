# ci-pnpm-vitest

**복사형.** `files/` 를 레포 루트에 복사하면 일단 돈다.

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

### `typecheck:web`

두 사실이 겹칠 때만 생기는 구멍이다.

1. 별도 `tsconfig.json` 을 가진 하위 디렉터리는 루트 `tsc` 에 안 잡힌다
2. Vitest 는 esbuild 를 통해 도는데, esbuild 는 타입을 **검사하지 않고 지운다**

그래서 그 디렉터리의 타입 오류는 typecheck 도 test 도 안 걸리고 main 에 들어간다. herald 에서는 `web/` 이 그 디렉터리였고 `web/tests/OutletCard.test.tsx` 가 이걸 드러냈다.

## 바꿔야 할 것

| 위치 | 무엇 |
|---|---|
| `node-version: 24` | 대상 레포의 Node 버전 |
| `pnpm check:pr-title` | **스크립트를 직접 써야 한다.** 조각에 안 들어 있다. `process.env.PR_TITLE` 을 읽어 그 레포가 원하는 규칙을 검사한다 |
| `pnpm typecheck:web` | `web` 을 실제 하위 디렉터리 이름으로. tsconfig 가 여러 개면 스텝을 그만큼 늘린다 |
| `branches: [main]` | 기본 브랜치 이름이 다르면 |

## 안 써도 되는 조건

**PR 제목 검사를 뺀다:**

- squash merge 를 안 쓴다. 그러면 제목은 커밋 제목이 되지 않고 검사할 이유가 사라진다
- 검사할 규칙이 없다. 커밋 제목 언어나 형식에 대한 합의가 없으면 검사도 없다
- required status check 가 여러 개다. 이 경우 별도 job 으로 빼는 쪽이 낫다. `test` 안에 둘 이유가 사라진다

**`typecheck:web` 을 뺀다:**

- tsconfig 가 하나다. 루트 typecheck 가 전부 덮는다
- 하위 디렉터리 tsconfig 가 있어도 루트 tsconfig 의 `references` 나 `include` 로 이미 잡힌다. 확인하고 뺀다

둘 다 빼면 남는 건 평범한 pnpm CI 이고, 이 조각을 쓸 이유도 없다.
