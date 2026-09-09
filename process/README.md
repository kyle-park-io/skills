# process

작업 절차. superpowers가 덮지 못하는 내 고유 관례만 여기 둔다.

## 이미 덮여 있는 것

아래 목록은 Claude Code 환경에서 확인한 기준이다. `superpowers` 14개 스킬이 소프트웨어 작업의 4단계를 전부 덮는다. Codex에서는 현재 세션에 설치된 스킬을 따로 확인한다.

| 단계 | 스킬 |
|---|---|
| 설계 | `brainstorming` · `writing-plans` · `using-git-worktrees` · `using-superpowers` |
| 실행 | `executing-plans` · `subagent-driven-development` · `dispatching-parallel-agents` · `test-driven-development` |
| 검증 | `systematic-debugging` · `requesting-code-review` · `receiving-code-review` · `verification-before-completion` |
| 마무리·메타 | `finishing-a-development-branch` · `writing-skills` |

여기에 Claude Code 내장 `code-review` · `simplify` · `security-review` · `run`이 실행 도구로 붙는다.

내장 `code-review`와 `superpowers:requesting-code-review`는 **겹치지 않는다.** 전자는 diff를 직접 훑는 *실행 도구*, 후자는 리뷰어 서브에이전트를 *디스패치하는 절차*다.

## 보강할 것

| 도구 | 역할 |
|---|---|
| `claude-md-management` | CLAUDE.md 품질 감사 + 세션 학습 캡처 |
| `mattpocock-skills` | 스펙·티켓 분해, 도메인 모델링 (올타임 15위) |
| `claude-code-setup` | 레포를 분석해 필요한 훅·스킬·MCP를 역으로 추천 |
| `remember` | 대화를 계층형 로그로 압축, 세션 간 컨텍스트 유지 |

## 여기 넣을 스킬 후보

**superpowers와 겹치면 만들지 않는다.** 내 고유 관례만:

- `handoff-note`: 세션을 끊을 때 남기는 형식
- `repo-onboarding`: 내 레포들에서 반복되는 진입 순서

## 설치

```bash
# Claude Code
claude plugin install process@kyle-skills

# Codex
codex plugin add process@kyle-skills
```

스킬은 `process/skills/` 아래에 둔다.
