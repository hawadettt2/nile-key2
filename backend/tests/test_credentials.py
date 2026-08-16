import asyncio

import pytest

from app.core.credentials.api_key_credential import ApiKeyCredential
from app.core.credentials.client_id_secret_credential import ClientIdSecretCredential
from app.core.credentials.credential_store import CredentialStore
from app.core.credentials.username_password_credential import UsernamePasswordCredential


class TestApiKeyCredential:
    def test_get_type(self):
        cred = ApiKeyCredential(key="abc123", source="env")
        assert cred.get_type() == "api_key"

    def test_mask_more_than_4_chars(self):
        cred = ApiKeyCredential(key="abcdef123456", source="env")
        assert cred.mask() == "abcd***"

    def test_mask_4_chars_or_less(self):
        cred = ApiKeyCredential(key="abcd", source="env")
        assert cred.mask() == "***"

        cred2 = ApiKeyCredential(key="abc", source="env")
        assert cred2.mask() == "***"

        cred3 = ApiKeyCredential(key="", source="env")
        assert cred3.mask() == "***"

    def test_is_empty_true(self):
        cred = ApiKeyCredential(key="", source="env")
        assert cred.is_empty() is True

    def test_is_empty_false(self):
        cred = ApiKeyCredential(key="abc123", source="env")
        assert cred.is_empty() is False

    def test_source(self):
        cred = ApiKeyCredential(key="abc123", source="vault")
        assert cred.source() == "vault"

    def test_on_before_use(self):
        cred = ApiKeyCredential(key="abc123", source="env")
        asyncio.run(cred.on_before_use())

    def test_on_after_use(self):
        cred = ApiKeyCredential(key="abc123", source="env")
        asyncio.run(cred.on_after_use())

    def test_on_expiry(self):
        cred = ApiKeyCredential(key="abc123", source="env")
        asyncio.run(cred.on_expiry())


class TestUsernamePasswordCredential:
    def test_get_type(self):
        cred = UsernamePasswordCredential(username="user", password="pass", source="env")
        assert cred.get_type() == "username_password"

    def test_mask_more_than_4_chars(self):
        cred = UsernamePasswordCredential(username="user", password="abcdef123456", source="env")
        assert cred.mask() == "abcd***"

    def test_mask_4_chars_or_less(self):
        cred = UsernamePasswordCredential(username="user", password="abcd", source="env")
        assert cred.mask() == "***"

    def test_is_empty_true(self):
        cred = UsernamePasswordCredential(username="", password="", source="env")
        assert cred.is_empty() is True

        cred2 = UsernamePasswordCredential(username="user", password="", source="env")
        assert cred2.is_empty() is True

        cred3 = UsernamePasswordCredential(username="", password="pass", source="env")
        assert cred3.is_empty() is True

    def test_is_empty_false(self):
        cred = UsernamePasswordCredential(username="user", password="pass123", source="env")
        assert cred.is_empty() is False

    def test_source(self):
        cred = UsernamePasswordCredential(username="user", password="pass", source="aws_secrets_manager")
        assert cred.source() == "aws_secrets_manager"

    def test_on_before_use(self):
        cred = UsernamePasswordCredential(username="user", password="pass", source="env")
        asyncio.run(cred.on_before_use())

    def test_on_after_use(self):
        cred = UsernamePasswordCredential(username="user", password="pass", source="env")
        asyncio.run(cred.on_after_use())

    def test_on_expiry(self):
        cred = UsernamePasswordCredential(username="user", password="pass", source="env")
        asyncio.run(cred.on_expiry())


class TestClientIdSecretCredential:
    def test_get_type(self):
        cred = ClientIdSecretCredential(client_id="cid", client_secret="secret", source="env")
        assert cred.get_type() == "client_id_secret"

    def test_mask_more_than_4_chars(self):
        cred = ClientIdSecretCredential(client_id="cid", client_secret="abcdef123456", source="env")
        assert cred.mask() == "abcd***"

    def test_mask_4_chars_or_less(self):
        cred = ClientIdSecretCredential(client_id="cid", client_secret="abcd", source="env")
        assert cred.mask() == "***"

    def test_is_empty_true(self):
        cred = ClientIdSecretCredential(client_id="", client_secret="", source="env")
        assert cred.is_empty() is True

        cred2 = ClientIdSecretCredential(client_id="cid", client_secret="", source="env")
        assert cred2.is_empty() is True

        cred3 = ClientIdSecretCredential(client_id="", client_secret="secret", source="env")
        assert cred3.is_empty() is True

    def test_is_empty_false(self):
        cred = ClientIdSecretCredential(client_id="cid", client_secret="secret123", source="env")
        assert cred.is_empty() is False

    def test_source(self):
        cred = ClientIdSecretCredential(client_id="cid", client_secret="secret", source="vault")
        assert cred.source() == "vault"

    def test_on_before_use(self):
        cred = ClientIdSecretCredential(client_id="cid", client_secret="secret", source="env")
        asyncio.run(cred.on_before_use())

    def test_on_after_use(self):
        cred = ClientIdSecretCredential(client_id="cid", client_secret="secret", source="env")
        asyncio.run(cred.on_after_use())

    def test_on_expiry(self):
        cred = ClientIdSecretCredential(client_id="cid", client_secret="secret", source="env")
        asyncio.run(cred.on_expiry())


class TestCredentialStore:
    def test_register_and_get(self):
        store = CredentialStore()
        cred = ApiKeyCredential(key="abc123", source="env")
        store.register("my_key", cred)
        result = store.get("my_key")
        assert result is cred

    def test_get_missing_returns_none(self):
        store = CredentialStore()
        assert store.get("missing") is None

    def test_get_or_raise_success(self):
        store = CredentialStore()
        cred = ApiKeyCredential(key="abc123", source="env")
        store.register("my_key", cred)
        result = store.get_or_raise("my_key")
        assert result is cred

    def test_get_or_raise_missing_raises(self):
        store = CredentialStore()
        with pytest.raises(KeyError):
            store.get_or_raise("missing")

    def test_list_sources(self):
        store = CredentialStore()
        store.register("key1", ApiKeyCredential(key="abc", source="env"))
        store.register("key2", UsernamePasswordCredential(username="u", password="p", source="vault"))
        sources = store.list_sources()
        assert sources == {"key1": "env", "key2": "vault"}

    def test_list_all(self):
        store = CredentialStore()
        store.register("key1", ApiKeyCredential(key="abc", source="env"))
        store.register("key2", ApiKeyCredential(key="def", source="env"))
        names = store.list_all()
        assert set(names) == {"key1", "key2"}

    def test_list_all_empty(self):
        store = CredentialStore()
        assert store.list_all() == []

    def test_overwrite_registration(self):
        store = CredentialStore()
        cred1 = ApiKeyCredential(key="abc", source="env")
        cred2 = ApiKeyCredential(key="def", source="vault")
        store.register("my_key", cred1)
        store.register("my_key", cred2)
        assert store.get("my_key") is cred2
