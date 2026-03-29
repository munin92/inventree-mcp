from typing import Any
from ..server import mcp, get_client


@mcp.tool
async def sales_order(
    operation: str,
    pk: int | None = None,
    customer: int | None = None,
    data: dict | None = None,
) -> Any:
    """
    Sales order lifecycle.

    Operations:
    - list: List sales orders. Optional filter: customer (int).
    - get: Get sales order by pk.
    - create: Create SO. data: {customer, reference (optional)}.
    - update: Update SO by pk. Pass data dict.
    - delete: Delete SO by pk.
    - issue: Issue SO by pk.
    - ship: Mark SO as shipped by pk.
    - complete: Complete SO by pk.
    - cancel: Cancel SO by pk.
    - line_list: List line items for SO pk.
    - line_add: Add line item. data: {order, part, quantity, sale_price (optional)}.
    - line_update: Update line item by pk. Pass data dict.
    - shipment_list: List shipments for SO pk.
    - shipment_create: Create shipment for SO pk. data: {reference (optional)}.
    """
    c = get_client()

    match operation:
        case "list":
            params = {"customer": customer} if customer else None
            return await c.get_all("/api/order/so/", params=params)
        case "get":
            return await c.get(f"/api/order/so/{pk}/")
        case "create":
            return await c.post("/api/order/so/", json=data or {})
        case "update":
            return await c.patch(f"/api/order/so/{pk}/", json=data or {})
        case "delete":
            await c.delete(f"/api/order/so/{pk}/")
            return {"deleted": pk}
        case "issue":
            return await c.post(f"/api/order/so/{pk}/issue/", json={})
        case "ship":
            return await c.post(f"/api/order/so/{pk}/ship/", json={})
        case "complete":
            return await c.post(f"/api/order/so/{pk}/complete/", json={})
        case "cancel":
            return await c.post(f"/api/order/so/{pk}/cancel/", json={})
        case "line_list":
            return await c.get_all("/api/order/so-line/", params={"order": pk})
        case "line_add":
            return await c.post("/api/order/so-line/", json=data or {})
        case "line_update":
            return await c.patch(f"/api/order/so-line/{pk}/", json=data or {})
        case "shipment_list":
            return await c.get_all("/api/order/so/shipment/", params={"order": pk})
        case "shipment_create":
            return await c.post("/api/order/so/shipment/", json={**(data or {}), "order": pk})
        case _:
            raise ValueError(f"Unknown operation: {operation!r}")
