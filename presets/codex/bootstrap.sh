#!/usr/bin/env bash
set -eu

marketplace_present() {
  codex plugin marketplace list | awk -v name="$1" 'NR > 1 && $1 == name { found = 1 } END { exit !found }'
}

plugin_enabled() {
  codex plugin list | awk -v selector="$1" \
    '$1 == selector && $2 == "installed," && $3 == "enabled" { found = 1 } END { exit !found }'
}

if ! marketplace_present "kyle-skills"; then
  codex plugin marketplace add kyle-park-io/skills
fi

for plugin in \
  "superpowers@openai-curated-remote" \
  "process@kyle-skills"
do
  if ! plugin_enabled "$plugin"; then
    codex plugin add "$plugin"
  fi
done

codex plugin marketplace list
codex plugin list | awk \
  '$1 == "superpowers@openai-curated-remote" || $1 == "process@kyle-skills"'
