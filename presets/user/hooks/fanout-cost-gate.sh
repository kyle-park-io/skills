#!/usr/bin/env bash
# 병렬 Claude 세션을 띄우는 Bash 명령을 가로채 세션 수를 계산하고, 그 수를
# 사용자에게 띄운 뒤 명시적 확인이 없으면 실행을 막는다.
#
# 왜 있는가
#   2026-09-09 에 트리거 eval 을 14 쿼리 x 3회로 백그라운드 실행했고, 그것이
#   Opus 세션 42개, 에이전트 작업 113분이 되어 사용량 한도를 태웠다. 대화
#   컨텍스트는 싸다 (그 세션 전체가 178k / 1M). 비싼 것은 세션을 새로 여는
#   일이고, 각 세션이 자기 시스템 프롬프트를 새로 싣는다. 그 수는 명령을 읽으면
#   실행 전에 계산된다.
#
# 왜 deny 인가
#   permissionDecision "ask" 는 권한 프롬프트를 거치는데, bypassPermissions
#   모드에서는 그 프롬프트가 건너뛰어질 수 있다. 이 규칙은 모드와 무관하게
#   서야 하므로 deny 로 막고 확인 토큰으로 연다.
#
# 통과시키는 법
#   CLAUDE_FANOUT_ACK=<세션 수> 를 명령 앞에 붙인다. 숫자가 계산값과 정확히
#   일치해야 한다. 즉 실행하려면 그 수를 먼저 알아야 하고, deny 메시지가 그
#   수를 알려주므로 한 번은 사용자 눈앞을 지나간다.

set -uo pipefail

payload=$(cat 2>/dev/null) || exit 0
cmd=$(printf '%s' "$payload" | jq -r '.tool_input.command // ""' 2>/dev/null) || exit 0
[ -n "$cmd" ] || exit 0

# fan-out 신호가 전혀 없으면 조용히 통과한다. 이 훅은 모든 Bash 호출마다 돌므로
# 여기서 대부분이 걸러져야 한다.
printf '%s' "$cmd" \
  | grep -qE 'real-trigger-eval|claude[[:space:]]+(-p|--print)([[:space:]]|$)' || exit 0

is_eval=0
printf '%s' "$cmd" | grep -q 'real-trigger-eval' && is_eval=1

sessions=0
queries=0
runs=0

if [ "$is_eval" = 1 ]; then
  evalset=$(printf '%s' "$cmd" | sed -nE 's/.*--eval-set[= ]+([^[:space:]]+).*/\1/p' | tail -1)
  # eval-set 파일이 실제로 있을 때만 센다. 없으면 그 명령은 argparse 나 json.load
  # 에서 죽으므로 세션을 하나도 띄우지 않는다. 문서나 커밋 메시지에 이 명령을
  # 적는 경우가 여기 걸리는데, 그때 막으면 순수한 오탐이다.
  if [ -n "$evalset" ] && [ -f "$evalset" ]; then
    n=$(jq 'length' "$evalset" 2>/dev/null)
    case "$n" in ''|*[!0-9]*) n=0 ;; *) queries=$n ;; esac
    # 스크립트의 argparse 기본값이 3 이다. 여기서 1 로 잡으면 과소 계산한다.
    runs=$(printf '%s' "$cmd" | grep -oE -- '--runs[= ]+[0-9]+' | grep -oE '[0-9]+' | tail -1)
    runs=${runs:-3}
    sessions=$(( queries * runs ))
  fi
fi

# 명령 하나에 여러 번 박힌 직접 호출도 센다
occurrences=$(printf '%s' "$cmd" | grep -oE 'claude[[:space:]]+(-p|--print)' | wc -l | tr -d ' ')
[ "$occurrences" -gt "$sessions" ] && sessions=$occurrences

# 세션 두 개 이하는 통과시킨다. 한 번 물어보는 비용이 그 실행보다 비싸다.
[ "$sessions" -le 2 ] && exit 0

model=$(printf '%s' "$cmd" | sed -nE 's/.*--model[= ]+([^[:space:]]+).*/\1/p' | tail -1)
[ -n "$model" ] || model="기본값"

if [ "$sessions" = "$occurrences" ]; then
  detail="직접 호출 ${occurrences}회"
else
  detail="쿼리 ${queries} x 반복 ${runs}"
fi

ack=$(printf '%s' "$cmd" | sed -nE 's/.*CLAUDE_FANOUT_ACK=([0-9]+).*/\1/p' | tail -1)

if [ "$ack" = "$sessions" ]; then
  jq -n --arg s "$sessions" --arg m "$model" \
    '{systemMessage: ("확인된 병렬 실행: 독립 Claude 세션 " + $s + "개, 모델 " + $m)}'
  exit 0
fi

reason="이 명령은 독립 Claude 세션 ${sessions}개를 띄웁니다 (${detail}, 모델 ${model}).

세션 하나하나가 자기 시스템 프롬프트를 새로 싣고 대상 레포를 탐색합니다. 대화
컨텍스트가 아니라 이쪽이 사용량 한도를 태웁니다.

실행하기 전에 사용자에게 이 수를 말하고 허락을 받으십시오. 더 싼 방법이 있는지
먼저 검토하십시오 (반복 횟수 줄이기, 더 싼 모델로 훑기, 더 작은 대상 레포).

허락을 받았다면 명령 앞에 CLAUDE_FANOUT_ACK=${sessions} 를 붙여 다시 실행합니다."

jq -n --arg r "$reason" --arg s "$sessions" --arg m "$model" \
  '{systemMessage: ("차단됨: 이 명령은 Claude 세션 " + $s + "개를 띄웁니다 (모델 " + $m + "). 비용을 확인받아야 실행됩니다."),
    hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'
exit 0
