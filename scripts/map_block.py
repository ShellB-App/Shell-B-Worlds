#!/usr/bin/env python3
"""Print a world as the fenced `map` block the Worlds app plays: paste it into a Shell:B chat, or hand it to Atlas.

    python3 -I scripts/map_block.py apollo-sites
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if len(sys.argv) != 2:
    sys.exit(__doc__)
spec = json.loads((ROOT / "worlds" / sys.argv[1] / "world.json").read_text())
block = {"body": spec["body"], **(spec.get("scene") or {}), "title": spec["name"]}
if spec.get("tour"):
    block["tour"] = [{k: s[k] for k in ("title", "text", "lat", "lon", "zoom", "pitch", "bearing", "body", "seconds") if k in s} for s in spec["tour"]]
print("```map\n" + json.dumps(block, ensure_ascii=False, indent=1) + "\n```")
