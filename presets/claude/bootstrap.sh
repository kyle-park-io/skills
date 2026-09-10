#!/usr/bin/env bash
# Claude Code 유저 스코프를 이 레포의 프리셋으로 맞춘다.
#
# 왜 있는가
#   Claude 셋업은 선언적 JSON 병합이라 스크립트 없이도 되는 것처럼 보인다.
#   유저 스코프만 보면 맞다. 병합으로 안 되는 단계가 둘 있다.
#
#   훅 복사가 하나다. 파일 시스템 작업이고, 하필 그것이 병렬 실행 비용
#   게이트다. 손에 맡긴 결과가 2026-09-09 이다. 게이트를 레포에 만들어 두고,
#   게이트가 없는 머신에서 Opus 세션 42개를 띄워 사용량 한도를 태웠다.
#
#   프로젝트 스코프가 켜는 플러그인의 캐시 설치가 나머지 하나다. 유저 캐시에
#   없는 플러그인을 프로젝트 설정이 켜면 세션 시작 때 로드 에러로 떨어진다.
#   `skills` 레포가 `skill-authoring` 으로 그 상태였다.
#
#   Serena 설정은 아예 다른 파일에 산다. 병합의 사정거리 밖이라 따로 만진다.
#
# 순서가 중요하다
#   훅 파일을 먼저 복사하고 설정을 나중에 병합한다. 반대로 하면 settings.json 이
#   없는 스크립트를 가리키는 구간이 생기고, 그 사이 모든 Bash 호출이 그것을
#   실행하려 든다. 부분 적용이 아무것도 안 한 것보다 나쁜 유일한 지점이다.
#
#   캐시 설치도 병합보다 앞이다. `claude plugin install` 은 설치한 플러그인을
#   유저 스코프에서 켜고 나간다. 병합이 뒤에 와야 프리셋의 `false` 가 남는다.

set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/../.." && pwd)
claude_home=${CLAUDE_CONFIG_DIR:-"$HOME/.claude"}
settings="$claude_home/settings.json"

cd "$repo_root"

for dependency in python3 jq claude; do
  command -v "$dependency" >/dev/null || {
    echo "필요한 명령이 없다: $dependency" >&2
    exit 1
  }
done

# 1. 훅 스크립트를 먼저 복사한다.
mkdir -p "$claude_home/hooks"
install -m 755 presets/user/hooks/fanout-cost-gate.sh "$claude_home/hooks/"
echo "훅 설치: $claude_home/hooks/fanout-cost-gate.sh"

# 2. 프로젝트 스코프가 켜는 플러그인을 유저 캐시에 깐다.
#
#    유저 스코프에서 켜는 플러그인은 병합만으로 설치된다. 프로젝트 스코프는
#    그렇지 않다. Codex 가 `codex plugin add` 로 메우는 자리와 같다.
#    이미 있는 것은 건너뛴다. `claude plugin install` 은 멱등하지만 매번 유저
#    스코프를 `true` 로 되돌려 놓아서, 그냥 돌리면 3단계가 매 실행마다 다섯 줄을
#    `true -> false` 로 찍고 백업을 남긴다. 바뀐 것만 찍혀야 출력이 검증이 된다.
echo
echo "캐시 설치"
claude plugin marketplace add kyle-park-io/skills >/dev/null
installed=$(claude plugin list --json | jq -r '.[] | select(.scope == "user") | .id')
for plugin in \
  "backend@kyle-skills" \
  "dashboard@kyle-skills" \
  "frontend@kyle-skills" \
  "infra@kyle-skills" \
  "skill-authoring@kyle-skills"
do
  if printf '%s\n' "$installed" | grep -qxF "$plugin"; then
    echo "  $plugin (이미 있음)"
    continue
  fi
  claude plugin install "$plugin" >/dev/null
  echo "  $plugin 설치"
done

# 3. 설정을 병합한다. 실제로 바뀔 때만 백업이 남는다.
#
#    2단계가 켜 둔 도메인 플러그인이 여기서 프리셋의 `false` 로 되돌아간다.
echo
echo "설정 병합: $settings"
python3 "$script_dir/merge-settings.py" presets/user/settings.json "$settings" \
  --backup-dir "$claude_home/backups"

# 4. Serena 가 여는 창을 끈다.
#
#    `~/.serena/serena_config.yml` 은 Claude 설정이 아니라 Serena 자신의 설정이라
#    병합으로 닿지 않는다. 끄지 않으면 세션을 적재할 때마다 브라우저 탭이 열린다.
echo
echo "Serena 설정"
python3 "$script_dir/serena-config.py" --backup-dir "$claude_home/backups"

# 5. 값을 채워야 하는 env 를 알린다.
#
#    비어 있어도 서버가 뜨는 것과 뜨지 못하는 것을 구분해서 적는다. 둘을 같은
#    말투로 경고하면 진짜 죽은 쪽이 묻힌다.
if [ -z "$(jq -r '.env.CONTEXT7_API_KEY // ""' "$settings")" ]; then
  echo
  echo "알림: CONTEXT7_API_KEY 가 비어 있다. 익명으로 연결되고 rate limit 만 낮다."
  echo "  https://context7.com/dashboard 에서 발급해 $settings 에 넣는다."
fi

if [ -z "$(jq -r '.env.GITHUB_PERSONAL_ACCESS_TOKEN // ""' "$settings")" ]; then
  echo
  echo "경고: GITHUB_PERSONAL_ACCESS_TOKEN 이 비어 있다. github MCP 가 400 으로 죽는다."
  echo "  빈 Bearer 헤더가 나가기 때문이고, 이쪽은 context7 과 달리 빈 값을 받아주지 않는다."
  echo "  https://github.com/settings/tokens 에서 발급해 $settings 에 넣는다."
  echo "  붙이지 않을 거라면 enabledPlugins 의 github 을 false 로 내린다."
fi

# 6. 게이트가 실제로 서는지 확인한다.
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
