import re
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Timestamp patterns — ordonnés par priorité (1 = meilleur / plus précis)
# Chaque entrée : (priorité, nom, regex compilée, liste de strptime formats)
# fmt_list=None → parser spécial géré dans _parse_timestamp()
# ---------------------------------------------------------------------------
_TIMESTAMP_PATTERNS = [
    # ── Priorité 1-2 : ISO 8601 ─────────────────────────────────────────────
    # 2024-01-15T14:23:01.123456+00:00  /  2024-01-15T14:23:01Z
    (1, "iso8601_tz",
     re.compile(r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2}))'),
     ["%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z",
      "%Y-%m-%d %H:%M:%S.%f%z", "%Y-%m-%d %H:%M:%S%z"]),

    # 2024-01-15T14:23:01  /  2024-01-15 14:23:01,123
    (2, "iso8601",
     re.compile(r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?)'),
     ["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S",
      "%Y-%m-%d %H:%M:%S,%f", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"]),

    # ── Priorité 3 : Apache / Nginx ─────────────────────────────────────────
    # [15/Jan/2024:14:23:01 +0000]
    (3, "apache",
     re.compile(r'\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} [+-]\d{4})\]'),
     ["%d/%b/%Y:%H:%M:%S %z"]),

    # ── Priorité 4 : RFC 2822 ───────────────────────────────────────────────
    # Mon, 15 Jan 2024 14:23:01 +0000
    (4, "rfc2822",
     re.compile(r'(\w{3},\s+\d{1,2}\s+\w{3}\s+\d{4}\s+\d{2}:\d{2}:\d{2}\s+[+-]\d{4})'),
     ["%a, %d %b %Y %H:%M:%S %z"]),

    # ── Priorité 5 : ctime() ────────────────────────────────────────────────
    # Mon Jan 15 14:23:01 2024  /  Mon Jan 15 14:23:01.123 2024
    (5, "ctime",
     re.compile(r'(\w{3}\s+\w{3}\s{1,2}\d{1,2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?\s+\d{4})'),
     ["%a %b %d %H:%M:%S %Y", "%a %b  %d %H:%M:%S %Y",
      "%a %b %d %H:%M:%S.%f %Y", "%a %b  %d %H:%M:%S.%f %Y"]),

    # ── Priorité 6 : Oracle / old-Unix ──────────────────────────────────────
    # 15-Jan-2024 14:23:01  /  15-Jan-2024:14:23:01
    (6, "oracle_date",
     re.compile(r'(\d{2}-\w{3}-\d{4}[: ]\d{2}:\d{2}:\d{2})'),
     ["%d-%b-%Y %H:%M:%S", "%d-%b-%Y:%H:%M:%S"]),

    # ── Priorité 7 : Syslog avec année ──────────────────────────────────────
    # 2024 Jan 15 14:23:01
    (7, "syslog_year",
     re.compile(r'(\d{4}\s+\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})'),
     ["%Y %b %d %H:%M:%S"]),

    # ── Priorité 8 : Syslog avec ms/µs ──────────────────────────────────────
    # Jan 15 14:23:01.123  /  *Jan 15 14:23:01.123 (Cisco IOS)
    (8, "syslog_ms",
     re.compile(r'[*.]?\s*(\w{3}\s{1,2}\d{1,2}\s+\d{2}:\d{2}:\d{2}\.\d+)'),
     ["%b %d %H:%M:%S.%f", "%b  %d %H:%M:%S.%f"]),

    # ── Priorité 9 : Syslog standard ────────────────────────────────────────
    # Jan 15 14:23:01  /  Jan  5 09:01:00
    (9, "syslog",
     re.compile(r'(\w{3}\s{1,2}\d{1,2}\s+\d{2}:\d{2}:\d{2})'),
     ["%b %d %H:%M:%S", "%b  %d %H:%M:%S"]),

    # ── Priorité 10 : Date slash avec heure (US ou EU) ──────────────────────
    # 01/15/2024 14:23:01  /  15/01/2024 14:23:01.123
    (10, "date_slash",
     re.compile(r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?)'),
     ["%m/%d/%Y %H:%M:%S.%f", "%m/%d/%Y %H:%M:%S",
      "%d/%m/%Y %H:%M:%S.%f", "%d/%m/%Y %H:%M:%S"]),

    # ── Priorité 11 : Date tiret US ─────────────────────────────────────────
    # 01-15-2024 14:23:01
    (11, "date_dash",
     re.compile(r'(\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}:\d{2})'),
     ["%m-%d-%Y %H:%M:%S", "%d-%m-%Y %H:%M:%S"]),

    # ── Priorité 12 : Android logcat ────────────────────────────────────────
    # 01-15 14:23:01.123
    (12, "android_logcat",
     re.compile(r'\b(\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d+)'),
     ["%m-%d %H:%M:%S.%f"]),

    # ── Priorité 13 : TAI64N (qmail, daemontools, s6) ───────────────────────
    # @4000000065a5b1e30a2b9a7c
    (13, "tai64n",
     re.compile(r'(@[0-9a-f]{24})\b'),
     None),  # parser spécial

    # ── Priorité 14 : Epoch float ────────────────────────────────────────────
    # 1705329781.123
    (14, "epoch_float",
     re.compile(r'\b(\d{10}\.\d+)\b'),
     None),  # parser spécial

    # ── Priorité 15 : Epoch int ──────────────────────────────────────────────
    # 1705329781
    (15, "epoch_int",
     re.compile(r'\b(\d{10})\b'),
     None),  # parser spécial
]



from osir_lib.core.OsirDecorator import osir_internal_module
from osir_lib.core.LogUtils import LogUtils
from osir_lib.core.OsirModule import OsirModule
from osir_lib.logger import AppLogger, CustomLogger
from pathlib import Path
from dissect.database.sqlite3.sqlite3 import SQLite3

logger: CustomLogger = AppLogger().get_logger()
 

@osir_internal_module
class SqliteModule(LogUtils):
    """
    PyModule to perform processing operations on Audit logs.
    """

    def __init__(self, module: OsirModule):
        """
        Initializes the Module.

        Args:
            case_path (str): The directory path where case files are stored and operations are performed.
            module (OsirModule): Instance of OsirModule containing configuration details for the extraction process.
        """
        self.module = module
        LogUtils.__init__(self, ctx=module)
        self._file_to_process = module.input.match

    def __call__(self) -> bool:
        """
        Execute the internal processor of the module.
        Returns:
            bool: True if the processing completes successfully, False otherwise.
        """
        try:
            logger.debug(f"Processing Started: \n File Input: {self.module.input.file} \n")

            writer_queue = self.start_writer_thread()

            for line in self.get_log():
                if not line.strip():
                    continue
                writer_queue.put(self.parse_line(line))

            writer_queue.put(None)

            logger.debug(f"Processing Done: \n File Input: {self.module.input.file} \n")

        except Exception as exc:
            logger.error_handler(exc)
            return False

        return True
    

    # ---------------------------------------------------------------------------
    # Parser
    # ---------------------------------------------------------------------------

    def _parse_timestamp(self, raw: str, fmt_list: list | None, name: str) -> datetime | None:
        """Convertit la chaîne brute en datetime selon le type de pattern."""
        if name == "tai64n":
            # TAI64N : @<16 hex = secondes TAI><8 hex = nanosecondes>
            # TAI epoch = Unix epoch + 2^62
            try:
                secs = int(raw[1:17], 16) - (2 ** 62)
                return datetime.fromtimestamp(secs, tz=timezone.utc)
            except (ValueError, OSError):
                return None

        if name in ("epoch_float", "epoch_int"):
            try:
                return datetime.fromtimestamp(float(raw), tz=timezone.utc)
            except (ValueError, OSError):
                return None

        normalized = raw.replace("Z", "+00:00")
        for fmt in fmt_list:
            try:
                s = normalized.replace(",", ".") if "%f" in fmt else normalized
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        return None


    def parse_line(self, line: str) -> dict:
        """
        Analyse une ligne de log et retourne un dict avec :
        - timestamp_raw  : chaîne brute trouvée (None si absent)
        - timestamp      : datetime ISO 8601 str (None si absent ou non parseable)
        - timestamp_fmt  : nom du format détecté (None si absent)
        - message        : reste de la ligne après le timestamp
        """
        line = line.rstrip("\n\r")

        best_priority = None
        best_match = None
        best_name = None
        best_fmts = None

        for priority, name, pattern, fmts in _TIMESTAMP_PATTERNS:
            m = pattern.search(line)
            if m and (best_priority is None or priority < best_priority):
                best_priority = priority
                best_match = m
                best_name = name
                best_fmts = fmts

        if best_match is None:
            return {
                "timestamp_raw": None,
                "timestamp": None,
                "timestamp_fmt": None,
                "message": line,
            }

        raw_ts = best_match.group(1)
        dt = self._parse_timestamp(raw_ts, best_fmts, best_name)
        message = line[best_match.end():].lstrip(" :-")

        return {
            "timestamp_raw": raw_ts,
            "timestamp": dt.isoformat() if dt else None,
            "timestamp_fmt": best_name,
            "message": message,
        }