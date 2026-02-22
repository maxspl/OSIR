#!/usr/bin/env python3
"""
This script provides a single entry point for OSIR setup.
It wraps the existing Bash setup scripts and exposes a Python interface.
====================================================================================

Classes description:
- DockerClient: Shells out to docker and parses results (easy to mock).
- BoxPrinter: All banner/box UI rendering in one place.
- ProcessRunner: Helpers to stream/attach child processes.
- Component: Parameterized behavior for MASTER/AGENT (install/start/stop/status).
- Launcher: CLI parsing, sudo elevation, config reuse/new prompts, dispatch.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from shutil import get_terminal_size
from typing import Iterable, List, Tuple, Dict, Optional
from contextlib import contextmanager
import hashlib
# Optional wide-character support for perfect box alignment with emojis/Unicode.
try:
    # pip install wcwidth
    from wcwidth import wcswidth as _wcswidth  # type: ignore
except Exception:
    def _wcswidth(s: str) -> int:
        """Fallback width calculation using len() when wcwidth is unavailable.

        Args:
            s: Input string.

        Returns:
            int: Estimated display width equal to len(s).
        """
        return len(s)

# ────────────────────────────────────────────────────────────────────────────────
# UI constants
# ────────────────────────────────────────────────────────────────────────────────
BORDER = "─"
TITLE_L = "┌"
TITLE_R = "┐"
MID_L = "├"
MID_R = "┤"
BOX_V = "│"
BOX_B_L = "└"
BOX_B_R = "┘"


# ────────────────────────────────────────────────────────────────────────────────
# Utilities
# ────────────────────────────────────────────────────────────────────────────────
def pretty_yaml_or_text(path: Path) -> str:
    """Render a file as pretty YAML if possible, otherwise return plain text.

    Attempts to load the file as YAML and dump it with stable key order. When
    loading fails or the content is not valid YAML, returns the raw file text.

    Args:
        path: Path to a YAML or text file.

    Returns:
        str: Human-friendly YAML dump or raw text.
    """
    try:
        import yaml  # lazy import; optional dependency for nicer previews
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data is None:
            return Path(path).read_text(encoding="utf-8")
        return yaml.safe_dump(data, sort_keys=False)
    except Exception:
        return Path(path).read_text(encoding="utf-8")


def format_ports(ports_raw: str) -> str:
    """Convert Docker inspect ports JSON into a compact mapping string.

    Args:
        ports_raw: JSON string from `docker inspect ... .NetworkSettings.Ports`.

    Returns:
        str: Compact mapping such as "0.0.0.0:8501->8501/tcp, 443->443/tcp" or "-".
    """
    try:
        if not ports_raw:
            return "-"
        data = json.loads(ports_raw)
        if not isinstance(data, dict) or not data:
            return "-"
        parts: List[str] = []
        for container_port, bindings in data.items():
            if not bindings:
                parts.append(f"{container_port} -> (unpublished)")
                continue
            for b in bindings:
                host_ip = b.get("HostIp", "")
                host_port = b.get("HostPort", "")
                if host_ip and host_port:
                    parts.append(f"{host_ip}:{host_port}->{container_port}")
                elif host_port:
                    parts.append(f"{host_port}->{container_port}")
                else:
                    parts.append(f"(unknown)->{container_port}")
        return ", ".join(parts) if parts else "-"
    except Exception:
        return ports_raw or "-"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _find_component_dockerfile_path(repo_root: Path, component_key: str, container_name: str) -> Optional[Path]:
    """
    Best-effort: find the Dockerfile used for the main service of the component,
    by reading setup/<component>/docker-compose.yml.

    Returns absolute Path or None if not found / not parseable.
    """
    compose_path = repo_root / "setup" / component_key / "docker-compose.yml"
    if not compose_path.is_file():
        return None

    # If PyYAML is not installed, we cannot parse compose reliably.
    try:
        compose_obj = _load_yaml_or_die(compose_path)
    except SystemExit:
        return None

    services = compose_obj.get("services") or {}
    candidates = _matching_service_names(component_key, container_name)
    targets = _services_to_patch(compose_obj, candidates, container_name)
    if not targets:
        return None

    # Take the first matching service (master/agent service)
    svc = services.get(targets[0]) or {}
    build = svc.get("build")

    # build can be string (context) or dict
    compose_dir = compose_path.parent
    if isinstance(build, str):
        context_dir = (compose_dir / build).resolve()
        dockerfile_rel = "Dockerfile"
    elif isinstance(build, dict):
        context_dir = (compose_dir / str(build.get("context", "."))).resolve()
        dockerfile_rel = str(build.get("dockerfile", "Dockerfile"))
    else:
        return None

    dockerfile_path = (context_dir / dockerfile_rel).resolve()
    if dockerfile_path.is_file():
        return dockerfile_path

    # fallback: if referenced dockerfile missing, try a common default
    fallback = (context_dir / "Dockerfile").resolve()
    return fallback if fallback.is_file() else None


# ────────────────────────────────────────────────────────────────────────────────
# Temporary in-place compose patching
# ────────────────────────────────────────────────────────────────────────────────
def _load_yaml_or_die(path: Path) -> Dict:
    try:
        import yaml  # type: ignore
    except Exception:
        sys.exit("PyYAML is required for --debug-shell. Please run: pip install pyyaml")
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as e:
        sys.exit(f"Failed to parse compose file '{path}': {e}")


def _dump_yaml_or_die(obj: Dict) -> str:
    try:
        import yaml  # type: ignore
        return yaml.safe_dump(obj, sort_keys=False)
    except Exception as e:
        sys.exit(f"Failed to serialize YAML: {e}")


def _matching_service_names(component: str, container_name: str) -> List[str]:
    """Service names we will try to patch.

    Your compose uses:
      master            (container_name: master-master)
      master-offline    (container_name: master-master)
    and for agent:
      agent
      agent-offline
    """
    base = component  # 'master' or 'agent'
    return [
        base,                # 'master' / 'agent'
        f"{base}-offline",   # 'master-offline' / 'agent-offline'
        container_name,      # 'master-master' / 'agent-agent' (just in case)
    ]


def _services_to_patch(compose_obj: Dict, names: List[str], container_name: str) -> List[str]:
    services = compose_obj.get("services") or {}
    found: List[str] = []
    # 1) Direct name matches
    for n in names:
        if n in services:
            found.append(n)
    # 2) container_name matches
    for svc_name, svc in services.items():
        if isinstance(svc, dict) and str(svc.get("container_name", "")).strip() == container_name:
            if svc_name not in found:
                found.append(svc_name)
    return found


@contextmanager
def temporarily_patch_compose_image_labels(
    compose_path: Path,
    component: str,
    container_name: str,
    image_labels: Dict[str, str],
    ui: "BoxPrinter",
):
    """
    Patch docker-compose.yml in-place to inject *image* labels into the build section.

    We set:
      services.<svc>.build.labels.<key> = <value>

    Only affects the services matching the component main container (master/agent).
    Restores the original compose after setup finishes.
    """
    compose_path = compose_path.resolve()
    backup_path = compose_path.with_suffix(compose_path.suffix + ".bak.labels")
    original_text = compose_path.read_text(encoding="utf-8")

    # Requires PyYAML (same as your debug-shell patcher)
    compose_obj = _load_yaml_or_die(compose_path)

    candidates = _matching_service_names(component, container_name)
    targets = _services_to_patch(compose_obj, candidates, container_name)

    if not targets:
        ui.box(
            "IMAGE LABELS – Compose patcher",
            f"Compose file: {compose_path}\n"
            f"Could not find a service matching any of: {', '.join(candidates)}\n"
            f"and no service with container_name == {container_name}.\n\n"
            "No label patch applied. Fingerprint comparison may show UNKNOWN.",
        )
        try:
            yield
        finally:
            pass
        return

    services = compose_obj.get("services") or {}
    patched_services: List[str] = []

    for svc_name in targets:
        svc = services.get(svc_name) or {}
        build = svc.get("build")

        # Ensure build is a dict (we need build.labels)
        if isinstance(build, str):
            build = {"context": build}
        elif build is None:
            build = {"context": "."}
        elif not isinstance(build, dict):
            continue

        labels = build.get("labels")
        if labels is None:
            labels = {}
        if not isinstance(labels, dict):
            # If labels exists but not dict, skip to avoid corrupting
            continue

        for k, v in image_labels.items():
            labels[k] = v

        build["labels"] = labels
        svc["build"] = build
        services[svc_name] = svc
        patched_services.append(svc_name)

    compose_obj["services"] = services
    patched_text = _dump_yaml_or_die(compose_obj)

    backup_path.write_text(original_text, encoding="utf-8")
    compose_path.write_text(patched_text, encoding="utf-8")

    ui.box(
        "IMAGE LABELS – Compose patcher",
        f"Compose file patched: {compose_path}\n"
        f"Services patched: {', '.join(patched_services)}\n"
        f"Injected build labels:\n" + "\n".join([f"  - {k}={v}" for k, v in image_labels.items()]),
    )

    try:
        yield
    finally:
        try:
            compose_path.write_text(backup_path.read_text(encoding="utf-8"), encoding="utf-8")
        finally:
            backup_path.unlink(missing_ok=True)


@contextmanager
def temporarily_patch_compose_in_place(compose_path: Path, component: str, container_name: str, ui: "BoxPrinter"):
    """Backup docker-compose.yml, patch entrypoint->bash for selected services, then restore.

    We detect services by:
      - trying names like ['master', 'master-master'] (or agent variants)
      - and any service whose 'container_name' equals the container_name we need.

    We also print which file and which services were patched for transparency.
    """
    compose_path = compose_path.resolve()
    backup_path = compose_path.with_suffix(compose_path.suffix + ".bak")
    original_text = compose_path.read_text(encoding="utf-8")
    compose_obj = _load_yaml_or_die(compose_path)

    # Find target services
    candidates = _matching_service_names(component, container_name)
    targets = _services_to_patch(compose_obj, candidates, container_name)

    if not targets:
        ui.box(
            "DEBUG SHELL - Compose patcher",
            f"Compose file: {compose_path}\n"
            f"Could not find a service matching any of: {', '.join(candidates)}\n"
            f"and no service with container_name == {container_name}.\n\n"
            "No patch applied. Your stack may still start OSIR.py.\n"
            "Tip: set the service name to match or set container_name to the expected container.",
        )
        # Yield without changing the file
        try:
            yield
        finally:
            pass
        return

    # Apply patch
    services = compose_obj.get("services") or {}
    for name in targets:
        svc = services.get(name) or {}
        svc["command"] = ["bash"]
        svc["tty"] = True
        svc["stdin_open"] = True
        services[name] = svc

    patched_text = _dump_yaml_or_die(compose_obj)

    # Write backup + patched
    backup_path.write_text(original_text, encoding="utf-8")
    compose_path.write_text(patched_text, encoding="utf-8")

    ui.box(
        "DEBUG SHELL - Compose patcher",
        f"Compose file patched: {compose_path}\n"
        f"Services set to entrypoint=bash: {', '.join(targets)}\n\n"
        "Note: running containers will be (re)created by your setup script using this patched entrypoint.\n"
        "The original compose file will be restored right after setup finishes.",
    )

    try:
        yield
    finally:
        # Always restore compose
        try:
            compose_path.write_text(backup_path.read_text(encoding="utf-8"), encoding="utf-8")
        finally:
            backup_path.unlink(missing_ok=True)


# ────────────────────────────────────────────────────────────────────────────────
# UI / printing
# ────────────────────────────────────────────────────────────────────────────────
class BoxPrinter:
    """Utilities for drawing boxed sections and banners in the terminal."""

    def box(self, title: str, body: str) -> None:
        """Print a framed box with a title and multi-line body.

        Uses Unicode box-drawing characters and accounts for wide characters
        when `wcwidth` is available. Lines are wrapped hard at visible width.

        Args:
            title: Title displayed in the box header.
            body: Multi-line string to render inside the box body.
        """
        width = max(60, min(120, get_terminal_size((100, 20)).columns))
        line = BORDER * (width - 2)
        print(f"{TITLE_L}{line}{TITLE_R}")
        title_line = f" {title} ".center(width - 2, " ")
        print(f"{BOX_V}{title_line}{BOX_V}")
        print(f"{MID_L}{line}{MID_R}")

        for ln in body.rstrip("\n").splitlines() or [""]:
            remaining = ln
            # Wrap considering display width if wcwidth is available.
            while _wcswidth(remaining) > width - 4:
                visible_part = ""
                current_width = 0
                for ch in remaining:
                    ch_w = _wcswidth(ch)
                    if current_width + ch_w > width - 4:
                        break
                    visible_part += ch
                    current_width += ch_w
                print(f"{BOX_V} {visible_part}{' ' * (width - 4 - current_width)} {BOX_V}")
                remaining = remaining[len(visible_part):]
            pad = " " * (width - 4 - _wcswidth(remaining))
            print(f"{BOX_V} {remaining}{pad} {BOX_V}")

        print(f"{BOX_B_L}{line}{BOX_B_R}")

    def start_banner(
        self,
        component: str,
        *,
        attach: bool,
        offline: bool,
        debug: bool,
        config_flag: bool,
        note: str | None = None,
    ) -> None:
        """Print a standardized 'start' banner for a component.

        Args:
            component: Component name, e.g., "MASTER" or "AGENT".
            attach: Whether the component will be started attached (interactive).
            offline: Whether to run in offline mode.
            debug: Whether to enable debug mode.
            config_flag: Whether configuration is being reused/applied.
            note: Optional additional note to display.
        """
        flags = [
            f"attach={attach}",
            f"offline={offline}",
            f"debug={debug}",
            f"config_flag={config_flag}",
        ]
        body = "Starting component…\n" + " • " + "\n • ".join(flags)
        if note:
            body += f"\n\nNote: {note}"
        self.box(f"▶ START - {component.upper()}", body)

    def skip_banner(self, component: str, reason: str) -> None:
        """Print a 'skipped' banner with a reason.

        Args:
            component: Component name, e.g., "MASTER" or "AGENT".
            reason: Human-readable reason for skipping.
        """
        self.box(f"⏭ START - {component.upper()} (SKIPPED)", reason)


# ────────────────────────────────────────────────────────────────────────────────
# Docker client wrapper
# ────────────────────────────────────────────────────────────────────────────────
class DockerClient:
    """Thin wrapper around Docker CLI used by the launcher."""

    def _run(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Run a command returning CompletedProcess without raising.

        Args:
            cmd: Command and arguments.

        Returns:
            subprocess.CompletedProcess: Completed process with captured output.

        Raises:
            SystemExit: If Docker is not installed or not in PATH.
        """
        try:
            return subprocess.run(cmd, capture_output=True, text=True, check=False)
        except FileNotFoundError:
            sys.exit("Docker is not installed or not in PATH.")

    def images_by_ref(self, ref_pattern: str) -> List[Dict]:
        """List Docker images that match a reference filter.

        Args:
            ref_pattern: Reference filter, e.g., "master-*" or "agent-*".

        Returns:
            list[dict]: List of images with keys repo, tag, id, created, size.
        """
        fmt = "{{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}\t{{.Size}}"
        cp = self._run(["docker", "images", "--filter", f"reference={ref_pattern}", "--format", fmt])
        images: List[Dict] = []
        for line in cp.stdout.strip().splitlines():
            parts = line.split("\t")
            if len(parts) != 5:
                continue
            repo, tag, img_id, created, size = parts
            images.append({"repo": repo, "tag": tag, "id": img_id, "created": created, "size": size})
        return images

    def inspect_container(self, name: str) -> Optional[Dict]:
        """Inspect a container, returning structured fields.

        Args:
            name: Container name.

        Returns:
            dict | None: Minimal container info or None if missing/unavailable.
        """
        cp = self._run(["docker", "inspect", name])
        if cp.returncode != 0 or not cp.stdout.strip():
            return None
        try:
            info = json.loads(cp.stdout)
            if not info:
                return None
            obj = info[0]
            state = obj.get("State", {}) or {}
            network = obj.get("NetworkSettings", {}) or {}
            ports = network.get("Ports", {})
            cid = obj.get("Id", "")
            cname = obj.get("Name", "") or ""
            if cname.startswith("/"):
                cname = cname[1:]
            health_obj = state.get("Health")
            health = (health_obj or {}).get("Status", "n/a")
            return {
                "id": cid,
                "name": cname,
                "status": state.get("Status", "unknown"),
                "health": health,
                "running": bool(state.get("Running", False)),
                "ports_raw": json.dumps(ports),
            }
        except Exception:
            return None

    def list_container_names(self) -> List[str]:
        """Return all Docker container names (running and stopped).

        Returns:
            list[str]: Container names, possibly empty on error.
        """
        cp = self._run(["docker", "ps", "-a", "--format", "{{.Names}}"])
        if cp.returncode != 0:
            return []
        return [ln.strip() for ln in cp.stdout.splitlines() if ln.strip()]

    def container_has_process(self, name: str, pattern: str) -> Tuple[bool, str]:
        """Check whether a process matching a pattern is running inside a container.

        Args:
            name: Container name.
            pattern: Substring to search for in `ps -eo pid,comm,args` output.

        Returns:
            tuple[bool, str]: (True, first matching line) if found and container
            is running; otherwise (False, detail message).
        """
        pre = self._run(["docker", "inspect", name, "--format", "{{.State.Running}}"])
        if pre.returncode != 0 or pre.stdout.strip().lower() != "true":
            return (False, "container not running. Start it using OSIR_launcher.py start command")
        cmd = [
            "docker", "exec", name, "sh", "-lc",
            r"ps -eo pid,comm,args | grep -F -- '{}' | grep -v grep || true".format(pattern),
        ]
        cp = self._run(cmd)
        lines = [ln for ln in cp.stdout.splitlines() if ln.strip()]
        return (len(lines) > 0, lines[0].strip() if lines else "")


    def save_images(self, image_refs: List[str], out_tar: Path) -> None:
        """
        Save images into a tar archive (docker save -o ...).
        image_refs: list like ["master-master:latest", "master-redis:latest"] (tag may vary)
        """
        if not image_refs:
            sys.exit(f"No images found to export for {out_tar.name}.")
        out_tar.parent.mkdir(parents=True, exist_ok=True)
        cmd = ["docker", "save", "-o", str(out_tar), *image_refs]
        cp = self._run(cmd)
        if cp.returncode != 0:
            sys.exit(f"docker save failed:\n{cp.stderr or cp.stdout}")

    def load_images(self, in_tar: Path) -> None:
        """Load images from a tar archive (docker load -i ...)."""
        if not in_tar.is_file():
            sys.exit(f"Input tar not found: {in_tar}")
        cmd = ["docker", "load", "-i", str(in_tar)]
        cp = self._run(cmd)
        if cp.returncode != 0:
            sys.exit(f"docker load failed:\n{cp.stderr or cp.stdout}")

    def container_image_id(self, name: str) -> Optional[str]:
        """
        Return image ID used by a container (works for running or stopped containers).
        """
        cp = self._run(["docker", "inspect", name, "--format", "{{.Image}}"])
        if cp.returncode != 0:
            return None
        val = (cp.stdout or "").strip()
        return val or None

    def image_labels(self, image_id_or_ref: str) -> Dict[str, str]:
        """
        Return image labels dict for an image id/ref.
        """
        cp = self._run(["docker", "image", "inspect", image_id_or_ref, "--format", "{{json .Config.Labels}}"])
        if cp.returncode != 0:
            return {}
        raw = (cp.stdout or "").strip()
        if not raw or raw == "null":
            return {}
        try:
            obj = json.loads(raw)
            return obj if isinstance(obj, dict) else {}
        except Exception:
            return {}
        

