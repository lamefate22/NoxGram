from src.core.exceptions import CryptoError
from src.core.crypto import NoxCrypto
import pytest
import os


def test_encrypt_decrypt_simple():
    password = "testpassword"
    salt = os.urandom(16)
    crypto = NoxCrypto(password=password, salt=salt)
    original_data = "simple_content"

    encrypted_data = crypto.encrypt(original_data)
    decrypted_data = crypto.decrypt(encrypted_data)

    assert decrypted_data == original_data


def test_encrypt_decrypt_unicode():
    password = "testpassword"
    salt = os.urandom(16)
    crypto = NoxCrypto(password=password, salt=salt)
    original_data = "Привет, мир! 你好, 世界! 👋"

    encrypted_data = crypto.encrypt(original_data)
    decrypted_data = crypto.decrypt(encrypted_data)

    assert decrypted_data == original_data


def test_encrypt_empty_string_raises_error():
    password = "testpassword"
    salt = os.urandom(16)
    crypto = NoxCrypto(password=password, salt=salt)
    empty_data = ""

    with pytest.raises(CryptoError, match="An empty string was passed to the encryption function."):
        crypto.encrypt(empty_data)


def test_decrypt_empty_string_raises_error():
    password = "testpassword"
    salt = os.urandom(16)
    crypto = NoxCrypto(password=password, salt=salt)
    empty_data = ""

    with pytest.raises(CryptoError, match="An empty string was passed to the decryption function."):
        crypto.decrypt(empty_data)


def test_decrypt_with_wrong_password_fails():
    shared_salt = os.urandom(16)
    original_data = "secret_message"

    crypto_correct_pw = NoxCrypto(password="correct_password", salt=shared_salt)
    crypto_wrong_pw = NoxCrypto(password="wrong_password", salt=shared_salt)

    encrypted_data = crypto_correct_pw.encrypt(original_data)

    with pytest.raises(CryptoError, match="An error occurred during decryption. An incorrect token may have been transmitted."):
        crypto_wrong_pw.decrypt(encrypted_data)


def test_decrypt_with_wrong_salt_fails():
    password = "testpassword"
    salt1 = os.urandom(16)
    salt2 = os.urandom(16)
    original_data = "some secret data"

    assert salt1 != salt2

    crypto_correct_salt = NoxCrypto(password=password, salt=salt1)
    crypto_wrong_salt = NoxCrypto(password=password, salt=salt2)

    encrypted_data = crypto_correct_salt.encrypt(original_data)

    with pytest.raises(CryptoError, match="An error occurred during decryption. An incorrect token may have been transmitted."):
        crypto_wrong_salt.decrypt(encrypted_data)


def test_decrypt_tampered_data_fails():
    password = "testpassword"
    salt = os.urandom(16)
    crypto = NoxCrypto(password=password, salt=salt)
    original_data = "test_data_to_tamper"

    encrypted_data = crypto.encrypt(original_data)

    tampered_encrypted_data = encrypted_data[:-1] + "a"

    with pytest.raises(CryptoError, match="An error occurred during decryption. An incorrect token may have been transmitted."):
        crypto.decrypt(tampered_encrypted_data)


def test_decrypt_invalid_base64_string_raises_error():
    password = "testpassword"
    salt = os.urandom(16)
    crypto = NoxCrypto(password=password, salt=salt)
    invalid_base64_data = "this is not valid base64 data"

    with pytest.raises(CryptoError, match="An error occurred during decryption. An incorrect token may have been transmitted."):
        crypto.decrypt(invalid_base64_data)
