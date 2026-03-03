from src.infrastructure.config import NoxConfig
from src.core.models import SettingsModel, SessionModel
from src.core.exceptions import ConfigError
import pytest
import json


@pytest.fixture
def temp_config_path(tmp_path):
    return tmp_path / "test_config.nox"


@pytest.mark.asyncio
async def test_load_non_existent_file_creates_default(temp_config_path):
    config = NoxConfig(path=temp_config_path)

    loaded_data = await config.load()

    assert isinstance(loaded_data, SettingsModel)
    assert len(loaded_data.sessions) == 0
    assert temp_config_path.exists()
    assert json.loads(temp_config_path.read_text()) == {"sessions": {}}


@pytest.mark.asyncio
async def test_save_and_load_cycle(temp_config_path):
    config_write = NoxConfig(path=temp_config_path)
    session_data = SessionModel(
        salt="some_salt",
        api_id=12345,
        api_hash="some_hash",
        session_string="encrypted_session_string"
    )
    await config_write.add_session(phone="1234567890", session_data=session_data)
    await config_write.save()

    config_read = NoxConfig(path=temp_config_path)
    loaded_data = await config_read.load()

    assert loaded_data.sessions["1234567890"] == session_data


@pytest.mark.asyncio
async def test_add_remove_session(temp_config_path):
    config = NoxConfig(path=temp_config_path)
    await config.load()

    session_data = SessionModel(
        salt="some_salt_2",
        api_id=54321,
        api_hash="another_hash",
        session_string="another_encrypted_session_string"
    )

    await config.add_session(phone="0987654321", session_data=session_data)

    assert "0987654321" in config.data.sessions
    assert config.get_session(phone="0987654321") == session_data

    await config.remove_session(phone="0987654321")

    assert "0987654321" not in config.data.sessions
    assert config.get_session(phone="0987654321") is None

    await config.save()
    config_read = NoxConfig(path=temp_config_path)
    await config_read.load()
    assert "0987654321" not in config_read.data.sessions


@pytest.mark.asyncio
async def test_load_corrupted_file_raises_error(tmp_path):
    corrupted_config_path = tmp_path / "corrupted_config.nox"
    corrupted_config_path.write_text("this is not valid json")

    config = NoxConfig(path=corrupted_config_path)

    with pytest.raises(ConfigError, match="An error occurred while loading the configuration:"):
        await config.load()
