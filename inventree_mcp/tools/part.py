from typing import Any
from ..server import mcp, get_client


@mcp.tool
async def part(
    operation: str,
    pk: int | None = None,
    category: int | None = None,
    search: str | None = None,
    data: dict | None = None,
) -> Any:
    """
    Part & category management.

    Operations:
    - list: List parts. Optional filters: category (int), search (str).
    - get: Get part by pk.
    - create: Create part. Pass data dict with fields (name, category, description, etc.).
    - update: Update part. Requires pk and data dict.
    - delete: Delete part by pk.
    - category_list: List all part categories.
    - category_get: Get category by pk.
    - category_create: Create category. Pass data dict with name, parent (optional).
    - category_update: Update category by pk. Pass data dict.
    - category_delete: Delete category by pk.
    - bom_list: List BOM items for part. Requires pk.
    - bom_add: Add BOM item. Pass data dict with part, sub_part, quantity.
    - bom_remove: Remove BOM item by pk.
    - bom_validate: Mark BOM as validated for part. Requires pk.
    - suppliers: List supplier parts for a part. Requires pk.
    - parameters: List parameters for a part. Requires pk.
    - parameter_set: Set/create parameter. Pass data dict with part, template, data.
    - parameter_delete: Delete parameter by pk.
    - stock_summary: Get stock availability summary for part. Requires pk.
    - search: Full-text search parts. Requires search string.
    - attachments: List file attachments for a part. Requires pk.
    """
    c = get_client()
    params: dict = {}

    match operation:
        case "list":
            if category is not None:
                params["category"] = category
            if search:
                params["search"] = search
            return await c.get_all("/api/part/", params=params or None)
        case "get":
            return await c.get(f"/api/part/{pk}/")
        case "create":
            return await c.post("/api/part/", json=data or {})
        case "update":
            return await c.patch(f"/api/part/{pk}/", json=data or {})
        case "delete":
            await c.delete(f"/api/part/{pk}/")
            return {"deleted": pk}
        case "category_list":
            return await c.get_all("/api/part/category/")
        case "category_get":
            return await c.get(f"/api/part/category/{pk}/")
        case "category_create":
            return await c.post("/api/part/category/", json=data or {})
        case "category_update":
            return await c.patch(f"/api/part/category/{pk}/", json=data or {})
        case "category_delete":
            await c.delete(f"/api/part/category/{pk}/")
            return {"deleted": pk}
        case "bom_list":
            return await c.get_all("/api/bom/", params={"part": pk})
        case "bom_add":
            return await c.post("/api/bom/", json=data or {})
        case "bom_remove":
            await c.delete(f"/api/bom/{pk}/")
            return {"deleted": pk}
        case "bom_validate":
            return await c.post(f"/api/part/{pk}/bom-validate/", json={})
        case "suppliers":
            return await c.get_all("/api/company/part/", params={"part": pk})
        case "parameters":
            return await c.get_all("/api/part/parameter/", params={"part": pk})
        case "parameter_set":
            return await c.post("/api/part/parameter/", json=data or {})
        case "parameter_delete":
            await c.delete(f"/api/part/parameter/{pk}/")
            return {"deleted": pk}
        case "stock_summary":
            return await c.get(f"/api/part/{pk}/")
        case "search":
            return await c.get_all("/api/part/", params={"search": search})
        case "attachments":
            return await c.get_all("/api/attachment/", params={"model_type": "part", "model_id": pk})
        case _:
            raise ValueError(f"Unknown operation: {operation!r}")
