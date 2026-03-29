import pytest
import respx
import httpx
from inventree_mcp.tools.part import part
from inventree_mcp import config


@pytest.fixture(autouse=True)
def patch_settings(monkeypatch):
    monkeypatch.setattr(config.settings, "inventree_url", "http://test.local")
    monkeypatch.setattr(config.settings, "inventree_token", "tok")


@pytest.mark.asyncio
async def test_part_list():
    with respx.mock(base_url="http://test.local") as mock:
        mock.get("/api/part/").mock(return_value=httpx.Response(200, json={
            "count": 1, "next": None, "results": [{"pk": 1, "name": "Widget"}]
        }))
        result = await part(operation="list")
    assert result[0]["pk"] == 1


@pytest.mark.asyncio
async def test_part_get():
    with respx.mock(base_url="http://test.local") as mock:
        mock.get("/api/part/42/").mock(return_value=httpx.Response(200, json={"pk": 42, "name": "Bolt"}))
        result = await part(operation="get", pk=42)
    assert result["pk"] == 42


@pytest.mark.asyncio
async def test_part_unknown_operation():
    with pytest.raises(ValueError, match="Unknown operation"):
        await part(operation="foobar")
