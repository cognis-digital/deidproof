"""DEIDPROOF MCP server — exposes scan() as an MCP tool for Cognis.Studio."""
from __future__ import annotations
from deidproof.core import scan, to_json

def serve() -> int:
    """Start an MCP stdio server. Requires the optional 'mcp' extra:
        pip install "cognis-deidproof[mcp]"
    """
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception:
        print("Install the MCP extra: pip install 'cognis-deidproof[mcp]'")
        return 1
    app = FastMCP("deidproof")

    @app.tool()
    def deidproof_scan(target: str) -> str:
        """Re-identification risk assessment that computes k-anonymity, l-diversity, and HIPAA Safe Harbor compliance on a dataset.. Returns JSON findings."""
        return to_json(scan(target))

    app.run()
    return 0
