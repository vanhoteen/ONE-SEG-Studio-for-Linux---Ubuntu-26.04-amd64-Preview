# ONE SEG Studio · Linux preview

Development port targeting Ubuntu 24.04/26.04 LTS, x86-64. This is not yet a tested Linux release or a self-contained AppImage. The macOS application and DMG are unchanged. The existing transport preparation and RF template are reused without changing modulation settings.

## Install dependencies on the Linux test machine

### Build installable Debian packages

On Ubuntu 24.04 or 26.04 amd64, run `bash linux/build-deb.sh --install-deps` from the repository. This installs build prerequisites (sudo), downloads a pinned official TSDuck package with SHA-256 verification, compiles gr-isdbt into a staging directory, checks the staged Python bindings and prepares a three-second test without RF. It produces `dist/linux-ubuntu<24-or-26>-amd64/` containing the application `.deb`, official TSDuck companion `.deb`, checksums and a one-command installer. Copy the whole folder to the target machine and run `bash INSTALL.sh`. No compilation takes place during installation. Runtime dependencies require Internet access and are managed by apt. The installed app appears in the desktop applications menu.

The package pins GNU Radio to the build machine's package version to prevent silently mixing native ABIs. If Ubuntu updates GNU Radio, rebuild the package against that version. The author ran this build successfully on Ubuntu 26.04 amd64, installed the resulting packages and confirmed Sony reception. Ubuntu 24.04 remains untested. The tested installer is uploaded separately by the author.

### Manual development setup

```sh
sudo apt update
sudo apt install python3-tk python3-numpy ffmpeg gnuradio gnuradio-dev \
  cmake build-essential pybind11-dev python3-dev python3-packaging \
  libgsl-dev libspdlog-dev libfmt-dev libboost-all-dev libvolk2-dev \
  soapysdr-tools soapysdr-module-hackrf hackrf
```

Install the Ubuntu 24 x86-64 TSDuck binary package from https://tsduck.io/tsduck-binaries/ using `sudo apt install ./downloaded-package.deb`. Check that `tstabcomp --version` works. Do not install macOS runtime files on Linux.

From the repository directory:

```sh
bash linux/build-isdbt.sh
/usr/bin/python3 linux/check.py
/usr/bin/python3 linux/smoke.py
/usr/bin/python3 linux/studio.py
```

The build script compiles the included gr-isdbt snapshot against the Linux machine's GNU Radio and Python. It installs to /usr/local with sudo; the GUI must run as your normal user. If USB access is denied, check the HackRF package's udev rules and reconnect the device; do not run the GUI as root.

## Workflow

1. Check tools. This imports libraries without constructing a transmitter.
2. Detect HackRF probes the device without starting a stream.
3. Select a video, channel, video bitrate and gain. RF amplifier defaults off and gain defaults to zero.
4. Prepare video. No RF starts. Changing any setting invalidates preparation.
5. Transmit explicitly starts RF. Follow your local frequency, power and authorization requirements as described in the main README.
6. Stop, or close the window, terminates the child process group, with a forced stop after three seconds if necessary.

Prepared files are stored in `$XDG_DATA_HOME/one-seg-studio` (default `~/.local/share/one-seg-studio`). The video is a finite test, not a guaranteed seamless loop. The preview interface is English only; translations, the integrated waveform and standalone packaging are still pending.

## Validation status

On 2026-09-16 the smoke test passed using the existing bundled macOS tools: three seconds of bars plus audio, H.264 320×240, AAC, both layers aligned to 188-byte packets, zero reported continuity errors, and generated transmitter syntax checked without execution. Python and shell syntax checks also passed. This validates the shared preparation pipeline, not the Linux runtime.

On 2026-09-16 the author reported successful native compilation, staged ISDB-T import, preparation smoke test, Debian installation, GUI operation and HackRF/Sony reception on Ubuntu 26.04 amd64. This remains an experimental preview; no wider distribution or receiver compatibility is claimed.

The Debian build selects the matching Ubuntu TSDuck package and VOLK development package, and derives the Python ABI requirement from the build interpreter. Each installer checks the exact Ubuntu version recorded at build time.
