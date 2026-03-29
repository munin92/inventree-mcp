from typing import Any
from ..server import mcp, get_client


@mcp.tool
async def barcode(
    operation: str,
    barcode_data: str | None = None,
    pk: int | None = None,
    model_type: str | None = None,
    data: dict | None = None,
) -> Any:
    """
    Barcode scan, assign, unassign, lookup.

    Operations:
    - scan: Scan a barcode string. barcode_data required.
    - lookup: Look up what object a barcode points to. barcode_data required.
    - assign: Assign barcode to object. data: {barcode, model_type, pk}.
    - unassign: Remove barcode from object. data: {model_type, pk}.
    """
    c = get_client()

    match operation:
        case "scan":
            return await c.post("/api/barcode/", json={"barcode": barcode_data})
        case "lookup":
            return await c.post("/api/barcode/", json={"barcode": barcode_data})
        case "assign":
            return await c.post("/api/barcode/link/", json=data or {})
        case "unassign":
            return await c.post("/api/barcode/unlink/", json=data or {})
        case _:
            raise ValueError(f"Unknown operation: {operation!r}")
