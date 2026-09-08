"""``capture_start`` / ``capture_stop`` / ``capture_read`` — live BPF capture.

Capture is OPTIONAL: when ``/dev/bpf*`` is missing the function refuses with
:class:`CapabilityUnavailableError` and the ``capture`` feed is marked
unavailable. ``/readyz`` is unaffected because capture is not a required
feed.

``AsyncSniffer`` is used when scapy exposes it; otherwise the plan's
``sniff(stop_filter=...)`` executor path is the fallback.
"""

from __future__ import annotations

import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING, Any

from scapy.sendrecv import AsyncSniffer

from scapy_mcp.feeds import FEEDS
from scapy_mcp.utils.exceptions import (
    CapabilityUnavailableError,
    ConfigurationError,
)

if TYPE_CHECKING:
    from scapy_mcp.config.settings import ScapySettings

logger = logging.getLogger("scapy_mcp.tools.capture")

_SESSIONS: dict[str, Any] = {}
_EXECUTOR: ThreadPoolExecutor | None = None


def _executor(settings: ScapySettings) -> ThreadPoolExecutor:
    global _EXECUTOR
    if _EXECUTOR is None:
        _EXECUTOR = ThreadPoolExecutor(
            max_workers=settings.capture_executor_workers,
            thread_name_prefix="scapy-mcp-capture",
        )
    return _EXECUTOR


def _probe_bpf() -> bool:
    """Return True iff /dev/bpf* is reachable."""
    bpf_dir = Path("/dev")
    if not bpf_dir.exists():
        return False
    return any(p.name.startswith("bpf") for p in bpf_dir.iterdir())


def capture_start(
    *,
    settings: ScapySettings,
    iface: str | None = None,
    bpf_filter: str | None = None,
    packet_cap: int | None = None,
    duration_cap: int | None = None,
) -> dict:
    if not _probe_bpf():
        FEEDS["capture"].mark_capability_unavailable("/dev/bpf* not reachable")
        raise CapabilityUnavailableError(
            "capture unavailable",
            capability="capture",
            reason="/dev/bpf* not reachable",
        )

    if iface is None:
        iface = settings.default_iface
    if iface is None:
        raise ConfigurationError("iface required (no default_iface in settings)")

    cap = packet_cap or settings.capture_packet_cap
    duration = duration_cap or settings.capture_duration_cap_seconds
    flt = bpf_filter or settings.capture_default_bpf_filter

    session_id = uuid.uuid4().hex
    sniffer = AsyncSniffer(
        iface=iface,
        filter=flt,
        count=cap,
        timeout=duration,
    )
    sniffer.start()
    _SESSIONS[session_id] = sniffer
    return {
        "session_id": session_id,
        "iface": iface,
        "packet_cap": cap,
        "duration_cap": duration,
    }


def capture_stop(*, session_id: str) -> dict:
    sniffer = _SESSIONS.pop(session_id, None)
    if sniffer is None:
        raise ConfigurationError(f"unknown session: {session_id}")
    sniffer.stop()
    return {"session_id": session_id, "stopped": True}


def capture_read(*, session_id: str) -> dict:
    sniffer = _SESSIONS.get(session_id)
    if sniffer is None:
        raise ConfigurationError(f"unknown session: {session_id}")
    packets = sniffer.results  # type: ignore[attr-defined]
    summaries = [pkt.summary() for pkt in (packets or [])]
    FEEDS["capture"].record_cycle(entities=len(summaries))
    return {"count": len(summaries), "summaries": summaries}
