"""Cleanup argument contract using fake repo paths and deletion spies only."""
import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def cleanup(tmp_path, monkeypatch):
    source = Path(__file__).resolve().parents[1] / 'scripts/cleanup_pytest_artifacts.py'
    spec = importlib.util.spec_from_file_location('cleanup_fixture', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, '__file__', str(tmp_path / 'scripts/cleanup_pytest_artifacts.py'))
    calls = []
    monkeypatch.setattr(module, '_remove_tree', calls.append)
    return module, calls


def test_help_exits_before_glob_or_delete(cleanup, capsys, monkeypatch):
    module, calls = cleanup
    monkeypatch.setattr(Path, 'glob', lambda *args: pytest.fail('help must not enumerate'))
    with pytest.raises(SystemExit) as error:
        module.main(['--help'])
    assert error.value.code == 0
    assert 'usage:' in capsys.readouterr().out
    assert calls == []


def test_unknown_option_exits_before_delete(cleanup, monkeypatch):
    module, calls = cleanup
    monkeypatch.setattr(Path, 'glob', lambda *args: pytest.fail('unknown flag must not enumerate'))
    with pytest.raises(SystemExit) as error:
        module.main(['--unknown'])
    assert error.value.code == 2
    assert calls == []


def test_zero_args_preserves_legacy_matching_behavior(cleanup, tmp_path):
    module, calls = cleanup
    expected = []
    for relative in ('.pytest-work-old', '.pytest-work-local-old', 'pytest-cache-files-old',
                     'data/.pytest-work-old', 'data/.pytest-work-local-old', 'data/pytest-cache-files-old'):
        path = tmp_path / relative
        path.mkdir(parents=True)
        expected.append(path)
    assert module.main([]) == 0
    assert set(calls) == set(expected)
    assert all(path.exists() for path in expected)  # spy never deletes


def test_keep_directories_untouched(cleanup, tmp_path):
    module, calls = cleanup
    for name in ('.pytest-work', '.pytest_cache'):
        (tmp_path / name).mkdir()
    assert module.main([]) == 0
    assert calls == []
    assert (tmp_path / '.pytest-work').is_dir()
    assert (tmp_path / '.pytest_cache').is_dir()
