#!/usr/bin/env bash
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/../.." && pwd)
codex_config=${CODEX_HOME:-"$HOME/.codex"}/config.toml

cd "$repo_root"

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
  "infra@kyle-skills"
do
  codex plugin add "$plugin" --json >/dev/null
done

python3 "$script_dir/set-plugin-enabled.py" "$codex_config" true \
  "process@kyle-skills"
python3 "$script_dir/set-plugin-enabled.py" "$codex_config" false \
  "backend@kyle-skills" \
  "dashboard@kyle-skills" \
  "frontend@kyle-skills" \
  "infra@kyle-skills"

codex plugin marketplace list
codex plugin list | awk \
  '$1 == "superpowers@openai-curated-remote" || \
   $1 == "process@kyle-skills" || \
   $1 == "backend@kyle-skills" || \
   $1 == "dashboard@kyle-skills" || \
   $1 == "frontend@kyle-skills" || \
   $1 == "infra@kyle-skills"'
