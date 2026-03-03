from src.core.models import SettingsModel, SessionModel
from pydantic_core import PydanticSerializationError
from src.infrastructure.decorators import debug
from src.core.exceptions import ConfigError
from src.infrastructure.logger import log
from pydantic import ValidationError
from typing import Optional
from pathlib import Path
import aiofiles


class NoxConfig:
    """
    Class for working with the application configuration.
    """
    def __init__(self, path: str = "data/config.nox"):
        self.path = Path(path)
        self.data = SettingsModel()
        log.info(f"initialized NoxConfig(path={path}) successfully")

    async def _ensure_config_exists(self) -> None:
        """A private method that checks for the presence of a config. If it doesn't exist, it creates it."""
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            await self.save()

    @debug()
    async def load(self) -> SettingsModel:
        """Loads the config from the disk. If it is missing, it creates an empty one."""
        await self._ensure_config_exists()
        try:
            async with aiofiles.open(self.path, mode="r", encoding="utf-8") as f:
                content = await f.read()
                self.data = SettingsModel.model_validate_json(content)
                return self.data
        except (OSError, ValidationError) as e:
            raise ConfigError(f"An error occurred while loading the configuration: {e}")

    @debug()
    async def save(self) -> None:
        """Saves the settings to a file."""
        try:
            tmp_path = self.path.with_suffix(".tmp")
            async with aiofiles.open(tmp_path, mode="w", encoding="utf-8") as f:
                await f.write(self.data.model_dump_json(indent=4))

            tmp_path.replace(self.path)
        except (OSError, PydanticSerializationError) as e:
            raise ConfigError(f"An error occurred while saving the configuration: {e}")

    @debug(mask_call_info=True)
    async def remove_session(self, phone: str) -> None:
        """Removes a session from the config and saves it."""
        if phone in self.data.sessions:
            del self.data.sessions[phone]
            await self.save()

    @debug(mask_call_info=True)
    async def add_session(self, phone: str, session_data: SessionModel) -> None:
        """Adds a new session to the config and saves it."""
        self.data.sessions[phone] = session_data
        await self.save()

    def get_session(self, phone: str) -> Optional[SessionModel]:
        """Returns a session from the config."""
        return self.data.sessions.get(phone)
