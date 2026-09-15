#!/usr/bin/env bash
# Stamp a build id onto every module import in app.html before deploying.
#
# GitHub Pages serves each file with max-age=600 and mobile Safari holds ES
# modules longer than that, so a phone kept running the old rig.js after a fix
# had shipped and reported "nothing changed". A new query string per build makes
# every import a new URL. The same id is shown on screen, so whoever is looking
# can tell at a glance which build they are on.
#
# Usage: ./stamp.sh            (id = UTC timestamp)
set -euo pipefail
cd "$(dirname "$0")"
ID="${1:-$(date -u +%Y%m%d%H%M)}"
sed -i '' -E "s#from '\./(rig|parts|accessories|wheels)\.js(\?v=[^']*)?'#from './\1.js?v=${ID}'#g" app.html
sed -i '' -E "s#const BUILD = '[^']*'#const BUILD = '${ID}'#" app.html
grep -c "?v=${ID}'" app.html | xargs echo "imports stamped:"
echo "build ${ID}"
