from typing import Any
from ..server import mcp, get_client


@mcp.tool
async def purchase_order(
    operation: str,
    pk: int | None = None,
    supplier: int | None = None,
    data: dict | None = None,
) -> Any:
    """
    Purchase order lifecycle.

    Operations:
    - list: List purchase orders. Optional filter: supplier (int).
    - get: Get purchase order by pk.
    - create: Create PO. data: {supplier, reference (optional), description (optional)}.
    - update: Update PO by pk. Pass data dict.
    - delete: Delete PO by pk.
    - issue: Issue (place) purchase order by pk.
    - receive: Receive items for PO pk. data: {items: [{pk, quantity, location (optional)}]}.
    - complete: Mark PO as complete by pk.
    - cancel: Cancel PO by pk.
    - line_list: List line items for PO pk.
    - line_add: Add line item. data: {order, part, quantity, purchase_price (optional)}.
    - line_update: Update line item by pk. Pass data dict.
    """
    c = get_client()

    match operation:
        case "list":
            params = {"supplier": supplier} if supplier else None
            return await c.get_all("/api/order/po/", params=params)
        case "get":
            return await c.get(f"/api/order/po/{pk}/")
        case "create":
            return await c.post("/api/order/po/", json=data or {})
        case "update":
            return await c.patch(f"/api/order/po/{pk}/", json=data or {})
        case "delete":
            await c.delete(f"/api/order/po/{pk}/")
            return {"deleted": pk}
        case "issue":
            return await c.post(f"/api/order/po/{pk}/issue/", json={})
        case "receive":
            return await c.post(f"/api/order/po/{pk}/receive/", json=data or {})
        case "complete":
            return await c.post(f"/api/order/po/{pk}/complete/", json={})
        case "cancel":
            return await c.post(f"/api/order/po/{pk}/cancel/", json={})
        case "line_list":
            return await c.get_all("/api/order/po-line/", params={"order": pk})
        case "line_add":
            return await c.post("/api/order/po-line/", json=data or {})
        case "line_update":
            return await c.patch(f"/api/order/po-line/{pk}/", json=data or {})
        case _:
            raise ValueError(f"Unknown operation: {operation!r}")
