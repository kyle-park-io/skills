# skill-authoring

스킬 자체를 만들고 검증하는 법.

## 원칙

**스킬 작성은 프로세스 문서에 적용한 TDD다.** 실패 케이스를 먼저 잡고 문서를 고친다. 안 그러면 "읽으면 맞는 말인데 실제로는 발동 안 하는" 스킬이 쌓인다.

## 발동 정확도가 전부다

스킬이 안 뽑히는 이유는 대개 내용이 아니라 `description`이다.

- **트리거 상황을 구체적으로** 쓴다. "코드를 잘 짜게 도와줌"이 아니라 "마이그레이션을 작성하기 전에"
- **다른 스킬과 구별되게** 쓴다. description이 겹치면 둘 다 안 뽑힌다
- 애매하면 **측정한다.** 감으로 고치지 않는다. 다만 아래 함정을 먼저 읽는다

## 측정할 때 프록시를 재지 않는다

`skill-creator`의 트리거 eval 은 스킬을 실제로 설치하지 않는다. `.claude/commands/` 에 커맨드 파일을 심어 흉내낸다. **그 프록시는 실물 플러그인 스킬만큼 발동하지 않는다.**

`schema-review`를 같은 쿼리 20개(발동 10 / 무발동 10)로 Claude Code의
프록시와 실물 플러그인에서 쿼리당 3회씩 재봤다. 아래 숫자는 Codex 측정값이
아니다.

| | 프록시 | 실물 플러그인 |
|---|---|---|
| recall | 11% | **100%** |
| precision | 100% | 100% |
| 정확도 | 56% | **100%** |

프록시 기준으로는 "이 스킬은 사실상 안 뜬다"는 결론이 나왔다. 실물에서는 발동해야 할 10개가 전부 떴고(대부분 3/3, 7초 안에), 무발동이어야 할 10개는 전부 0/3 이었다. 프록시에서 0/3 이던 쿼리가 실물에서는 3/3 으로 뒤집힌다.

**그 수치는 스킬의 발동률이 아니라 프록시의 발동률이었다.** 이걸 모르고 description 을 고치면, 멀쩡한 스킬을 존재하지도 않는 문제에 맞춰 망가뜨린다. 실제로 이 사례에서 최적화 루프는 원본보다 나쁜 개선안을 세 번 제안했다.

프록시 기준 결과가 나쁘면 고치기 전에 실물로 대조한다.

```bash
python3 scripts/real-trigger-eval.py \
  --harness claude \
  --eval-set eval.json \
  --project <플러그인을 켜둔 레포> \
  --skill schema-review \
  --out result.json
```

Codex에서는 `--harness codex`를 쓴다. 이 경로는 `codex exec --json`에서
대상 `SKILL.md`를 실제로 읽은 명령을 관측한다. 명시 호출은 호스트가 본문을
선주입할 수 있으므로 description의 암시 발동 평가에는 넣지 않는다. 결과에는
하네스, 모델, 스킬 이름을 함께 기록해 서로 다른 환경의 숫자를 섞지 않는다.

측정 조건도 결과를 바꾼다.

- **빈 디렉터리에서 재지 않는다.** 스킬이 다룰 코드가 실제로 있는 레포에서 잰다
- **부정 쿼리는 근접 사례로 채운다.** "피보나치 함수 써줘"를 DB 스킬의 부정 케이스로 넣으면 아무것도 검증되지 않는다. 키워드가 겹치는데 발동하면 안 되는 것을 넣는다 (마이그레이션 스킬이라면 "마이그레이션 도구 뭐 쓸지 골라줘")
- **정확도만 보지 않는다.** 긍정과 부정이 반반이면 "한 번도 발동 안 함"이 정확히 50%를 준다. precision 과 recall 을 따로 본다

## 하네스 이식성

이 레포의 스킬은 Claude Code 와 Codex 양쪽에서 그대로 돈다. 조건은 하나다.

**스킬은 툴이 아니라 동작을 부른다.** "서브에이전트를 띄운다"는 양쪽에서 성립하지만 "Task 툴을 호출한다"는 Codex 에서 무의미하다. 하네스별로 스킬을 갈라 쓰고 싶어지면 본문이 너무 낮은 수준에서 쓰였다는 신호다.

셸 명령(`git`, `npm`, `terraform`)은 하네스가 아니라 시스템에 속하므로 그대로 쓴다.

하네스별로 다른 건 매니페스트뿐이고, 그건 `domains.json` 에서 생성된다. 스킬을 추가할 때 매니페스트를 건드릴 일은 없다.

## 붙일 도구

| 도구 | 가용성 | 역할 |
|---|---|---|
| `skill-creator` | Claude 공식 플러그인 / Codex 시스템 | 생성·개선과 기본 검증 |
| `superpowers:writing-skills` | 양쪽 Superpowers | 스킬 작성을 TDD로 |
| `plugin-dev` | Claude Code | 훅·MCP 통합·마켓플레이스 배포 7개 스킬. 묶어서 배포할 단계면 |
| `plugin-creator` | Codex 기본 제공 | 플러그인 골격과 로컬 마켓플레이스 구성 |
| `hookify` | Claude Code | 반복 실수를 훅으로 강제. 내장 `update-config`와 겹치니 둘 중 하나만 |

## 변환 도구

문서를 스킬로 바꿔야 할 때:

- [`virgiliojr94/book-to-skill`](https://github.com/virgiliojr94/book-to-skill): 기술서 PDF → 스킬
- [`yusufkaraaslan/Skill_Seekers`](https://github.com/yusufkaraaslan/Skill_Seekers): 문서 사이트·레포·PDF → 스킬
- [`agentskills/agentskills`](https://github.com/agentskills/agentskills): 스킬 포맷 스펙

## 안전

외부 스킬은 [`NVIDIA/SkillSpector`](https://github.com/NVIDIA/SkillSpector)로 스캔한 뒤에 넣는다. 루트 README의 절차 참조.

## 설치

이 도메인의 `skills/`는 아직 비어 있다. 지금은 양쪽에서 제공되는 `skill-creator`와
하네스별 플러그인 도구를 쓰며, 자체 규칙이 생긴 뒤 이 플러그인을 설치한다.

```bash
# Claude Code
claude plugin install skill-authoring@kyle-skills

# Codex
codex plugin add skill-authoring@kyle-skills
```

스킬은 `skill-authoring/skills/` 아래에 둔다.
