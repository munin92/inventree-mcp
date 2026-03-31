import pytest
import respx
import httpx
from inventree_mcp.tools.purchase_order import purchase_order
from inventree_mcp import config


@pytest.fixture(autouse=True)
def patch_settings(monkeypatch):
    monkeypatch.setattr(config.settings, "inventree_url", "http://test.local")
    monkeypatch.setattr(config.settings, "inventree_token", "tok")


@pytest.mark.asyncio
async def test_po_list():
    with respx.mock(base_url="http://test.local") as mock:
        mock.get("/api/order/po/").mock(return_value=httpx.Response(200, json={"count": 0, "next": None, "results": []}))
        result = await purchase_order(operation="list")
    assert result == []


@pytest.mark.asyncio
async def test_po_receive():
    with respx.mock(base_url="http://test.local") as mock:
        mock.post("/api/order/po/5/receive/").mock(return_value=httpx.Response(200, json={"success": True}))
        result = await purchase_order(operation="receive", pk=5, data={"items": [{"pk": 1, "quantity": 10}]})
    assert result["success"] is True
