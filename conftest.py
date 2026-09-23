"""
conftest.py - Cấu hình pytest cho dự án.

File này:
- Tự động thêm thư mục gốc vào sys.path
- Không cần pytest.ini hay setup.py riêng
"""

import sys
from pathlib import Path

# Thêm thư mục gốc dự án vào sys.path để import src.*
ROOT_DIR = Path(__file__).parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
