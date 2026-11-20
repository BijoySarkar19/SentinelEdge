import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token

def test_security_hardening():
    pw = "SuperSecretOperatorPassword2026!"
    hashed = hash_password(pw)
    assert verify_password(pw, hashed) is True
    assert verify_password("InvalidPassword", hashed) is False

    token = create_access_token({"sub": "admin-1", "role": "admin"})
    decoded = decode_access_token(token)
    assert decoded["sub"] == "admin-1"
