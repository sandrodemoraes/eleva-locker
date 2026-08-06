#!/usr/bin/env python3
"""Atalho legado — use tools/atualizar.py"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
raise SystemExit(
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "atualizar.py"), *sys.argv[1:]],
        cwd=ROOT,
    ).returncode
)
