import pytest
from infrastructure.auth.password import hash_password, verify_password


def test_hash_is_not_plaintext():
    hashed = hash_password("mypassword")
    assert hashed != "mypassword"


def test_verify_correct_password():
    hashed = hash_password("mypassword")
    assert verify_password("mypassword", hashed) is True


def test_verify_wrong_password():
    hashed = hash_password("mypassword")
    assert verify_password("wrong", hashed) is False


def test_same_password_different_hashes():
    """bcrypt uses a random salt — two hashes of the same password must differ."""
    h1 = hash_password("mypassword")
    h2 = hash_password("mypassword")
    assert h1 != h2
