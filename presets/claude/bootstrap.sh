#!/usr/bin/env bash
# Claude Code 유저 스코프를 이 레포의 프리셋으로 맞춘다.
#
# 왜 있는가
#   Codex 와 달리 Claude 셋업은 선언적 JSON 병합이라 스크립트 없이도 되는 것처럼
#   보인다. 실제로 마켓플레이스와 플러그인은 그렇다. 그렇지 않은 단계가 훅
#   복사 하나뿐인데, 하필 그것이 병렬 실행 비용 게이트다.
#
#   그 한 단계를 손에 맡긴 결과가 2026-09-09 이다. 게이트를 레포에 만들어 두고,
#   게이트가 없는 머신에서 Opus 세션 42개를 띄워 사용량 한도를 태웠다.
#
# 순서가 중요하다
#   훅 파일을 먼저 복사하고 설정을 나중에 병합한다. 반대로 하면 settings.json 이
#   없는 스크립트를 가리키는 구간이 생기고, 그 사이 모든 Bash 호출이 그것을
#   실행하려 든다. 부분 적용이 아무것도 안 한 것보다 나쁜 유일한 지점이다.

set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/../.." && pwd)
claude_home=${CLAUDE_CONFIG_DIR:-"$HOME/.claude"}
settings="$claude_home/settings.json"

cd "$repo_root"

for dependency in python3 jq; do
  command -v "$dependency" >/dev/null || {
    echo "필요한 명령이 없다: $dependency" >&2
    exit 1
  }
done

# 1. 훅 스크립트를 먼저 복사한다.
mkdir -p "$claude_home/hooks"
install -m 755 presets/user/hooks/fanout-cost-gate.sh "$claude_home/hooks/"
echo "훅 설치: $claude_home/hooks/fanout-cost-gate.sh"

# 2. 설정을 병합한다. 실제로 바뀔 때만 백업이 남는다.
echo "설정 병합: $settings"
python3 "$script_dir/merge-settings.py" presets/user/settings.json "$settings" \
  --backup-dir "$claude_home/backups"

# 3. 값을 채워야 하는 env 를 알린다.
if [ -z "$(jq -r '.env.CONTEXT7_API_KEY // ""' "$settings")" ]; then
  echo
  echo "경고: CONTEXT7_API_KEY 가 비어 있다. 비워두면 401 이 난다."
  echo "  https://context7.com/dashboard 에서 발급해 $settings 에 넣는다."
fi

# 4. 게이트가 실제로 서는지 확인한다.
#
#    Codex bootstrap 이 plugin list 로 끝나는 것과 같은 이유다. 설치했다는 것과
#    동작한다는 것은 다르고, 이 훅은 동작하지 않아도 조용하다.
echo
echo "게이트 검증"

hook="$claude_home/hooks/fanout-cost-gate.sh"
eval_set=evals/project-templates.json
expected=$(( $(jq 'length' "$eval_set") * 3 ))
command_line="python3 scripts/real-trigger-eval.py --harness claude --eval-set $eval_set --skill project-templates --out /tmp/result.json"

# 훅은 fan-out 신호가 없으면 아무것도 출력하지 않고 빠진다. 그 경우를 빈 객체로
# 바꿔야 아래 jq 가 입력 없이 침묵하지 않는다.
probe() {
  output=$(jq -n --arg c "$1" '{tool_input: {command: $c}}' | "$hook")
  [ -n "$output" ] || output='{}'
  printf '%s' "$output"
}

denied=$(probe "$command_line" | jq -r '.hookSpecificOutput.permissionDecision // ""')
if [ "$denied" != "deny" ]; then
  echo "실패: 세션 ${expected}개짜리 명령이 차단되지 않았다" >&2
  exit 1
fi
echo "  차단됨: 세션 ${expected}개 (쿼리 $(jq 'length' "$eval_set") x 반복 3)"

allowed=$(probe "CLAUDE_FANOUT_ACK=$expected $command_line" \
  | jq -r '.hookSpecificOutput.permissionDecision // "allow"')
if [ "$allowed" != "allow" ]; then
  echo "실패: CLAUDE_FANOUT_ACK=$expected 가 통과되지 않았다" >&2
  exit 1
fi
echo "  통과됨: CLAUDE_FANOUT_ACK=$expected"

untouched=$(probe "git status" | jq -r '.hookSpecificOutput.permissionDecision // "allow"')
if [ "$untouched" != "allow" ]; then
  echo "실패: fan-out 과 무관한 명령이 차단됐다" >&2
  exit 1
fi
echo "  무관한 명령은 통과"

echo
echo "완료. 새 대화를 열어야 플러그인 목록이 다시 적재된다."
