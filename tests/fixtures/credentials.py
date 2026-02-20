"""Test credentials — loaded from environment variables with safe defaults.

CI pipelines should set TEST_USER_PASSWORD, TEST_ADMIN_PASSWORD, TEST_API_KEY,
and TEST_TOKEN via the secrets manager. For local development, either configure
a `.env` file (loaded by python-dotenv) or rely on the dummy defaults below.

DO NOT commit real secrets into source control.
"""

import os

import pytest

# Centralised test credential constants — read from env, fall back to dummies
_TEST_USER_PASSWORD = os.environ.get("TEST_USER_PASSWORD", "test_password_placeholder")
_TEST_ADMIN_PASSWORD = os.environ.get("TEST_ADMIN_PASSWORD", "admin_password_placeholder")
_TEST_API_KEY = os.environ.get("TEST_API_KEY", "test_api_key_placeholder")
_TEST_TOKEN = os.environ.get("TEST_TOKEN", "test_token_placeholder")


@pytest.fixture
def test_user_credentials():
    return {
        "username": "test_user",
        "password": _TEST_USER_PASSWORD,
        "email": "test@example.com",
    }


@pytest.fixture
def test_admin_credentials():
    return {
        "username": "admin_user",
        "password": _TEST_ADMIN_PASSWORD,
        "email": "admin@example.com",
    }


# Shared dict for modules that import credentials directly
TEST_CREDENTIALS = {
    "username": "test_user",
    "password": _TEST_USER_PASSWORD,
    "api_key": _TEST_API_KEY,
    "token": _TEST_TOKEN,
}
