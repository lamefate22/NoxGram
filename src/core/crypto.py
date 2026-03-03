from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from src.infrastructure.decorators import debug
from src.core.exceptions import CryptoError
from src.infrastructure.logger import log
import base64


class NoxCrypto:
    """
    Class for encrypting session strings.
    Uses PBKDF2 to generate a key from a password and Fernet for encryption.
    """
    __slots__ = ("salt", "_key", "_fernet")

    def __init__(self, password: str, salt: bytes):
        self.salt = salt
        self._key = self._derive_key(password)
        self._fernet = Fernet(self._key)
        log.info(f"initialized NoxCrypto(password=***, salt={salt}) successfully")

    @debug(mask_call_info=True)
    def encrypt(self, data: str) -> str:
        """
        Encrypts the data passed to the function.

        :param data: content to encrypt.
        """
        if not data:
            raise CryptoError("An empty string was passed to the encryption function.")

        try:
            encrypted_bytes = self._fernet.encrypt(bytes(data, "utf-8"))
            return str(encrypted_bytes, "utf-8")
        except TypeError:
            raise CryptoError("An error occurred during encryption. An incorrect type was passed to the Fernet.encrypt() function.")

    @debug(mask_call_info=True)
    def decrypt(self, data: str) -> str:
        """
        Decrypts the data passed to the function.

        :param data: content to decrypt.
        """
        if not data:
            raise CryptoError("An empty string was passed to the decryption function.")

        try:
            decrypted_bytes = self._fernet.decrypt(bytes(data, "utf-8"))
            return str(decrypted_bytes, "utf-8")
        except (InvalidToken, TypeError):
            raise CryptoError("An error occurred during decryption. An incorrect token may have been transmitted.")

    def _derive_key(self, password: str) -> bytes:
        """
        Creates a full-fledged key from the password.

        :param password: encryption password.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=500_000,
        )
        key_raw = kdf.derive(bytes(password, "utf-8"))
        return base64.urlsafe_b64encode(key_raw)
