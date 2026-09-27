import glob
import os
import shutil
import subprocess
import sys

import pytest

OSIR_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OSIR_SRC = os.path.join(OSIR_ROOT, "src")
if OSIR_SRC not in sys.path:
    sys.path.insert(0, OSIR_SRC)

from osir_vrl.osir_vrl.OsirVrlModel import OsirVrlModel  # noqa: E402

TRANSFORM_V2 = os.path.join(OSIR_ROOT, "configs", "dependencies", "transform_v2")

# legacy configs migrated to the new transformations/timeline format
EXPECTED_CONFIGS = {
    "linux/mactime.yml",
    "network/zeek_conn.yml",
    "windows/audit_vrl.yml",
    "windows/evtx.yml",
}

# one config has a pre-existing VRL bug: the original hand-written .vrl does
# not compile either, so the compile check skips it
KNOWN_BROKEN_VRL = {"windows/live_response/dns_records.yml"}

VECTOR = shutil.which("vector")


def _yaml_files() -> list:
    return sorted(glob.glob(os.path.join(TRANSFORM_V2, "**", "*.yml"), recursive=True))


def test_migrated_configs_present():
    found = {os.path.relpath(p, TRANSFORM_V2) for p in _yaml_files()}
    assert EXPECTED_CONFIGS <= found, f"missing migrated configs: {EXPECTED_CONFIGS - found}"


@pytest.mark.parametrize("path", _yaml_files(), ids=lambda p: os.path.relpath(p, TRANSFORM_V2))
def test_migrated_config_loads_and_generates(path):
    model = OsirVrlModel.from_yaml(path)
    assert model.transformation, "no transformation blocks migrated"
    assert model.entries, "no transformation entries migrated"
    vrl = model.to_vrl()
    # linear transformations first, timeline (when any) rendered after
    assert "# transformations" in vrl
    if "# timeline" in vrl:
        assert vrl.index("# transformations") < vrl.index("# timeline")
    # metadata id (file stem) is used as module id
    assert "# Module VRL : " in vrl


@pytest.mark.skipif(VECTOR is None, reason="vector CLI not available")
@pytest.mark.parametrize("path", _yaml_files(), ids=lambda p: os.path.relpath(p, TRANSFORM_V2))
def test_migrated_config_vrl_compiles(path, tmp_path):
    rel = os.path.relpath(path, TRANSFORM_V2)
    if rel in KNOWN_BROKEN_VRL:
        pytest.skip("pre-existing bug: the original dns_records.vrl does not compile either")
    OsirVrlModel.from_yaml(path).save_vrl(str(tmp_path / "out.vrl"))
    event = tmp_path / "event.json"
    event.write_text("{}\n")
    proc = subprocess.run(
        [VECTOR, "vrl", "-p", str(tmp_path / "out.vrl"), "-i", str(event), "-o"],
        stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=60,
    )
    output = proc.stdout + proc.stderr
    assert proc.returncode == 0, output
    assert "error[E" not in output, output