# ────────────────────────────────────────────────────────────────────────────────
# Process helpers
# ────────────────────────────────────────────────────────────────────────────────
class ProcessRunner:
    """Helpers to execute child processes with optional streaming output."""

    @staticmethod
    def run_process(command: List[str], cwd: Optional[Path] = None, stream: bool = True, env: Optional[Dict[str, str]] = None) -> int:
        """Run a child process, optionally streaming stdout to the console.

        Args:
            command: Command and arguments.
            cwd: Working directory for the command.
            stream: If True, stream stdout live; otherwise capture silently.
            env: Optional environment overrides.

        Returns:
            int: Process exit code.
        """
        process = subprocess.Popen(
            command,
            cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE if stream else None,
            stderr=subprocess.STDOUT if stream else None,
            text=True,
            env=env,
        )
        if stream and process.stdout:
            try:
                for line in process.stdout:
                    sys.stdout.write(line)
            except KeyboardInterrupt:
                process.terminate()
                process.wait()
                return process.returncode
        return process.wait()

    @staticmethod
    def run_interactive(command: List[str], cwd: Optional[Path] = None, env: Optional[Dict[str, str]] = None) -> int:
        """Run a child process interactively, inheriting stdio.

        Args:
            command: Command and arguments.
            cwd: Working directory for the command.
            env: Optional environment overrides.

        Returns:
            int: Process exit code, or 130 on Ctrl-C.
        """
        try:
            completed = subprocess.run(
                command,
                cwd=str(cwd) if cwd else None,
                check=False,
                env=env,
            )
            return completed.returncode
        except KeyboardInterrupt:
            return 130


