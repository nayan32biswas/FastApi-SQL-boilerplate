#!/usr/bin/env bash

set -e
set -x

# mypy app cli
ruff check app cli
ruff format app cli --check
