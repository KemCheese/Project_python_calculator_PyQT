"""
Entry point chính của ứng dụng PyQt6 Calculator.

File này:
1. Khởi tạo QApplication
2. Cấu hình logging
3. Set font và DPI
4. Tạo MainWindow
5. Chạy event loop

Author: PyQt6 Calculator Project
Python: 3.10+
"""

from __future__ import annotations

import logging
import sys
import os
from pathlib import Path

# Thêm thư mục gốc vào sys.path để import các module trong src/
ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt, QLocale
    from PyQt6.QtGui import QFont, QFontDatabase
    PYQT_VERSION = 6
except ImportError:
    from PyQt5.QtWidgets import QApplication  # type: ignore[no-redef]
    from PyQt5.QtCore import Qt, QLocale  # type: ignore[no-redef]
    from PyQt5.QtGui import QFont, QFontDatabase  # type: ignore[no-redef]
    PYQT_VERSION = 5

from src.ui.main_window import MainWindow


def configure_logging(debug: bool = False) -> None:
    """Cấu hình logging cho ứng dụng.

    Args:
        debug: True để bật DEBUG level, False cho WARNING.
    """
    level = logging.DEBUG if debug else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main() -> int:
    """Hàm chính khởi chạy ứng dụng.

    Returns:
        Exit code (0 = thành công).
    """
    # Bật debug mode nếu có biến môi trường CALC_DEBUG=1
    debug_mode = os.environ.get("CALC_DEBUG", "0") == "1"
    configure_logging(debug=debug_mode)

    logger = logging.getLogger(__name__)
    logger.info("Starting PyQt%d Calculator (Python %s)", PYQT_VERSION, sys.version.split()[0])

    # ── Khởi tạo QApplication ────────────────────────────────
    # Phải tạo QApplication trước tất cả widget
    app = QApplication(sys.argv)
    app.setApplicationName("Máy Tính")
    app.setApplicationDisplayName("PyQt Calculator")
    app.setOrganizationName("PyQt Calculator Project")
    app.setApplicationVersion("1.0.0")

    # ── Cấu hình High DPI ────────────────────────────────────
    if PYQT_VERSION == 6:
        # PyQt6: high DPI được bật mặc định
        pass
    else:
        # PyQt5: cần bật thủ công
        if hasattr(Qt, "AA_EnableHighDpiScaling"):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # type: ignore
        if hasattr(Qt, "AA_UseHighDpiPixmaps"):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  # type: ignore

    # ── Set font mặc định ────────────────────────────────────
    # Ưu tiên Segoe UI (Windows), SF Pro (macOS), rồi fallback hệ thống
    preferred_fonts = ["Segoe UI", "SF Pro Display", "Inter", "Helvetica Neue"]
    available_families = QFontDatabase.families() if PYQT_VERSION == 6 else QFontDatabase().families()
    chosen_font = None
    for font_name in preferred_fonts:
        if any(font_name.lower() in f.lower() for f in available_families):
            chosen_font = font_name
            break

    if chosen_font:
        app.setFont(QFont(chosen_font, 10))
        logger.debug("Using font: %s", chosen_font)
    else:
        app.setFont(QFont("sans-serif", 10))

    # ── Tạo và hiển thị MainWindow ───────────────────────────
    window = MainWindow()
    window.show()
    window.raise_()
    window.activateWindow()

    logger.info("Window displayed successfully")

    # ── Chạy event loop ──────────────────────────────────────
    exit_code = app.exec()
    logger.info("Application exited with code %d", exit_code)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
