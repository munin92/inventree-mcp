from typing import Any
from ..server import mcp, get_client


@mcp.tool
async def label(
    operation: str,
    pk: int | None = None,
    category: str | None = None,
    data: dict | None = None,
) -> Any:
    """
    Label template listing and printing.

    category must be one of: part, stock, stocklocation, build.

    Operations:
    - list_templates: List label templates for a category.
    - get_template: Get label template by pk and category.
    - print: Print label. pk=template pk, category, data={items: [pk, ...]}.
    - list_part: List part label templates.
    - list_stock: List stock label templates.
    """
    c = get_client()

    match operation:
        case "list_part":
            return await c.get_all("/api/label/part/")
        case "list_stock":
            return await c.get_all("/api/label/stock/")
        case "list_templates":
            return await c.get_all(f"/api/label/{category}/")
        case "get_template":
            return await c.get(f"/api/label/{category}/{pk}/")
        case "print":
            return await c.post(f"/api/label/{category}/{pk}/print/", json=data or {})
        case _:
            raise ValueError(f"Unknown operation: {operation!r}")
