#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
source /etc/os-release
EXPECTED="$(cat UBUNTU_VERSION)"
if [[ "${ID:-}" != ubuntu || "${VERSION_ID:-}" != "$EXPECTED" || "$(dpkg --print-architecture)" != amd64 ]]; then
    echo "This package requires Ubuntu $EXPECTED on Intel/AMD 64-bit." >&2
    exit 1
fi
sha256sum --check SHA256SUMS
sudo apt-get update
sudo apt-get install --yes "./tsduck_3.45-4798.ubuntu${EXPECTED%%.*}_amd64.deb" ./one-seg-studio_0.1.0~linuxpreview4_amd64.deb
echo 'Installed. Open ONE SEG Studio from the applications menu.'
