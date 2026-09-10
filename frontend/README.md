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
| `frontend-design-premium` | Codex 전역 카탈로그 | 프론트엔드 디자인과 구현 |
| `playwright` | Claude Code 플러그인 / Codex는 프로젝트에 직접 구성 | 브라우저 자동화·E2E |
| `chrome-devtools-mcp` | Claude Code 플러그인 / Codex는 MCP로 직접 구성 | 성능 트레이스 기록·네트워크 분석 |
| `modern-web-guidance` | Claude Code | 최신 웹 베스트 프랙티스 주입 |
| `figma` | 양쪽 카탈로그, Codex는 전역 | 디자인 파일·컴포넌트·토큰 직접 읽기 |
| `superdesign` | 양쪽 카탈로그, Codex는 전역 | 코드베이스 읽고 시안 생성 |
| [`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 외부 OSS | UI/UX 판단 기준 주입 (올타임 84위) |

Codex 카탈로그는 갱신되므로 설치 전에 `codex plugin list`로 다시 확인한다.
같은 이름이 없다는 이유로 Claude 설정을 Codex에 그대로 옮기지 않는다.
현재 원격 카탈로그 항목은 프로젝트 `.codex/config.toml`로 범위를 줄일 수 있는
로컬 마켓플레이스 플러그인과 다르다. 따라서 전역 설치는 실제로 여러 레포에서
쓸 때만 하고, 프로젝트 격리가 필요한 스킬은 `.agents/skills/`, 외부 연결은
프로젝트 MCP, 브라우저 검증기는 프로젝트 의존성으로 둔다.

2026-09-10 카탈로그 기준 번들 스킬은 `frontend-design-premium` 2개,
`superdesign` 1개, `figma` 12개, `vercel` 54개다. 넷을 전부 설치하면 프론트와
무관한 세션에도 후보 69개가 늘어나므로 기본 구성에는 넣지 않는다.

## 현재 상태

| 스킬 | 맡는 판단 |
|---|---|
| `perf-triage` | 느리다는 신고를 재현하고 수정 전후를 같은 지표로 측정 |
| `a11y-pass` | 자동 검사와 키보드·포커스·상태 검증을 함께 수행 |
| `component-boundary` | 변경 이유와 상태 소유권으로 컴포넌트 경계를 결정 |

## 설정 프리셋

이 도메인의 도구는 [`nextjs-vercel`](../presets/project/nextjs-vercel) 프리셋에 들어간다. 적용법은 [`presets/README.md`](../presets)를 본다.

## 설치

```bash
# Claude Code
claude plugin install frontend@kyle-skills

# Codex: 사용자 캐시는 한 번 준비하고 프로젝트 설정을 복사한다
bash presets/codex/bootstrap.sh
cp -r presets/project/nextjs-vercel/.codex <대상 레포>/
```

스킬은 `frontend/skills/` 아래에 둔다.
