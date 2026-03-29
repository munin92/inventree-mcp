import pytest
from inventree_mcp.client import InvenTreeClient
from inventree_mcp.config import settings


@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setattr(settings, "inventree_url", "http://test.local")
    monkeypatch.setattr(settings, "inventree_token", "test-token")
    return settings


@pytest.fixture
def client(mock_settings):
    return InvenTreeClient(
        base_url=mock_settings.inventree_url,
        token=mock_settings.inventree_token,
    )
