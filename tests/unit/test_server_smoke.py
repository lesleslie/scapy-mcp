"""Server smoke tests — FastMCP wiring, baseline tools, profile gating.

These tests construct the FastMCP app via ``asyncio.run`` because
``apply_tool_profile`` reaches into a running event loop. They do not bind
a transport.
"""
from __future__ import annotations

import asyncio

import pytest
from fastmcp import FastMCP

from scapy_mcp.config.settings import ScapySettings
from scapy_mcp.server import build_runtime
from scapy_mcp.tools.profiles import EXPECTED_BASELINE


def _build(settings: ScapySettings) -> FastMCP:
    """Construct the FastMCP app from a sync test."""
    return asyncio.run(build_runtime(settings=settings).build_mcp_app_async())


def _tool_names(app: FastMCP) -> set[str]:
    """FastMCP 3.x ``list_tools`` is async; bridge from sync tests."""
    return {t.name for t in asyncio.run(app.list_tools())}


@pytest.fixture
def settings() -> ScapySettings:
    return ScapySettings(_env_file=None)


def test_app_is_fastmcp_instance() -> None:
    from scapy_mcp.server import get_app

    assert isinstance(_build(ScapySettings(_env_file=None)), FastMCP)


def test_all_four_baseline_tools_registered(settings: ScapySettings) -> None:
    app = _build(settings)
    registered = _tool_names(app)
    assert EXPECTED_BASELINE.issubset(registered), (
        f"missing baseline tools: {EXPECTED_BASELINE - registered}"
    )


def test_standard_profile_unregisters_transmit_tools() -> None:
    """Spec §6.3: transmit is ``full``-only. The decorators always attach
    transmit_packet / probe_packet; the profile gate must explicitly remove
    them when profile != "full".
    """
    settings = ScapySettings(_env_file=None, tool_profile="standard")
    app = _build(settings)
    tools = _tool_names(app)
    assert "transmit_packet" not in tools
    assert "probe_packet" not in tools


def test_build_runtime_returns_runtime(settings: ScapySettings) -> None:
    runtime = build_runtime(settings=settings)
    assert runtime.settings == settings
