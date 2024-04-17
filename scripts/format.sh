#!/bin/sh -e

set -x

ruff check app cli --fix
ruff format app cli
