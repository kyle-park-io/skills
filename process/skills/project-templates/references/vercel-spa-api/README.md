# vercel-spa-api

**복사형.** 단, `vercel.json` 의 값은 대부분 바꿔야 한다.

정적 SPA 와 서버리스 함수를 한 Vercel 배포에 올리는 레포용. `.vercelignore` 가 이 조각의 본체이고 `vercel.json` 은 라우팅 함정 하나 때문에 딸려 있다.

## 출처

`mantle-kr-herald`

| 커밋 | 무엇 |
|---|---|
| `414d422` | 공유 라우트 테이블 위에 함수로 API 서빙 |
| `eec45cf` | 함수 번들링 수정 (`ERR_MODULE_NOT_FOUND`) |
| `63b0d2e` | 함수 리전 고정 |
| `174ddbd` | 모든 깊이의 `/api` 경로를 함수로 (rewrite 추가) |

리전과 프리뷰 배포의 근거는 커밋이 아니라 `docs/ko/setup/vercel.md` 와 `docs/ko/deploy.md` 에 있다. **커밋 메시지만 보면 관문 1 에서 떨어뜨릴 뻔했다.** 근거를 찾을 때 `docs/` 도 같이 본다.

## 왜 있는가

### 이 배포는 조용히 죽는다

세 사고가 전부 같은 모양이었다. **정적 레이어는 200 을 계속 돌려주고 API 만 죽는다.** SPA 는 엣지 404 와 빈 목록을 구분하지 못하므로 셸을 렌더하고 "항목이 없습니다"를 띄운다. 밖에서 보면 배포가 멀쩡해 보인다.

그래서 이 조각의 모든 항목은 "배포가 성공한 것처럼 보이는데 안 도는" 경우를 막는다. 배포 실패를 막는 게 아니다.

### `.vercelignore` 의 앵커링

`vercel deploy` 는 커밋이 아니라 **로컬 디렉터리를 업로드한다.** 두 가지가 여기서 나온다.

**첫째, 시크릿이 딸려 올라간다.** 워킹 트리에 있는 gitignore 된 `.env` 나 서비스 계정 키는 `git status` 에 안 보인다. CLI 가 `.gitignore` 로 폴백하는지 여부에 배포 안전을 걸지 않는다. 여기에 명시한다.

**둘째, 앵커링을 빼면 필요한 것까지 지운다.** gitignore 문법에서 `translation/` 은 **모든 깊이**의 그 이름 디렉터리를 잡는다. herald 의 첫 버전이 앵커 없이 쓰였고, 그게 `src/domain/translation/` 과 `src/domain/conversion/` 을 조용히 제외했다. 번들러가 인라인할 게 없어진 함수가 배포는 "성공"했고 모든 API 요청이 이걸로 죽었다.

```
ERR_MODULE_NOT_FOUND: Cannot find module '/var/task/src/adapters/db/createDb'
```

`/deploy/` 도 같은 이유로 앵커돼 있다. 앵커를 빼면 `src/deploy/` 를 같이 잡는다.

### `vercel.json` 의 rewrite

`api/[...path].ts` 는 catch-all 처럼 보이지만 **Vercel 의 zero-config 빌더는 그렇게 읽지 않는다.** `...path` 라는 이름의 단일 동적 세그먼트로 문자 그대로 취급한다. 생성되는 라우팅 테이블은 이렇다.

```
{ "src": "^/api/([^/]+)$", "dest": "/api/[...path]?...path=$1" }   세그먼트 하나
{ "src": "^/api(/.*)?$",   "status": 404 }                        나머지 전부
```

herald 는 클라이언트가 네 단계 깊이(`/api/outlets/:itemId/:type/:outletId`)까지 요청했으므로 대부분의 화면이 도달 불가였다. `/api/status` 는 401 로 함수에 닿고 `/api/publish/state` 는 404 로 엣지에서 끊겼다.

**배포 없이 확인하는 법이 있다.** `npx vercel build` 가 `.vercel/output/config.json` 에 실제 라우팅 테이블을 쓴다.

### `git.deploymentEnabled: false`

프리뷰 배포를 끈다. 얻는 것은 배포 통제가 아니라 **오리진이 정확히 하나가 되는 것**이다.

프리뷰가 켜져 있으면 브랜치마다 다른 오리진이 생긴다. 그러면 CSRF 허용 오리진, 쿠키 도메인, CORS 를 전부 "여러 개일 수 있다"는 전제로 써야 한다. 프리뷰를 끄면 그 전제가 사라지고 설정이 값 하나로 줄어든다.

배포는 `vercel deploy --prod` 로 명시적으로 한다. 그래서 이 조각의 `.vercelignore` 가 필요해진다. 둘은 같은 결정의 양면이다.

**더 강한 상태가 있다.** Git 저장소를 프로젝트에 아예 연결하지 않으면 (`link` 가 `null`) push 로 생기는 배포 자체가 존재하지 않는다. `deploymentEnabled: false` 는 그것보다 약하다.

### `regions`

데이터베이스와 함수가 다른 대륙에 있으면 **화면 하나를 그릴 때마다 쿼리가 그만큼 왕복한다.** herald 는 한국에서 쓰므로 싱가포르(`sin1`)로 고정했다.

**여기 함정이 있다.** 함수 리전은 나중에 바꿀 수 있지만 **데이터베이스 리전은 생성 후 변경할 수 없는 경우가 많다** (Neon 이 그렇다). 그리고 Vercel 마켓플레이스의 Neon 이 주는 아시아 리전은 `sin1` 과 시드니뿐이었다. 즉 이 값은 배포 설정이 아니라 **데이터베이스를 만들기 전에 내려야 하는 결정**이다.

## 바꿔야 할 것

| 위치 | 무엇 |
|---|---|
| `.vercelignore` 의 `/deploy/`, `/output/` | 대상 레포에 없으면 지운다. **있는데 이름이 다르면 반드시 앵커해서 추가한다** |
| `.vercelignore` 의 `/web/dist/`, `/web/tests/` | 실제 SPA 디렉터리 이름으로 |
| `buildCommand`, `outputDirectory` | 대상 레포의 빌드 스크립트와 출력 경로 |
| `regions` | 데이터베이스와 같은 리전으로. **데이터베이스를 만들기 전에 정한다** (위 참조) |
| `rewrites` 의 `destination` | 실제 함수 파일 경로로 |
| 앵커링 테스트 | herald 는 `tests/deploy/vercelignore.test.ts` 로 앵커 없는 디렉터리 패턴을 빌드에서 떨군다. **조각에 안 들어 있다.** 직접 써야 한다 |

마지막 항목이 중요하다. 앵커링은 사람이 기억할 수 있는 규칙이 아니다. herald 도 한 번 당하고 나서 테스트로 못박았다.

## 안 써도 되는 조건

- **Git 연동 배포만 쓴다.** `vercel deploy` CLI 를 안 쓰면 워킹 트리 업로드 문제가 없다. `.vercelignore` 대신 `.gitignore` 가 이미 답이다. 단 `git.deploymentEnabled: false` 도 같이 뺀다
- **API 가 없다.** 순수 정적 배포면 rewrite 도 함수 번들링 문제도 없다. `.vercelignore` 의 시크릿 항목만 가져간다
- **API 경로가 한 세그먼트뿐이다.** `/api/status` 만 있고 그 아래가 없으면 zero-config 라우팅으로 충분하다. rewrite 를 뺀다
- **Vercel 이 아니다.** 이 조각은 전부 Vercel 의 zero-config 빌더 동작에 의존한다. 다른 플랫폼에는 아무것도 이식되지 않는다
