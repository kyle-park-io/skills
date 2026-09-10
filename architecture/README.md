# architecture

코드베이스 구조를 파악하고, 그 이해를 문서·다이어그램으로 고정하는 스킬.

## 에이전트가 실패하는 지점

**grep으로 훑은 결과를 구조 이해라고 착각한다.** 심볼의 실제 참조 관계를 모른 채 "이 함수는 여기서만 쓰인다"고 단정하고, 그 위에 리팩터링을 얹는다. 필요한 건 코드를 더 잘 쓰는 능력이 아니라 **이미 있는 코드를 심볼 단위로 정확히 읽는 능력**이다.

## 붙일 도구

아래는 역할 카탈로그이며 `architecture@kyle-skills`의 의존성 목록이 아니다.
Claude Code와 Codex의 카탈로그 이름은 일대일로 대응하지 않으므로 각 하네스에서
설치 전에 다시 확인한다.

| 도구 | 역할 |
|---|---|
| `serena` | 시맨틱 코드 분석 MCP. 심볼 단위 이해·리팩터링 (oraios/serena, 29K) |
| `typescript-lsp` / `pyright-lsp` / `gopls-lsp` | 언어 서버 직결. 정의 이동·참조 찾기를 추측이 아닌 사실로 |
| `sourcegraph` | 레포 여러 개 걸친 참조 추적 |
| `code-modernization` | 레거시 해체를 preflight → assess → 실행 구조로 |
| [`tt-a1i/archify`](https://github.com/tt-a1i/archify) | 아키텍처·시퀀스·데이터플로우 다이어그램 (2026-09 1주차 스타 증가 1위) |

## 현재 상태

이 도메인의 `skills/`는 아직 비어 있다. 현재 플러그인을 설치해도 아키텍처
스킬이나 위 도구가 함께 설치되지는 않는다.

## 여기 넣을 스킬 후보

- `codebase-mapping`: 새 레포 진입 시 경계·의존성·진입점을 찾는 순서
- `adr-writing`: 결정 기록 포맷과 언제 남길지의 기준
- `diagram-first`: 코드 쓰기 전 데이터 흐름을 먼저 그리게 강제
- `boundary-review`: 모듈 경계가 새는지 판별하는 체크리스트

## 설치

```bash
# Claude Code
claude plugin install architecture@kyle-skills

# Codex
codex plugin add architecture@kyle-skills
```

스킬은 `architecture/skills/` 아래에 둔다.
