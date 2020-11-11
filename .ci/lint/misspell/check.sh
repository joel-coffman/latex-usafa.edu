#!/bin/bash

set -u


files="$(git diff-tree --no-commit-id --name-only -r HEAD)"
if [ 0 -lt $# ]; then
  files=$@
fi


args="."

ignores=( $(find . -name .misspellignore) )
if [ ${#ignores[@]} -gt 0 ]; then
  args="--invert-match $(for file in $ignores; do echo "--file=$file"; done)"
fi


! misspell --error $files | grep $args | grep --invert-match .misspellignore
