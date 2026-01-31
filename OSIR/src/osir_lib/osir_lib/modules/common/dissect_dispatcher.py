from __future__ import annotations
import os

from osir_lib.core.OsirDecorator import osir_internal_module
from osir_lib.core.OsirModule import OsirModule
from osir_lib.logger import AppLogger, CustomLogger

from dissect.target import Target
from flow.record.jsonpacker import JsonRecordPacker
from dissect.target.exceptions import TargetError, LoaderError, TargetPathNotFoundError, UnsupportedPluginError, PluginNotFoundError

logger: CustomLogger = AppLogger().get_logger()

@osir_internal_module
class DissectDispatcher():
    """
    Generic dispatcher to run dissect plugins on a directory input and write JSONL output.

    The plugin to run is taken from:
      - module.optional.plugin (preferred)

    Example YAML:
      module: activites_cache
      alt_module: dissect_dispatcher
      optional:
        plugin: activitiescache

    This will call:  t.activitiescache() on a Target opened on the input dir.
    """

    def __init__(self, case_path: str, module: OsirModule) -> None:
        self.module = module
        self.case_path = case_path


    def __call__(self) -> bool:

        # plugin key
        plugin_name = None
        if isinstance(self.module.optional, dict):
            plugin_name = self.module.optional.get("plugin")
        if not plugin_name:
            logger.error("No dissect plugin specified in optional.plugin")
            return False
        
        # Handle input dir
        if self.module.input.type != "dir":
            logger.error(f"Unsupported input type {self.module.input.type}")
            return False
        input_path = self.module.input.match
        if not input_path:
            logger.error("input.dir is empty")
            return False
        
        # Open target
        logger.debug(f"Opening dissect Target on: {input_path}")
        try:
            t = Target.open(input_path)
        except TargetPathNotFoundError as e:
            logger.error(f"[!] Target path not found: {input_path} ({e})")
            return False
        except LoaderError as e:
            logger.error(f"[!] Could not recognize target at {input_path}: {e}")
            return False
        except TargetError as e:
            logger.error(f"[!] Target error opening {input_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"[!] Unexpected error opening target {input_path}: {e}")
            return False

        # Run plugin on Target
        packer = JsonRecordPacker(indent=None)

        try:
            logger.debug(f"Running dissect Target method plugin '{plugin_name}'")
            iterator = getattr(t, plugin_name)()
        except UnsupportedPluginError as e:
            msg = e.root_cause_str() if hasattr(e, "root_cause_str") else str(e)
            logger.error(f"[i] 'activitiescache' plugin not supported for this target: {msg}")
            return True
        except PluginNotFoundError as e:
            logger.error(f"[i] 'activitiescache' plugin not available in this dissect install: {e}")
            return True
        except Exception as e:
            logger.error(f"[!] Error initialising 'activitiescache' plugin: {e}")
            return False

        # Construct output file
        out_path = self.module.output.output_file
        # stem = os.path.splitext(os.path.basename(input_path))[0]

        # try:
        #     if self.module.output.output_file:
        #         self._format_output_file()
        #         out_path = os.path.join(self.default_output_dir, self.module.output.output_file)
        #         os.makedirs(os.path.dirname(out_path), exist_ok=True)
        #     else:
        #         # Default: write in module dir
        #         os.makedirs(self.default_output_dir, exist_ok=True)
        #         out_path = os.path.join(self.default_output_dir, f"{stem}.jsonl")
        # except Exception as e:
        #     logger.error(f"Failed to prepare output path: {e}")
        #     return False
        
        # Write output file
        try:
            logger.debug(f"Writing dissect output to: {out_path}")
            with open(out_path, "w", encoding="utf-8") as fh:
                for obj in iterator:
                    line = packer.pack(obj) 
                    fh.write(line + "\n")
        except Exception as e:
            logger.error(f"Failed to write JSONL '{out_path}': {e}")
            return False

        return True