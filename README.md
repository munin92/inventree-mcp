# inventree-mcp

MCP server for [InvenTree](https://inventree.org) — exposes InvenTree inventory management as tools for LLMs (Claude, GPT-4, etc.) via the [Model Context Protocol](https://modelcontextprotocol.io).

## Installation

> **Note:** the PyPI name `inventree-mcp` belongs to the upstream InvenTree
> project's own MCP server, not to this one. Install from the container image
> or from source.

```bash
docker run -p 8001:8001 \
  -e INVENTREE_URL=http://your-inventree:8000 \
  -e INVENTREE_TOKEN=your-token \
  ghcr.io/munin92/inventree-mcp:latest
```

From source:

```bash
git clone https://github.com/munin92/inventree-mcp
cd inventree-mcp && pip install -e .
```

## Configuration

Set these environment variables (or create a `.env` file):

| Variable | Description | Default |
|----------|-------------|---------|
| `INVENTREE_URL` | InvenTree base URL | `http://localhost:8000` |
| `INVENTREE_TOKEN` | Shared API token | *(required unless a caller identity is used, see below)* |
| `MCP_HOST` | Listen host | `0.0.0.0` |
| `MCP_PORT` | Listen port | `8001` |
| `OIDC_JWKS_URI` | JWKS endpoint of the token issuer | *(optional)* |
| `OIDC_ISSUER` | Expected `iss` claim | *(optional)* |
| `OIDC_AUDIENCE` | Expected `aud` claim | *(optional)* |
| `OIDC_USERNAME_CLAIM` | Claim holding the InvenTree username | `preferred_username` |
| `MCP_BASE_URL` | Public URL of this server | *(required with OIDC)* |
| `INVENTREE_REMOTE_USER_HEADER` | Header InvenTree reads the user from | `X-Auth-Request-REMOTE_USER` |

Generate an API token in InvenTree under *Settings → User → API Tokens*.

## Who is calling?

Three ways, in this order of precedence:

1. **`X-Inventree-Token` header** — the caller sends their own InvenTree token
   with the request. Most specific, so it wins.
2. **A verified JWT** — with the `OIDC_*` settings present, the server checks
   the token itself and maps its identity claim onto an InvenTree user (see
   below). No token is stored anywhere.
3. **`INVENTREE_TOKEN`** from the environment — every caller sees the same data.

With identity checking enabled and no caller identity at all, the call **fails**
rather than quietly using the shared token.

## Running

```bash
# From environment variables or .env file
inventree-mcp
```

The server listens on `http://0.0.0.0:8001/mcp` by default.

## Available Tools

Each tool takes an `operation` parameter to select the action:

| Tool | Operations |
|------|-----------|
| `part` | `list`, `get`, `create`, `update`, `delete`, `category_list`, `category_get`, `category_create`, `category_update`, `category_delete`, `bom_list`, `bom_add`, `bom_remove`, `bom_validate`, `suppliers`, `parameters`, `parameter_set`, `parameter_delete`, `stock_summary`, `search`, `attachments` |
| `stock` | `list`, `get`, `create`, `update`, `delete`, `transfer`, `count`, `add`, `remove`, `merge`, `location_list`, `location_get`, `location_create`, `location_update`, `location_delete`, `history` |
| `build_order` | `list`, `get`, `create`, `update`, `delete`, `complete`, `outputs` |
| `purchase_order` | `list`, `get`, `create`, `update`, `delete`, `issue`, `receive`, `complete` |
| `sales_order` | `list`, `get`, `create`, `update`, `delete`, `issue`, `complete` |
| `return_order` | `list`, `get`, `create`, `update`, `delete` |
| `company` | `list`, `get`, `create`, `update`, `delete`, `contacts`, `addresses` |
| `barcode` | `scan`, `link`, `unlink` |
| `label` | `list`, `print` |
| `attachment` | `list`, `upload`, `delete` |
| `report` | `list`, `print` |
| `system` | `info`, `version`, `health` |

## Kubernetes (Agent Gateway)

Deploy as a Kubernetes service and federate via [Agent Gateway](https://agentgateway.dev):

```yaml
# Service must use appProtocol: agentgateway.dev/mcp
apiVersion: v1
kind: Service
metadata:
  name: inventree-mcp
spec:
  ports:
    - port: 8001
      appProtocol: agentgateway.dev/mcp
```

See [Agent Gateway MCP Federation](https://agentgateway.dev/docs/kubernetes/latest/tutorials/mcp-federation/) for full setup.

## License

MIT

## Caller identity (optional)

By default the server talks to InvenTree with **one shared token** — every
caller sees the same data.

Alternatively it can verify incoming JWTs itself and act **as the calling
person** against InvenTree. Each person then sees their own data, and no token
has to be stored anywhere — neither on the server nor in a client config.

```env
OIDC_JWKS_URI=https://keycloak.example/realms/master/protocol/openid-connect/certs
OIDC_ISSUER=https://keycloak.example/realms/master
OIDC_AUDIENCE=https://your-gateway.example/mcp
MCP_BASE_URL=https://inventree-mcp.example
```

On the InvenTree side, enable `INVENTREE_REMOTE_LOGIN` and point
`INVENTREE_REMOTE_LOGIN_HEADER` at the same header.

The default `X-Auth-Request-REMOTE_USER` is deliberately the header that
oauth2-proxy already emits for browser SSO, so this server slots into an
existing setup instead of introducing a second mechanism.

### Who may set the header?

On the browser path, nobody but the proxy: Traefik's `authResponseHeaders`
**replace** whatever a client sends, so it cannot be injected there.

This server, however, talks to InvenTree directly, bypassing the proxy — here
**it** is the trusted component. Anyone who can also reach InvenTree directly
can set the header too. Whether that matters depends on who can run processes
in your network; a shared API token would be just as readable in the same spot.

### Two deliberate design choices

**No silent fallback.** If identity checking is enabled and the caller brings no
usable identity, the call fails. Falling back to the shared token would create a
data separation that does not exist and that nobody would notice.

**The user header replaces the token, it does not accompany it.** With both
present, InvenTree would use the token and the separation would be void.

The three OIDC settings only take effect together — two out of three leave the
server in its previous mode rather than running it half-protected.
