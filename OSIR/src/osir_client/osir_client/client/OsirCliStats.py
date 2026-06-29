"""
Interactive task-statistics navigator for OSIR.

Lets an analyst browse cases, list their handlers (running first), select a
handler (or the whole case) and display aggregated task statistics computed
server-side: counts per status, per-module breakdown, throughput and ETA.
Supports a watch mode that refreshes the view periodically.

All data is fetched through the OSIR REST API via OsirClient:
    GET  /api/case                       -> cases
    POST /api/case/{name}/handler        -> handlers of a case
    POST /api/handler/{id}/stats         -> stats for one handler
    GET  /api/case/{name}/stats          -> stats for a whole case
"""
from __future__ import annotations

import time
from typing import TYPE_CHECKING, List, Optional

from rich.console import Console
from rich.text import Text

from osir_api.api.model.OsirApiCaseModel import GetCaseListResponse, GetCaseHandlerResponse
from osir_api.api.model.OsirApiTaskModel import GetTaskStatsResponse
from osir_client.client.OsirCliDisplay import OsirCliDisplay, _status_text

from osir_lib.logger import AppLogger
from osir_lib.logger.logger import CustomLogger

if TYPE_CHECKING:
    from osir_client.client.OsirClient import OsirClient

logger: CustomLogger = AppLogger(__name__).get_logger()
console = Console()

_ACTIVE_STATUSES = ("processing_started", "task_created")


