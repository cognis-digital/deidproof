"""DEIDPROOF MCP server — exposes deidproof_scan() as an MCP tool for Cognis.Studio."""
from __future__ import annotations

import json

from deidproof.core import analyze_csv


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
        """Re-identification risk assessment that computes k-anonymity, l-diversity,
        and HIPAA Safe Harbor compliance on a dataset. Returns JSON findings."""
        try:
            report = analyze_csv(target)
        except (FileNotFoundError, IsADirectoryError, PermissionError, UnicodeDecodeError, ValueError) as exc:
            return json.dumps({"error": str(exc)})
        return json.dumps(report.to_dict(), indent=2)

    app.run()
    return 0
