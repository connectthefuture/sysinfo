#!/usr/bin/env bash
set -eo pipefail
test -n "${DEBUG:-}" && set -x

success() {
	printf '\r  [ \033[00;32mOK\033[0m ] Link checking %s...\n' "$1"
}

fail() {
	printf '\r  [\033[0;31mFAIL\033[0m] Link checking %s...\n' "$1"
	exit 1
}

info() {
	printf '\r  [ \033[00;34m??\033[0m ] %s\n' "$1"
}

check() {
	local filename="$1"

        awesome_bot "$filename" --allow-redirect --allow-dupe  || fail "$filename"
	success "$filename"
}

find_files() {
	git ls-tree -r HEAD | grep -E '^100644.*\.md$' | awk '{print $4}'
}

check_all_markdown() {
	echo 'Link checking all markdown files...'
	find_files | while read -r file; do
		check "$file"
	done
}

# if being executed, check all markdown files, otherwise do nothing
if [ $SHLVL -gt 1 ]; then
	check_all_markdown
else
	return 0
fi
