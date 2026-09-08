# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-09-08

### Added

- auth: Wire BearerTokenMiddleware into Runtime lifespan
- Call validate_auth_config at startup
- scapy-mcp: Capture start/stop/read with /dev/bpf* probe
- scapy-mcp: Craft + dissect tools with malformed-input typed errors
- scapy-mcp: Deterministic PCAP fixture generator + 6 fixtures
- scapy-mcp: Emission controller (4 controls + probe cap) and LayerSpec union
- scapy-mcp: Feed registry (3 required, 2 optional) and wiring-discipline signals
- scapy-mcp: Initialize git repo, flat layout, packaging test
- scapy-mcp: Pcap read/write with path-containment guard
- scapy-mcp: ScapySettings with all §13.4 keys
- scapy-mcp: Server.py with profile-gated transmit, /readyz, baseline tools
- scapy-mcp: Transmit + probe tools, four-control + probe-target gate
- scapy-mcp: Typed exception hierarchy

### Fixed

- scapy-mcp: Cli hosts build_asgi_app via uvicorn so /readyz route mounts
- scapy-mcp: Env_nested_delimiter for nested AuthConfig env vars
- scapy-mcp: Phase 1 prep — gitignore fixtures, server __main__ guard

### Testing

- scapy-mcp: Per-tool e2e tests; transmit asserts refusal
- scapy-mcp: Phase 0b known-layers gate for http_get fixture

### Internal

- scapy-mcp: README, ratchet coverage to 85, e2e + capture/transmit extras
- scapy-mcp: Satisfy crackerjack gate for flat layout
