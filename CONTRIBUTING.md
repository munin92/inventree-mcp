# Contributing

Thanks for taking a look. This is a small project, so the process is short.

## Getting set up

```bash
uv venv
uv pip install --python .venv/bin/python -e .
uv pip install --python .venv/bin/python pytest pytest-asyncio respx
.venv/bin/python -m pytest tests/ -q
```

`smoke_test.py` in the repository root is **not** part of the suite — it talks
to a live InvenTree instance. Run `pytest tests/` rather than `pytest`.

## Branches and commits

- Branch off `develop`; `main` is the release branch.
- Conventional commits (`feat:`, `fix:`, `docs:`, `chore:`) — the changelog is
  generated from them.
- One concern per pull request. A refactor bundled with a feature is two
  reviews wearing one hat.

## What a good change looks like

**Tests describe behaviour, not implementation.** A test named
`test_no_silent_fallback_without_token` still makes sense after the internals
are rewritten; `test_get_client_returns_none` does not.

**Include a control case.** A test asserting that something is *denied* proves
nothing unless a sibling test proves the same call *succeeds* under the right
conditions. Otherwise a typo in the tool name would make the test pass for the
wrong reason.

**Comments explain why, not what.** The code already says what it does. Write
down the reasoning that would otherwise be lost — especially where a simpler
version was rejected for a concrete reason.

## Security-relevant changes

Anything touching authentication, credentials, or which data a caller can see:

- **Fail closed.** If a check cannot be performed, deny — never fall through to
  a shared credential. Silent fallbacks create separations that do not exist
  and that nobody notices until it matters.
- **Make partial configuration a startup error**, not a half-protected server.
- Say in the pull request what an attacker could do if the change is wrong.
  If that is hard to answer, the change needs a second look.

## Adding tools

Tools live in `inventree_mcp/tools/` and register via the `@mcp.tool`
decorator. Follow the existing shape: one module per InvenTree domain, an
`operation` parameter selecting the action, and `get_client()` for API access —
never build a client by hand, or per-caller identity will quietly skip your tool.
