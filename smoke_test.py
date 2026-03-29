"""
End-to-end smoke test against live InvenTree.

Prerequisites:
  1. Port-forward InvenTree: kubectl port-forward -n applications svc/inventree 8000:8000
  2. Copy .env.example to .env and fill in INVENTREE_TOKEN and MCP_BEARER_TOKEN
  3. Start server: inventree-mcp (or: python -m inventree_mcp.server)

Run: python smoke_test.py
"""
import asyncio
from fastmcp import Client


async def main():
    async with Client("http://localhost:8001/mcp") as c:
        tools = await c.list_tools()
        print(f"Tools ({len(tools)}): {[t.name for t in tools]}")
        assert len(tools) == 12, f"Expected 12 tools, got {len(tools)}"

        result = await c.call_tool("system", {"operation": "version"})
        print(f"InvenTree version: {result}")

        parts = await c.call_tool("part", {"operation": "list"})
        print(f"Parts count: {len(parts)}")

        categories = await c.call_tool("part", {"operation": "category_list"})
        print(f"Categories: {len(categories)}")

        stock_items = await c.call_tool("stock", {"operation": "list"})
        print(f"Stock items: {len(stock_items)}")

    print("\nSmoke test PASSED")


asyncio.run(main())
