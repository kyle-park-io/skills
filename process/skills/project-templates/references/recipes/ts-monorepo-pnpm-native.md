# ts-monorepo-pnpm-native

pnpm 워크스페이스 TypeScript 모노레포. 네이티브 애드온 의존성이 있고, 배포 대상 없이 로컬에서 도는 CLI/에이전트. CI 는 GitHub Actions 에서 typecheck + vitest 만.

출처는 `jarvis` 하나다. **레시피가 두 번째 레포를 만나기 전까지는 jarvis 의 구성을 적어둔 것에 지나지 않는다.** 두 번째 스택이 들어올 때 여기 뺄 것과 남길 것이 갈린다.

## 쓴다

| 조각 | 왜 |
|---|---|
| [`pnpm-native-build-allowlist`](../pnpm-native-build-allowlist) | 네이티브 애드온 (`better-sqlite3`) 이 있다. 이 스택 정의의 절반이 이 조건이다. **감지 테스트는 조각에 없으니 같이 써야 한다** |
| [`ci-pnpm-vitest`](../ci-pnpm-vitest) | pnpm + vitest CI 의 골조. 단 **두 스텝 다 조건부다.** 아래 참조 |

### `ci-pnpm-vitest` 를 그대로 쓰지 않는 부분

이 스택에서 그 조각의 두 스텝은 이렇게 갈린다.

- **`typecheck:web`: 뺀다.** 모노레포지만 패키지 tsconfig 가 전부 루트 `tsconfig.base.json` 을 상속하고 `pnpm -r typecheck` 가 각 패키지에서 `tsc` 를 돌린다. 루트 typecheck 가 안 덮는 하위 디렉터리가 없다. 조각 README 의 "안 써도 되는 조건" 두 번째 항목에 그대로 해당한다
- **PR 제목 검사: 조건이 반만 맞는다.** 판단이 필요하므로 아래 별도 항목으로 뺐다

## 안 쓴다

| 조각 | 왜 |
|---|---|
| [`vercel-spa-api`](../vercel-spa-api) | **배포 대상이 없다.** 로컬에서 도는 CLI 다. 서버리스 함수도 SPA 도 없으니 rewrite 규칙이 가리킬 것이 없다 |
| [`systemd-timer`](../systemd-timer) | **스케줄러가 프로세스 안에 있다.** `jarvis` 는 croner 로 인프로세스 스케줄링을 한다 (`packages/scheduler`). 바깥에서 깨워줄 타이머가 필요 없다. **단 이 판단은 구동 방식에 묶여 있다.** 상시 구동 데몬으로 가거나 CLI 를 크론으로 때리는 쪽으로 바뀌면 이 줄을 다시 본다 |

`systemd-timer` 가 여기 "안 쓴다"로 들어가 있는 게 이 레시피 파일의 존재 이유다. "스케줄러가 있는 레포"라는 이유로 따라오기 쉬운데, 필요 여부를 정하는 건 스케줄러의 유무가 아니라 **스케줄링이 프로세스 안에 있느냐 밖에 있느냐**다.

## 넣은 것

### PR 제목 검사 (`ci-pnpm-vitest`)

> 여기서 쓴 스크립트는 2026-09-10 에 조각으로 되돌아갔다 (`ci-pnpm-vitest/files/scripts/check-pr-title.js`). 다음 레포는 새로 쓰지 않는다.

**조건이 세 개 다 맞아서 넣었다.** `jarvis` PR #20, 2026-09-10. 확인한 상태:

| 조각이 요구하는 조건 | 이 스택에서 |
|---|---|
| squash merge 를 쓴다 | **참.** `squash_merge_commit_title: COMMIT_OR_PR_TITLE`. 커밋이 여럿인 PR 은 PR 제목이 main 의 커밋 제목이 된다. 히스토리가 그 모양이다 (`feat(core): pure allocation engine (#1)`) |
| 검사할 규칙이 있다 | **참.** `CLAUDE.md` 에 "Commit messages → English" 가 적혀 있고, 히스토리는 Conventional Commits 형태로 균일하다. 둘 다 강제하는 관문이 없다 |
| required status check 가 하나뿐이다 (그래서 `test` 안에 둔다) | **참.** ruleset `protect-main` 이 active 고, `required_status_checks` 가 `build` 하나뿐이며 `bypass_actors` 가 비어 있다. **레거시 `branches/main/protection` 엔드포인트는 404 를 준다.** ruleset 은 거기 안 잡힌다. `repos/{owner}/{repo}/rulesets` 를 봐야 한다 |

