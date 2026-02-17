import pytest

@pytest.fixture
def test_user_credentials():
    return {
        "username": "test_user",
        "password": "test_password_123",
        "email": "test@example.com",
    }

@pytest.fixture
def test_admin_credentials():
    return {
        "username": "admin_user",
        "password": "admin_password_123",
        "email": "admin@example.com",
    }