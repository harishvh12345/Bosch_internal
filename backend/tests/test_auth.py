import pytest
from app.core.security import security_service

def test_password_hashing():
    password = "supersecretpassword123"
    hashed = security_service.hash_password(password)
    
    assert hashed != password
    assert security_service.verify_password(password, hashed)
    assert not security_service.verify_password("wrongpassword", hashed)

def test_jwt_token_generation():
    claims = {"sub": "test_user_id", "role": "Employee"}
    token = security_service.create_access_token(claims, expires_delta=10)
    
    assert token is not None
    assert isinstance(token, str)
    
    decoded = security_service.decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "test_user_id"
    assert decoded["role"] == "Employee"

def test_jwt_token_invalid():
    decoded = security_service.decode_access_token("invalid.jwt.token.string")
    assert decoded is None