class OsirCliStats:
    """Interactive and one-shot statistics views on cases/handlers."""

    def __init__(self, api: "OsirClient"):
        self._api = api

    # ------------------------------------------------------------------ #
    # API fetchers
    # ------------------------------------------------------------------ #

    def _fetch_cases(self) -> list:
        response: GetCaseListResponse = self._api.get(
            "/api/case", response_model=GetCaseListResponse
        )
        return response.response or []

    def _fetch_handlers(self, case_name: str) -> list:
        response: GetCaseHandlerResponse = self._api.post(
            f"/api/case/{case_name}/handler", response_model=GetCaseHandlerResponse
        )
        handlers = response.response or []
        if not isinstance(handlers, list):
            handlers = [handlers]
        # Running handlers first, then most recent first.
        def _key(h):
            running = 0 if h.processing_status in _ACTIVE_STATUSES else 1
            created = getattr(h, "created_at", None)
            return (running, -(created.timestamp() if created else 0))
        return sorted(handlers, key=_key)

    def _fetch_handler_stats(self, handler_id: str) -> dict:
        response: GetTaskStatsResponse = self._api.post(
            f"/api/handler/{handler_id}/stats", response_model=GetTaskStatsResponse
        )
        return response.response or {}

    def _fetch_case_stats(self, case_name: str) -> dict:
        response: GetTaskStatsResponse = self._api.get(
            f"/api/case/{case_name}/stats", response_model=GetTaskStatsResponse
        )
        return response.response or {}

    # ------------------------------------------------------------------ #
    # One-shot / watch display (also used by the non-interactive CLI)
    # ------------------------------------------------------------------ #

    def show(
        self,
        case_name: Optional[str] = None,
        handler_id: Optional[str] = None,
        watch: Optional[int] = None,
    ) -> None:
        """Display stats for a handler (priority) or a whole case.

        Args:
            case_name: case scope when no handler_id is given.
            handler_id: handler scope.
            watch: refresh interval in seconds; None = render once.
        """
        if not case_name and not handler_id:
            logger.error("show() requires a case name or a handler id")
            return

        if handler_id:
            fetch = lambda: self._fetch_handler_stats(handler_id)  # noqa: E731
            title = f"Handler {handler_id}"
        else:
            fetch = lambda: self._fetch_case_stats(case_name)  # noqa: E731
            title = f"Case {case_name}"

        try:
            while True:
                stats = fetch()
                if watch:
                    console.clear()
                OsirCliDisplay.task_stats(stats, title=title)
                if not watch:
                    return
                console.print(
                    Text(f"refresh every {watch}s — Ctrl+C to stop", style="dim italic")
                )
                time.sleep(watch)
        except KeyboardInterrupt:
            console.print()

    # ------------------------------------------------------------------ #
    # Interactive navigation
    # ------------------------------------------------------------------ #

    def run_interactive(self) -> None:
        """Cases -> handlers -> stats navigation loop."""
        try:
            while True:
                case = self._select_case()
                if case is None:
                    return
                self._handler_screen(case)
        except KeyboardInterrupt:
            console.print()

    # ----- screens ----------------------------------------------------- #

    def _select_case(self):
        cases = self._fetch_cases()
        if not cases:
            console.print("[red]No case found.[/red]")
            return None

        console.print()
        console.rule("[bold cyan]📁 Cases")
        for idx, case in enumerate(cases, start=1):
            console.print(f"  [bold]{idx}[/bold]. {case.name} [dim]{case.case_uuid}[/dim]")

        choice = self._ask("case number, or q to quit")
        if choice in ("q", None):
            return None
        index = self._to_index(choice, len(cases))
        if index is None:
            return self._select_case()
        return cases[index]

    def _handler_screen(self, case) -> None:
        while True:
            handlers = self._fetch_handlers(case.name)

            console.print()
            console.rule(f"[bold cyan]⚙️  Handlers — case {case.name}")
            if not handlers:
                console.print("[yellow]No handler on this case yet.[/yellow]")
            for idx, h in enumerate(handlers, start=1):
                line = Text(f"  {idx}. ")
                line.append(str(h.handler_id), style="dim")
                line.append("  ")
                line.append_text(_status_text(h.processing_status))
                line.append(f"  {len(h.task_id or [])} tasks", style="blue")
                modules = ", ".join(h.modules or [])
                if modules:
                    line.append(f"  [{modules}]", style="magenta")
                if getattr(h, "created_at", None):
                    line.append(f"  {h.created_at:%Y-%m-%d %H:%M}", style="dim")
                console.print(line)

            choice = self._ask("handler number | a = whole case | r = refresh | b = back | q = quit")
            if choice == "q":
                raise KeyboardInterrupt
            if choice in ("b", None):
                return
            if choice == "r":
                continue
            if choice == "a":
                self._stats_screen(case=case)
                continue
            index = self._to_index(choice, len(handlers))
            if index is not None:
                self._stats_screen(case=case, handler=handlers[index])

    def _stats_screen(self, case, handler=None) -> None:
        while True:
            if handler is not None:
                stats = self._fetch_handler_stats(str(handler.handler_id))
                title = f"Handler {handler.handler_id} — case {case.name}"
            else:
                stats = self._fetch_case_stats(case.name)
                title = f"Case {case.name} (all handlers)"

            console.print()
            OsirCliDisplay.task_stats(stats, title=title)

            choice = self._ask("r = refresh | w = watch (5s) | b = back | q = quit")
            if choice == "q":
                raise KeyboardInterrupt
            if choice in ("b", None):
                return
            if choice == "w":
                self.show(
                    case_name=case.name,
                    handler_id=str(handler.handler_id) if handler is not None else None,
                    watch=5,
                )
            # 'r' or anything else: loop and re-render

    # ----- input helpers ------------------------------------------------ #

    @staticmethod
    def _ask(prompt: str) -> Optional[str]:
        try:
            value = console.input(f"[bold cyan]>[/bold cyan] {prompt}: ").strip().lower()
            return value or None
        except EOFError:
            return "q"

    @staticmethod
    def _to_index(choice: Optional[str], length: int) -> Optional[int]:
        try:
            index = int(choice) - 1
            if 0 <= index < length:
                return index
        except (TypeError, ValueError):
            pass
        console.print("[red]Invalid choice.[/red]")
        return None
