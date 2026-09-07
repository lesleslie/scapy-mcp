# scapy-mcp

MCP server that wraps [scapy](https://scapy.net) for packet crafting, dissection,
pcap staging, and live capture. Tools operate on a worker that holds a
`scapy_mcp.config.settings.ScapySettings` instance and respects a four-stage
transmit policy before any frame leaves the host.

## Tools

| Group    | Tool             | Purpose |
|----------|------------------|---------|
| craft    | `craft_packet`   | Build a `Packet` from a `LayerSpec` discriminated union. |
| dissect  | `dissect_bytes`  | Parse raw bytes into layers + summary text. |
| pcap     | `read_pcap`      | Read a pcap from `pcap_write_dir` with offset/limit. |
| pcap     | `write_pcap`     | Stage a pcap into `pcap_write_dir` (paths outside the dir refused). |
| capture  | `capture_start`  | Start a BPF-filtered capture (optional feed). |
| capture  | `capture_stop`   | Stop the in-progress capture. |
| capture  | `capture_read`   | Read a range of captured frames. |
| transmit | `transmit_packet`| Send a single packet after every transmit control passes. |
| transmit | `probe_packet`   | One-shot emit at a small BPF, used to confirm the surface works. |

## Four transmit controls

Every `transmit_packet` call is checked against:

1. **Master kill-switch** (`transmit_enabled: bool`, default `false`). The default
   refuses every frame — you must set `SCAPY_MCP_TRANSMIT_ENABLED=true` to
   permit emission at all.
2. **L3 CIDR allow-list** (`transmit_allow_l3_cidrs: list[str]`). Set to
   `["0.0.0.0/0"]` for unrestricted L3; production deployments pin the
   specific CIDRs the worker is allowed to reach.
3. **L2 destination allow-flag** (`transmit_allow_l2: bool`, default `false`).
   Pure ARP / ND / RAW frames require this flag; L3 packets do not.
4. **Broadcast opt-in** (`transmit_allow_broadcast: bool`, default `false`).
   Even after the L2/L3 allow-list, broadcasts refuse unless this is `true`.

A fifth control caps probe-target count: `transmit_max_probe_targets: int`
(default `16`).

A refusal emits an `EmissionRefusedError` with the failing `control` name and a
human-readable reason. The wrapper logs a `scapy-write-would-refuse` /
`scapy-transmit-refused` warning so the refusal is visible without polluting
the caller's error stream.

## BPF probe (`capture`)

Capture is OPTIONAL. When `/dev/bpf*` is missing the function refuses with
`CapabilityUnavailableError` and the `capture` feed is marked unavailable.
`/readyz` stays 200 because capture is not a required feed.

## Deterministic fixtures

Tests do **not** open raw sockets. All packet construction is exercised
against in-memory fixtures under `tests/fixtures/`. Each fixture includes a
hand-crafted `bytes()` body that round-trips through `craft_packet` →
`rdpcap`/`wrpcap` → `dissect_bytes`. No real network frames in the suite.

Regenerate via:

```bash
python -m scripts.gen_pcap_fixtures
```

## Default = closed-by-default transmit

The shipped defaults cannot emit a frame:

```
transmit_enabled = false
transmit_allow_l3_cidrs = []
transmit_allow_l2 = false
transmit_allow_broadcast = false
```

A worker installs only what its operator explicitly approves. See
`scapy_mcp/config/settings.py` for the full settings surface.

## License

BSD-3-Clause.
