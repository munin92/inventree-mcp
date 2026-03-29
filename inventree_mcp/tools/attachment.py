from typing import Any
from ..server import mcp, get_client


@mcp.tool
async def attachment(
    operation: str,
    pk: int | None = None,
    model_type: str | None = None,
    model_id: int | None = None,
    data: dict | None = None,
    file_path: str | None = None,
) -> Any:
    """
    File attachments on any object (upload, list, delete).

    model_type: part, stock, build, purchaseorder, salesorder, etc.

    Operations:
    - list: List attachments for a model. model_type and model_id required.
    - get: Get attachment metadata by pk.
    - upload: Upload file attachment. model_type, model_id, file_path required.
    - delete: Delete attachment by pk.
    - download_url: Get download URL for attachment pk.
    """
    c = get_client()

    match operation:
        case "list":
            return await c.get_all("/api/attachment/", params={"model_type": model_type, "model_id": model_id})
        case "get":
            return await c.get(f"/api/attachment/{pk}/")
        case "upload":
            with open(file_path, "rb") as f:
                fname = file_path.split("/")[-1]
                return await c.post(
                    "/api/attachment/",
                    data={"model_type": model_type, "model_id": str(model_id)},
                    files={"attachment": (fname, f)},
                )
        case "delete":
            await c.delete(f"/api/attachment/{pk}/")
            return {"deleted": pk}
        case "download_url":
            meta = await c.get(f"/api/attachment/{pk}/")
            return {"url": meta.get("attachment")}
        case _:
            raise ValueError(f"Unknown operation: {operation!r}")
