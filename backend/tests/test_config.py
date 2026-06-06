from app.config import settings


def test_settings_load_required_values():
    assert settings.database_url
    assert settings.secret_key
    assert 0 <= settings.confidence_threshold <= 1