# ────────────────────────────────────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────────────────────────────────────
@dataclass
class AppConfig:
    """Application configuration resolved from CLI flags.

    Attributes:
        offline: Run in offline mode.
        debug: Enable debug mode.
        attach: Attach to the process rather than backgrounding it.
        config_master: Reuse/apply master configuration (implies '-c' for master).
        config_agent: Reuse/apply agent configuration (implies '-c' for agent).
        debug_shell: Start containers with entrypoint=bash so you can run OSIR manually.
    """
    offline: bool = False
    debug: bool = False
    attach: bool = False
    config_master: bool = False
    config_agent: bool = False
    debug_shell: bool = False


# ────────────────────────────────────────────────────────────────────────────────
# Component model
# ────────────────────────────────────────────────────────────────────────────────
class Component:
    """Represents an OSIR component (master or agent) with lifecycle commands."""

    def __init__(
        self,
        key: str,
        label: str,
        container: str,
        expected_process: str,
        setup_script: Path,
        uninstall_script: Path,
        docker: DockerClient,
        ui: BoxPrinter,
    ):
        """Initialize a component.

        Args:
            key: Short key ("master" | "agent").
            label: Display label ("MASTER" | "AGENT").
            container: Docker container name.
            expected_process: Process command expected inside the container.
            setup_script: Path to the bash setup script.
            uninstall_script: Path to the bash uninstall script.
            docker: Docker client interface.
            ui: UI printer.
        """
        self.key = key
        self.label = label
        self.container = container
        self.expected_process = expected_process
        self.setup_script = setup_script
        self.uninstall_script = uninstall_script
        self.docker = docker
        self.ui = ui

    def is_running(self) -> Tuple[bool, str]:
        """Check if the expected process is running in the component container.

        Returns:
            tuple[bool, str]: (True, detail) if running; else (False, reason).
        """
        return self.docker.container_has_process(self.container, self.expected_process)

    def _locate_compose_file(self, repo_root: Path) -> Path:
        """Locate the compose file used by the setup script for this component.

        We always use setup/<component>/docker-compose.yml as you confirmed.
        """
        p = repo_root / "setup" / self.key / "docker-compose.yml"
        if not p.is_file():
            sys.exit(f"Compose file not found for {self.key}: {p}")
        return p

    def install(self, cfg: AppConfig, repo_root: Path) -> None:
        """Run the component's setup script.

        Args:
            cfg: Current application configuration.
            repo_root: Path to the repository root.

        Raises:
            SystemExit: If the setup script fails.
        """
        cmd: List[str] = ["bash", str(self.setup_script)]
        if cfg.debug:
            cmd.append("-d")
        if cfg.offline:
            cmd.append("-o")
        if (self.key == "master" and cfg.config_master) or (self.key == "agent" and cfg.config_agent):
            cmd.append("-c")
        self.ui.box(f"{self.label} - Setup", f"Executing {self.key} setup script…")

        compose_path = self._locate_compose_file(repo_root)

        # Compute Dockerfile fingerprint (best-effort)
        dockerfile_path = _find_component_dockerfile_path(repo_root, self.key, self.container)
        fingerprint = sha256_file(dockerfile_path) if dockerfile_path and dockerfile_path.is_file() else None

        labels: Dict[str, str] = {}
        if fingerprint:
            labels = {
                "osir.dockerfile.sha256": fingerprint,
                "osir.dockerfile.path": str(dockerfile_path.relative_to(repo_root)) if dockerfile_path else "",
                "osir.component": self.key,
            }
        else:
            # No hard fail: best-effort. Status will show UNKNOWN.
            self.ui.box(
                f"{self.label} – Fingerprint",
                "Could not locate/parse Dockerfile for fingerprinting.\n"
                "Image label injection skipped. Status may show UNKNOWN for fingerprint check.",
            )

        # Apply patches (labels + optional debug-shell) around the setup call
        exit_code: int
        try:
            if labels:
                with temporarily_patch_compose_image_labels(compose_path, self.key, self.container, labels, self.ui):
                    if cfg.debug_shell:
                        with temporarily_patch_compose_in_place(compose_path, self.key, self.container, self.ui):
                            exit_code = ProcessRunner.run_interactive(cmd, cwd=repo_root)
                    else:
                        exit_code = ProcessRunner.run_interactive(cmd, cwd=repo_root)
            else:
                if cfg.debug_shell:
                    with temporarily_patch_compose_in_place(compose_path, self.key, self.container, self.ui):
                        exit_code = ProcessRunner.run_interactive(cmd, cwd=repo_root)
                else:
                    exit_code = ProcessRunner.run_interactive(cmd, cwd=repo_root)
        except SystemExit:
            raise
        except Exception as e:
            sys.exit(f"{self.label} setup failed unexpectedly: {e}")

        if exit_code != 0:
            sys.exit(f"{self.label.capitalize()} setup failed with exit code {exit_code}.")

    def start(self, cfg: AppConfig) -> None:
        """Start (or attach to) the container that already has OSIR.py as PID 1."""
        info = self.docker.inspect_container(self.container)
        if not info:
            sys.exit(f"Container '{self.container}' not found. Run the {self.key} setup first.")

        self.ui.box(
            f"{self.label} - Start",
            f"Ensuring container '{self.container}' is running (ENTRYPOINT may be OSIR.py or bash)…",
        )

        running = bool(info.get("running", False))

        if cfg.debug_shell:
            manual = "--web" if self.key == "master" else "--agent"
            self.ui.box(
                f"{self.label} - DEBUG SHELL",
                "Container started with bash as entrypoint.\n\n"
                "⚠️  Now you have to run manually inside the shell:\n"
                f"   OSIR.py {manual}\n\n"
                "The container will exit if you close this shell without starting OSIR.py.",
            )

        if cfg.attach:
            if running:
                ProcessRunner.run_interactive(["docker", "attach", self.container])
            else:
                rc = ProcessRunner.run_interactive(["docker", "start", "-a", self.container])
                if rc != 0:
                    sys.exit(f"Failed to start {self.key} attached (exit {rc}).")
            return

        if running:
            print(f"✅ {self.label} already running.")
            return

        rc = ProcessRunner.run_process(["docker", "start", self.container], stream=False)
        if rc != 0:
            sys.exit(f"Failed to start {self.key} in background (exit {rc}).")

        if self.key == "master":
            print("✅ Master started. Connect to http://master_host:8501 to start using OSIR.")
        else:
            print("✅ Agent started.")

    def launch(self, cfg: AppConfig, repo_root: Path) -> None:
        """Install then start the component unless it is already running.

        Prints a start banner, checks for the expected process, and either
        skips or performs install + start.

        Args:
            cfg: Current application configuration.
            repo_root: Path to the repository root.
        """
        config_flag = (cfg.config_master if self.key == "master" else cfg.config_agent)
        self.ui.start_banner(
            self.label,
            attach=cfg.attach,
            offline=cfg.offline,
            debug=cfg.debug,
            config_flag=config_flag,
        )

        running, _detail = self.is_running()
        if running:
            self.ui.skip_banner(
                self.label,
                f"Already running: {self.expected_process} found in container '{self.container}'.",
            )
            if cfg.attach:
                print("    (attach requested, but process is already running; not starting another instance)")
            return

        self.install(cfg, repo_root)
        self.start(cfg)

    def stop(self, extra_flags: List[str], repo_root: Path) -> None:
        """Stop the component using its uninstall script.

        Args:
            extra_flags: Additional CLI flags to pass to the uninstall script.
            repo_root: Path to the repository root.

        Raises:
            SystemExit: If the uninstall script fails.
        """
        cmd: List[str] = ["bash", str(self.uninstall_script), *extra_flags]
        print(f"[+] Stopping {self.key}…")
        exit_code = ProcessRunner.run_process(cmd, cwd=repo_root, stream=True)
        if exit_code != 0:
            sys.exit(f"{self.label.capitalize()} stopping failed with exit code {exit_code}.")


