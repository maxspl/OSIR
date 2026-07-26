# Loki-RS (vendored)

High-performance YARA & IOC scanner, used by the `loki_orc` and `loki_uac`
OSIR modules through `loki_scan.sh`.

## Origin

| | |
|---|---|
| Upstream | <https://github.com/Neo23x0/Loki-RS> |
| Version | v2.12.0 (tag `v2.12.0`, commit `4a3964aefdca24d6e9d80a0248acc57a95a6de61`) |
| Binaries | `loki-linux-x86_64-v2.12.0.tar.gz`, sha256 `fa4ec0b77f8471ecb143c8c070a6e8b91ad48d02bebccf1e114f9898945221a7` |
| Files taken from it | `loki`, `loki-util`, `signatures/` |
| Modified | no, the binaries are the unmodified official release |

## License

**GPL-3.0-or-later**, Copyright (c) 2025 Florian Roth. The full text is in
[LICENSE](LICENSE), as required when the binaries are redistributed.

The corresponding source code of these binaries is published by the upstream
project at the release and commit given above, and can be obtained from
<https://github.com/Neo23x0/Loki-RS/tree/v2.12.0>.

OSIR is licensed under Apache-2.0 and only *executes* these binaries as separate
processes - there is no linking and no derived work, so shipping them side by
side is mere aggregation and does not place OSIR under the GPL.

## YARA rules (`signatures/yara/`)

The rules come from the [YARA Forge](https://github.com/YARAHQ/yara-forge)
`core` package and are refreshed by `loki_scan.sh` (`loki-util update`). They
are **not** covered by the license above: each rule carries its own `license`
and its source repository in its metadata, inside the `.yar` file. The pack
currently mixes CC BY-SA 4.0, Detection Rule License 1.1, BSD-2-Clause,
Apache-2.0, MIT and a few vendor-specific terms; all of them require
attribution, which the embedded metadata provides as long as the file is
redistributed as-is.

IOC lists in `signatures/iocs/` are empty placeholders, to be filled with your
own indicators.
