from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box
from typing import Optional
from osir_service.postgres.model.OsirDbTaskModel import OsirDbTaskModel

from osir_api.api.model.OsirApiModuleModel import OsirModuleTreeModel, OsirModuleOsGroupModel, OsirModuleSubGroupModel

console = Console()

STATUS_COLORS = {
    "task_created":        "cyan",    # noqa: E241
    "processing_started":  "yellow",  # noqa: E241
    "processing_done":     "green",   # noqa: E241
    "processing_failed":   "red",     # noqa: E241
}


def _status_text(status: Optional[str]) -> Text:
    color = STATUS_COLORS.get(status, "white")
    icons = {
        "task_created":         "⏳",   # noqa: E241
        "processing_started":   "🔄",   # noqa: E241
        "processing_done":      "✅",   # noqa: E241
        "processing_failed":    "❌",   # noqa: E241
    }
    icon = icons.get(status, "•")
    return Text(f"{icon} {status or 'N/A'}", style=color)


class OsirCliDisplay:

    @staticmethod
    def cases(cases: list) -> None:
        table = Table(
            title="📁 Cases",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold cyan"
        )
        table.add_column("UUID", style="dim", no_wrap=True)
        table.add_column("Name", style="bold white")

        for case in cases:
            table.add_row(str(case.case_uuid), case.name)

        console.print(table)

    @staticmethod
    def handlers(handlers: list, title: str = "Handlers") -> None:
        table = Table(
            title=f"⚙️  {title}",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold cyan"
        )
        table.add_column("Handler ID", style="dim", no_wrap=True)
        table.add_column("Case UUID", style="dim", no_wrap=True)
        table.add_column("Status")
        table.add_column("Modules", style="magenta")
        table.add_column("Tasks", style="blue")

        for h in handlers:
            table.add_row(
                str(h.handler_id),
                str(h.case_uuid),
                _status_text(h.processing_status),
                ", ".join(h.modules) or "N/A",
                str(len(h.task_id))
            )

        console.print(table)

    @staticmethod
    def tasks(tasks: list) -> None:
        table = Table(
            title="📋 Tasks",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold cyan"
        )
        table.add_column("Task ID", style="dim", no_wrap=True)
        table.add_column("Module", style="bold white")
        table.add_column("Agent", style="magenta")
        table.add_column("Status")
        table.add_column("Timestamp", style="dim")

        for task in tasks:
            table.add_row(
                str(task.task_id),
                task.module,
                task.agent,
                _status_text(task.processing_status),
                str(task.timestamp)
            )

        console.print(table)

    @staticmethod
    def modules(tree: OsirModuleTreeModel) -> None:

        def _add_modules(table: Table, category: str, subcategory: str, modules: list[str]) -> None:
            for module in modules:
                table.add_row(category, subcategory, module)

        def _render_os_group(table: Table, category: str, group: OsirModuleOsGroupModel) -> None:
            # Top-level OS modules
            _add_modules(table, category, "—", group.modules)

            # dissect subgroup
            if getattr(group, "dissect", None):
                _add_modules(table, category, "dissect", group.dissect.modules)

            # live_response subgroup
            if getattr(group, "live_response", None):
                lr = group.live_response
                _add_modules(table, category, "live_response", lr.modules)

                # live_response nested subgroups (unix only)
                for subgroup_name in ["packages", "storage", "process", "network", "hardware", "system"]:
                    subgroup = getattr(lr, subgroup_name, None)
                    if subgroup:
                        _add_modules(table, category, f"live_response / {subgroup_name}", subgroup.modules)

        def _render_flat_group(table: Table, category: str, group: OsirModuleSubGroupModel) -> None:
            _add_modules(table, category, "—", group.modules)

        table = Table(
            title="🧩 Modules",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold cyan"
        )
        table.add_column("Category", style="bold cyan", no_wrap=True)
        table.add_column("Subcategory", style="magenta")
        table.add_column("Module", style="white")

        # Top-level ungrouped modules
        _add_modules(table, "—", "—", tree.modules)

        # OS groups (windows / unix)
        for os_name in ["windows", "unix"]:
            group = getattr(tree, os_name, None)
            if group:
                _render_os_group(table, os_name, group)

        # Flat groups
        for category_name in ["splunk", "scan", "network", "pre_process", "test"]:
            group = getattr(tree, category_name, None)
            if group:
                _render_flat_group(table, category_name, group)

        console.print(table)

    @staticmethod
    def modules_flat(
            modules: list[str],
            category: str,
            subcategory: Optional[str] = None,
            subsubcategory: Optional[str] = None
    ) -> None:
        parts = [p for p in [category, subcategory, subsubcategory] if p]
        title = " / ".join(parts)

        table = Table(
            title=f"🧩 Modules — {title}",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold cyan"
        )
        table.add_column("Module", style="white")

        for module in modules:
            table.add_row(module)

        console.print(table)

    @staticmethod
    def profiles(profiles: list) -> None:
        table = Table(
            title="📑 Profiles",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold cyan"
        )
        table.add_column("Name", style="bold white")

        for profile in profiles:
            table.add_row(profile)

        console.print(table)
    
    @staticmethod
    def task_info(task: OsirDbTaskModel) -> None:
        from rich.panel import Panel

        console = Console()

        # --- Main Info Table ---
        table = Table(box=box.ROUNDED, show_header=False, title="📋 Task Info", title_style="bold cyan")
        table.add_column("Field", style="bold cyan", no_wrap=True)
        table.add_column("Value", style="white")

        table.add_row("Task ID",    str(task.task_id))                      # noqa: E241
        table.add_row("Case UUID",  str(task.case_uuid))                    # noqa: E241
        table.add_row("Agent",      task.agent)                             # noqa: E241
        table.add_row("Module",     task.module)                            # noqa: E241
        table.add_row("Input",      task.input)                             # noqa: E241
        table.add_row("Output",     task.output or "N/A")                   # noqa: E241
        table.add_row("Status",     _status_text(task.processing_status))   # noqa: E241
        table.add_row("Timestamp",  str(task.timestamp))                    # noqa: E241

        console.print(table)

        # --- Trace Panel ---
        if task.trace:
            trace = task.trace

            # Timing table
            timing_table = Table(box=box.SIMPLE, show_header=False)
            timing_table.add_column("Field", style="bold magenta")
            timing_table.add_column("Value", style="white")

            timing_table.add_row("Function",  trace.get("function", "N/A"))                 # noqa: E241
            timing_table.add_row("Start",     trace.get("start_time", "N/A"))               # noqa: E241
            timing_table.add_row("End",       trace.get("end_time", "N/A"))                 # noqa: E241
            timing_table.add_row("Duration",  f"{trace.get('duration_seconds', 'N/A')}s")   # noqa: E241

            console.print(Panel(timing_table, title="⏱️  Trace", border_style="magenta"))

            # Logs
            if trace.get("logs"):
                log_colors = {
                    "[DEBUG]":      "dim white",    # noqa: E241
                    "[INFO]":       "green",        # noqa: E241
                    "[WARNING]":    "yellow",       # noqa: E241
                    "[ERROR]":      "bold red",     # noqa: E241
                }

                log_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
                log_table.add_column("Level", no_wrap=True, width=10)
                log_table.add_column("Message", style="white")

                for log_line in trace["logs"]:
                    level = "UNKNOWN"
                    color = "white"
                    for key, col in log_colors.items():
                        if key in log_line:
                            level = key.strip("[]")
                            color = col
                            break
                    log_table.add_row(Text(level, style=color), log_line)

                console.print(Panel(log_table, title="📜 Logs", border_style="blue"))