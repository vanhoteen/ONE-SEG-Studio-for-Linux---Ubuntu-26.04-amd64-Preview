#!/usr/bin/env bash
# Build on Ubuntu 24.04/26.04 amd64; never starts RF or installs the resulting app.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "$(uname -s)" != Linux ]]; then
    echo 'Compile this package on Ubuntu 24.04 or 26.04 (Intel/AMD 64-bit).' >&2
    exit 1
fi
source /etc/os-release
if [[ "${ID:-}" != ubuntu || ( "${VERSION_ID:-}" != 24.04 && "${VERSION_ID:-}" != 26.04 ) || "$(dpkg --print-architecture)" != amd64 ]]; then
    echo 'This first package targets Ubuntu 24.04/26.04 amd64 only.' >&2
    exit 1
fi
UBUNTU_MAJOR="${VERSION_ID%%.*}"
if [[ "$UBUNTU_MAJOR" == 26 ]]; then
    VOLK_PACKAGE=libvolk-dev
    TSDUCK_SHA=318317926aa2c04d1e1d4da11143e696fd27aaf4cfcdba3902c0c9fdcdf14214
else
    VOLK_PACKAGE=libvolk2-dev
    TSDUCK_SHA=0023689f76e75b64e45253771208bcf8ca95b91fbfd0900da097c729f3c39fde
fi
if [[ "${1:-}" == --install-deps ]]; then
    sudo apt-get update
    sudo apt-get install --yes build-essential cmake gnuradio gnuradio-dev \
        python3-dev python3-numpy python3-tk python3-packaging python3-pygccxml \
        pybind11-dev libgsl-dev libspdlog-dev libfmt-dev libboost-all-dev "$VOLK_PACKAGE" \
        ffmpeg soapysdr-tools soapysdr-module-hackrf hackrf curl ca-certificates
