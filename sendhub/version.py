import re
from pathlib import Path

try:
    raw = Path(__file__).with_name("VERSION").read_text(encoding="utf-8").strip()
    # Accept: 0.25.10  |  VERSION=0.25.10  |  VERSION="0.25.10"
    m = re.search(r'^\s*(?:VERSION\s*=\s*)?["\']?([0-9]+(?:\.[0-9]+)*)["\']?\s*$', raw)
    if not m:
        raise RuntimeError(f"VERSION file malformed: {raw!r}")
    VERSION = m.group(1)
except Exception:
    VERSION = "0.25.10"
