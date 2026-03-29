import pytest
import respx
import httpx
from inventree_mcp.tools.system import system
from inventree_mcp import config


@pytest.fixture(autouse=True)
def patch_settings(monkeypatch):
    monkeypatch.setattr(config.settings, "inventree_url", "http://test.local")
    monkeypatch.setattr(config.settings, "inventree_token", "tok")


@pytest.mark.asyncio
async def test_system_version():
    with respx.mock(base_url="http://test.local") as mock:
        mock.get("/api/").mock(return_value=httpx.Response(200, json={"version": "1.2.3", "system_health": True}))
        result = await system(operation="version")
    assert result["version"] == "1.2.3"
