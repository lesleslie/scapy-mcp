"""scapy-mcp CLI entry point."""
from __future__ import annotations

from scapy_mcp.config.settings import get_settings
from scapy_mcp.server import _run_async_safely, build_runtime


def main() -> None:
    settings = get_settings()
    runtime = build_runtime(settings=settings)
    mcp_app = runtime.build_mcp_app()
    _run_async_safely(
        mcp_app.run_async(
            transport="streamable-http",
            port=settings.http_port or 3056,
        ),
    )


if __name__ == "__main__":
    main()