elif [[ $# -gt 0 ]]; then
    echo 'Usage: bash linux/build-deb.sh [--install-deps]' >&2
    exit 1
fi
for tool in cmake dpkg-deb curl sha256sum; do
    command -v "$tool" >/dev/null || { echo "Missing $tool; use --install-deps" >&2; exit 1; }
done
BUILD="$ROOT/linux/build-deb/ubuntu$UBUNTU_MAJOR"
STAGE="$BUILD/package"
DIST="$ROOT/dist/linux-ubuntu${UBUNTU_MAJOR}-amd64"
mkdir -p "$BUILD" "$DIST"
# Version-pinned official TSDuck companion package, checked before installation.
TSDUCK="tsduck_3.45-4798.ubuntu${UBUNTU_MAJOR}_amd64.deb"
curl --fail --location --retry 3 \
    "https://github.com/tsduck/tsduck/releases/download/v3.45-4798/$TSDUCK" \
    --output "$DIST/$TSDUCK.download"
printf '%s  %s\n' "$TSDUCK_SHA" \
    "$DIST/$TSDUCK.download" | sha256sum --check
mv "$DIST/$TSDUCK.download" "$DIST/$TSDUCK"
if [[ "$(dpkg-query -W -f='${Version}' tsduck 2>/dev/null || true)" != "3.45-4798.ubuntu${UBUNTU_MAJOR}" ]]; then
    echo 'Installing the verified TSDuck package for the preparation test.'
    sudo apt-get install --yes "$DIST/$TSDUCK"
fi
cmake -S "$ROOT/third_party/gr-isdbt" -B "$BUILD/native" \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
    -DGR_PYTHON_DIR=/usr/lib/python3/dist-packages \
    -DPYTHON_EXECUTABLE=/usr/bin/python3 -DENABLE_DOXYGEN=OFF
cmake --build "$BUILD/native" --parallel "${ONESEG_BUILD_JOBS:-2}"
# Stage, never install the native module into the build machine.
if [[ -e "$STAGE" ]]; then
    echo "Build staging directory already exists: $STAGE" >&2
    echo 'Move or remove this staging directory before rebuilding.' >&2
    exit 1
fi
mkdir -p "$STAGE"
DESTDIR="$STAGE" cmake --install "$BUILD/native"
test -f "$STAGE/usr/lib/python3/dist-packages/gnuradio/isdbt/__init__.py"
APP="$STAGE/usr/share/one-seg-studio"
mkdir -p "$APP/linux" "$STAGE/usr/bin" "$STAGE/usr/share/applications" \
    "$STAGE/usr/share/icons/hicolor/256x256/apps" "$STAGE/DEBIAN" \
    "$STAGE/usr/share/doc/one-seg-studio"
cp -R "$ROOT/Payload" "$APP/"
cp "$ROOT/prepare.py" "$ROOT/signal_tx.py" "$APP/"
cp "$ROOT/linux/studio.py" "$ROOT/linux/check.py" "$ROOT/linux/smoke.py" "$APP/linux/"
mkdir -p "$APP/Assets"
cp "$ROOT/Assets/one-seg-logo.png" "$APP/Assets/one-seg-logo.png"
cp "$ROOT/Assets/app-icon.png" "$STAGE/usr/share/icons/hicolor/256x256/apps/one-seg-studio.png"
cp "$ROOT/linux/one-seg-studio.desktop" "$STAGE/usr/share/applications/"
cp "$ROOT/LICENSE-NOTICE.md" "$ROOT/linux/README.md" "$STAGE/usr/share/doc/one-seg-studio/"
cp "$ROOT/third_party/gr-isdbt/COPYING" "$STAGE/usr/share/doc/one-seg-studio/copyright-isdbt"
cat > "$STAGE/usr/bin/one-seg-studio" <<'LAUNCHER'
#!/bin/sh
exec /usr/bin/python3 /usr/share/one-seg-studio/linux/studio.py "$@"
LAUNCHER
chmod 755 "$STAGE/usr/bin/one-seg-studio"
GR_VERSION="$(dpkg-query -W -f='${Version}' gnuradio)"
PY_MIN="$(/usr/bin/python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
PY_MAX="$(/usr/bin/python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor+1}")')"
cat > "$STAGE/DEBIAN/control" <<CONTROL
Package: one-seg-studio
Version: 0.1.0~linuxpreview2
Section: video
Priority: optional
Architecture: amd64
Maintainer: vanhoteen <hackrfapp@villarejo.de>
Depends: python3 (>= $PY_MIN), python3 (<< $PY_MAX), python3-tk, python3-numpy, gnuradio (= $GR_VERSION), ffmpeg, soapysdr-tools, soapysdr-module-hackrf, hackrf, tsduck (>= 3.45)
Conflicts: gr-isdbt
Installed-Size: $(du -sk "$STAGE/usr" | cut -f1)
Homepage: https://github.com/vanhoteen/ONE-SEG-Studio-
Description: One-Seg video preparation and HackRF transmitter — Linux preview
 Native Linux frontend with precompiled gr-isdbt. No compiler is needed
 on the receiving computer. Targets Ubuntu $VERSION_ID amd64.
 RF starts only from the explicit Transmit control.
CONTROL
printf '%s\n' 'activate-noawait ldconfig' > "$STAGE/DEBIAN/triggers"
# Check the STAGED bindings, not a potentially preinstalled gr-isdbt.
LIBPATH="$(find "$STAGE/usr" -name 'libgnuradio-isdbt.so*' -printf '%h\n' | sort -u | paste -sd: -)"
test -n "$LIBPATH"
LD_LIBRARY_PATH="$LIBPATH${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
    /usr/bin/python3 - "$STAGE" <<'PY'
from pathlib import Path
import sys
from gnuradio import gr
import gnuradio
path = Path(sys.argv[1])/'usr/lib/python3/dist-packages/gnuradio'
gnuradio.__path__.insert(0, str(path))
import gnuradio.isdbt
assert str(path) in gnuradio.isdbt.__file__
print('Staged gr-isdbt imports successfully. No RF.')
PY
/usr/bin/python3 "$APP/linux/smoke.py"
dpkg-deb --root-owner-group --build "$STAGE" "$DIST/one-seg-studio_0.1.0~linuxpreview2_amd64.deb"
cp "$ROOT/linux/install.sh" "$DIST/INSTALL.sh"
printf '%s\n' "$VERSION_ID" > "$DIST/UBUNTU_VERSION"
chmod 755 "$DIST/INSTALL.sh"
cp "$ROOT/linux/INSTALL.es.md" "$DIST/LEEME.md"
(cd "$DIST" && sha256sum ./*.deb > SHA256SUMS)
echo "Ready: $DIST"
echo 'Copy the entire folder to the target computer. No RF has been started.'
