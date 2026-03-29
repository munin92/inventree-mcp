from typing import Any
from ..server import mcp, get_client


@mcp.tool
async def report(
    operation: str,
    pk: int | None = None,
    category: str | None = None,
    data: dict | None = None,
) -> Any:
    """
    Report template listing and generation.

    category must be one of: bom, build, po, so, ro, slr, test.

    Operations:
    - list_templates: List report templates for a category.
    - get_template: Get report template by pk and category.
    - generate: Generate report. pk=template pk, category, data={items: [pk, ...]}.
    """
    c = get_client()

    match operation:
        case "list_templates":
            return await c.get_all(f"/api/report/{category}/")
        case "get_template":
            return await c.get(f"/api/report/{category}/{pk}/")
        case "generate":
            return await c.post(f"/api/report/{category}/{pk}/print/", json=data or {})
        case _:
            raise ValueError(f"Unknown operation: {operation!r}")
