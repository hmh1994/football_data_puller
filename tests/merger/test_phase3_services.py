from types import SimpleNamespace

import httpx
import pytest

from football_data_manager.merger.services.resource_validator import (
    ResourceValidationClient,
)
from football_data_manager.merger.services.translator import TranslatorService


@pytest.mark.asyncio
async def test_translator_returns_original_without_api_key() -> None:
    config = SimpleNamespace(
        api_list=SimpleNamespace(
            anthropic=SimpleNamespace(key=None),
        )
    )
    translator = TranslatorService(config)

    assert await translator.translate_word("Arsenal") == "Arsenal"
    assert await translator.translate_word("") == ""
    await translator.close()


def test_translator_parse_json_payload() -> None:
    raw = 'prefix {"original":"Arsenal","translated":"아스널"} suffix'
    parsed = TranslatorService._parse_json(raw)
    assert parsed.original == "Arsenal"
    assert parsed.translated == "아스널"


@pytest.mark.asyncio
async def test_resource_validator_caches_success() -> None:
    client = ResourceValidationClient()
    call_count = {"head": 0}

    async def fake_head(url: str):
        call_count["head"] += 1
        return SimpleNamespace(status_code=200)

    client._client.head = fake_head  # type: ignore[method-assign]
    url = "https://example.com/a.png"
    assert await client.validate_url_exists(url) is True
    assert await client.validate_url_exists(url) is True
    assert call_count["head"] == 1
    await client.close()


@pytest.mark.asyncio
async def test_resource_validator_handles_network_error_and_caches_false() -> None:
    client = ResourceValidationClient()
    call_count = {"head": 0}

    async def fake_head(url: str):
        call_count["head"] += 1
        raise httpx.ConnectError("network error")

    client._client.head = fake_head  # type: ignore[method-assign]
    url = "https://example.com/missing.png"
    assert await client.validate_url_exists(url) is False
    assert await client.validate_url_exists(url) is False
    assert call_count["head"] == 1
    await client.close()
