#!/usr/bin/env bash
set -euo pipefail

tag=bertlesherp

docker build --rm --tag="$tag" . >&2
docker run --publish=8888:80 "$tag" "$@"
