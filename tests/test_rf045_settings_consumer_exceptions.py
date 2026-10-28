"""RF-045 C2/C3: Settings keeps caller environment precedence and typed failures."""

from __future__ import annotations

import pytest

from libs.core.settings import Settings


def test_rf045_settings_does_not_override_preexisting_consumer_environment(monkeypatch, tmp_path):
    env_file = tmp_path / "settings.env"
    env_file.write_text("KIWOOM_MODE=mock\nKIWOOM_HTTP_TIMEOUT_SEC=17\n", encoding="utf-8")
    monkeypatch.setenv("KIWOOM_MODE", "real")
    monkeypatch.delenv("KIWOOM_HTTP_TIMEOUT_SEC", raising=False)

    settings = Settings.from_env(env_file)

    assert settings.kiwoom_mode == "real"
    assert settings.kiwoom_http_timeout_sec == 17
    assert settings.base_url == settings.kiwoom_base_url_real


def test_rf045_settings_rejects_invalid_integer_from_temp_env(monkeypatch, tmp_path):
    env_file = tmp_path / "invalid.env"
    env_file.write_text("KIWOOM_RETRY_MAX=not-an-int\n", encoding="utf-8")
    monkeypatch.delenv("KIWOOM_RETRY_MAX", raising=False)

    with pytest.raises(ValueError, match="Invalid int for KIWOOM_RETRY_MAX: not-an-int"):
        Settings.from_env(env_file)
