from pathlib import Path
from daisys_mcp.utils import make_output_path, is_file_writeable


def test_make_output_path_default(monkeypatch, tmp_path):
    # Redirect Path.home() to a temp location
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    path = make_output_path(None)
    assert path.exists()
    assert path.name == "Desktop"


def test_make_output_path_relative(monkeypatch, tmp_path):
    relative_dir = "outputs"
    base_path = str(tmp_path)
    path = make_output_path(relative_dir, base_path)
    assert path.exists()
    assert path.name == "outputs"
    assert is_file_writeable(path)


def test_make_output_path_absolute(tmp_path):
    absolute_dir = str(tmp_path / "absolute_output")
    path = make_output_path(absolute_dir)
    assert path.exists()
    assert path.name == "absolute_output"
    assert is_file_writeable(path)
