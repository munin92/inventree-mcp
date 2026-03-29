from typing import Any
from ..server import mcp, get_client


@mcp.tool
async def stock(
    operation: str,
    pk: int | None = None,
    part: int | None = None,
    location: int | None = None,
    data: dict | None = None,
) -> Any:
    """
    Stock item & location management.

    Operations:
    - list: List stock items. Optional filters: part (int), location (int).
    - get: Get stock item by pk.
    - create: Create stock item. data: {part, location, quantity}.
    - update: Update stock item by pk. Pass data dict.
    - delete: Delete stock item by pk.
    - transfer: Transfer stock items. data: {items: [{pk, quantity}], location}.
    - count: Perform stocktake on item pk. data: {quantity, notes (optional)}.
    - add: Add stock to item pk. data: {quantity, notes (optional)}.
    - remove: Remove stock from item pk. data: {quantity, notes (optional)}.
    - merge: Merge stock items. data: {items: [pk, ...], location}.
    - location_list: List all stock locations.
    - location_get: Get stock location by pk.
    - location_create: Create location. data: {name, parent (optional)}.
    - location_update: Update location by pk. Pass data dict.
    - location_delete: Delete location by pk.
    - history: Get tracking history for stock item pk.
    """
    c = get_client()

    match operation:
        case "list":
            params = {}
            if part:
                params["part"] = part
            if location:
                params["location"] = location
            return await c.get_all("/api/stock/", params=params or None)
        case "get":
            return await c.get(f"/api/stock/{pk}/")
        case "create":
            return await c.post("/api/stock/", json=data or {})
        case "update":
            return await c.patch(f"/api/stock/{pk}/", json=data or {})
        case "delete":
            await c.delete(f"/api/stock/{pk}/")
            return {"deleted": pk}
        case "transfer":
            return await c.post("/api/stock/transfer/", json=data or {})
        case "count":
            return await c.post(f"/api/stock/{pk}/count/", json=data or {})
        case "add":
            return await c.post("/api/stock/add/", json={**(data or {}), "items": [{"pk": pk}]})
        case "remove":
            return await c.post("/api/stock/remove/", json={**(data or {}), "items": [{"pk": pk}]})
        case "merge":
            return await c.post("/api/stock/merge/", json=data or {})
        case "location_list":
            return await c.get_all("/api/stock/location/")
        case "location_get":
            return await c.get(f"/api/stock/location/{pk}/")
        case "location_create":
            return await c.post("/api/stock/location/", json=data or {})
        case "location_update":
            return await c.patch(f"/api/stock/location/{pk}/", json=data or {})
        case "location_delete":
            await c.delete(f"/api/stock/location/{pk}/")
            return {"deleted": pk}
        case "history":
            return await c.get_all("/api/stock/tracking/", params={"item": pk})
        case _:
            raise ValueError(f"Unknown operation: {operation!r}")
