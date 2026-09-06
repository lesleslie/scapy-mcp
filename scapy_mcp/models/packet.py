"""PacketSpec — an ordered stack of layer specs."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from scapy_mcp.models.layers import LayerSpec


class PacketSpec(BaseModel):
    """Packet built bottom-up: layers[0] is the wire-most, layers[-1] is payload."""

    model_config = ConfigDict(extra="forbid")
    layers: list[LayerSpec]
