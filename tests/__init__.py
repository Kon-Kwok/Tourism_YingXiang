from pathlib import Path
import sys


SRC_DIR = Path(__file__).resolve().parent.parent / "src"
src_path = str(SRC_DIR)
if src_path not in sys.path:
    sys.path.insert(0, src_path)
