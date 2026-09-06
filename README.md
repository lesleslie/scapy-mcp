# scapy-mcp

> **Scaffold status: PyPI name reservation.** This package is a placeholder scaffold to claim
> the `scapy-mcp` name on PyPI. The MCP server is not yet implemented.

MCP server wrapping [Scapy](https://scapy.net/) — interactive packet
manipulation library. Provides access to:

- **Packet crafting** — build L2/L3/L4 packets from Pythonic layers
- **Dissection** — decode captured packet bytes into structured summaries
- **Live capture** — sniff interfaces with optional BPF filters
- **PCAP I/O** — read and write `.pcap` / `.pcapng` files
- **Protocol layers** — TCP, UDP, ICMP, ARP, DNS, TLS, raw

## Reserve the PyPI name

```bash
cd /Users/les/Projects/scapy-mcp
uv build
uv publish  # uses UV_PUBLISH_TOKEN from env
```

The package name `scapy-mcp` is currently free on PyPI (verified 2026-08-31).
Publishing a placeholder 0.1.0 release locks the name.

## Connection to flowscape

The `flowscape` design spec
(`docs/superpowers/specs/2026-08-31-flowscape-design.md`) explicitly lists
`scapy-mcp` as a future integration under **Out of scope / future work**:

> scapy-mcp / unifi-mcp integration — Enrichment plugins for `heuristics.py`
> / `graph.py` — v2+

This scaffold is the name-reservation placeholder for that v2 integration.

## Architecture (planned)

Mirrors the `raindropio-mcp` pattern in this ecosystem:

- `scapy` as the core packet manipulation dependency
- `fastmcp` for the MCP server surface (tools = scapy operations)
- `oneiric` for layered config (`settings/scapy-mcp.yaml`, `local.yaml`,
  env vars) — configures default interface, capture mode (live vs offline),
  optional `SCAPY_MCP_PRIVILEGED_HELPER` for `/dev/bpf*` ACLs
- `mcp-common` for bootstrap, health endpoints
- `pydantic`/`pydantic-settings` for typed config models
- Live capture requires root or a ChmodBPF-style helper (same constraint
  documented for flowscape)

## Status

| Phase | State |
|---|---|
| PyPI name reservation | **pending** (run `uv publish`) |
| Spec / plan | not written |
| Implementation | not started |
| Tests | not started |

## License

BSD-3-Clause.