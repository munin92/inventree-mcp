import pytest
import respx
import httpx
from inventree_mcp.tools.barcode import barcode
from inventree_mcp import config


@pytest.fixture(autouse=True)
def patch_settings(monkeypatch):
    monkeypatch.setattr(config.settings, "inventree_url", "http://test.local")
    monkeypatch.setattr(config.settings, "inventree_token", "tok")


@pytest.mark.asyncio
async def test_barcode_scan():
    with respx.mock(base_url="http://test.local") as mock:
        mock.post("/api/barcode/").mock(return_value=httpx.Response(200, json={"part": {"pk": 1}}))
        result = await barcode(operation="scan", barcode_data="INV-PART-1")
    assert "part" in result
