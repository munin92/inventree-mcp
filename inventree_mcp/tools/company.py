from typing import Any
from ..server import mcp, get_client


@mcp.tool
async def company(
    operation: str,
    pk: int | None = None,
    is_supplier: bool | None = None,
    is_manufacturer: bool | None = None,
    is_customer: bool | None = None,
    part: int | None = None,
    data: dict | None = None,
) -> Any:
    """
    Suppliers, manufacturers, customers, contacts, addresses.

    Operations:
    - list: List companies. Filters: is_supplier, is_manufacturer, is_customer (bool).
    - get: Get company by pk.
    - create: Create company. data: {name, is_supplier, is_manufacturer, is_customer, ...}.
    - update: Update company by pk. Pass data dict.
    - delete: Delete company by pk.
    - contacts: List contacts for company pk.
    - contact_create: Create contact. data: {company, name, phone, email}.
    - contact_delete: Delete contact by pk.
    - addresses: List addresses for company pk.
    - address_create: Create address. data: {company, title, line1, postcode, country}.
    - supplier_parts: List supplier parts. Optional filter: part (int).
    - manufacturer_parts: List manufacturer parts. Optional filter: part (int).
    """
    c = get_client()

    match operation:
        case "list":
            params = {}
            if is_supplier is not None:
                params["is_supplier"] = is_supplier
            if is_manufacturer is not None:
                params["is_manufacturer"] = is_manufacturer
            if is_customer is not None:
                params["is_customer"] = is_customer
            return await c.get_all("/api/company/", params=params or None)
        case "get":
            return await c.get(f"/api/company/{pk}/")
        case "create":
            return await c.post("/api/company/", json=data or {})
        case "update":
            return await c.patch(f"/api/company/{pk}/", json=data or {})
        case "delete":
            await c.delete(f"/api/company/{pk}/")
            return {"deleted": pk}
        case "contacts":
            return await c.get_all("/api/company/contact/", params={"company": pk})
        case "contact_create":
            return await c.post("/api/company/contact/", json=data or {})
        case "contact_delete":
            await c.delete(f"/api/company/contact/{pk}/")
            return {"deleted": pk}
        case "addresses":
            return await c.get_all("/api/company/address/", params={"company": pk})
        case "address_create":
            return await c.post("/api/company/address/", json=data or {})
        case "supplier_parts":
            params = {"part": part} if part else None
            return await c.get_all("/api/company/part/", params=params)
        case "manufacturer_parts":
            params = {"part": part} if part else None
            return await c.get_all("/api/company/part/manufacturer/", params=params)
        case _:
            raise ValueError(f"Unknown operation: {operation!r}")
