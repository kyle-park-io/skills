# skill-authoring

스킬 자체를 만들고 검증하는 법.

## 원칙

**스킬 작성은 프로세스 문서에 적용한 TDD다.** 실패 케이스를 먼저 잡고 문서를 고친다. 안 그러면 "읽으면 맞는 말인데 실제로는 발동 안 하는" 스킬이 쌓인다.

## 발동 정확도가 전부다

스킬이 안 뽑히는 이유는 대개 내용이 아니라 `description`이다.

- **트리거 상황을 구체적으로** 쓴다. "코드를 잘 짜게 도와줌"이 아니라 "마이그레이션을 작성하기 전에"
- **다른 스킬과 구별되게** 쓴다. description이 겹치면 둘 다 안 뽑힌다
- 애매하면 `skill-creator`의 **eval 실행 + 변동성 분석**으로 측정한다. 감으로 고치지 않는다

## 붙일 도구

| 도구 | 역할 |
|---|---|
| `skill-creator` | 생성·개선 + **eval 실행 · 변동성 분석 · description 최적화** |
| `superpowers:writing-skills` | 스킬 작성을 TDD로 |
| `plugin-dev` | 훅·MCP 통합·마켓플레이스 배포 7개 스킬. 묶어서 배포할 단계면 |
| `hookify` | 반복 실수를 훅으로 강제. 내장 `update-config`와 겹치니 둘 중 하나만 |

## 변환 도구

문서를 스킬로 바꿔야 할 때:

- [`virgiliojr94/book-to-skill`](https://github.com/virgiliojr94/book-to-skill): 기술서 PDF → 스킬
- [`yusufkaraaslan/Skill_Seekers`](https://github.com/yusufkaraaslan/Skill_Seekers): 문서 사이트·레포·PDF → 스킬
- [`agentskills/agentskills`](https://github.com/agentskills/agentskills): 스킬 포맷 스펙

## 안전

외부 스킬은 [`NVIDIA/SkillSpector`](https://github.com/NVIDIA/SkillSpector)로 스캔한 뒤에 넣는다. 루트 README의 절차 참조.

## 설치

```bash
claude plugin install skill-authoring@kyle-skills
```

스킬은 `skill-authoring/skills/` 아래에 둔다.
