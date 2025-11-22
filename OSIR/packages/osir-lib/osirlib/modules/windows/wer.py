from __future__ import annotations
import os
import json
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from osirlib.core.BaseModule import BaseModule
from osirlib.core.PyModule import PyModule
from osirlib.logger import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()

SECTION_RE = re.compile(r'^\[(.+?)\]\s*$')
SIG_RE = re.compile(r'^Sig\[(\d+)\]\.(Name|Value)$', re.IGNORECASE)
DYN_RE = re.compile(r'^DynamicSig\[(\d+)\]\.(Name|Value)$', re.IGNORECASE)
OSINFO_RE = re.compile(r'^OsInfo\[(\d+)\]\.(Key|Value)$', re.IGNORECASE)
STATE_RE = re.compile(r'^State\[(\d+)\]\.(Key|Value)$', re.IGNORECASE)
LMOD_RE = re.compile(r'^LoadedModule\[(\d+)\]$', re.IGNORECASE)


def _slug(s: str) -> str:
    """Normalize a string.
    Converts to ASCII, lowercases, replaces non-alphanumerics with underscores,
    and collapses repeated underscores.

    Args:
        s (str): Any input string.

    Returns:
        str: Normalized key (e.g., 'System version' -> 'system_version').
    """
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^\w]+", "_", s.lower())
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "key"


