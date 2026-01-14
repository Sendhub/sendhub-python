"""
Module to provide the package version from the VERSION file.
"""

import re
from pathlib import Path
from typing import Optional


def get_version() -> str:
    """
    Reads the VERSION file and extracts the version string.
    Returns:
        str: The version string (e.g., '0.26.01').
    Raises:
        RuntimeError: If the VERSION file is malformed.
    """
    try:
        raw: str = (
            Path(__file__).with_name("VERSION").read_text(encoding="utf-8").strip()
        )
        # Accept: 0.26.01  |  VERSION=0.26.01  |  VERSION="0.26.01"
        m: Optional[re.Match[str]] = re.search(
            r'^\s*(?:VERSION\s*=\s*)?["\']?([0-9]+(?:\.[0-9]+)*)["\']?\s*$', raw
        )
        if not m:
            raise RuntimeError(f"VERSION file malformed: {raw!r}")
        return m.group(1)
    except Exception:
        return "0.26.01"


VERSION: str = get_version()
