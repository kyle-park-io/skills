# frontend

UI 구현, 성능 진단, 브라우저 검증.

## 에이전트가 실패하는 지점

**2년 전 패턴을 쓴다.** 학습 시점에 굳은 API와 관례를 최신인 양 낸다. 그리고 "동작한다"에서 멈춘다. 느린 이유는 실측 없이 추측한다.

`playwright`는 "동작하나"를 보고, `chrome-devtools-mcp`는 "왜 느린가"를 본다. 둘은 대체재가 아니다.

## 붙일 도구

도구 이름은 하네스마다 같지 않다. 2026-09-10 현재 Codex 공식 카탈로그에서
직접 확인한 항목만 Codex로 표시했다.

| 도구 | 가용성 | 역할 |
|---|---|---|
| `frontend-design` | Claude Code | 템플릿 티 안 나는 UI 생성 |
| `frontend-design-premium` | Codex 공식 카탈로그 | 프론트엔드 디자인과 구현 |
| `playwright` | Claude Code 플러그인 / Codex는 프로젝트에 직접 구성 | 브라우저 자동화·E2E |
| `chrome-devtools-mcp` | Claude Code 플러그인 / Codex는 MCP로 직접 구성 | 성능 트레이스 기록·네트워크 분석 |
| `modern-web-guidance` | Claude Code | 최신 웹 베스트 프랙티스 주입 |
| `figma` | 양쪽 카탈로그 | 디자인 파일·컴포넌트·토큰 직접 읽기 |
| `superdesign` | 양쪽 카탈로그 | 코드베이스 읽고 시안 생성 |
| [`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 외부 OSS | UI/UX 판단 기준 주입 (올타임 84위) |

Codex 카탈로그는 갱신되므로 설치 전에 `codex plugin list`로 다시 확인한다.
같은 이름이 없다는 이유로 Claude 설정을 Codex에 그대로 옮기지 않는다.

## 현재 상태

이 도메인의 `skills/`는 아직 비어 있다. 아래 설치 명령은 배포 경로를 확인할
때만 의미가 있고, 현재 버전을 설치해도 프론트엔드 스킬은 추가되지 않는다.

## 여기 넣을 스킬 후보

- `perf-triage`: 느리다는 신고를 받았을 때 측정 순서 (추측 금지)
- `a11y-pass`: 머지 전 접근성 최소 검증
- `component-boundary`: 상태를 어디까지 끌어올릴지의 기준

## 설정 프리셋

이 도메인의 도구는 [`nextjs-vercel`](../presets/project/nextjs-vercel) 프리셋에 들어간다. 적용법은 [`presets/README.md`](../presets)를 본다.

## 설치

```bash
# Claude Code
claude plugin install frontend@kyle-skills

# Codex
codex plugin add frontend@kyle-skills
```

스킬은 `frontend/skills/` 아래에 둔다.