class WerParser(PyModule):
    """Parse Windows WER files under an input path and export a single JSONL file.

    This module walks the provided input directory and parses each WER report.
    """

    def __init__(self, case_path: str, module: BaseModule) -> None:
        """Initialize the WerParser.

        Args:
            case_path (str): Base case path used by the framework.
            module (BaseModule): Module configuration with input/output descriptors.
        """
        super().__init__(case_path, module)

    def __call__(self) -> bool:
        """Execute the parser workflow.

        Walks the input path to find .wer files, parses them, and writes one JSONL
        line per file to self.module.output.output_file under self.default_output_dir.

        Returns:
            bool: True on success, False on any error.

        Logs:
            Errors and progress are logged via the configured logger.

        Raises:
            None: All exceptions are handled and logged; the method returns False on failure.
        """
        if self.module.input.type not in {"dir", "file"}:
            logger.error(f"Unsupported input type {self.module.input.type}")
            return False

        input_path = self.module.input.dir
        if not input_path:
            logger.error("input.dir is empty")
            return False

        in_path = Path(input_path)
        try:
            if in_path.is_file():
                if in_path.suffix.lower() != ".wer":
                    logger.error(f"Input file is not a .wer: {in_path}")
                    return False
                wer_files: List[Path] = [in_path]
            else:
                wer_files = [p for p in in_path.rglob("*.wer") if p.is_file()]
        except Exception as e:
            logger.error(f"Failed to enumerate WER files under '{input_path}': {e}")
            return False

        if not wer_files:
            logger.warning(f"No .wer files found under '{input_path}'")
            return False

        # Prepare output path 
        try:
            self._format_output_file()
            out_path = os.path.join(self.default_output_dir, self.module.output.output_file)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to prepare output path: {e}")
            return False

        total = 0
        try:
            logger.debug(f"writing output to : {out_path}")
            with open(out_path, "w", encoding="utf-8") as fh:
                for p in wer_files:
                    rec = self._parse_single_wer_file(p)
                    if rec is None:
                        continue
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    total += 1
        except Exception as e:
            logger.error(f"Failed to write JSONL '{out_path}': {e}")
            return False

        logger.info(f"Wrote {total} WER record(s) to {out_path}")
        return True

    # ---------------------------
    # Internal helpers
    # ---------------------------

    def _parse_single_wer_file(self, path: Path) -> Optional[Dict[str, Any]]:
        """Read and parse a single WER file.

        Attempts UTF-16-LE first (most common), then UTF-8, then Latin-1 as a last resort.

        Args:
            path (Path): Path to a .wer file.

        Returns:
            Optional[Dict[str, Any]]: Final JSON-ready record (with structured fields)
            or None if parsing fails (errors are logged).

        Raises:
            None: Exceptions are caught and logged.
        """
        try:
            try:
                text = path.read_text(encoding="utf-16-le", errors="strict")
            except UnicodeError:
                try:
                    text = path.read_text(encoding="utf-8", errors="strict")
                except UnicodeError:
                    text = path.read_text(encoding="latin-1", errors="replace")
        except Exception as e:
            logger.error(f"Failed to read '{path}': {e}")
            return None

        try:
            nested = self._parse_wer_text(text)
            flat = self._flatten_nested(nested)

            # Build structured fields from numbered keys
            loaded_modules = self._extract_loaded_modules(flat)
            os_info = self._extract_key_value_pairs(flat, OSINFO_RE)
            state = self._extract_key_value_pairs(flat, STATE_RE)
            dyn_raw, dyn_norm = self._extract_dynamic_signatures(flat)

            # Promote common fields (leave originals intact)
            self._add_common_aliases(flat)

            # Problem signatures from PS_ keys (normalized)
            problem_signatures = self._extract_problem_signatures(flat)

            # Start record with scalar fields excluding numbered/handled patterns
            record: Dict[str, Any] = {
                k: v for k, v in flat.items()
                if not (
                    k.startswith("ProblemSignatures.PS_")
                    or DYN_RE.match(k)
                    or OSINFO_RE.match(k)
                    or STATE_RE.match(k)
                    or LMOD_RE.match(k)
                )
            }

            # Nest Response.* under "Response"
            response_fields = {k.split(".", 1)[1]: v for k, v in flat.items()
                               if k.startswith("Response.") and "." in k}
            if response_fields:
                record["Response"] = response_fields

            # Structured fields
            if loaded_modules:
                record["loaded_modules"] = loaded_modules
            if os_info:
                record["os_info"] = os_info
            if state:
                record["state"] = state
            if dyn_norm:
                record["dynamic_signatures"] = dyn_norm
            if dyn_raw:
                record["dynamic_signatures_raw"] = dyn_raw
            if problem_signatures:
                record["problem_signatures"] = problem_signatures

            record["_file"] = str(path)
            return record
        except Exception as e:
            logger.error(f"Failed to parse '{path}': {e}")
            return None

    def _parse_wer_text(self, text: str) -> Dict[str, Any]:
        """Parse raw WER text into a nested dictionary.

        Preserves duplicate keys as lists. Recognizes INI-like sections.
        Pairs Sig[n].Name/Sig[n].Value into PS_<Name> keys inside their section.

        Args:
            text (str): Raw content of a .wer file.

        Returns:
            Dict[str, Any]: Nested mapping of sections to key/value pairs. The root-level
            (no section header) is stored under the key "<root>".

        Raises:
            None: Parsing errors are not expected; any issue results in best-effort parsing.
        """
        data: Dict[str, Any] = {}
        section = "<root>"
        data[section] = {}

        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith(("#", ";")):
                continue

            m = SECTION_RE.match(line)
            if m:
                section = m.group(1).strip()
                data.setdefault(section, {})
                continue

            if "=" in line:
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip()
                target = data.setdefault(section, {})
                if k in target:
                    cur = target[k]
                    if isinstance(cur, list):
                        cur.append(v)
                    else:
                        target[k] = [cur, v]
                else:
                    target[k] = v

        # Pair Sig[n].Name/Value into PS_<Name>
        for sec_name, sec_dict in list(data.items()):
            if not isinstance(sec_dict, dict):
                continue
            sig_pairs: Dict[int, Dict[str, str]] = {}
            for k in list(sec_dict.keys()):
                m = SIG_RE.match(k)
                if m:
                    idx = int(m.group(1))
                    which = m.group(2).capitalize()
                    sig_pairs.setdefault(idx, {})[which] = sec_dict[k]

            for idx, pair in sig_pairs.items():
                name = pair.get("Name", f"Sig[{idx}]")
                val = pair.get("Value", "")
                key = f"PS_{name}".replace(" ", "_")[:120]
                sec_dict[key] = val

            # Remove raw Sig[...] keys after pairing
            for k in list(sec_dict.keys()):
                if SIG_RE.match(k):
                    del sec_dict[k]

        return data

    def _flatten_nested(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten a nested WER mapping into a single-level dict.

        The resulting keys are either the root keys as-is, or Section.Key for values
        that originated under a named section. Lists are joined with ' | '.

        Args:
            data (Dict[str, Any]): Nested mapping produced by _parse_wer_text.

        Returns:
            Dict[str, Any]: Flattened mapping suitable for JSONL/CSV export.

        Raises:
            None
        """
        flat: Dict[str, Any] = {}
        for sec, kv in data.items():
            if not isinstance(kv, dict):
                continue
            for k, v in kv.items():
                if isinstance(v, list):
                    v = " | ".join(map(str, v))
                if sec == "<root>":
                    flat[k] = v
                else:
                    flat[f"{sec}.{k}"] = v
        return flat

    def _add_common_aliases(self, flat: Dict[str, Any]) -> None:
        """Add convenient alias keys for commonly queried fields, if present.

        This does not remove or rename original keys; it only adds short aliases.

        Args:
            flat (Dict[str, Any]): Flattened mapping from _flatten_nested.

        Returns:
            None

        Notes:
            These aliases are heuristic conveniences based on common WER layouts.
            They may not be present in all reports.
        """
        aliases = {
            "EventType": ("EventType",),
            "AppName": ("ProblemSignatures.PS_Application_Name",),
            "AppVersion": ("ProblemSignatures.PS_Application_Version",),
            "FaultModule": ("ProblemSignatures.PS_Fault_Module_Name",),
            "FaultModuleVersion": ("ProblemSignatures.PS_Fault_Module_Version",),
            "ExceptionCode": ("ProblemSignatures.PS_Exception_Code",),
            "ExceptionOffset": ("ProblemSignatures.PS_Exception_Offset",),
            "Bucket": ("ReportInformation.Bucket", "ReportInformation.BucketId"),
        }
        for out_key, candidates in aliases.items():
            for c in candidates:
                if c in flat:
                    flat[out_key] = flat[c]
                    break

    # -------- New structured extractors --------

    def _extract_loaded_modules(self, flat: Dict[str, Any]) -> List[str]:
        """Collect LoadedModule[n] entries into a list, sorted by index.

        Removes the matched keys from `flat`.

        Args:
            flat (Dict[str, Any]): Flat mapping of all fields.

        Returns:
            List[str]: Ordered list of module paths.
        """
        tmp: List[Tuple[int, str]] = []
        for k in list(flat.keys()):
            m = LMOD_RE.match(k)
            if m:
                tmp.append((int(m.group(1)), flat[k]))
                del flat[k]
        tmp.sort(key=lambda x: x[0])
        return [v for _, v in tmp]

    def _extract_key_value_pairs(self, flat: Dict[str, Any], pattern: re.Pattern) -> Dict[str, str]:
        """Collect numbered Key/Value pairs (e.g., OsInfo[n].Key/Value) into a dict.

        Removes the matched keys from `flat`.

        Args:
            flat (Dict[str, Any]): Flat mapping.
            pattern (Pattern): Compiled regex matching keys like 'OsInfo[NN].Key/Value'.

        Returns:
            Dict[str, str]: Mapping from the captured Key to its Value.
        """
        pairs: Dict[int, Dict[str, str]] = {}
        for k in list(flat.keys()):
            m = pattern.match(k)
            if not m:
                continue
            idx = int(m.group(1))
            attr = m.group(2)
            pairs.setdefault(idx, {})[attr] = flat[k]
            del flat[k]

        out: Dict[str, str] = {}
        for idx in sorted(pairs.keys()):
            key = pairs[idx].get("Key")
            val = pairs[idx].get("Value")
            if key is not None and val is not None:
                out[key] = val
        return out

    def _extract_dynamic_signatures(self, flat: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Collect DynamicSig[n].Name/Value into raw and normalized dicts.

        Removes the matched keys from `flat`.

        Args:
            flat (Dict[str, Any]): Flat mapping.

        Returns:
            Tuple[Dict[str, str], Dict[str, str]]: (raw, normalized) dicts.
        """
        pairs: Dict[int, Dict[str, str]] = {}
        for k in list(flat.keys()):
            m = DYN_RE.match(k)
            if not m:
                continue
            idx = int(m.group(1))
            attr = m.group(2)
            pairs.setdefault(idx, {})[attr] = flat[k]
            del flat[k]

        raw: Dict[str, str] = {}
        norm: Dict[str, str] = {}
        for idx in sorted(pairs.keys()):
            name = pairs[idx].get("Name")
            val = pairs[idx].get("Value")
            if name and val is not None:
                raw[name] = val
                norm[_slug(name)] = val
        return raw, norm

    def _extract_problem_signatures(self, flat: Dict[str, Any]) -> Dict[str, str]:
        """Collect ProblemSignatures.PS_* keys into a normalized dict.

        Args:
            flat (Dict[str, Any]): Flat mapping.

        Returns:
            Dict[str, str]: Mapping with slugified keys (e.g., 'application_name').
        """
        out: Dict[str, str] = {}
        for k, v in flat.items():
            if not k.startswith("ProblemSignatures.PS_"):
                continue
            name = k.split("ProblemSignatures.PS_", 1)[1]
            out[_slug(name)] = v
        return out
