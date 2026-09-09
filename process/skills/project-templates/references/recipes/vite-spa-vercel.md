# vite-spa-vercel

Vite + React SPA 와 서버리스 함수를 한 Vercel 배포에 올리고, pnpm + Vitest 로 CI 를 도는 레포.

출처는 `mantle-kr-herald` 하나다. **레시피가 두 번째 레포를 만나기 전까지는 herald 의 구성을 적어둔 것에 지나지 않는다.** 두 번째 스택이 들어올 때 여기 뺄 것과 남길 것이 갈린다.

## 쓴다

| 조각 | 왜 |
|---|---|
| [`ci-pnpm-vitest`](../ci-pnpm-vitest) | pnpm + Vitest. `web/` 이 별도 tsconfig 를 가지므로 `typecheck:web` 스텝이 그대로 산다 |
| [`vercel-spa-api`](../vercel-spa-api) | `vercel deploy` CLI 로 배포하고, API 경로가 두 세그먼트를 넘는다. 두 조건 모두 참이라 rewrite 와 `.vercelignore` 앵커링이 필요하다 |

## 안 쓴다

| 조각 | 왜 |
|---|---|
| [`systemd-timer`](../systemd-timer) | **스택과 직교한다.** herald 는 이걸 쓰지만 Vercel 배포와는 무관하고, 내 머신에서 도는 파이프라인이 있을 때만 필요하다. 그런 게 없는 Vite SPA 는 이 조각을 안 본다 |

`systemd-timer` 가 여기 "안 쓴다"로 들어가 있는 게 이 레시피 파일의 존재 이유다. herald 를 그대로 베끼면 스케줄러가 따라오는데, 그건 herald 가 Vercel 앱이어서가 아니라 herald 가 번역 파이프라인을 돌려서다.

## 조각이 안 덮는 것

새 레포를 세울 때 이 레시피로 안 되는 것들. 조각으로 만들 근거가 아직 없어서 빠진 것이지 필요 없어서가 아니다.

- `check:pr-title` 스크립트 본체 (`ci-pnpm-vitest` 의 "바꿔야 할 것" 참조)
- `.vercelignore` 앵커링 테스트 (`vercel-spa-api` 의 "바꿔야 할 것" 참조)
- `tsconfig.json`, `vite.config.ts`, `vitest.config.ts`. 전부 스캐폴딩이 주는 것이라 관문 2 에서 떨어졌다
