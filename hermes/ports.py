"""Ports on LightBringer. The bus is 8789. 8787 is Gmail OAuth now."""

from __future__ import annotations

BUS_PORT = 8789
GATEWAY_PORT = 8642
FCC_PORT = 8082
FILE_BUS_PORT = 8650
MCP_GATE_PORT = 8790

# Retired or owned. A starter that binds one of these steals another service.
REFUSED_BUS_PORTS = frozenset({8787, 8788, GATEWAY_PORT, FCC_PORT, FILE_BUS_PORT, MCP_GATE_PORT})

REFUSAL = {
    8787: "8787 is the Gmail OAuth callback",
    8788: "8788 is the Windows Hermes python listener",
    GATEWAY_PORT: "8642 is the Hermes gateway",
    FCC_PORT: "8082 is the FCC proxy",
    FILE_BUS_PORT: "8650 is the file bus",
    MCP_GATE_PORT: "8790 is mcp-gate",
}


def bus_port(requested: int | None = None) -> int:
    port = BUS_PORT if requested is None else int(requested)
    if port in REFUSED_BUS_PORTS:
        raise ValueError(REFUSAL[port])
    if port < 1 or port > 65535:
        raise ValueError(f"port {port} is outside 1-65535")
    return port
