import pytest
import respx
import httpx
from inventree_mcp.tools.build_order import build_order
from inventree_mcp import config


@pytest.fixture(autouse=True)
def patch_settings(monkeypatch):
    monkeypatch.setattr(config.settings, "inventree_url", "http://test.local")
    monkeypatch.setattr(config.settings, "inventree_token", "tok")


@pytest.mark.asyncio
async def test_build_list():
    with respx.mock(base_url="http://test.local") as mock:
        mock.get("/api/build/").mock(return_value=httpx.Response(200, json={"count": 0, "next": None, "results": []}))
        result = await build_order(operation="list")
    assert result == []


@pytest.mark.asyncio
async def test_build_complete():
    with respx.mock(base_url="http://test.local") as mock:
        mock.post("/api/build/7/complete/").mock(return_value=httpx.Response(200, json={"status": "complete"}))
        result = await build_order(operation="complete", pk=7, data={})
    assert result["status"] == "complete"
