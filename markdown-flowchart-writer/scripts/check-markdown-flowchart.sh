#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-.}"

printf "Checking Markdown files in: %s\n" "$TARGET_DIR"

printf "\n1) Checking hard tabs...\n"
if grep -RIn $'\t' "$TARGET_DIR" --include='*.md'; then
  printf "\nERROR: Hard tabs found. Replace tabs with spaces.\n"
  exit 1
else
  printf "OK: No hard tabs found.\n"
fi

printf "\n2) Checking possible ASCII flowchart characters...\n"
if grep -RInE '[┌┐└┘├┤┬┴┼─│]' "$TARGET_DIR" --include='*.md'; then
  printf "\nWARNING: Box-drawing characters found. Consider converting diagrams to Mermaid.\n"
else
  printf "OK: No box-drawing characters found.\n"
fi

printf "\n3) Checking Mermaid blocks...\n"
if grep -RIn '```mermaid' "$TARGET_DIR" --include='*.md'; then
  printf "OK: Mermaid blocks detected.\n"
else
  printf "WARNING: No Mermaid blocks detected.\n"
fi
