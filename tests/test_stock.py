import pytest
import respx
import httpx
from inventree_mcp.tools.stock import stock
from inventree_mcp import config


@pytest.fixture(autouse=True)
def patch_settings(monkeypatch):
    monkeypatch.setattr(config.settings, "inventree_url", "http://test.local")
    monkeypatch.setattr(config.settings, "inventree_token", "tok")


@pytest.mark.asyncio
async def test_stock_list():
    with respx.mock(base_url="http://test.local") as mock:
        mock.get("/api/stock/").mock(return_value=httpx.Response(200, json={
            "count": 1, "next": None, "results": [{"pk": 1, "part": 5, "quantity": 10}]
        }))
        result = await stock(operation="list")
    assert result[0]["pk"] == 1


@pytest.mark.asyncio
async def test_stock_transfer():
    with respx.mock(base_url="http://test.local") as mock:
        mock.post("/api/stock/transfer/").mock(return_value=httpx.Response(200, json={"success": True}))
        result = await stock(operation="transfer", data={"items": [{"pk": 1, "quantity": 5}], "location": 2})
    assert result["success"] is True
