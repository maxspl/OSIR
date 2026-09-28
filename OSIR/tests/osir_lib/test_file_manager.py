"""Unit tests for the osir_lib core helpers (no network, no database)."""
import os

from osir_lib.core.FileManager import FileManager
from osir_lib.core.OsirConstants import OSIR_PATHS, OSIR


def test_osir_version():
    assert OSIR.VERSION == 2.1


def test_paths_are_isolated_under_osir_home():
    """The test conftest redirects OSIR_HOME; every path must follow."""
    home = os.environ["OSIR_HOME"]
    assert str(OSIR_PATHS.CASES_DIR) == os.path.join(home, "share", "cases")
    assert str(OSIR_PATHS.PROFILES_DIR) == os.path.join(home, "OSIR", "configs", "profiles")
    assert str(OSIR_PATHS.MODULES_DIR) == os.path.join(home, "OSIR", "configs", "modules")
    assert OSIR_PATHS.CASES_DIR.is_dir()


def test_get_yaml_files(tmp_path):
    (tmp_path / "a.yml").write_text("modules: []\n")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.yml").write_text("modules: []\n")
    (tmp_path / "ignored.txt").write_text("nope")

    names = FileManager.get_yaml_files(str(tmp_path))
    assert sorted(names) == ["a.yml", "b.yml"]

    relative = FileManager.get_yaml_files(str(tmp_path), relative=True)
    assert sorted(relative) == ["a.yml", os.path.join("sub", "b.yml")]


def test_get_subdirectories(tmp_path):
    (tmp_path / "case_one").mkdir()
    (tmp_path / "case_two").mkdir()
    (tmp_path / "not_a_dir.txt").write_text("x")

    assert sorted(FileManager.get_subdirectories(tmp_path)) == ["case_one", "case_two"]


def test_get_subfiles(tmp_path):
    (tmp_path / "one.evtx").write_bytes(b"1")
    (tmp_path / "two.evtx").write_bytes(b"2")
    (tmp_path / "subdir").mkdir()

    files = {f.name for f in FileManager.get_subfiles(tmp_path)}
    assert files == {"one.evtx", "two.evtx"}
    assert FileManager.get_subfiles(tmp_path / "missing") == []


def test_create_case(tmp_path):
    status, path = FileManager.create_case(str(tmp_path), "fresh_case")
    assert status == "created"
    assert os.path.isdir(path)

    status, path = FileManager.create_case(str(tmp_path), "fresh_case")
    assert status == "exists"


def test_get_cases_path():
    FileManager.create_case(str(OSIR_PATHS.CASES_DIR), "known_case")
    assert FileManager.get_cases_path("known_case") is not None
    assert FileManager.get_cases_path("unknown_case") is None
