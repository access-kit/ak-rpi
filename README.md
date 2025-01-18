# ak-rpi

[![Release](https://img.shields.io/github/v/release/access-kit/ak-rpi)](https://img.shields.io/github/v/release/access-kit/ak-rpi)
[![Build status](https://img.shields.io/github/actions/workflow/status/access-kit/ak-rpi/main.yml?branch=main)](https://github.com/access-kit/ak-rpi/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/access-kit/ak-rpi/branch/main/graph/badge.svg)](https://codecov.io/gh/access-kit/ak-rpi)
[![Commit activity](https://img.shields.io/github/commit-activity/m/access-kit/ak-rpi)](https://img.shields.io/github/commit-activity/m/access-kit/ak-rpi)
[![License](https://img.shields.io/github/license/access-kit/ak-rpi)](https://img.shields.io/github/license/access-kit/ak-rpi)

This is a repository for synchronizing Raspberry Pis with AccessKit.

- **Github repository**: <https://github.com/access-kit/ak-rpi/>
- **Documentation** <https://access-kit.github.io/ak-rpi/> (coming soon...)

## Getting Started: Linux/Raspberry Pi Mode

This instructions will handle automatically installing the required dependencies, configuring the connection to AccessKit, and setting up autostarting via systemd or running manually. They assume you have already setup your Raspberry Pi and connected it to the internet (either through Ethernet or WiFi).

1. Open a terminal and navigate to the directory where you want to clone the repository; the default home location is typically fine.
1. First, download the repository using `git clone https://github.com/access-kit/ak-rpi.git` which will clone the repository into a directory named `ak-rpi`.
1. Next, navigate into the `ak-rpi` directory using `cd ak-rpi`
1. Finally, run `make setup`, which will install the necessary dependencies and configure the connection to AccessKit, along with optional autostart via a systemd service.

### Audio Configuration

The Raspberry Pi supports various audio output options, including:

- Built-in audio jack (on models that have it)
- HDMI audio output
- USB audio devices (e.g., USB sound cards, DACs)
- Bluetooth audio (requires additional configuration)

To configure your audio device:

1. Connect your audio device (if using USB or external device)
1. Configure your default audio device:
   ```bash
   make configure-audio
   ```
   This interactive script will:
   - Show available audio devices
   - Let you choose which card and device to use as default
   - Create either system-wide (`/etc/asound.conf`) or user-specific (`~/.asoundrc`) configuration
   - Automatically backup any existing configuration
   - Test the audio output
1. After configuration, you may need to reboot your Raspberry Pi for changes to take effect.

Common audio devices and their typical card numbers:

- Card 0: Usually the built-in audio (if present)
- Card 1: Often the first USB audio device
- Card 2+: Additional USB devices or HDMI outputs

Troubleshooting tips:

- If no sound is playing, check the volume levels using `alsamixer`
- For USB devices, try unplugging and reconnecting the device
- Some USB audio devices may need additional power; use a powered USB hub if necessary
- If using HDMI audio, ensure it's enabled in `/boot/config.txt`

## Getting Started: Desktop/User Mode

1. Make sure your system has `poetry` installed and can run `Makefiles`.
1. Add a `config.json` file to the root directory with the `syncUrl` and `password` fields completed.
1. Add an audio file (`.wav` or `.mp3`) to the `media/` directory.
1. Execute `make install-and-run`.

## Getting Started: Dev Mode

```bash
make install
```
