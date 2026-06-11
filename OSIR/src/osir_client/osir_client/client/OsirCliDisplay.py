from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box
from typing import Optional
from osir_service.postgres.model.OsirDbTaskModel import OsirDbTaskModel

from osir_api.api.model.OsirApiModuleModel import OsirModuleGroupModel

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
    def task_stats(stats: dict, title: str = "Task statistics") -> None:
        """Render the aggregated stats payload returned by /stats endpoints."""
        total = stats.get("total", 0)
        by_status = stats.get("by_status", {})
        by_module = stats.get("by_module", {})

        # --- global summary with bars ---
        summary = Table(
            title=f"📊 {title}",
            box=box.ROUNDED,
            title_style="bold cyan",
        )
        summary.add_column("Status")
        summary.add_column("Count", justify="right", style="bold white")
        summary.add_column("%", justify="right")
        summary.add_column("", min_width=32)

        for status in ("task_created", "processing_started", "processing_done", "processing_failed"):
            count = by_status.get(status, 0)
            pct = (100.0 * count / total) if total else 0.0
            bar = Text("█" * int(round(pct * 0.3)), style=STATUS_COLORS.get(status, "white"))
            summary.add_row(_status_text(status), str(count), f"{pct:5.1f}%", bar)

        summary.add_section()
        summary.add_row(Text("total", style="bold"), str(total), "", "")
        console.print(summary)

        # --- timing line ---
        def _fmt_duration(seconds) -> str:
            seconds = int(seconds)
            h, rem = divmod(seconds, 3600)
            m, s = divmod(rem, 60)
            if h:
                return f"{h}h {m:02d}m {s:02d}s"
            if m:
                return f"{m}m {s:02d}s"
            return f"{s}s"

        timing = Text()
        if stats.get("first_task_at"):
            timing.append(f"⏱ started: {stats['first_task_at'][:19]} UTC", style="bold")
        if stats.get("duration_seconds") is not None:
            state = "running" if stats.get("running") else "finished"
            style = "yellow" if stats.get("running") else "green"
            timing.append(f"  duration: {_fmt_duration(stats['duration_seconds'])} ", style="bold")
            timing.append(f"({state})", style=style)
            if not stats.get("running") and stats.get("last_finished_at"):
                timing.append(f"  ended: {stats['last_finished_at'][:19]} UTC", style="dim")
        if timing.plain:
            console.print(timing)

        # --- progress / throughput line ---
        done_min = stats.get("done_last_min", 0)
        failed_min = stats.get("failed_last_min", 0)
        pending = by_status.get("task_created", 0) + by_status.get("processing_started", 0)
        line = Text()
        line.append(f"progress: {stats.get('progress_pct', 0.0):.1f}%  ", style="bold green")
        line.append(f"throughput: {done_min}/min", style="cyan")
        if failed_min:
            line.append(f" (+{failed_min} failed/min)", style="red")
        if done_min and pending:
            eta_min = pending / done_min
            line.append(f"  ETA: ~{int(eta_min)} min", style="magenta")
        console.print(line)

        # --- per module breakdown ---
        if by_module:
            modules = Table(
                title="🧩 Per module",
                box=box.SIMPLE_HEAVY,
                title_style="bold cyan",
            )
            modules.add_column("Module", style="magenta")
            modules.add_column("⏳ created", justify="right", style="cyan")
            modules.add_column("🔄 started", justify="right", style="yellow")
            modules.add_column("✅ done", justify="right", style="green")
            modules.add_column("❌ failed", justify="right", style="red")
            modules.add_column("Total", justify="right", style="bold white")

            def _sort_key(item):
                _, c = item
                running = c.get("processing_started", 0) + c.get("task_created", 0)
                return (-running, -c.get("processing_failed", 0), -c.get("total", 0))

            for module, counts in sorted(by_module.items(), key=_sort_key):
                modules.add_row(
                    module,
                    str(counts.get("task_created", 0)),
                    str(counts.get("processing_started", 0)),
                    str(counts.get("processing_done", 0)),
                    str(counts.get("processing_failed", 0)),
                    str(counts.get("total", 0)),
                )
            console.print(modules)

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
    def modules(tree: "OsirModuleGroupModel", title: str = "Modules") -> None:
        """Renders a module tree node recursively. Generic: the category
        column is the directory path, whatever the tree looks like."""
        table = Table(
            title=f"🧩 {title}",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold cyan"
        )
        table.add_column("Category", style="bold cyan", no_wrap=True)
        table.add_column("Module", style="white")

        def _walk(group: "OsirModuleGroupModel", prefix: str) -> None:
            for module in group.modules:
                table.add_row(prefix or "—", module)
            for name in sorted(group.groups):
                _walk(group.groups[name], f"{prefix} / {name}" if prefix else name)

        _walk(tree, "")
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