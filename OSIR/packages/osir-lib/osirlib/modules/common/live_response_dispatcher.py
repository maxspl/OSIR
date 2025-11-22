from __future__ import annotations
import os
from typing import Callable, Dict
from osirlib.core.BaseModule import BaseModule
from osirlib.core.PyModule import PyModule
from osirlib.logger import AppLogger, CustomLogger

# Import all parsers
from osirlib.modules.windows.live_response.arp_cache_parser import ArpCacheParser
from osirlib.modules.windows.live_response.bits_jobs_parser import BitsJobsParser
from osirlib.modules.windows.live_response.dns_cache_parser import DnsCacheParser
from osirlib.modules.windows.live_response.dns_records_parser import DnsRecordsParser
from osirlib.modules.windows.live_response.enumlocs_parser import EnumLocsParser
from osirlib.modules.windows.live_response.handle_parser import HandleParser
from osirlib.modules.windows.live_response.listdlls_parser import ListDllsParser
from osirlib.modules.windows.live_response.netstat_parser import NetstatParser
from osirlib.modules.windows.live_response.routes_parser import RoutesParser
from osirlib.modules.windows.live_response.tcpvcon_parser import TcpvconParser
from osirlib.modules.windows.live_response.wmi_eventconsumer_parser import WmiEventConsumerParser

logger: CustomLogger = AppLogger().get_logger()

# map parsers to optional.parser field in config files
PARSER_MAP: Dict[str, Callable[[str], list]] = {
    "bits_jobs": BitsJobsParser().parse,
    "dns_cache": DnsCacheParser().parse,
    "dns_records": DnsRecordsParser().parse,
    "enumlocs": EnumLocsParser().parse,
    "handle": HandleParser().parse,
    "listdlls": ListDllsParser().parse,
    "netstat": NetstatParser().parse,
    "routes": RoutesParser().parse,
    "tcpvcon": TcpvconParser().parse,
    "wmi_eventconsumer": WmiEventConsumerParser().parse,
    "arp_cache": ArpCacheParser().parse,
}


class WinLiveResponseDispatcher(PyModule):
    """
    Minimal dispatcher: single-file input, JSONL output.
    Uses PyModule's _format_output_file/_format_output_dir when provided.
    """

    def __init__(self, case_path: str, module: BaseModule) -> None:
        super().__init__(case_path, module)

    def __call__(self) -> bool:
        # parser key
        parser_key = None
        if isinstance(self.module.optional, dict):
            parser_key = self.module.optional.get("parser")
        if not parser_key:
            logger.error("No parser specified in optional.parser")
            return False

        parser = PARSER_MAP.get(parser_key)
        if not parser:
            logger.error(f"Unsupported parser {parser_key}")
            return False

        # Handle input file
        if self.module.input.type != "file":
            logger.error(f"Unsupported input type {self.module.input.type}")
            return False
        input_path = self.module.input.file
        if not input_path:
            logger.error("input.file is empty")
            return False

        # Read input (utf-8 with latin-1 fallback)
        try:
            try:
                with open(input_path, "r", encoding="utf-8") as fh:
                    text = fh.read()
            except UnicodeDecodeError:
                with open(input_path, "r", encoding="latin-1") as fh:
                    text = fh.read()
        except Exception as e:
            logger.error(f"Failed to read input '{input_path}': {e}")
            return False

        # Parse
        try:
            records = parser(text) 
        except Exception as e:
            logger.error(f"Parser '{parser_key}' failed: {e}")
            return False

        # Construct output file
        out_path = None
        stem = os.path.splitext(os.path.basename(input_path))[0]

        try:
            if self.module.output.output_file:
                self._format_output_file()
                out_path = os.path.join(self.default_output_dir, self.module.output.output_file)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
            else:
                # Default: write in module dir
                os.makedirs(self.default_output_dir, exist_ok=True)
                out_path = os.path.join(self.default_output_dir, f"{stem}.jsonl")
        except Exception as e:
            logger.error(f"Failed to prepare output path: {e}")
            return False

        # Write JSONL
        try:
            logger.debug(f"writing output to : {out_path}")
            with open(out_path, "w", encoding="utf-8") as fh:
                fh.write(records)
        except Exception as e:
            logger.error(f"Failed to write JSONL '{out_path}': {e}")
            return False

        return True