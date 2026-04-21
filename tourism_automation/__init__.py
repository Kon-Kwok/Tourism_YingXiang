"""Runtime shim for the src-based tourism_automation package."""

from pathlib import Path


_SRC_PACKAGE_DIR = Path(__file__).resolve().parent.parent / "src" / "tourism_automation"
if _SRC_PACKAGE_DIR.exists():
    __path__.append(str(_SRC_PACKAGE_DIR))
