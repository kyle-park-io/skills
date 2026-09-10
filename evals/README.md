# evals

`scripts/real-trigger-eval.py` 가 먹는 트리거 쿼리 셋. 스킬 하나에 파일 하나.

## 왜 여기인가

**스킬 폴더 안에 두지 않는다.** 도메인 폴더는 통째로 플러그인 페이로드가 되므로, 거기 넣으면 스킬을 설치한 사람에게 아무 쓸모없는 파일이 따라간다. 설정 파일을 도메인에 두지 않는 것과 같은 이유다.

`presets/` 와 같은 성격이다. 이 레포를 클론한 사람, 즉 스킬을 **고치는** 사람만 쓴다.

**이 디렉터리가 없어서 이미 하나를 잃었다.** `a29fa11` 이 `schema-review` 를 20 쿼리로 측정했지만 커밋에는 스크립트만 들어갔다. 숫자는 커밋 메시지에 남고 쿼리는 사라졌으므로, 그 스킬을 다시 재려면 셋을 처음부터 다시 짜야 한다.

## 형식

```json
[
  {"query": "...", "should_trigger": true},
  {"query": "...", "should_trigger": false}
]
```

양성과 음성을 비슷한 수로 섞는다.

**음성 쿼리가 이 파일의 값을 정한다.** 명백히 무관한 질문은 아무것도 검증하지 않는다. 음성은 **이웃 스킬로 가야 맞는 질문**으로 채운다. 어느 스킬과 헷갈릴지를 먼저 이름으로 떠올리고, 그쪽 상황을 쿼리로 쓴다.

`project-templates` 의 음성 7개가 그렇게 만들어졌다. `claude-code-setup` 의 자동화 추천, `superpowers:brainstorming` 의 새 기능 설계, `systematic-debugging` 의 CI 고장, `claude-md-management`, `architecture`. 다섯 다 "레포를 보고 무엇을 넣을지 정한다" 로 들린다.

## 돌리는 법

```bash
python3 scripts/real-trigger-eval.py \
    --harness claude \
    --eval-set evals/<스킬>.json \
    --project <플러그인을 켜둔 레포> \
    --skill <스킬 이름> \
    --out /tmp/result.json
```

Codex를 잴 때는 `--harness codex`를 쓴다. 모델을 생략하면 현재 Codex 설정값을
사용한다. Codex는 암시 발동 뒤 실행한 `SKILL.md` 읽기 명령을 JSONL에서
관측한다. `$skill-name` 같은 명시 호출은 호스트가 본문을 미리 넣어 읽기 이벤트가
없을 수 있으므로 이 평가의 대상이 아니다.

**비용을 먼저 본다.** 쿼리 수 곱하기 `--runs` 만큼 독립 세션이 뜬다. Claude
Code에서는 `fanout-cost-gate` 훅이 그 수를 계산해 막으므로,
`CLAUDE_FANOUT_ACK=<세션 수>` 없이는 실행되지 않는다. Codex에는 이 Claude
훅이 적용되지 않으므로 실행자가 같은 계산을 직접 확인한다. 근거는
[`../presets/README.md`](../presets/README.md#병렬-실행-비용-훅).

## 언제 돌리나

**새 스킬마다 돌리지 않는다.** 진단이지 관문이 아니다. 기준은 [`../AGENTS.md`](../AGENTS.md#스킬을-추가하기-전에-통과할-것).

## 측정 기록

| 스킬 | 날짜 | 하네스 | 모델 | 쿼리 | 반복 | accuracy | precision | recall |
|---|---|---|---|---|---|---|---|---|
| `project-templates` | 2026-09-09 | Claude Code | `claude-opus-5` | 14 | 3 | 1.0 | 1.0 | 1.0 |
| `schema-review` | 2026-09-09 | Claude Code | `claude-opus-5` | 20 | 3 | 1.0 | - | 1.0 |

2026-09-10에 Codex CLI 0.153.4의 현재 설정 모델로 `project-templates` 양성
쿼리 하나를 1회 실행해 새 감지 경로가 실제 `SKILL.md` 로드를 잡는 것까지
확인했다. 평가 세트 전체를 돌린 결과가 아니므로 위 정확도 표에는 넣지 않는다.

`project-templates` 는 **경계에 걸린 쿼리가 하나도 없었다.** 양성 7개가 전부 3/3, 음성 7개가 전부 0/3 이다. 1/3 이나 2/3 이 나오는 쿼리가 `description` 의 애매한 표현을 가리키는데, 그게 없었다.

`schema-review` 의 숫자는 `a29fa11` 커밋 메시지에서 옮겨왔다. 셋이 남아 있지 않아 재현할 수 없다.

**두 번 다 만점이다.** 정확도를 만든 것은 측정이 아니라 `description` 에 "이럴 때는 쓰지 않는다" 를 쓴 쪽이고, 측정은 그게 통했다는 것을 확인해줬을 뿐이다.
