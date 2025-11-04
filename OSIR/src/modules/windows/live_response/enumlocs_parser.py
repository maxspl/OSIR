from __future__ import annotations
import re
import json
from typing import List, Dict, Any


class EnumLocsParser:
    """Parse NTFSUtil EnumLocs output into per-volume JSONL records.

    Each JSON object (one per line) represents a volume and contains:
      * volume_id, status, filesystem
      * entries: list of sub-lines (each {"key", "value", "mounts": []})
      * flattened arrays for repeated keys:
          - MountedVolume, PhysicalDriveVolume, DiskInterfaceVolume, Snapshot
      * parameters: dict with all values from the global **Parameters** section

    Returns:
      JSONL (newline-separated JSON objects), one per volume.
    """

    # Match "Volume: <id>, <status>, <fs>" with a word boundary before "Volume:"
    _volume_header_anywhere = re.compile(
        r"\bVolume:\s*([^,]+),\s*([^,]+),\s*([^\s,]+)"
    )

    # Detect an optional mount annotation at the end:  ...  ["C:\"]
    _value_with_mounts = re.compile(r'^(?P<val>.*?)\s+(?P<m>\["[^"]*"\])\s*$')

    def parse(self, text: str) -> str:
        """Parse an EnumLocs text dump into JSONL (one record per volume).

        Args:
            text: Full textual output of NTFSUtil EnumLocs.

        Returns:
            A JSONL string. Each line is a JSON object describing one volume,
            including a parameters dict copied from the global Parameters section.
        """
        records: List[Dict[str, Any]] = []
        lines = text.splitlines()
        n = len(lines)

        # 1) Collect Parameters once, then copy into each volume record
        parameters: Dict[str, str] = {}
        i = 0
        in_params = False
        while i < n:
            raw = lines[i]
            line = raw.strip()

            if not in_params and line.startswith("Parameters"):
                in_params = True
                i += 1
                continue

            if in_params:
                # End parameters on non-indented or empty line
                if not raw or not raw.startswith(" "):
                    in_params = False
                    continue
                stripped = raw.strip()
                if ":" in stripped:
                    key, value = map(str.strip, stripped.split(":", 1))
                    parameters[key] = value  # keep raw
                i += 1
                continue

            i += 1

        # 2) Parse volumes: header + indented properties
        i = 0
        current_volume: Dict[str, Any] | None = None

        def commit_volume() -> None:
            """Finalize and store the current volume, attaching parameters."""
            nonlocal current_volume
            if current_volume is not None:
                for k in ("MountedVolume", "PhysicalDriveVolume", "DiskInterfaceVolume", "Snapshot"):
                    current_volume.setdefault(k, [])
                current_volume["parameters"] = dict(parameters)
                records.append(current_volume)
                current_volume = None

        def append_volume_entry(vol: Dict[str, Any], key: str, value_raw: str) -> None:
            """Append a structured sub-entry and update flattened arrays.

            Args:
                vol: Current volume record dict (mutated in-place).
                key: Raw key before the colon (e.g., 'MountedVolume').
                value_raw: Raw value text; may end with mount annotation(s) like ["C:\"].
            """
            mounts: List[str] = []
            val = value_raw

            m = self._value_with_mounts.match(value_raw)
            if m:
                val = m.group("val").rstrip()
                mounts = re.findall(r'\["([^"]*)"\]', value_raw)

            vol.setdefault("entries", []).append({
                "key": key,
                "value": val,
                "mounts": mounts,
            })

            if key in ("MountedVolume", "PhysicalDriveVolume", "DiskInterfaceVolume", "Snapshot"):
                vol.setdefault(key, []).append(val)

        while i < n:
            raw = lines[i]
            line = raw.strip()

            if not line:
                i += 1
                continue

            # Detect a true "Volume:" header (not "...Volume:")
            m = self._volume_header_anywhere.search(line)
            if m:
                # Guard: ensure the match is not part of a longer word (already handled by \b)
                # Commit the previous volume and start a new one
                commit_volume()

                volume_id, status, fs = (m.group(1).strip(), m.group(2).strip(), m.group(3).strip())
                current_volume = {
                    "type": "enumlocs_volume",
                    "volume_id": volume_id,
                    "status": status,
                    "filesystem": fs,
                    "entries": [],
                    "MountedVolume": [],
                    "PhysicalDriveVolume": [],
                    "DiskInterfaceVolume": [],
                    "Snapshot": [],
                }
                i += 1
                continue

            if current_volume is not None:
                # Volume properties are indented lines: "    Key: Value"
                if raw.startswith("    "):
                    trimmed = raw.strip()
                    if ":" in trimmed:
                        key, value = trimmed.split(":", 1)
                        append_volume_entry(current_volume, key.strip(), value.strip())
                    i += 1
                    continue

                # Non-indented line ends the current volume section
                commit_volume()
                # Do not advance; re-check this line for another header
                continue

            # Not in a volume; advance
            i += 1

        # Trailing volume
        commit_volume()

        return "\n".join(json.dumps(r, ensure_ascii=False) for r in records)
