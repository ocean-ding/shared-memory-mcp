#!/usr/bin/env python3
"""Minimal protocol smoke test using a fresh temporary memory root."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="shared-memory-mcp-") as memory_root:
        env = os.environ.copy()
        env.update(
            {
                "MDCG_ROOT": memory_root,
                "MDCG_AUX_ROOT": str(Path(memory_root) / "aux"),
                "MDCG_STATE_ROOT": str(Path(memory_root) / "state"),
                "MDCG_DATA_ROOT": str(Path(memory_root) / "data"),
                "MDCG_ACTOR": "smoke-test",
                "MDCG_MCP_SURFACE": "kernel",
                "PYTHONPATH": os.pathsep.join(
                    part for part in (str(REPO_ROOT), env.get("PYTHONPATH", "")) if part
                ),
                "PYTHONUTF8": "1",
            }
        )
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "shared-memory-mcp-smoke-test", "version": "0.1.0"},
            },
        }
        result = subprocess.run(
            [sys.executable, "-X", "utf8", "-m", "md_cg.mcp_server"],
            cwd=REPO_ROOT,
            env=env,
            input=json.dumps(request, ensure_ascii=False) + "\n",
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )

    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        return result.returncode or 1
    first_line = next((line for line in result.stdout.splitlines() if line.strip()), "")
    try:
        response = json.loads(first_line)
    except json.JSONDecodeError:
        print("FAIL: MCP server did not return JSON-RPC initialize response")
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        return 1
    if response.get("id") != 1 or "result" not in response:
        print(f"FAIL: unexpected initialize response: {response}")
        print(result.stderr, file=sys.stderr)
        return 1
    print("PASS: MCP initialize handshake succeeded with an isolated empty memory root")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
