from src.core.auth import NoxAuth, AuthError
from src.core.crypto import NoxCrypto
from src.core.models import SessionModel, SettingsModel
from src.infrastructure.config import NoxConfig
from src.ui.console import NoxConsole
from unittest.mock import AsyncMock, Mock, patch, call
from telethon import TelegramClient
from telethon.sessions import StringSession
import pytest
import os
import re
from src.core.exceptions import CryptoError


@pytest.fixture
def mock_config():
    config = AsyncMock(spec=NoxConfig)
    config.data = SettingsModel(sessions={})
    config.load.return_value = config.data
    config.add_session = AsyncMock()
    config.get_session.return_value = None
    return config


@pytest.fixture
def mock_console():
    console = Mock(spec=NoxConsole)
    console.ask_confirm.return_value = False
    console.ask_integer.return_value = 12345
    console.ask_autocomplete.return_value = "1234567890"
    return console


@pytest.fixture
def mock_crypto_instance_factory():
    crypto = Mock(spec=NoxCrypto)
    crypto.encrypt.return_value = "encrypted_session_string"
    crypto.decrypt.return_value = "decrypted_session_string"
    crypto.salt = Mock()
    crypto.salt.decode.return_value = b"test_salt_bytes_"[:16].decode()
    return crypto


@pytest.mark.asyncio
@patch('src.core.auth.TelegramClient', autospec=True)
@patch('src.core.auth.NoxCrypto', autospec=True)
@patch('src.core.auth.StringSession', autospec=True)
async def test_manual_login_success(
    mock_string_session_cls, mock_nox_crypto_cls, mock_telegram_client_cls, mock_config, mock_console,
    mock_crypto_instance_factory
):
    mock_console.ask_confirm.return_value = False
    mock_console.ask_text.side_effect = ["+1234567890", "API_HASH", "password"]
    mock_console.ask_integer.return_value = 12345

    mock_client_instance = mock_telegram_client_cls.return_value
    mock_client_instance.start = AsyncMock()
    mock_client_instance.session = Mock()
    mock_client_instance.session.save.return_value = "raw_session_string"

    mock_nox_crypto_cls.return_value = mock_crypto_instance_factory

    auth = NoxAuth(config=mock_config, console=mock_console)
    client = await auth.login()

    assert client is not None
    mock_config.add_session.assert_called_once()



@pytest.mark.asyncio
@patch('src.core.auth.TelegramClient', autospec=True)
@patch('src.core.auth.NoxCrypto', autospec=True)
@patch('src.core.auth.StringSession', autospec=True)
async def test_automatic_login_success(
    mock_string_session_cls, mock_nox_crypto_cls, mock_telegram_client_cls, mock_config, mock_console, mock_crypto_instance_factory
):
    phone_number = "+1234567890"
    stored_salt = b"stored_salt_bytes_"[:16]
    stored_api_id = 54321
    stored_api_hash = "STORED_API_HASH"
    stored_encrypted_session = "STORED_ENCRYPTED_SESSION"
    stored_decrypted_session = "STORED_DECRYPTED_SESSION"


    session_data = SessionModel(
        salt=stored_salt.decode(),
        api_id=stored_api_id,
        api_hash=stored_api_hash,
        session_string=stored_encrypted_session
    )
    mock_config.data.sessions[phone_number] = session_data
    mock_config.get_session.return_value = session_data


    mock_console.ask_confirm.return_value = True
    mock_console.ask_autocomplete.return_value = phone_number
    mock_console.ask_text.return_value = "password_for_decryption"


    mock_client_instance = mock_telegram_client_cls.return_value
    mock_client_instance.start = AsyncMock()

    mock_nox_crypto_instance = mock_crypto_instance_factory
    mock_nox_crypto_cls.return_value = mock_nox_crypto_instance
    mock_nox_crypto_instance.decrypt.return_value = stored_decrypted_session

    mock_string_session_cls.return_value = Mock(spec=StringSession)


    auth = NoxAuth(config=mock_config, console=mock_console)
    client = await auth.login()

    mock_console.ask_confirm.assert_called_once_with("Do you want to use auto-login")
    mock_console.ask_autocomplete.assert_called_once_with(
        hint="Select an authorized session", choices=[phone_number]
    )
    mock_console.ask_text.assert_called_once_with("Enter your decryption password")

    mock_config.get_session.assert_called_once_with(phone=phone_number)

    mock_nox_crypto_cls.assert_called_once_with(
        password="password_for_decryption",
        salt=stored_salt
    )
    mock_nox_crypto_instance.decrypt.assert_called_once_with(data=stored_encrypted_session)

    mock_telegram_client_cls.assert_called_once_with(
        mock_string_session_cls.return_value,
        stored_api_id,
        stored_api_hash
    )
    mock_client_instance.start.assert_called_once_with(phone=phone_number)

    assert client == mock_client_instance


