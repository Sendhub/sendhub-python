import importlib
import logging

import sendhub.constants as constants


def test_constants_production_env_sets_error_level(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT_DETAIL", "production")
    reloaded = importlib.reload(constants)
    assert reloaded.ENVIRONMENT_DETAIL == "production"
    assert reloaded.LOGGER.level == logging.ERROR
    assert reloaded.VERIFY_SSL is True

    monkeypatch.setenv("ENVIRONMENT_DETAIL", "development")
    importlib.reload(constants)
