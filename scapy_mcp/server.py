"""FastMCP server — scapy-mcp entry point.

The ``Runtime`` class wraps a ``ScapySettings`` instance and lazily
constructs the FastMCP app on first access. The ``/readyz`` route returns
503 when any required feed reports unhealthy; capture/transmit are
optional, so their absence does NOT trigger 503.

Transmit tools are gated to the ``full`` profile (spec §6.3) — the
``standard`` and ``minimal`` profiles drop the transmit group via
``apply_tool_profile``.
"""
from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from fastapi import FastAPI, Response
from fastmcp import FastMCP
from mcp_common.baseline_tools import register_baseline_tools, seed_liveness_context
from mcp_common.health import register_http_health_route
from mcp_common.tools.dispatch import ToolProfile, _apply_tool_profile_async

from scapy_mcp import __version__
from scapy_mcp.config.settings import ScapySettings, get_settings
from scapy_mcp.feeds import as_components, required_feeds_healthy
from scapy_mcp.tools.profiles import (
    PROFILE_REGISTRATIONS,
    SCAPY_MANDATORY_GROUPS,
    TRANSMIT_GROUPS,
    ServerBundle,
    register_all_tool_groups,
)

APP_NAME = "scapy-mcp"


def _run_async_safely(coro: Any) -> Any:
    """Bridge from sync (CLI / tests) into the async tool surface."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(asyncio.run, coro).result()


def build_runtime(*, settings: ScapySettings | None = None) -> "Runtime":
    s = settings or get_settings()
    return Runtime(settings=s)


class Runtime:
    def __init__(self, *, settings: ScapySettings) -> None:
        self.settings = settings
        self.asgi_app: FastAPI | None = None
        self._mcp_app: FastMCP | None = None

    def build_mcp_app(self) -> FastMCP:
        return asyncio.run(self.build_mcp_app_async())

    async def build_mcp_app_async(self) -> FastMCP:
        if self._mcp_app is not None:
            return self._mcp_app
        bundle = ServerBundle(settings=self.settings)
        app = FastMCP(name=APP_NAME, version=__version__)

        # Baseline tools + liveness seed must precede domain registration so
        # the four ``EXPECTED_BASELINE`` names exist even if domain setup
        # raises later. Mirrors mcp-common's wiring discipline.
        seed_liveness_context(service_name=APP_NAME, version=__version__)
        register_baseline_tools(app)
        register_http_health_route(
            app,
            service_name=APP_NAME,
            version=__version__,
            extra_components=as_components(),
        )

        registration_map = register_all_tool_groups(app, bundle)
        # The dispatch will RE-register per-profile groups below, so undo the
        # unconditional attachment we just did — otherwise ``standard`` would
        # keep ``transmit_packet`` because the dispatch only ADDS groups, it
        # does not remove tools that fall outside the active profile.
        for tool_name in (
            "craft_packet",
            "dissect_bytes",
            "read_pcap",
            "write_pcap",
            "capture_start",
            "capture_stop",
            "capture_read",
            "transmit_packet",
            "probe_packet",
            "health",
        ):
            local = getattr(app, "_local_provider", None)
            if local is not None and hasattr(local, "remove_tool"):
                try:
                    local.remove_tool(tool_name)
                except (KeyError, ValueError):
                    pass

        profile_name = self.settings.tool_profile
        await _apply_tool_profile_async(
            app,
            profile=ToolProfile(profile_name),
            profile_env_var="SCAPY_MCP_TOOL_PROFILE",
            registrations=PROFILE_REGISTRATIONS,
            registration_map=registration_map,
            register_all_fn=lambda srv: register_all_tool_groups(srv, bundle),
            mandatory_groups=SCAPY_MANDATORY_GROUPS,
            essential_tool_names=frozenset(
                {
                    "discover_tools",
                    "get_liveness",
                    "get_readiness",
                    "health_check_all",
                },
            ),
            discovery_fn=None,
        )

        self._mcp_app = app
        return app

    def build_asgi_app(self) -> FastAPI:
        if self.asgi_app is not None:
            return self.asgi_app
        mcp_app = self.build_mcp_app()
        asgi = mcp_app.http_app()  # type: ignore[no-any-return]

        async def _readyz(_request: object) -> Response:
            if not required_feeds_healthy():
                return Response(
                    content='{"status":"degraded","reason":"required feed not healthy"}',
                    status_code=503,
                    media_type="application/json",
                )
            return Response(
                content='{"status":"ok"}',
                status_code=200,
                media_type="application/json",
            )

        asgi.add_route("/readyz", _readyz, methods=["GET"])  # type: ignore[arg-type]

        self.asgi_app = asgi
        return asgi


_default_runtime: Runtime | None = None


def _get_runtime() -> Runtime:
    global _default_runtime
    if _default_runtime is None:
        _default_runtime = build_runtime()
    return _default_runtime


def get_app() -> FastMCP:
    """Lazy accessor — mirrors archive-org-mcp's pattern."""
    return _get_runtime().build_mcp_app()
