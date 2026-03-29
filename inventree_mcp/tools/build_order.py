from typing import Any
from ..server import mcp, get_client


@mcp.tool
async def build_order(
    operation: str,
    pk: int | None = None,
    part: int | None = None,
    data: dict | None = None,
) -> Any:
    """
    Manufacturing build orders.

    Operations:
    - list: List build orders. Optional filter: part (int).
    - get: Get build order by pk.
    - create: Create build order. data: {part, quantity, title (optional)}.
    - update: Update build order by pk. Pass data dict.
    - delete: Delete build order by pk.
    - issue: Issue (start) build order by pk.
    - complete: Complete build order by pk. data: {accept_overallocated (optional)}.
    - cancel: Cancel build order by pk.
    - allocate: Auto-allocate stock for build order by pk. data: {interchangeable (optional)}.
    """
    c = get_client()

    match operation:
        case "list":
            params = {"part": part} if part else None
            return await c.get_all("/api/build/", params=params)
        case "get":
            return await c.get(f"/api/build/{pk}/")
        case "create":
            return await c.post("/api/build/", json=data or {})
        case "update":
            return await c.patch(f"/api/build/{pk}/", json=data or {})
        case "delete":
            await c.delete(f"/api/build/{pk}/")
            return {"deleted": pk}
        case "issue":
            return await c.post(f"/api/build/{pk}/issue/", json={})
        case "complete":
            return await c.post(f"/api/build/{pk}/complete/", json=data or {})
        case "cancel":
            return await c.post(f"/api/build/{pk}/cancel/", json={})
        case "allocate":
            return await c.post(f"/api/build/{pk}/auto-allocate/", json=data or {})
        case _:
            raise ValueError(f"Unknown operation: {operation!r}")
