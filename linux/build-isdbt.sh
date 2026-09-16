#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "$(uname -s)" != Linux ]]; then
    echo 'Run this build on Linux.' >&2
    exit 1
fi
cmake -S "$ROOT/third_party/gr-isdbt" -B "$ROOT/linux/build-isdbt" \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local \
    -DPYTHON_EXECUTABLE=/usr/bin/python3 -DENABLE_DOXYGEN=OFF
cmake --build "$ROOT/linux/build-isdbt" --parallel 2
sudo cmake --install "$ROOT/linux/build-isdbt"
sudo ldconfig
/usr/bin/python3 -c 'from gnuradio import gr; import gnuradio.isdbt; print("ISDB-T import OK; no RF")'
