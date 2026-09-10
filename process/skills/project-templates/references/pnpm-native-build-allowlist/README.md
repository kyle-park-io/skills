# pnpm-native-build-allowlist

**복사형.** `files/` 를 레포 루트에 복사하면 일단 돈다. 단, `packages` 글로브와 허용 목록은 대상 레포의 것으로 바꿔야 한다.

> **마지막 검증**: 2026-09-10 에 `jarvis` 에서 뽑음. 뽑을 때 `pnpm 11.25.0` / `Node 24.15.0` 에서 실제로 돌려 확인했다 (`pnpm --filter @jarvis/store exec vitest run src/smoke.test.ts` → 네이티브 빌드가 돌고 2 tests passed). **새 레포에 적용해본 적 없다.**
>
> 썩는 값: **`allowBuilds` 라는 필드 이름 자체.** pnpm 이 이 허용 목록을 부르는 이름은 메이저 버전 사이에서 바뀌어왔다. 여기 확인된 것은 `pnpm 11.25.0` 이 `allowBuilds` 를 읽는다는 것뿐이다. 다른 메이저에서는 **이름이 틀려도 에러가 아니라 그냥 무시된다** — 즉 이 조각이 막으려는 바로 그 조용한 실패로 되돌아간다. 쓰기 전에 대상 레포의 pnpm 메이저에서 `pnpm approve-builds` 를 한 번 돌려 어떤 이름으로 쓰는지 확인한다.

pnpm 워크스페이스에서 네이티브 애드온을 가진 의존성의 빌드를 허용하는 한 줄. 조각의 내용은 `allowBuilds` 필드 하나고, `packages` 는 그걸 담기 위한 골조다.

## 출처

`jarvis` `pnpm-workspace.yaml` (`git@github.com:kyle-park-io/jarvis.git`, 뽑을 때 HEAD `f858f8d`)

| 커밋 | 무엇 |
|---|---|
| `f8aee63` | 워크스페이스 최초 생성. `esbuild` 만 허용 |
| `9a9a79c` | `better-sqlite3` 추가 (#2, store 영속 계층) |

## 왜 있는가

**설치가 실패하지 않는다는 것이 문제다.**

pnpm 11 은 의존성의 install 스크립트를 기본적으로 막는다. 네이티브 애드온을 가진 패키지에서 이것은 바인딩이 컴파일되지 않는다는 뜻인데, `pnpm install` 은 "ignored build scripts" 정도의 안내만 찍고 성공한다. 깨진 사실은 한참 뒤, 그 모듈을 처음 import 하는 지점에서 드러난다.

CI 에서 이 시차가 특히 나쁘다. install 이 첫 스텝이라 초록색으로 지나가고, 실제 실패는 그 모듈을 우연히 먼저 import 하는 테스트 파일에서 난다. 증상이 원인과 다른 파일에 나타난다.

jarvis 는 2026-07-14 에 `better-sqlite3` 로 `@jarvis/store` 를 세우면서 이걸 만났다. 고친 방식이 조각의 나머지 절반이다 — `docs/plans/2026-07-14-store-persistence.md` 의 Step 3 이 허용 목록을 추가하고, **Step 4 가 인메모리 DB 를 여는 테스트를 같이 넣는다.** Step 5 의 기대값에 그 의도가 적혀 있다: *"2 tests PASS (if the second fails to load `better-sqlite3`, the build did not run — revisit Step 3)"*.

허용 목록만으로는 절반이다. 목록이 비거나 이름이 틀렸을 때 그 사실을 **큰 소리로, 지정된 자리에서** 알려주는 테스트가 있어야 조용한 실패가 조용하지 않게 된다.

## 바꿔야 할 것

| 위치 | 무엇 |
|---|---|
| `packages:` 글로브 | 대상 레포의 워크스페이스 구조로. 모노레포가 아니면 이 필드째 뺀다 |
| `allowBuilds:` 항목 | **jarvis 의 의존성이다. 그대로 쓰지 않는다.** 대상 레포에서 `pnpm approve-builds` 를 돌려 현재 락파일이 실제로 빌드하려는 것만 남긴다 |
| 감지 테스트 | **직접 써야 한다. 조각에 안 들어 있다.** 허용한 네이티브 모듈을 import 해서 최소 동작 하나를 시키는 테스트를, 그 모듈을 쓰는 패키지 안에 둔다. jarvis 판은 `packages/store/src/smoke.test.ts` 의 `it('can open an in-memory SQLite database (native module built)')` — `new Database(':memory:')` 로 `SELECT 1 + 1` 을 돌린다. 경로가 레포마다 다르므로 조각이 파일로 들고 있지 않다 |

## 안 써도 되는 조건

- **네이티브 애드온 의존성이 없다.** 순수 JS 의존성만이면 install 스크립트가 막혀도 잃는 게 없다. 이 조각의 이유가 통째로 사라진다
- **의존성이 prebuilt 바이너리만 받고 컴파일하지 않는다.** 확인 방법은 하나다 — 빈 허용 목록으로 clean install 하고 감지 테스트를 돌린다. 통과하면 이 방어선이 필요 없다
- **pnpm 을 안 쓴다.** npm/yarn 은 install 스크립트를 막지 않는다. 이 필드는 pnpm 것이고 다른 매니저는 읽지 않는다

`allowBuilds` 를 빼면 남는 건 평범한 `pnpm-workspace.yaml` 이고, 이 조각을 쓸 이유도 없다.
