import httpx
from typing import Any
from urllib.parse import urlparse, parse_qs


class InvenTreeClient:
    def __init__(self, base_url: str, token: str):
        self._base_url = base_url.rstrip("/")
        self._headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json",
        }

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    async def get(self, path: str, params: dict | None = None) -> Any:
        async with httpx.AsyncClient() as c:
            resp = await c.get(self._url(path), params=params, headers=self._headers)
            resp.raise_for_status()
            return resp.json()

    async def get_all(self, path: str, params: dict | None = None) -> list:
        p = dict(params or {})
        p["limit"] = 100
        p["offset"] = 0
        results = []
        while True:
            data = await self.get(path, params=p)
            results.extend(data.get("results", []))
            next_url = data.get("next")
            if not next_url:
                break
            # Parse the offset from the next URL to handle non-uniform page sizes
            parsed = urlparse(next_url)
            qs = parse_qs(parsed.query)
            if "offset" in qs:
                p["offset"] = int(qs["offset"][0])
            else:
                p["offset"] += p["limit"]
        return results

    async def post(self, path: str, json: dict | None = None, data: dict | None = None, files: dict | None = None) -> Any:
        async with httpx.AsyncClient() as c:
            if files:
                resp = await c.post(self._url(path), data=data or {}, files=files,
                                    headers={k: v for k, v in self._headers.items() if k != "Content-Type"})
            else:
                resp = await c.post(self._url(path), json=json, headers=self._headers)
            resp.raise_for_status()
            return resp.json() if resp.content else {}

    async def patch(self, path: str, json: dict) -> Any:
        async with httpx.AsyncClient() as c:
            resp = await c.patch(self._url(path), json=json, headers=self._headers)
            resp.raise_for_status()
            return resp.json()

    async def delete(self, path: str) -> None:
        async with httpx.AsyncClient() as c:
            resp = await c.delete(self._url(path), headers=self._headers)
            resp.raise_for_status()