# ────────────────────────────────────────────────────────────────────────────────
# Status rendering
# ────────────────────────────────────────────────────────────────────────────────
def fmt_container_block(cinfo: Optional[Dict]) -> str:
    """Format a container info dict as a multi-line block.

    Args:
        cinfo: Container info dict as returned by DockerClient.inspect_container.

    Returns:
        str: Human-readable block or "(container not found)".
    """
    if not cinfo:
        return "(container not found)"
    health = cinfo.get("health", "n/a")
    ports = format_ports(cinfo.get("ports_raw", ""))
    return (
        f"Name:    {cinfo.get('name', '')}\n"
        f"ID:      {cinfo.get('id', '')[:12]}\n"
        f"Status:  {cinfo.get('status', 'unknown')}  (health: {health})\n"
        f"Running: {cinfo.get('running', False)}\n"
        f"Ports:   {ports}"
    )


def fmt_images(imgs: List[Dict]) -> str:
    """Format a list of Docker images as table-like text.

    Args:
        imgs: List of image dicts from DockerClient.images_by_ref().

    Returns:
        str: Multi-line string table or "(no images found)".
    """
    if not imgs:
        return "(no images found)"
    rows = ["REPOSITORY:TAG      IMAGE ID        CREATED          SIZE"]
    for im in imgs:
        rows.append(f"{im['repo']}:{im['tag']:<14} {im['id']:<14} {im['created']:<15} {im['size']}")
    return "\n".join(rows)


