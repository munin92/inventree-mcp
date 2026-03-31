# inventree-mcp

MCP server for [InvenTree](https://inventree.org) — exposes InvenTree inventory management as tools for LLMs (Claude, GPT-4, etc.) via the [Model Context Protocol](https://modelcontextprotocol.io).

## Installation

```bash
pip install inventree-mcp
```

## Configuration

Set these environment variables (or create a `.env` file):

| Variable | Description | Default |
|----------|-------------|---------|
| `INVENTREE_URL` | InvenTree base URL | `http://localhost:8000` |
| `INVENTREE_TOKEN` | API token | *(required)* |
| `MCP_HOST` | Listen host | `0.0.0.0` |
| `MCP_PORT` | Listen port | `8001` |
| `MCP_BEARER_TOKEN` | Bearer token for MCP auth | *(optional)* |

Generate an API token in InvenTree under *Settings → User → API Tokens*.

## Running

```bash
# From environment variables or .env file
inventree-mcp
```

The server listens on `http://0.0.0.0:8001/mcp` by default.

## Docker

```bash
docker run -p 8001:8001 \
  -e INVENTREE_URL=http://your-inventree:8000 \
  -e INVENTREE_TOKEN=your-token \
  ghcr.io/munin92/inventree-mcp:latest
```

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
