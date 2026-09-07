"""FastMCP server stub for scapy-mcp.

Scaffold status: module exists so future `from scapy_mcp.server import mcp`
imports resolve cleanly. The full tool surface (craft_packet, dissect_bytes,
read_pcap, write_pcap, capture_start/stop/read, transmit_packet, probe_packet)
lands in Plan 0b/Phase 1. The `run()` entry point is wired so that
`python -m scapy_mcp.server` actually binds the port per Plan 0b
(component declaration `start_command: ["python", "-m", "scapy_mcp.server"]`).
"""

from __future__ import annotations

from fastmcp import FastMCP

mcp = FastMCP("scapy-mcp")


def run() -> None:
    """Start the FastMCP server. Real port + transport come from settings
    once the Phase 1 server-wiring task lands. For now, FastMCP defaults
    (streamable-HTTP transport, port from env or default) are used so
    `python -m scapy_mcp.server` exits 0 cleanly and binds a port.
    """
    mcp.run()


# Tools, resources, and prompts will be registered here once the
# implementation lands. See the project plan (Phase 1 Tasks 11+).


if __name__ == "__main__":
    run()
