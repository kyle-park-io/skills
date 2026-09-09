# frontend

UI 구현, 성능 진단, 브라우저 검증.

## 에이전트가 실패하는 지점

**2년 전 패턴을 쓴다.** 학습 시점에 굳은 API와 관례를 최신인 양 낸다. 그리고 "동작한다"에서 멈춘다. 느린 이유는 실측 없이 추측한다.

`playwright`는 "동작하나"를 보고, `chrome-devtools-mcp`는 "왜 느린가"를 본다. 둘은 대체재가 아니다.

## 붙일 도구

| 도구 | 역할 |
|---|---|
| `frontend-design` | 템플릿 티 안 나는 UI 생성 |
| `playwright` | 브라우저 자동화·E2E |
| `chrome-devtools-mcp` | 성능 트레이스 기록·네트워크 분석 |
| `modern-web-guidance` | 최신 웹 베스트 프랙티스 주입 |
| `figma` | 디자인 파일·컴포넌트·토큰 직접 읽기 |
| `superdesign` | 코드베이스 읽고 시안 생성 |
| [`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | UI/UX 판단 기준 주입 (올타임 84위) |

## 여기 넣을 스킬 후보

- `perf-triage`: 느리다는 신고를 받았을 때 측정 순서 (추측 금지)
- `a11y-pass`: 머지 전 접근성 최소 검증
- `component-boundary`: 상태를 어디까지 끌어올릴지의 기준

## 설정 프리셋

이 도메인의 도구는 [`nextjs-vercel`](../presets/project/nextjs-vercel) 프리셋에 들어간다. 적용법은 [`presets/README.md`](../presets)를 본다.
