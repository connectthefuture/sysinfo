#!/usr/bin/env bash
set -eo pipefail
test -n "${DEBUG:-}" && set -x

# if being executed, check all executables, otherwise do nothing
if [ $SHLVL -gt 1 ]; then
	gem install awesome_bot
else
	return 0
fi