def group_containers_by_prefix(prefix: str, docker: DockerClient) -> List[Dict]:
    """Collect container infos whose names start with a given prefix.

    Args:
        prefix: Container name prefix, e.g., "master-" or "agent-".
        docker: Docker client instance.

    Returns:
        list[dict]: Sorted list of container info (running first).
    """
    names = docker.list_container_names()
    matched = [n for n in names if n.startswith(prefix)]
    infos: List[Dict] = []
    for n in matched:
        ci = docker.inspect_container(n)
        infos.append(ci if ci else {"name": n, "status": "unknown", "health": "n/a", "running": False, "id": "-", "ports_raw": ""})
    infos.sort(key=lambda x: (not x.get("running", False), x.get("name", "")))  # running first
    return infos


# ────────────────────────────────────────────────────────────────────────────────
# Launcher / CLI
# ────────────────────────────────────────────────────────────────────────────────
class Launcher:
    """Top-level application: wiring, CLI, elevation, and dispatch."""

    def __init__(self) -> None:
        """Initialize launcher, clients, and component instances."""
        self.ui = BoxPrinter()
        self.docker = DockerClient()
        self.repo_root = Path(__file__).resolve().parent
        self.setup_dir = self.repo_root / "setup"
        self.conf_dir = self.setup_dir / "conf"
        self.master = Component(
            key="master",
            label="MASTER",
            container="master-master",
            expected_process="OSIR.py --web",
            setup_script=self.repo_root / "setup" / "master" / "master_setup.sh",
            uninstall_script=self.repo_root / "setup" / "master" / "master_uninstall.sh",
            docker=self.docker,
            ui=self.ui,
        )
        self.agent = Component(
            key="agent",
            label="AGENT",
            container="agent-agent",
            expected_process="OSIR.py --agent",
            setup_script=self.repo_root / "setup" / "agent" / "agent_setup.sh",
            uninstall_script=self.repo_root / "setup" / "agent" / "agent_uninstall.sh",
            docker=self.docker,
            ui=self.ui,
        )

    def _fingerprint_status(self, component: Component) -> Tuple[str, str]:
        """
        Returns (status_text, details) for dockerfile fingerprint check.
        status_text is short; details is optional longer info.
        """
        dockerfile_path = _find_component_dockerfile_path(self.repo_root, component.key, component.container)
        if not dockerfile_path or not dockerfile_path.is_file():
            return ("UNKNOWN ❓", "Dockerfile not found / compose not parseable (best-effort).")

        local_fp = sha256_file(dockerfile_path)

        img_id = self.docker.container_image_id(component.container)
        if not img_id:
            # Container may not exist yet; try to infer by image repo name equal to container name
            imgs = self.docker.images_by_ref(f"{component.key}-*")
            pick = next((im for im in imgs if im.get("repo") == component.container and im.get("tag") not in (None, "", "<none>")), None)
            if pick:
                img_id = f"{pick['repo']}:{pick['tag']}"
            else:
                return ("UNKNOWN ❓", "No container and no matching local image found.")

        labels = self.docker.image_labels(img_id)
        img_fp = (labels.get("osir.dockerfile.sha256") or "").strip()

        if not img_fp:
            return ("UNKNOWN ❓", "Image has no osir.dockerfile.sha256 label (built with older launcher ?).")

        if img_fp == local_fp:
            return ("Up to date ✅", f"dockerfile={dockerfile_path.relative_to(self.repo_root)}")
        
        comp = component.key  # "master" or "agent"
        detail = (
            f"dockerfile changed: {dockerfile_path.relative_to(self.repo_root)}\n"
            "Recommended actions:\n"
            f"  1) Delete old image(s): sudo python3 osir-launcher.py stop -i {comp}\n"
            f"  2) Build again:        sudo python3 osir-launcher.py start {comp}"
        )
        return ("OUTDATED ⚠️", detail)
    def _cfg_path_for(self, component: str) -> Path:
        """Return path to the per-component config file.

        Args:
            component: "master" or "agent".

        Returns:
            Path: Config file path (master.yml or agent.yml).
        """
        return self.conf_dir / ("master.yml" if component == "master" else "agent.yml")

    def _ensure_config_when_flagged(self, component: str) -> None:
        """Ensure that a component config exists when --config was specified.

        Args:
            component: "master" or "agent".

        Raises:
            SystemExit: If the expected config file does not exist.
        """
        cp = self._cfg_path_for(component)
        if not cp.is_file():
            sys.exit(f"--config specified for '{component}' but {cp} was not found.")

    def _ask_reuse_or_new(self, component_label: str, cfg_path: Path) -> str:
        """Prompt user to reuse existing config, create new, or abort.

        Args:
            component_label: Display label ("master" or "agent").
            cfg_path: Path to the discovered config file.

        Returns:
            str: One of "reuse", "new", "abort".
        """
        preview = pretty_yaml_or_text(cfg_path)
        self.ui.box(f"Detected previous {component_label} configuration: {cfg_path}", preview)
        print("\nFound an existing configuration.")
        while True:
            choice = input("[R]euse this config / [N]ew setup / [A]bort? ").strip().lower()
            if choice in ("r", "reuse"):
                return "reuse"
            if choice in ("n", "new"):
                return "new"
            if choice in ("a", "abort", "q", "quit", "exit"):
                return "abort"
            print("Please enter R, N, or A.")

    def _maybe_prompt_for_reuse(self, args: argparse.Namespace, component: str) -> None:
        """Conditionally prompt for reusing config if it exists.

        Sets args.config_{component}=True when reusing or in non-tty contexts.

        Args:
            args: Parsed CLI namespace (mutated).
            component: "master" or "agent".
        """
        cp = self._cfg_path_for(component)
        if not cp.is_file():
            return
        if getattr(args, "config", False):
            setattr(args, f"config_{component}", True)
            return
        if sys.stdin.isatty():
            decision = self._ask_reuse_or_new(component, cp)
            if decision == "abort":
                sys.exit("Aborted by user.")
            if decision == "reuse":
                setattr(args, f"config_{component}", True)
        else:
            setattr(args, f"config_{component}", True)


    # ────────────────────────────────────────────────────────────────────────────
    # Airgap helpers
    # ────────────────────────────────────────────────────────────────────────────
    def _refs_from_pattern(self, pattern: str) -> List[str]:
        """Convert images_by_ref() output into docker refs 'repo:tag'."""
        imgs = self.docker.images_by_ref(pattern)
        refs: List[str] = []
        for im in imgs:
            repo = (im.get("repo") or "").strip()
            tag = (im.get("tag") or "").strip()
            if not repo or not tag or tag == "<none>":
                continue
            refs.append(f"{repo}:{tag}")
        # stable ordering for reproducibility
        return sorted(set(refs))

    def cmd_airgap(self, args: argparse.Namespace) -> None:
        """Handle 'airgap export/load' to save/load component images as tar."""
        if args.airgap_cmd == "export":
            out_dir = Path(args.out).resolve()
            out_dir.mkdir(parents=True, exist_ok=True)

            if args.component in ("master", "all"):
                refs = self._refs_from_pattern("master-*")
                out_tar = out_dir / "master_containers.tar"
                self.ui.box(
                    "AIRGAP - Export MASTER images",
                    f"Exporting {len(refs)} image(s) to:\n{out_tar}",
                )
                self.docker.save_images(refs, out_tar)

            if args.component in ("agent", "all"):
                refs = self._refs_from_pattern("agent-*")
                out_tar = out_dir / "agent_containers.tar"
                self.ui.box(
                    "AIRGAP - Export AGENT images",
                    f"Exporting {len(refs)} image(s) to:\n{out_tar}",
                )
                self.docker.save_images(refs, out_tar)

            self.ui.box("AIRGAP - Export complete", f"Archives written under:\n{out_dir}")
            return

        if args.airgap_cmd == "load":
            in_dir = Path(args.in_dir).resolve()

            if args.component in ("master", "all"):
                in_tar = in_dir / "master_containers.tar"
                self.ui.box("AIRGAP - Load MASTER images", f"Loading:\n{in_tar}")
                self.docker.load_images(in_tar)

            if args.component in ("agent", "all"):
                in_tar = in_dir / "agent_containers.tar"
                self.ui.box("AIRGAP - Load AGENT images", f"Loading:\n{in_tar}")
                self.docker.load_images(in_tar)

            self.ui.box("AIRGAP - Load complete", f"Archives loaded from:\n{in_dir}")
            return

        sys.exit("Unknown airgap command.")
    def parse_arguments(self) -> argparse.Namespace:
        """Build and parse the command-line interface.

        Returns:
            argparse.Namespace: Parsed arguments.
        """
        parser = argparse.ArgumentParser(description="Unified OSIR launcher.")
        subparsers = parser.add_subparsers(dest="command", required=True)

        p_start = subparsers.add_parser("start", help="Install and start components")
        start_sub = p_start.add_subparsers(dest="component", required=True)

        p_start_master = start_sub.add_parser("master", help="Install and start the MASTER component")
        p_start_master.add_argument("--offline", action="store_true", help="Use offline images/assets (no network pulls) during setup.")
        p_start_master.add_argument("--debug", action="store_true", help="Enable debug mode for setup scripts (passes -d to master_setup.sh).")
        p_start_master.add_argument("--config", action="store_true", help="Reuse/apply existing MASTER configuration (equivalent to passing -c to setup).")
        p_start_master.add_argument("--attach", action="store_true", help="Attach to the container process after start (interactive).")
        p_start_master.add_argument("--debug-shell", action="store_true", help="Patch compose to start with 'bash' entrypoint so you can run OSIR.py manually.")

        p_start_agent = start_sub.add_parser("agent", help="Install and start the AGENT component")
        p_start_agent.add_argument("--offline", action="store_true", help="Use offline images/assets (no network pulls) during setup.")
        p_start_agent.add_argument("--debug", action="store_true", help="Enable debug mode for setup scripts (passes -d to agent_setup.sh).")
        p_start_agent.add_argument("--config", action="store_true", help="Reuse/apply existing AGENT configuration (equivalent to passing -c to setup).")
        p_start_agent.add_argument("--attach", action="store_true", help="Attach to the container process after start (interactive).")
        p_start_agent.add_argument("--debug-shell", action="store_true", help="Patch compose to start with 'bash' entrypoint so you can run OSIR.py manually.")

        p_start_all = start_sub.add_parser("all", help="Install and start both MASTER and AGENT")
        p_start_all.add_argument("--offline", action="store_true", help="Use offline images/assets (no network pulls) during both setups.")
        p_start_all.add_argument("--debug", action="store_true", help="Enable debug mode for both setup scripts.")
        p_start_all.add_argument("--config", action="store_true", help="Reuse/apply existing configurations for BOTH components.")
        p_start_all.add_argument("--debug-shell", action="store_true", help="Patch compose for both components to start with 'bash' entrypoint.")

        p_stop = subparsers.add_parser("stop", help="Stop master or agent")
        un_sub = p_stop.add_subparsers(dest="component", required=True)

        p_un_master = un_sub.add_parser("master", help="Stop MASTER component",)
        p_un_master.add_argument("-i", "--images", action="store_true", help="Additionally remove Docker images related to the MASTER component.")

        p_un_agent = un_sub.add_parser("agent", help="Stop AGENT component")
        p_un_agent.add_argument("-v", "--vagrant", action="store_true", help="Also remove Vagrant-related resources used by the agent (if applicable).")
        p_un_agent.add_argument("-d", "--dockur", action="store_true", help="Also remove Dockur-related resources used by the agent (if applicable).")
        p_un_agent.add_argument("-i", "--images", action="store_true", help="Additionally remove Docker images related to the AGENT component.")

        p_status = subparsers.add_parser("status", help="Show OSIR status")
        p_status.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Show all master-* and agent-* container statuses and related images",
        )

        p_airgap = subparsers.add_parser("airgap", help="Air-gapped workflow (export/load docker images)")
        airgap_sub = p_airgap.add_subparsers(dest="airgap_cmd", required=True)

        p_airgap_export = airgap_sub.add_parser("export", help="Export docker images to tar archives")
        p_airgap_export.add_argument("component", choices=["master", "agent", "all"])
        p_airgap_export.add_argument(
            "--out",
            default=str(self.repo_root / "setup" / "offline_release"),
            help="Output directory for tar archives (default: setup/offline_release)",
        )

        p_airgap_load = airgap_sub.add_parser("load", help="Load docker images from tar archives")
        p_airgap_load.add_argument("component", choices=["master", "agent", "all"])
        p_airgap_load.add_argument(
            "--in",
            dest="in_dir",
            default=str(self.repo_root / "setup" / "offline_release"),
            help="Input directory containing tar archives (default: setup/offline_release)",
        )

        return parser.parse_args()

    def cmd_start(self, args: argparse.Namespace) -> None:
        """Handle the 'start' command for master, agent, or all.

        This performs config checks/prompts, builds AppConfig, and dispatches.

        Args:
            args: Parsed CLI arguments for the start command.

        Raises:
            SystemExit: When required directories/configs are missing.
        """
        if not self.setup_dir.is_dir():
            sys.exit("Could not locate the `setup` directory.")

        if args.component == "master":
            if getattr(args, "config", False):
                self._ensure_config_when_flagged("master")
                setattr(args, "config_master", True)
            else:
                self._maybe_prompt_for_reuse(args, "master")
        elif args.component == "agent":
            if getattr(args, "config", False):
                self._ensure_config_when_flagged("agent")
                setattr(args, "config_agent", True)
            else:
                self._maybe_prompt_for_reuse(args, "agent")
        elif args.component == "all":
            if getattr(args, "config", False):
                self._ensure_config_when_flagged("master")
                self._ensure_config_when_flagged("agent")
                setattr(args, "config_master", True)
                setattr(args, "config_agent", True)
            else:
                self._maybe_prompt_for_reuse(args, "master")
                self._maybe_prompt_for_reuse(args, "agent")

        cfg = AppConfig(
            offline=getattr(args, "offline", False),
            debug=getattr(args, "debug", False),
            attach=getattr(args, "attach", False),
            config_master=getattr(args, "config_master", False),
            config_agent=getattr(args, "config_agent", False),
            debug_shell=getattr(args, "debug_shell", False),
        )

        if args.component == "master":
            self.master.launch(cfg, self.repo_root)
        elif args.component == "agent":
            self.agent.launch(cfg, self.repo_root)
        elif args.component == "all":
            self.ui.box("▶ START - ALL", "Beginning start sequence for MASTER and AGENT…")
            self.master.launch(cfg, self.repo_root)
            self.agent.launch(cfg, self.repo_root)

    def cmd_stop(self, args: argparse.Namespace) -> None:
        """Handle the 'stop' command for master or agent.

        Args:
            args: Parsed CLI arguments for stop.
        """
        if args.component == "master":
            flags: List[str] = []
            if getattr(args, "images", False):
                flags.append("-i")
            self.master.stop(flags, self.repo_root)
        elif args.component == "agent":
            flags: List[str] = []
            if getattr(args, "vagrant", False):
                flags.append("-v")
            if getattr(args, "dockur", False):
                flags.append("-d")
            if getattr(args, "images", False):
                flags.append("-i")
            self.agent.stop(flags, self.repo_root)

    def cmd_status(self, args: argparse.Namespace) -> None:
        """Handle the 'status' command.

        Prints the expected in-container processes, their presence, and in verbose
        mode also prints images and all master-*/agent-* containers.

        Args:
            args: Parsed CLI arguments for status.
        """
        verbose = getattr(args, "verbose", False)

        m_ok, m_detail = self.docker.container_has_process("master-master", "OSIR.py --web")
        a_ok, a_detail = self.docker.container_has_process("agent-agent", "OSIR.py --agent")

        m_status = (
            "UP ✅ (OSIR.py --web running)"
            if m_ok
            else f"DOWN ❌ ({m_detail or 'start master using OSIR.py --web inside master-master container'})"
        )
        a_status = (
            "UP ✅ (OSIR.py --agent running)"
            if a_ok
            else f"DOWN ❌ ({a_detail or 'start agent using OSIR.py --agent inside agent-agent container'})"
        )

        m_fp, m_fp_detail = self._fingerprint_status(self.master)
        a_fp, a_fp_detail = self._fingerprint_status(self.agent)
        
        body = (
            "Expected processes inside containers:\n"
            "  • master-master : OSIR.py --web\n"
            "  • agent-agent   : OSIR.py --agent\n\n"
            f"Master process check : {m_status}\n"
            f"Agent process check  : {a_status}\n\n"
            "Dockerfile fingerprint check:\n"
            f"  • MASTER image : {m_fp}\n"
            f"    {m_fp_detail.replace(chr(10), chr(10) + '    ')}\n"
            f"  • AGENT  image : {a_fp}\n"
            f"    {a_fp_detail.replace(chr(10), chr(10) + '    ')}"
        )
        self.ui.box("OSIR status", body)

        if not verbose:
            return

        master_images = self.docker.images_by_ref("master-*")
        agent_images = self.docker.images_by_ref("agent-*")
        self.ui.box("Docker images - Master component (master-*)", fmt_images(master_images))
        self.ui.box("Docker images - Agent component (agent-*)", fmt_images(agent_images))

        master_containers = group_containers_by_prefix("master-", self.docker)
        agent_containers = group_containers_by_prefix("agent-", self.docker)

        def fmt_group(infos: List[Dict]) -> str:
            """Format a list of container infos into a double-spaced list.

            Args:
                infos: List of container info dicts.

            Returns:
                str: Human-readable grouped container info.
            """
            if not infos:
                return "(no containers found)"
            chunks = [fmt_container_block(ci) for ci in infos]
            return "\n\n".join(chunks)

        self.ui.box("Containers - master", fmt_group(master_containers))
        self.ui.box("Containers - agent", fmt_group(agent_containers))

    def ensure_env(self):
        """Ensures that .env files exist, copying from .env.example if needed."""
        import shutil
        from pathlib import Path
        
        for setup_type in ["agent", "master"]:
            env_path = Path(f"./setup/{setup_type}/.env")
            example_path = Path(f"./setup/{setup_type}/.env.example")
            
            if not env_path.exists():
                if not example_path.exists():
                    raise FileNotFoundError(
                        f"Missing {example_path}. Cannot create {env_path}. You must setup .env file !"
                    )
                shutil.copy(example_path, env_path)

    def main(self) -> None:
        """Program entrypoint: handle elevation, parse args, and dispatch."""
        if os.geteuid() != 0 and not os.environ.get("OSIR_LAUNCHER_AS_ROOT"):
            os.environ["OSIR_LAUNCHER_AS_ROOT"] = "1"
            try:
                os.execvp("sudo", ["sudo", "-E", sys.executable, os.path.realpath(__file__), *sys.argv[1:]])
            except Exception as exc:
                sys.exit(f"Failed to elevate privileges: {exc}")
        
        self.ensure_env()

        args = self.parse_arguments()
        if args.command == "start":
            self.cmd_start(args)
        elif args.command == "stop":
            self.cmd_stop(args)
        elif args.command == "status":
            self.cmd_status(args)
        elif args.command == "airgap":
            self.cmd_airgap(args)
        else:
            sys.exit(f"Unknown command: {args.command}")


# ────────────────────────────────────────────────────────────────────────────────
# __main__
# ────────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    Launcher().main()
