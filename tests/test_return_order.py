import pytest
import respx
import httpx
from inventree_mcp.tools.return_order import return_order
from inventree_mcp import config


@pytest.fixture(autouse=True)
def patch_settings(monkeypatch):
    monkeypatch.setattr(config.settings, "inventree_url", "http://test.local")
    monkeypatch.setattr(config.settings, "inventree_token", "tok")


@pytest.mark.asyncio
async def test_ro_list():
    with respx.mock(base_url="http://test.local") as mock:
        mock.get("/api/order/ro/").mock(return_value=httpx.Response(200, json={"count": 0, "next": None, "results": []}))
        result = await return_order(operation="list")
    assert result == []
