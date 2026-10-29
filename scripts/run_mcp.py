#!/usr/bin/env python3
"""Start the MCP server with a private memory root outside this repository."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MEMORY_ROOT = Path.home() / ".shared-memory-mcp" / "memory"


def main() -> int:
    memory_root = Path(
        os.environ.get("MDCG_ROOT", str(DEFAULT_MEMORY_ROOT))
    ).expanduser().resolve()
    memory_root.mkdir(parents=True, exist_ok=True)
    runtime_root = memory_root.parent / f".{memory_root.name}-runtime"
    runtime_root.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["MDCG_ROOT"] = str(memory_root)
    env.setdefault("MDCG_AUX_ROOT", str(runtime_root / "aux"))
    env.setdefault("MDCG_STATE_ROOT", str(runtime_root / "state"))
    env.setdefault("MDCG_DATA_ROOT", str(runtime_root / "data"))
    env.setdefault("MDCG_ACTOR", os.environ.get("USER", "shared-memory-user"))
    env.setdefault("MDCG_MCP_SURFACE", "kernel")
    env.setdefault("PYTHONUTF8", "1")
    env["PYTHONPATH"] = os.pathsep.join(
        part for part in (str(REPO_ROOT), env.get("PYTHONPATH", "")) if part
    )

    return subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "md_cg.mcp_server"],
        cwd=REPO_ROOT,
        env=env,
        check=False,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
