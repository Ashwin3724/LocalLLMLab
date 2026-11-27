"""Restore the included preview image from text-encoded chunks."""
from pathlib import Path
import base64
ROOT = Path(__file__).resolve().parent
parts = sorted((ROOT / "docs").glob("screenshot.png.part*.b64"))
if not parts:
    raise SystemExit("No encoded preview chunks found")
data = "".join(p.read_text().replace("\n", "") for p in parts)
(ROOT / "docs/screenshot.png").write_bytes(base64.b64decode(data, validate=True))
print("Restored docs/screenshot.png")
