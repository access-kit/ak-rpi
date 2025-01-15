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

This mode will handle automatically installing the required dependencies, configuring the connection to AccessKit, and setting up autostarting via systemd or LXDE autostart.

1. `git clone https://github.com/access-kit/ak-rpi.git`
2. `cd ak-rpi`
3. `make setup`

## Getting Started: Desktop/User Mode

1. Make sure your system has `poetry` installed and can run `Makefiles`.
1. Add a `config.json` file to the root directory with the `syncUrl` and `password` fields completed.
1. Add an audio file (`.wav` or `.mp3`) to the `media/` directory.
1. Execute `make install-and-run`.

## Getting Started: Dev Mode

```bash
make install
```