@pytest.mark.asyncio
@patch('src.core.auth.NoxCrypto', autospec=True)
@patch('src.core.auth.StringSession', autospec=True)
async def test_automatic_login_wrong_password_fails(
    mock_string_session_cls, mock_nox_crypto_cls, mock_config, mock_console, mock_crypto_instance_factory
):
    phone_number = "+1234567890"
    stored_salt = b"stored_salt_bytes_"[:16]
    stored_api_id = 54321
    stored_api_hash = "STORED_API_HASH"
    stored_encrypted_session = "STORED_ENCRYPTED_SESSION"

    session_data = SessionModel(
        salt=stored_salt.decode(),
        api_id=stored_api_id,
        api_hash=stored_api_hash,
        session_string=stored_encrypted_session
    )
    mock_config.data.sessions[phone_number] = session_data
    mock_config.get_session.return_value = session_data


    mock_console.ask_confirm.return_value = True
    mock_console.ask_autocomplete.return_value = phone_number
    mock_console.ask_text.return_value = "wrong_password"

    mock_nox_crypto_instance = mock_crypto_instance_factory
    mock_nox_crypto_cls.return_value = mock_nox_crypto_instance
    mock_nox_crypto_instance.decrypt.side_effect = CryptoError("Invalid token")

    auth = NoxAuth(config=mock_config, console=mock_console)

    with pytest.raises(AuthError, match=f"Decryption failed for .* session: Invalid token"):
        await auth.login()

    mock_nox_crypto_cls.assert_called_once_with(
        password="wrong_password",
        salt=stored_salt
    )
    mock_nox_crypto_instance.decrypt.assert_called_once_with(data=stored_encrypted_session)


@pytest.mark.asyncio
async def test_manual_login_session_exists_raises_error(mock_config, mock_console):
    phone_number = "+1234567890"
    mock_config.get_session.return_value = SessionModel(
        salt="abc", api_id=1, api_hash="hash", session_string="string"
    )

    mock_console.ask_confirm.return_value = False
    mock_console.ask_text.return_value = phone_number

    auth = NoxAuth(config=mock_config, console=mock_console)

    with pytest.raises(AuthError, match=re.escape(f"Session for {phone_number} already exists.")):
        await auth.login()

    mock_console.ask_text.assert_called_once_with(hint="Enter phone number")
    mock_config.get_session.assert_called_once_with(phone=phone_number)


@pytest.mark.asyncio
@patch('src.core.auth.TelegramClient', autospec=True)
@patch('src.core.auth.NoxCrypto', autospec=True)
@patch('src.core.auth.StringSession', autospec=True)
async def test_automatic_login_session_not_found_raises_error(
    mock_string_session_cls, mock_nox_crypto_cls, mock_telegram_client_cls, mock_config, mock_console,
    mock_crypto_instance_factory
):
    mock_config.data.sessions["+1111111111"] = SessionModel(
        salt="dummy_salt", api_id=1, api_hash="dummy_hash", session_string="dummy_string"
    )
    
    original_get_session = mock_config.get_session
    def get_session_side_effect(phone):
        if phone == "non_existent_phone":
            return None
        return original_get_session(phone)

    mock_config.get_session.side_effect = lambda phone: None if phone == "non_existent_phone" else SessionModel(
        salt="dummy_salt", api_id=1, api_hash="dummy_hash", session_string="dummy_string"
    )

    mock_console.ask_confirm.return_value = True
    mock_console.ask_autocomplete.return_value = "non_existent_phone"

    auth = NoxAuth(config=mock_config, console=mock_console)

    mock_client_instance = mock_telegram_client_cls.return_value
    mock_client_instance.start = AsyncMock()
    mock_client_instance.session = Mock() 

    mock_nox_crypto_instance = mock_crypto_instance_factory
    mock_nox_crypto_cls.return_value = mock_nox_crypto_instance


    with pytest.raises(AuthError, match=re.escape(f"Session for non_existent_phone not found in config.")):
        await auth.login()

    mock_console.ask_autocomplete.assert_called_once_with(
        hint="Select an authorized session", choices=["+1111111111"]
    )
    mock_config.get_session.assert_called_once_with(phone="non_existent_phone")
    mock_telegram_client_cls.assert_not_called()
    mock_nox_crypto_cls.assert_not_called()
