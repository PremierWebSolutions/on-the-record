#!/usr/bin/env bash
# Translate one transcript with the Claude CLI, then check the result.
#
#   tools/translate.sh inputs/call.txt [runs/call.json]
#
# Needs the Claude Code CLI (`claude`), signed in. MODEL defaults to sonnet;
# override with MODEL=opus tools/translate.sh ...
# The translator sees only the translator/ folder and the numbered transcript.
set -euo pipefail

here="$(cd "$(dirname "$0")/.." && pwd)"
input="${1:?usage: tools/translate.sh <transcript> [output.json]}"
name="$(basename "${input%.*}")"
out="${2:-$here/runs/$name.json}"
model="${MODEL:-sonnet}"

command -v claude >/dev/null || { echo "translate.sh: the claude CLI is not installed" >&2; exit 2; }

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# The system prompt is the translator folder, file by file, nothing else.
{
  for f in identity.md rules.md examples.md reference/input-format.md reference/fields.md \
           reference/triggers.md reference/output-schema.json; do
    [ -f "$here/translator/$f" ] || continue
    printf '\n===== translator/%s =====\n' "$f"
    cat "$here/translator/$f"
  done
} > "$tmp/system.md"

python3 "$here/tools/number.py" "$input" > "$tmp/numbered.txt"

printf 'Translate this transcript. source.file is "%s".\n\n' "$input" > "$tmp/prompt.txt"
cat "$tmp/numbered.txt" >> "$tmp/prompt.txt"

claude -p --model "$model" --system-prompt-file "$tmp/system.md" --tools "" \
  --no-session-persistence < "$tmp/prompt.txt" > "$tmp/reply.txt"

# Keep the reply's JSON object and nothing else.
python3 - "$tmp/reply.txt" "$out" <<'PY'
import json, sys
raw = open(sys.argv[1], encoding="utf-8").read()
start, end = raw.find("{"), raw.rfind("}")
if start == -1 or end == -1:
    sys.exit("translate.sh: the reply contained no JSON object")
obj = json.loads(raw[start:end + 1])
with open(sys.argv[2], "w", encoding="utf-8") as fh:
    json.dump(obj, fh, ensure_ascii=False, indent=2)
    fh.write("\n")
PY

echo "wrote $out"
python3 "$here/verify/check.py" --input "$input" --output "$out"
