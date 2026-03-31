from typing import Any
from ..server import mcp, get_client


@mcp.tool
async def return_order(
    operation: str,
    pk: int | None = None,
    customer: int | None = None,
    data: dict | None = None,
) -> Any:
    """
    Return order management.

    Operations:
    - list: List return orders. Optional filter: customer (int).
    - get: Get return order by pk.
    - create: Create RO. data: {customer, description (optional)}.
    - update: Update RO by pk. Pass data dict.
    - delete: Delete RO by pk.
    - issue: Issue RO by pk.
    - complete: Complete RO by pk.
    - cancel: Cancel RO by pk.
    """
    c = get_client()

    match operation:
        case "list":
            params = {"customer": customer} if customer else None
            return await c.get_all("/api/order/ro/", params=params)
        case "get":
            return await c.get(f"/api/order/ro/{pk}/")
        case "create":
            return await c.post("/api/order/ro/", json=data or {})
        case "update":
            return await c.patch(f"/api/order/ro/{pk}/", json=data or {})
        case "delete":
            await c.delete(f"/api/order/ro/{pk}/")
            return {"deleted": pk}
        case "issue":
            return await c.post(f"/api/order/ro/{pk}/issue/", json={})
        case "complete":
            return await c.post(f"/api/order/ro/{pk}/complete/", json={})
        case "cancel":
            return await c.post(f"/api/order/ro/{pk}/cancel/", json={})
        case _:
            raise ValueError(f"Unknown operation: {operation!r}")
