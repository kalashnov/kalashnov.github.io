#!/bin/sh
# Install quarto-live (https://github.com/r-wasm/quarto-live) into _extensions/r-wasm/live, pinned to a commit.
# _extensions/ is not kept in git; run this before rendering (the publish workflow does). To upgrade, change QL.
set -eu
QL=12fb30a5dd5e1bbe6d8ace96795eb1c114c80447   # main, 2026-06-08 (just after v0.2.0)
cd "$(dirname "$0")/.."
rm -rf _extensions/r-wasm/live
mkdir -p _extensions/r-wasm
curl -fsSL "https://github.com/r-wasm/quarto-live/archive/$QL.tar.gz" \
  | tar -xz -C _extensions/r-wasm --strip-components=2 "quarto-live-$QL/_extensions/live"
