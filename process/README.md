# process

작업 절차. superpowers가 덮지 못하는 내 고유 관례만 여기 둔다.

## 이미 덮여 있는 것

`superpowers` v6.3.0은 Claude Code와 Codex 공식 카탈로그에 같은 14개
스킬을 제공한다. 소프트웨어 작업의 4단계를 공통으로 덮으므로 이 도메인에는
그 절차를 복제하지 않는다. 다만 실제 설치 상태는 하네스마다 따로 확인한다.

| 단계 | 스킬 |
|---|---|
| 설계 | `brainstorming` · `writing-plans` · `using-git-worktrees` · `using-superpowers` |
| 실행 | `executing-plans` · `subagent-driven-development` · `dispatching-parallel-agents` · `test-driven-development` |
| 검증 | `systematic-debugging` · `requesting-code-review` · `receiving-code-review` · `verification-before-completion` |
| 마무리·메타 | `finishing-a-development-branch` · `writing-skills` |

여기에 Claude Code 내장 `code-review` · `simplify` · `security-review` · `run`이 실행 도구로 붙는다.

Codex에서는 시스템 스킬, `AGENTS.md`, 서브에이전트가 하네스 기본기로 붙는다.
`superpowers`가 명시한 병렬 실행 절차는 현재 도구 목록에 서브에이전트가 있을
때만 따른다. 설치 명령은 다음과 같다.

```bash
codex plugin add superpowers@openai-curated-remote
```

내장 `code-review`와 `superpowers:requesting-code-review`는 **겹치지 않는다.** 전자는 diff를 직접 훑는 *실행 도구*, 후자는 리뷰어 서브에이전트를 *디스패치하는 절차*다.

## 보강할 것

아래 이름은 Claude Code에서 확인한 카탈로그다. Codex에서는 `AGENTS.md`와
기본 스킬이 일부 역할을 맡으며, 같은 이름의 플러그인이 있다고 가정하지 않는다.

| 도구 | 역할 |
|---|---|
| `claude-md-management` | CLAUDE.md 품질 감사 + 세션 학습 캡처 |
| `mattpocock-skills` | 스펙·티켓 분해, 도메인 모델링 (올타임 15위) |
| `claude-code-setup` | 레포를 분석해 필요한 훅·스킬·MCP를 역으로 추천 |
| `remember` | 대화를 계층형 로그로 압축, 세션 간 컨텍스트 유지 |

## 들어 있는 스킬

| 스킬 | 언제 |
|---|---|
| [`project-templates`](skills/project-templates) | 성숙한 레포에서 CI·배포 설정을 근거와 함께 뽑아둘 때, 또는 새 레포에 그중 무엇을 넣을지 고를 때 |

`project-templates`의 조각은 `references/` 아래에 산다. **평소 컨텍스트 비용은 `description` 한 줄뿐이다.** `references/`는 읽기 전까지 안 들어오므로 조각이 늘어도 상주 비용은 그대로다.

`description`을 고치면 `scripts/real-trigger-eval.py`로 다시 잰다. 부정 쿼리는 `claude-code-setup`의 자동화 추천과 `superpowers:brainstorming` 쪽으로 채운다. 셋 다 "레포를 보고 무엇을 넣을지 정한다"로 들려서, 여기서 겹치는 것이 이 스킬의 주된 실패 방식이다.

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
