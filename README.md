# ak-rpi

[![Release](https://img.shields.io/github/v/release/szvsw/ak-rpi)](https://img.shields.io/github/v/release/szvsw/ak-rpi)
[![Build status](https://img.shields.io/github/actions/workflow/status/szvsw/ak-rpi/main.yml?branch=main)](https://github.com/szvsw/ak-rpi/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/szvsw/ak-rpi/branch/main/graph/badge.svg)](https://codecov.io/gh/szvsw/ak-rpi)
[![Commit activity](https://img.shields.io/github/commit-activity/m/szvsw/ak-rpi)](https://img.shields.io/github/commit-activity/m/szvsw/ak-rpi)
[![License](https://img.shields.io/github/license/szvsw/ak-rpi)](https://img.shields.io/github/license/szvsw/ak-rpi)

This is a repository for synchronizing Raspberry Pis with AccessKit.

- **Github repository**: <https://github.com/szvsw/ak-rpi/>
- **Documentation** <https://szvsw.github.io/ak-rpi/> (coming soon...)

## Getting Started: User Mode

1. Make sure your system has `poetry` installed and can run `Makefiles`.
1. Add a `config.json` file to the root directory with the `syncUrl` and `password` fields completed.
1. Add an audio file (`.wav` or `.mp3`) to the `media/` directory.
1. Execute `make install-and-run`.

## Getting Started: Dev Mode

```bash
make install
```