조각 그대로, **별도 job 이 아니라 기존 job 안에** 넣었다. 이 레포에서 그 job 이름은 `test` 가 아니라 `build` 다.

**규칙은 "ASCII 만"이 아니다.** jarvis 히스토리는 영어 제목 안에서 U+2014 엠대시와 `→` (U+2192) 를 쓴다 (`feat: Phase 2 execution <U+2014> jarvis do → draft PR`). ASCII 로 잡으면 그 레포 자기 커밋 20개 중 3개가 떨어진다. herald 가 실제로 당한 것은 한글이었으므로 규칙도 한글/CJK 여야 한다. 검사 대상이 "비-ASCII"가 아니라 "영어가 아닌 것"이라는 게 요점이다.

**스크립트는 자기 픽스처를 매 실행마다 검사하게 썼다.** 규칙이 정규식 하나라서, 그게 깨지면 전부 통과시키면서 초록색으로 보인다. 조각이 막으려는 종류의 조용한 실패가 검사기 자신에게 생긴다.

### 이 스택에서 herald 보다 노출이 큰 이유

herald 에서는 사람이 PR 제목을 타이핑했다. 여기서는 프로그램이 만든다. `packages/agent/src/executor.ts:128` 이 Phase 2 의 초안 PR 제목을 이렇게 조립한다:

```
[jarvis] #${number}: ${issue.title}
```

`issue.title` 은 외부 텍스트다. 그게 그대로 PR 제목이 되고, squash merge 되면 main 의 커밋 제목이 된다. 사람이 한 번도 다시 쓰지 않는 경로다. 조각이 말하는 "아무도 안 보는 유일한 텍스트"의 자동화된 판본이다.

**그래서 검사 규칙과 이 줄이 서로를 건드린다.** 규칙을 Conventional Commits 로 잡으면 `[jarvis] #12: ...` 는 검사에 걸린다. 둘 중 하나를 정해야 한다:

- `executor.ts` 가 Conventional 형태의 제목을 만들게 고친다 (히스토리가 균일해지므로 이쪽이 맞아 보인다)
- 검사 규칙이 `[jarvis] #N:` 접두사를 예외로 둔다 (자동 PR 만 히스토리에서 튄다)

## 조각이 안 덮는 것

새 레포를 이 스택으로 세울 때 이 레시피로 안 되는 것들. 조각으로 만들 근거가 아직 없어서 빠진 것이지 필요 없어서가 아니다.

- 네이티브 빌드 감지 테스트 본체 (`pnpm-native-build-allowlist` 의 "바꿔야 할 것" 참조)
- `tsconfig.base.json`, `.gitignore`, 패키지별 `tsconfig.json`. `jarvis` 에서 관문 1 또는 2 에 걸렸다. 아래 참조

### 관문에 떨어진 것 (`jarvis`, 2026-09-10)

두 번 판단하지 않기 위해 남긴다.

| 후보 | 떨어진 관문 |
|---|---|
| `.github/workflows/ci.yml` | **관문 2.** checkout / setup-pnpm / setup-node / install / typecheck / test 뿐이라 스캐폴딩과 차이가 없다. 기존 `ci-pnpm-vitest` 조각이 "골조"라고 부르는 바로 그것 |
| `tsconfig.base.json` 의 `noUncheckedIndexedAccess` | **관문 1.** 기본값과는 다르지만 (관문 2 통과) **왜 켰는지가 레포에 없다.** plan 문서들은 이 값을 "Tech Stack" 에 선언만 하고, 커밋 두 개 (`fix(core): make parseISODate typecheck under noUncheckedIndexedAccess` 등) 는 이 값이 치른 **비용**을 기록할 뿐 이유를 기록하지 않는다. 이유는 상상할 수 있지만 지어내지 않는다 |
| `.gitignore` 의 `design/`, `/data/`, `*.db` | **관문 3.** 이유는 파일 주석에 있다 (런타임 데이터는 `~/jarvis` 에, 개인 맥락이 든 스펙은 공개 레포 밖에). 하지만 조건이 "이 레포면 참"이라 조각이 되면 골격형이고, 세 줄짜리 골격형 gitignore 는 열어보는 비용이 다시 쓰는 비용보다 크다 |
