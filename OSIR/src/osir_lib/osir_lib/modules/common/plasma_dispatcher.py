from __future__ import annotations

import json
import re
from pathlib import Path

from osir_lib.core.OsirDecorator import osir_internal_module
from osir_lib.core.OsirModule import OsirModule
from osir_lib.logger import AppLogger, CustomLogger

logger: CustomLogger = AppLogger().get_logger()


@osir_internal_module
class PlasmaDispatcher():
    """Generic dispatcher running a CERT-EDF plasma dissector on a directory input.

    Plasma (https://github.com/CERT-EDF/plasma) is used as a library rather than
    through its CLI: the CLI only emits gzipped JSONL.

    The dissector to run is taken from module.optional.dissector.

    Example YAML:
        module: wtmp_utmp
        alt_module: plasma_dispatcher
        optional:
            dissector: linux_wtmp_utmp
            exclude_paths:
                - r"\\.db$"

    Optional keys:
        dissector (str):      plasma dissector slug (required)
        exclude_paths (list): regexes; selected artifacts matching any of them
                              are skipped. Needed because a few plasma selectors
                              are broader than the format they parse (e.g.
                              'wtmp*' also matches the unrelated wtmp.db).
        include_paths (list): regexes; when set, only artifacts matching at
                              least one of them are kept.
    """

    def __init__(self, case_path: str, module: OsirModule) -> None:
        self.module = module
        self.case_path = case_path

    @staticmethod
    def _compile(patterns) -> list:
        """Compile a YAML regex list, tolerating the r"..." quoting used in configs."""
        compiled = []
        for pattern in patterns or []:
            pattern = str(pattern)
            if pattern.startswith(('r"', "r'")):
                pattern = pattern[2:-1]
            try:
                compiled.append(re.compile(pattern))
            except re.error as exc:
                logger.warning(f"Ignoring invalid regex '{pattern}': {exc}")
        return compiled

    def __call__(self) -> bool:
        optional = self.module.optional if isinstance(self.module.optional, dict) else {}

        dissector_slug = optional.get("dissector")
        if not dissector_slug:
            logger.error("No plasma dissector specified in optional.dissector")
            return False

        input_path = self.module.input.match
        if not input_path:
            logger.error("input.match is empty")
            return False

        try:
            # Importing the package registers every bundled dissector.
            import edf_plasma_dissectors  # noqa: F401
            from edf_plasma_core.dissector import (
                DissectionContext,
                get_dissector_or_none,
            )
        except ImportError as exc:
            logger.error(f"[!] plasma is not installed in this agent image: {exc}")
            return False

        dissector = get_dissector_or_none(dissector_slug)
        if dissector is None:
            logger.warning(
                f"[i] plasma dissector '{dissector_slug}' is not registered "
                f"(missing optional dependency?), nothing to do"
            )
            return True

        target = Path(str(input_path))
        excludes = self._compile(optional.get("exclude_paths"))
        includes = self._compile(optional.get("include_paths"))

        try:
            dissector.set_state(target)
        except Exception as exc:
            logger.error(f"[!] Failed to initialise dissector '{dissector_slug}' state: {exc}")
            return False

        out_path = self.module.output.output_file
        logger.debug(f"Running plasma dissector '{dissector_slug}' on: {target}")

        selected = 0
        skipped = 0
        records = 0
        errors = 0

        try:
            with open(out_path, "w", encoding="utf-8") as fh:
                for artifact in dissector.select(target):
                    artifact_str = str(artifact)

                    if excludes and any(rex.search(artifact_str) for rex in excludes):
                        skipped += 1
                        continue
                    if includes and not any(rex.search(artifact_str) for rex in includes):
                        skipped += 1
                        continue

                    selected += 1
                    ctx = DissectionContext(
                        dissector=dissector.slug,
                        hostname=self.module.endpoint_name or "UNKNOWN",
                        source=artifact_str,
                        filepath=artifact,
                        state=dissector.state,
                    )

                    for record in dissector.dissect(ctx):
                        fh.write(json.dumps(record, separators=(',', ':'), default=str))
                        fh.write("\n")
                        records += 1

                    errors += len(ctx.errors)
                    for error in ctx.errors:
                        logger.warning(f"[!] {dissector_slug}: {error.reason}")
        except Exception as exc:
            logger.error(f"Failed to write JSONL '{out_path}': {exc}")
            return False

        logger.debug(
            f"{dissector_slug} done: artifacts={selected} skipped={skipped} "
            f"records={records} errors={errors} -> {out_path}"
        )
        return True
