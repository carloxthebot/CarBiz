#!/bin/sh
# Rebuild the parts library and refuse to continue if any step fails.
#
# Blender exits 0 even when the script inside it raised, so its output is
# scanned for a traceback as well -- a silent failure here used to let a
# deploy ship the previous parts.glb.
set -e
cd "$(dirname "$0")"

BLENDER=${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}
LOG=$(mktemp -t jimny-build)

echo "building parts.glb ..."
(cd blender && "$BLENDER" -b --factory-startup -P build_parts.py) >"$LOG" 2>&1 || {
  echo "FAIL: Blender exited non-zero"; tail -30 "$LOG"; exit 1; }
if grep -qiE "Traceback|SyntaxError|^Error:" "$LOG"; then
  echo "FAIL: the build script raised"; grep -iE -A6 "Traceback|SyntaxError|^Error:" "$LOG" | head -30; exit 1
fi

npx gltf-transform draco model/rims.glb model/rims.glb | tail -1
npx gltf-transform draco model/parts.glb model/parts.glb | tail -1

echo "checking dimensions ..."
(cd blender && "$BLENDER" -b --factory-startup -P spec_gate.py) 2>/dev/null | sed -n '/parts measured/,$p'
(cd blender && "$BLENDER" -b --factory-startup -P spec_gate.py) >/dev/null 2>&1 || {
  echo "FAIL: a part is outside its spec"; exit 1; }

echo "build ok"
