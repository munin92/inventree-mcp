from fastmcp import FastMCP
from .config import settings
from .client import InvenTreeClient

mcp = FastMCP(
    name="InvenTree MCP",
    instructions="Tools for managing InvenTree inventory. Each tool uses an 'operation' parameter to select the action.",
)


def get_client() -> InvenTreeClient:
    return InvenTreeClient(
        base_url=settings.inventree_url,
        token=settings.inventree_token,
    )


# Import tools (registers them on mcp via @mcp.tool decorator)
from .tools import *  # noqa: F401, E402


def main():
    mcp.run(
        transport="http",
        host=settings.mcp_host,
        port=settings.mcp_port,
    )


if __name__ == "__main__":
    main()
