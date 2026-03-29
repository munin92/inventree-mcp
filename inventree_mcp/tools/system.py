from typing import Any
from ..server import mcp, get_client


@mcp.tool
async def system(
    operation: str,
) -> Any:
    """
    System health, version, settings, users, groups, currencies.

    Operations:
    - version: Get InvenTree server version and API info.
    - health: Get system health status.
    - me: Get current authenticated user info.
    - users: List all users.
    - groups: List all user groups.
    - currencies: List configured currencies.
    - settings_global: Get global InvenTree settings.
    - settings_user: Get current user settings.
    """
    c = get_client()

    match operation:
        case "version":
            return await c.get("/api/")
        case "health":
            data = await c.get("/api/")
            return {"system_health": data.get("system_health"), "worker_running": data.get("worker_running")}
        case "me":
            return await c.get("/api/user/me/")
        case "users":
            return await c.get_all("/api/user/")
        case "groups":
            return await c.get_all("/api/user/group/")
        case "currencies":
            return await c.get_all("/api/currency/exchange/")
        case "settings_global":
            return await c.get_all("/api/settings/global/")
        case "settings_user":
            return await c.get_all("/api/settings/user/")
        case _:
            raise ValueError(f"Unknown operation: {operation!r}")
