#!/usr/bin/env bash
set -euo pipefail

# Google Java Format release asset: https://github.com/google/google-java-format/releases/tag/v1.28.0
version=1.28.0
sha256=32342e7c1b4600f80df3471da46aee8012d3e1445d5ea1be1fb71289b07cc735
root=$(cd "$(dirname "$0")/.." && pwd)
jar=${GOOGLE_JAVA_FORMAT_JAR:-${XDG_CACHE_HOME:-$HOME/.cache}/appforkids/google-java-format-${version}-all-deps.jar}
java=${JAVA_HOME:+$JAVA_HOME/bin/}java

case "${1:---check}" in
  --check) mode=(--dry-run --set-exit-if-changed) ;;
  --fix) mode=(--replace) ;;
  *) echo "Usage: $0 [--check|--fix]" >&2; exit 2 ;;
esac
if [ "$#" -gt 1 ]; then echo "Usage: $0 [--check|--fix]" >&2; exit 2; fi

if [ ! -f "$jar" ]; then
  mkdir -p "$(dirname "$jar")"
  download=$(mktemp "${TMPDIR:-/tmp}/appforkids-gjf.XXXXXXXX")
  trap 'rm -f "$download"' EXIT
  curl --fail --location --silent --show-error \
    "https://github.com/google/google-java-format/releases/download/v${version}/google-java-format-${version}-all-deps.jar" \
    --output "$download"
  actual=$(shasum -a 256 "$download" | awk '{print $1}')
  if [ "$actual" != "$sha256" ]; then echo "Formatter checksum mismatch" >&2; exit 1; fi
  cp "$download" "$jar"
fi
actual=$(shasum -a 256 "$jar" | awk '{print $1}')
if [ "$actual" != "$sha256" ]; then echo "Formatter checksum mismatch: $jar" >&2; exit 1; fi
find "$root/app/src" -type f -name '*.java' -print0 | xargs -0 "$java" -jar "$jar" "${mode[@]}"
