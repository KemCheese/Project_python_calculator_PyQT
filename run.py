"""
run.py - Script chạy nhanh từ thư mục gốc dự án.

Sử dụng:
    python run.py            # Chạy bình thường
    CALC_DEBUG=1 python run.py   # Chạy với debug log (Linux/Mac)
    set CALC_DEBUG=1 && python run.py  # Windows
"""

import sys
from pathlib import Path

# Thêm thư mục src vào path
ROOT = Path(__file__).parent
SRC = ROOT / "src"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SRC))

from src.main import main

if __name__ == "__main__":
    sys.exit(main())
