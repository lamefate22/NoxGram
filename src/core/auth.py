from src.core.exceptions import AuthError, CryptoError
from src.infrastructure.config import NoxConfig
from src.infrastructure.decorators import debug
from telethon.sessions import StringSession
from src.infrastructure.logger import log
from src.core.models import SessionModel
from src.core.crypto import NoxCrypto
from src.ui.console import NoxConsole
from telethon import TelegramClient
from typing import Tuple
import base64
import os


class NoxAuth:
    """A class for working with Telegram authorization."""
    def __init__(self, config: NoxConfig, console: NoxConsole):
        self.config = config
        self.console = console
        log.info(f"initialized NoxAuth(config={type(config).__name__}, console={type(console).__name__}) successfully")

    async def login(self) -> TelegramClient:
        """The main authorization method."""
        log.info("authenticating with NoxGram")

        await self.config.load()
        use_auto = self.console.ask_confirm("Do you want to use auto-login")

        if use_auto and len(self.config.data.sessions) > 0:
            return await self._automatic_login()
        return await self._manual_login()

    @debug()
    async def _manual_login(self) -> TelegramClient:
        """Log in to your account manually."""
        log.info("the manual authorization method is selected")
        phone, api_id, api_hash = self._ask_manual_login_data()
        client = TelegramClient(StringSession(), api_id, api_hash)
        await client.start(phone=phone)

        session = client.session.save()

        password = self.console.ask_text("Enter your encryption password")
        salt = os.urandom(16)
        crypto = NoxCrypto(password=password, salt=salt)
        encrypted_session = crypto.encrypt(data=session)

        session_data = SessionModel(
            salt=base64.urlsafe_b64encode(crypto.salt).decode('ascii'),
            api_id=api_id,
            api_hash=api_hash,
            session_string=encrypted_session
        )

        await self.config.add_session(phone=phone,session_data=session_data)
        return client

    @debug()
    async def _automatic_login(self) -> TelegramClient:
        """Log in to your account automatically."""
        log.info("the automatic authorization method is selected")
        phone, session_data = self._ask_automatic_login_data()

        try:
            password = self.console.ask_text("Enter your decryption password")
            salt = base64.urlsafe_b64decode(session_data.salt)
            crypto = NoxCrypto(password=password, salt=salt)
            decrypted_session = crypto.decrypt(data=session_data.session_string)
        except CryptoError as e:
            raise AuthError(f"Decryption failed for {session_data} session: {e}")

        client = TelegramClient(
            StringSession(decrypted_session),
            session_data.api_id,
            session_data.api_hash
        )

        await client.start(phone=phone)
        return client

    def _ask_manual_login_data(self) -> Tuple[str, int, str]:
        """Requests data for manual authorization."""
        phone = self.console.ask_text(hint="Enter phone number")

        if self.config.get_session(phone=phone) is not None:
            raise AuthError(f"Session for {phone} already exists.")

        api_id = self.console.ask_integer(hint="Enter account API_ID")
        api_hash = self.console.ask_text(hint="Enter account API_HASH")

        return phone, api_id, api_hash

    def _ask_automatic_login_data(self) -> Tuple[str, SessionModel]:
        """Requests data for automatic authorization."""
        choices = list(self.config.data.sessions.keys())
        phone = self.console.ask_autocomplete(hint="Select an authorized session", choices=choices)

        session_data = self.config.get_session(phone=phone)
        if not session_data:
            raise AuthError(f"Session for {phone} not found in config.")

        return phone, session_data
