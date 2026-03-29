import pytest
import respx
import httpx
from inventree_mcp.client import InvenTreeClient


@pytest.fixture
def client():
    return InvenTreeClient(base_url="http://test.local", token="test-token")


@pytest.mark.asyncio
async def test_get_single_page(client):
    with respx.mock(base_url="http://test.local") as mock:
        mock.get("/api/part/").mock(return_value=httpx.Response(200, json={
            "count": 2, "next": None, "results": [{"pk": 1}, {"pk": 2}]
        }))
        result = await client.get("/api/part/")
    assert result == {"count": 2, "next": None, "results": [{"pk": 1}, {"pk": 2}]}


@pytest.mark.asyncio
async def test_get_all_paginates(client):
    with respx.mock(base_url="http://test.local") as mock:
        mock.get("/api/part/", params={"limit": 100, "offset": 0}).mock(
            return_value=httpx.Response(200, json={
                "count": 3, "next": "http://test.local/api/part/?offset=2",
                "results": [{"pk": 1}, {"pk": 2}]
            })
        )
        mock.get("/api/part/", params={"limit": 100, "offset": 2}).mock(
            return_value=httpx.Response(200, json={
                "count": 3, "next": None, "results": [{"pk": 3}]
            })
        )
        results = await client.get_all("/api/part/")
    assert results == [{"pk": 1}, {"pk": 2}, {"pk": 3}]


@pytest.mark.asyncio
async def test_post(client):
    with respx.mock(base_url="http://test.local") as mock:
        mock.post("/api/part/").mock(return_value=httpx.Response(201, json={"pk": 42, "name": "Widget"}))
        result = await client.post("/api/part/", json={"name": "Widget"})
    assert result == {"pk": 42, "name": "Widget"}


@pytest.mark.asyncio
async def test_raises_on_error(client):
    with respx.mock(base_url="http://test.local") as mock:
        mock.get("/api/part/99/").mock(return_value=httpx.Response(404, json={"detail": "Not found"}))
        with pytest.raises(httpx.HTTPStatusError):
            await client.get("/api/part/99/")
