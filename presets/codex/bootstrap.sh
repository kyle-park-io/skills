#!/usr/bin/env bash
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/../.." && pwd)
codex_home=${CODEX_HOME:-"$HOME/.codex"}
codex_config=$codex_home/config.toml

cd "$repo_root"

# 줄표 차단 훅. Claude 부트스트랩과 같은 원본 스크립트를 쓴다.
#
# 훅 파일을 먼저 두고 hooks.json 을 나중에 병합한다. 반대로 하면 hooks.json 이
# 없는 스크립트를 가리키는 구간이 생긴다. 병합은 command 기준이라 이미 붙어 있는
# 다른 훅은 건드리지 않는다.
mkdir -p "$codex_home/hooks"
install -m 755 presets/user/hooks/no-dash-gate.py "$codex_home/hooks/"
echo "훅 설치: $codex_home/hooks/no-dash-gate.py"
python3 presets/claude/merge-settings.py presets/codex/hooks.json "$codex_home/hooks.json" \
  --backup-dir "$codex_home/backups"

if ! result=$(python3 presets/user/hooks/test-no-dash-gate.py "$codex_home/hooks/no-dash-gate.py" 2>&1); then
  printf '%s\n' "$result" >&2
  echo "실패: 줄표 차단 훅이 기대대로 막거나 통과시키지 않았다" >&2
  exit 1
fi
echo "  줄표 차단 훅 검증: $(printf '%s\n' "$result" | tail -1)"

# Codex 는 사용자가 신뢰하지 않은 훅을 실행하지 않는다. 신뢰는 훅 정의의 해시에
# 걸리므로 정의가 바뀌면 다시 신뢰해야 한다. 스크립트가 대신할 수 없는 단계다.
echo "알림: codex 를 열고 /hooks 에서 no-dash-gate 를 신뢰해야 실제로 동작한다."
echo

marketplace_present() {
  codex plugin marketplace list | awk -v name="$1" 'NR > 1 && $1 == name { found = 1 } END { exit !found }'
}

if ! marketplace_present "kyle-skills"; then
  codex plugin marketplace add kyle-park-io/skills
else
  codex plugin marketplace upgrade kyle-skills >/dev/null
fi

for plugin in \
  "superpowers@openai-curated-remote" \
  "process@kyle-skills"
do
  codex plugin add "$plugin" --json >/dev/null
done

for plugin in \
  "backend@kyle-skills" \
  "dashboard@kyle-skills" \
  "frontend@kyle-skills" \
  "infra@kyle-skills" \
  "skill-authoring@kyle-skills"
do
  codex plugin add "$plugin" --json >/dev/null
done

python3 "$script_dir/set-plugin-enabled.py" "$codex_config" true \
  "process@kyle-skills"
python3 "$script_dir/set-plugin-enabled.py" "$codex_config" false \
  "backend@kyle-skills" \
  "dashboard@kyle-skills" \
  "frontend@kyle-skills" \
  "infra@kyle-skills" \
  "skill-authoring@kyle-skills"

codex plugin marketplace list
codex plugin list | awk \
  '$1 == "superpowers@openai-curated-remote" || \
   $1 == "process@kyle-skills" || \
   $1 == "backend@kyle-skills" || \
   $1 == "dashboard@kyle-skills" || \
   $1 == "frontend@kyle-skills" || \
   $1 == "infra@kyle-skills" || \
   $1 == "skill-authoring@kyle-skills"'
