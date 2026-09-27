"""
Main Window - Cửa sổ chính của ứng dụng máy tính.

Đây là View trong mô hình MVC:
- View (main_window.py): Hiển thị UI, bắt sự kiện người dùng
- Controller: Logic điều hướng (trong class này, phần _handle_* methods)
- Model (calculator_engine.py, history_manager.py): Logic nghiệp vụ

Kiến trúc:
- MainWindow chứa CalculatorEngine và HistoryManager
- Người dùng tương tác qua nút hoặc bàn phím
- Input được validate bởi InputValidator
- Biểu thức hợp lệ được gửi đến CalculatorEngine
- Kết quả cập nhật vào display labels
- Lịch sử được lưu vào HistoryManager và hiển thị trong HistoryPanel

Author: PyQt6 Calculator Project
Python: 3.10+
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Optional

try:
    from PyQt6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QGridLayout, QLabel, QPushButton, QFrame,
        QSizePolicy, QApplication, QSplitter, QLineEdit,
    )
    from PyQt6.QtCore import (
        Qt, QSize, pyqtSlot, QTimer, QPropertyAnimation,
        QEasingCurve, QRect,
    )
    from PyQt6.QtGui import (
        QFont, QIcon, QKeyEvent, QPixmap, QColor,
        QFontDatabase, QClipboard, QPainter, QBrush,
    )
    PYQT_VERSION = 6
    AlignRight = Qt.AlignmentFlag.AlignRight
    AlignLeft = Qt.AlignmentFlag.AlignLeft
    AlignVCenter = Qt.AlignmentFlag.AlignVCenter
    AlignCenter = Qt.AlignmentFlag.AlignCenter
except ImportError:
    from PyQt5.QtWidgets import (  # type: ignore[no-redef]
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QGridLayout, QLabel, QPushButton, QFrame,
        QSizePolicy, QApplication, QSplitter, QLineEdit,
    )
    from PyQt5.QtCore import (  # type: ignore[no-redef]
        Qt, QSize, pyqtSlot, QTimer, QPropertyAnimation,
        QEasingCurve, QRect,
    )
    from PyQt5.QtGui import (  # type: ignore[no-redef]
        QFont, QIcon, QKeyEvent, QPixmap, QColor,
        QFontDatabase, QClipboard, QPainter, QBrush,
    )
    PYQT_VERSION = 5
    AlignRight = Qt.AlignRight  # type: ignore
    AlignLeft = Qt.AlignLeft  # type: ignore
    AlignVCenter = Qt.AlignVCenter  # type: ignore
    AlignCenter = Qt.AlignCenter  # type: ignore

from src.core.calculator_engine import CalculatorEngine, CalculationResult
from src.core.history_manager import HistoryManager, HistoryEntry
from src.utils.validators import InputValidator, DISPLAY_OPERATORS
from src.ui.widgets.history_panel import HistoryPanel

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Theme Definitions
# ─────────────────────────────────────────────────────────────

DARK_THEME: dict[str, str] = {
    "THEME_BG_PRIMARY":         "#1C1C1E",
    "THEME_BG_DISPLAY":         "#2C2C2E",
    "THEME_BG_TOOLBAR":         "#1C1C1E",
    "THEME_BG_HISTORY":         "#1C1C1E",
    "THEME_TEXT_PRIMARY":       "#FFFFFF",
    "THEME_TEXT_SECONDARY":     "#8E8E93",
    "THEME_TEXT_DISABLED":      "#48484A",
    "THEME_BORDER":             "#38383A",
    "THEME_BORDER_SUBTLE":      "#2C2C2E",
    "THEME_COLOR_ACCENT":       "#0A84FF",
    "THEME_COLOR_ERROR":        "#FF453A",
    "THEME_SCROLLBAR_HANDLE":   "#48484A",
    "THEME_SCROLLBAR_HOVER":    "#636366",
    # Number buttons: dark neutral
    "THEME_BTN_NUMBER_BG":      "#2C2C2E",
    "THEME_BTN_NUMBER_FG":      "#FFFFFF",
    "THEME_BTN_NUMBER_HOVER":   "#3A3A3C",
    "THEME_BTN_NUMBER_PRESSED": "#48484A",
    # Operator buttons: mid accent
    "THEME_BTN_OP_BG":          "#3A3A3C",
    "THEME_BTN_OP_FG":          "#FFFFFF",
    "THEME_BTN_OP_HOVER":       "#48484A",
    "THEME_BTN_OP_PRESSED":     "#636366",
    # Equals button: blue accent
    "THEME_BTN_EQUALS_BG":      "#0A84FF",
    "THEME_BTN_EQUALS_FG":      "#FFFFFF",
    "THEME_BTN_EQUALS_HOVER":   "#409CFF",
    "THEME_BTN_EQUALS_PRESSED": "#0071E3",
    # Clear button: red-ish warning
    "THEME_BTN_CLEAR_BG":       "#FF453A",
    "THEME_BTN_CLEAR_FG":       "#FFFFFF",
    "THEME_BTN_CLEAR_HOVER":    "#FF6961",
    "THEME_BTN_CLEAR_PRESSED":  "#D70015",
    # Function buttons: slightly lighter
    "THEME_BTN_FUNC_BG":        "#3A3A3C",
    "THEME_BTN_FUNC_FG":        "#EBEBF5",
    "THEME_BTN_FUNC_HOVER":     "#48484A",
    "THEME_BTN_FUNC_PRESSED":   "#636366",
    # Memory buttons: very subtle
    "THEME_BTN_MEM_BG":         "#1C1C1E",
    "THEME_BTN_MEM_FG":         "#8E8E93",
    "THEME_BTN_MEM_HOVER":      "#2C2C2E",
    "THEME_BTN_MEM_PRESSED":    "#3A3A3C",
    # Scientific buttons
    "THEME_BTN_SCI_BG":         "#2C2C2E",
    "THEME_BTN_SCI_FG":         "#EBEBF5",
    "THEME_BTN_SCI_HOVER":      "#3A3A3C",
    "THEME_BTN_SCI_PRESSED":    "#48484A",
}

LIGHT_THEME: dict[str, str] = {
    "THEME_BG_PRIMARY":         "#F2F2F7",
    "THEME_BG_DISPLAY":         "#FFFFFF",
    "THEME_BG_TOOLBAR":         "#F2F2F7",
    "THEME_BG_HISTORY":         "#FFFFFF",
    "THEME_TEXT_PRIMARY":       "#1C1C1E",
    "THEME_TEXT_SECONDARY":     "#8E8E93",
    "THEME_TEXT_DISABLED":      "#C7C7CC",
    "THEME_BORDER":             "#E5E5EA",
    "THEME_BORDER_SUBTLE":      "#F2F2F7",
    "THEME_COLOR_ACCENT":       "#007AFF",
    "THEME_COLOR_ERROR":        "#FF3B30",
    "THEME_SCROLLBAR_HANDLE":   "#C7C7CC",
    "THEME_SCROLLBAR_HOVER":    "#AEAEB2",
    # Number buttons: white
    "THEME_BTN_NUMBER_BG":      "#FFFFFF",
    "THEME_BTN_NUMBER_FG":      "#1C1C1E",
    "THEME_BTN_NUMBER_HOVER":   "#E5E5EA",
    "THEME_BTN_NUMBER_PRESSED": "#D1D1D6",
    # Operator buttons: light gray
    "THEME_BTN_OP_BG":          "#E5E5EA",
    "THEME_BTN_OP_FG":          "#1C1C1E",
    "THEME_BTN_OP_HOVER":       "#D1D1D6",
    "THEME_BTN_OP_PRESSED":     "#AEAEB2",
    # Equals button: blue
    "THEME_BTN_EQUALS_BG":      "#007AFF",
    "THEME_BTN_EQUALS_FG":      "#FFFFFF",
    "THEME_BTN_EQUALS_HOVER":   "#409CFF",
    "THEME_BTN_EQUALS_PRESSED": "#0063D1",
    # Clear button: red
    "THEME_BTN_CLEAR_BG":       "#FF3B30",
    "THEME_BTN_CLEAR_FG":       "#FFFFFF",
    "THEME_BTN_CLEAR_HOVER":    "#FF6961",
    "THEME_BTN_CLEAR_PRESSED":  "#D70015",
    # Function buttons: light
    "THEME_BTN_FUNC_BG":        "#E5E5EA",
    "THEME_BTN_FUNC_FG":        "#1C1C1E",
    "THEME_BTN_FUNC_HOVER":     "#D1D1D6",
    "THEME_BTN_FUNC_PRESSED":   "#AEAEB2",
    # Memory buttons
    "THEME_BTN_MEM_BG":         "#F2F2F7",
    "THEME_BTN_MEM_FG":         "#8E8E93",
    "THEME_BTN_MEM_HOVER":      "#E5E5EA",
    "THEME_BTN_MEM_PRESSED":    "#D1D1D6",
    # Scientific buttons
    "THEME_BTN_SCI_BG":         "#FFFFFF",
    "THEME_BTN_SCI_FG":         "#1C1C1E",
    "THEME_BTN_SCI_HOVER":      "#E5E5EA",
    "THEME_BTN_SCI_PRESSED":    "#D1D1D6",
}

# ─────────────────────────────────────────────────────────────
# MainWindow
# ─────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    """Cửa sổ chính của ứng dụng máy tính.

    Kế thừa QMainWindow, tích hợp:
    - CalculatorEngine cho tính toán
    - HistoryManager cho lịch sử
    - InputValidator cho validate input
    - HistoryPanel cho hiển thị lịch sử
    - Dark/Light mode switching qua QSS

    Attributes:
        _engine: Engine tính toán Shunting-Yard.
        _history_manager: Quản lý lịch sử.
        _validator: Bộ validate input.
        _expression: Biểu thức đang nhập (dạng display).
        _current_result: Kết quả hiện tại (str).
        _is_dark_mode: Trạng thái theme.
        _is_scientific_mode: Trạng thái chế độ scientific.
        _memory: Bộ nhớ máy tính.
        _error_state: True nếu đang ở trạng thái lỗi.
        _just_calculated: True nếu vừa nhấn '=' xong.
        _open_paren_count: Số dấu ngoặc mở chưa đóng.
    """

    def __init__(self) -> None:
        """Khởi tạo MainWindow."""
        super().__init__()

        # ── Core components ──────────────────────────────────
        self._engine = CalculatorEngine()
        self._history_manager = HistoryManager(max_entries=100)
        self._validator = InputValidator()

        # ── State variables ───────────────────────────────────
        self._expression: str = ""          # Biểu thức đang nhập
        self._current_result: str = "0"     # Số/kết quả hiển thị lớn
        self._is_dark_mode: bool = True     # Theme mặc định: dark
        self._is_scientific_mode: bool = False
        self._memory: float = 0.0           # M: bộ nhớ
        self._error_state: bool = False     # Đang hiển thị lỗi?
        self._just_calculated: bool = False # Vừa nhấn = ?
        self._open_paren_count: int = 0     # Số ngoặc mở chưa đóng
        self._history_visible: bool = False # Panel lịch sử đang hiện?
        self._raw_current_value: float | None = None  # Giá trị số thô

        # ── Setup UI ──────────────────────────────────────────
        self._setup_window()
        self._setup_ui()
        self._setup_connections()
        self._apply_theme()

        # Bắt đầu với kết quả "0"
        self._update_display()

    # ─── Window Setup ─────────────────────────────────────────

    def _setup_window(self) -> None:
        """Thiết lập thuộc tính cơ bản của cửa sổ."""
        self.setWindowTitle("Máy Tính")
        self.setMinimumSize(QSize(380, 580))
        self.resize(QSize(400, 600))

        # Set window icon từ emoji hoặc tự vẽ
        self._set_window_icon()

        # Cho phép focus để nhận keyboard events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def _set_window_icon(self) -> None:
        """Tạo và set icon cho cửa sổ ứng dụng."""
        # Kiểm tra file icon trước
        icon_path = Path(__file__).parent.parent.parent / "resources" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
            return

        # Tự vẽ icon bằng code nếu không có file
        size = 64
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Vẽ nền tròn màu xanh
        painter.setBrush(QBrush(QColor("#0A84FF")))
        painter.setPen(QColor(0, 0, 0, 0))
        painter.drawEllipse(2, 2, size - 4, size - 4)

        # Vẽ ký tự "=" trắng
        painter.setPen(QColor("#FFFFFF"))
        font = QFont("Arial", 28, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(
            0, 0, size, size,
            int(AlignCenter),
            "="
        )
        painter.end()

        self.setWindowIcon(QIcon(pixmap))

    # ─── UI Setup ─────────────────────────────────────────────

    def _setup_ui(self) -> None:
        """Thiết lập toàn bộ giao diện."""
        # Central widget
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Calculator container (left side) ──────────────────
        self._calc_container = QWidget()
        self._calc_container.setObjectName("calculatorContainer")
        calc_layout = QVBoxLayout(self._calc_container)
        calc_layout.setContentsMargins(0, 0, 0, 0)
        calc_layout.setSpacing(0)

        # Toolbar
        toolbar = self._create_toolbar()
        calc_layout.addWidget(toolbar)

        # Memory buttons row
        mem_row = self._create_memory_row()
        calc_layout.addWidget(mem_row)

        # Display area
        display = self._create_display_area()
        calc_layout.addWidget(display)

        # Button grid (standard mode)
        self._btn_grid_widget = self._create_standard_grid()
        calc_layout.addWidget(self._btn_grid_widget, 1)

        # Scientific grid (hidden by default)
        self._sci_grid_widget = self._create_scientific_grid()
        self._sci_grid_widget.setVisible(False)
        calc_layout.addWidget(self._sci_grid_widget)

        main_layout.addWidget(self._calc_container, 1)

        # ── History Panel (right side, hidden by default) ────
        self._history_panel = HistoryPanel()
        self._history_panel.setVisible(False)
        self._history_panel.setMinimumWidth(0)
        self._history_panel.setMaximumWidth(0)
        main_layout.addWidget(self._history_panel)

    def _create_toolbar(self) -> QWidget:
        """Tạo toolbar phía trên với các nút toggle.

        Returns:
            QWidget toolbar.
        """
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(4)

        # Mode label
        self._mode_label = QLabel("STANDARD")
        self._mode_label.setObjectName("modeLabel")

        # History toggle button
        self._btn_history_toggle = QPushButton("🕐")
        self._btn_history_toggle.setObjectName("btnHistoryToggle")
        self._btn_history_toggle.setToolTip("Lịch sử phép tính (Ctrl+H)")
        self._btn_history_toggle.setCheckable(True)

        # Scientific toggle button
        self._btn_sci_toggle = QPushButton("SCI")
        self._btn_sci_toggle.setObjectName("btnScientificToggle")
        self._btn_sci_toggle.setToolTip("Chế độ Khoa học (Ctrl+S)")
        self._btn_sci_toggle.setCheckable(True)

        # Theme toggle button
        self._btn_theme_toggle = QPushButton("🌙")
        self._btn_theme_toggle.setObjectName("btnThemeToggle")
        self._btn_theme_toggle.setToolTip("Chuyển giao diện Sáng/Tối")

        layout.addWidget(self._mode_label)
        layout.addStretch()
        layout.addWidget(self._btn_sci_toggle)
        layout.addWidget(self._btn_history_toggle)
        layout.addWidget(self._btn_theme_toggle)

        return toolbar

    def _create_memory_row(self) -> QWidget:
        """Tạo hàng nút bộ nhớ (MC, MR, M+, M-, MS).

        Returns:
            QWidget chứa các nút memory.
        """
        container = QFrame()
        container.setObjectName("memoryRow")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(8, 4, 8, 0)
        layout.setSpacing(4)

        memory_buttons = [
            ("MC", "btn_mc", "Xóa bộ nhớ"),
            ("MR", "btn_mr", "Đọc bộ nhớ"),
            ("M+", "btn_mplus", "Cộng vào bộ nhớ"),
            ("M−", "btn_mminus", "Trừ khỏi bộ nhớ"),
            ("MS", "btn_ms", "Lưu vào bộ nhớ"),
        ]

        self._memory_btns: dict[str, QPushButton] = {}

        for text, obj_name, tooltip in memory_buttons:
            btn = QPushButton(text)
            btn.setObjectName(obj_name)
            btn.setToolTip(tooltip)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            layout.addWidget(btn)
            self._memory_btns[obj_name] = btn

        # Memory indicator label
        self._memory_indicator = QLabel("M")
        self._memory_indicator.setObjectName("memoryIndicator")
        self._memory_indicator.setVisible(False)
        layout.addWidget(self._memory_indicator)

        # Cập nhật trạng thái ban đầu
        self._update_memory_button_states()

        return container

    def _create_display_area(self) -> QWidget:
        """Tạo khu vực hiển thị biểu thức và kết quả.

        Returns:
            QWidget chứa 2 ô QLineEdit.
        """
        container = QFrame()
        container.setObjectName("displayArea")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Label biểu thức (nhỏ, trên) -> Dùng QLineEdit để cuộn
        self._expression_label = QLineEdit("")
        self._expression_label.setObjectName("expressionLabel")
        self._expression_label.setAlignment(AlignRight | AlignVCenter)
        self._expression_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self._expression_label.setReadOnly(True)
        self._expression_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Label kết quả (to, dưới) -> Dùng QLineEdit để cuộn
        self._result_label = QLineEdit("0")
        self._result_label.setObjectName("resultLabel")
        self._result_label.setAlignment(AlignRight | AlignVCenter)
        self._result_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._result_label.setReadOnly(True)
        self._result_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        layout.addWidget(self._expression_label, 1)
        layout.addWidget(self._result_label, 2)

        return container

    def _create_button(
        self,
        text: str,
        obj_name: str,
        tooltip: str = "",
        font_size: int | None = None,
    ) -> QPushButton:
        """Helper tạo một QPushButton với cấu hình chuẩn.

        Args:
            text: Văn bản hiển thị trên nút.
            obj_name: Object name cho CSS selector.
            tooltip: Tooltip khi hover.
            font_size: Cỡ chữ tùy chỉnh (None = dùng mặc định CSS).

        Returns:
            QPushButton đã được cấu hình.
        """
        btn = QPushButton(text)
        btn.setObjectName(obj_name)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        if tooltip:
            btn.setToolTip(tooltip)
        if font_size:
            font = btn.font()
            font.setPointSize(font_size)
            btn.setFont(font)
        # Đảm bảo cửa sổ nhận focus lại sau khi click nút
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        return btn

    def _create_standard_grid(self) -> QWidget:
        """Tạo lưới nút bấm chế độ Standard.

        Layout (6 hàng × 4 cột):
        Row 0: [%]    [CE]    [C]    [⌫]
        Row 1: [¹/x]  [x²]    [√x]   [÷]
        Row 2: [7]    [8]     [9]    [×]
        Row 3: [4]    [5]     [6]    [−]
        Row 4: [1]    [2]     [3]    [+]
        Row 5: [±]    [0]     [.]    [=]
        """
        container = QFrame()
        container.setObjectName("buttonGrid")
        grid = QGridLayout(container)
        grid.setContentsMargins(8, 8, 8, 8)
        grid.setSpacing(6)

        # ── Hàng 0: %, CE, C, Backspace ───────────────
        btn_pct = self._create_button("%",  "btn_percent",   "Phần trăm")
        btn_ce  = self._create_button("CE", "btn_ce",        "Xóa entry (Delete)")
        btn_c   = self._create_button("C",  "btn_clear",     "Xóa tất cả (Esc)")
        btn_bs  = self._create_button("⌫",  "btn_backspace", "Xóa ký tự (Backspace)")

        # ── Hàng 1: 1/x, x², √x, ÷ ────────────────────
        btn_inv  = self._create_button("¹/x", "btn_inv",     "Nghịch đảo")
        btn_sqr  = self._create_button("x²",  "btn_sqr",     "Bình phương")
        btn_sqrt = self._create_button("√x",  "btn_sqrt",    "Căn bậc hai")
        btn_div  = self._create_button("÷",   "btn_div",     "Chia (/)")

        # ── Hàng 2: 7, 8, 9, × ────────────────────────
        btn_7   = self._create_button("7", "btn_7", "7")
        btn_8   = self._create_button("8", "btn_8", "8")
        btn_9   = self._create_button("9", "btn_9", "9")
        btn_mul = self._create_button("×", "btn_mul", "Nhân (*)")

        # ── Hàng 3: 4, 5, 6, − ────────────────────────
        btn_4   = self._create_button("4", "btn_4", "4")
        btn_5   = self._create_button("5", "btn_5", "5")
        btn_6   = self._create_button("6", "btn_6", "6")
        btn_sub = self._create_button("−", "btn_sub", "Trừ (-)")

        # ── Hàng 4: 1, 2, 3, + ────────────────────────
        btn_1   = self._create_button("1", "btn_1", "1")
        btn_2   = self._create_button("2", "btn_2", "2")
        btn_3   = self._create_button("3", "btn_3", "3")
        btn_add = self._create_button("+", "btn_add", "Cộng (+)")

        # ── Hàng 5: ±, 0, ., = ────────────────────────
        btn_neg = self._create_button("±", "btn_negate",  "Đổi dấu")
        btn_0   = self._create_button("0", "btn_0",       "0")
        btn_dot = self._create_button(".", "btn_dot",     "Dấu chấm thập phân")
        btn_eq  = self._create_button("=", "btn_equals",  "Tính kết quả (Enter)")

        # Thêm vào grid
        buttons = [
            [btn_pct, btn_ce, btn_c, btn_bs],
            [btn_inv, btn_sqr, btn_sqrt, btn_div],
            [btn_7, btn_8, btn_9, btn_mul],
            [btn_4, btn_5, btn_6, btn_sub],
            [btn_1, btn_2, btn_3, btn_add],
            [btn_neg, btn_0, btn_dot, btn_eq]
        ]
        
        for r, row_btns in enumerate(buttons):
            for c, btn in enumerate(row_btns):
                grid.addWidget(btn, r, c)

        # Thiết lập tỉ lệ cột và hàng
        for col in range(4):
            grid.setColumnStretch(col, 1)
        for r in range(6):
            grid.setRowStretch(r, 1)

        # Lưu references để kết nối signals sau
        self._standard_buttons = {
            "percent": btn_pct, "ce": btn_ce, "clear": btn_c, "backspace": btn_bs,
            "inv": btn_inv, "sqr": btn_sqr, "sqrt": btn_sqrt, "div": btn_div,
            "7": btn_7, "8": btn_8, "9": btn_9, "mul": btn_mul,
            "4": btn_4, "5": btn_5, "6": btn_6, "sub": btn_sub,
            "1": btn_1, "2": btn_2, "3": btn_3, "add": btn_add,
            "negate": btn_neg, "0": btn_0, "dot": btn_dot, "equals": btn_eq,
        }

        return container

    def _create_scientific_grid(self) -> QWidget:
        """Tạo hàng nút scientific.

        Returns:
            QWidget chứa hàng nút scientific.
        """
        container = QFrame()
        container.setObjectName("sciGrid")
        grid = QGridLayout(container)
        grid.setContentsMargins(8, 4, 8, 4)
        grid.setSpacing(6)

        sci_buttons = [
            ("(",    "btn_paren_open",  "Mở ngoặc"),
            (")",    "btn_paren_close", "Đóng ngoặc"),
            ("n!",   "btn_factorial",   "Giai thừa"),
            ("π",    "btn_pi",          "Pi ≈ 3.14159..."),
            ("e",    "btn_e_const",     "e ≈ 2.71828..."),
            ("sin",  "btn_sin",         "sin(x) - độ"),
            ("cos",  "btn_cos",         "cos(x) - độ"),
            ("tan",  "btn_tan",         "tan(x) - độ"),
            ("log",  "btn_log",         "log₁₀(x)"),
            ("ln",   "btn_ln",          "ln(x)"),
            ("asin", "btn_asin",        "arcsin(x)"),
            ("acos", "btn_acos",        "arccos(x)"),
            ("atan", "btn_atan",        "arctan(x)"),
        ]

        self._sci_buttons: dict[str, QPushButton] = {}

        for i, (text, obj_name, tip) in enumerate(sci_buttons):
            btn = self._create_button(text, obj_name, tip, font_size=11)
            row, col = divmod(i, 5)
            grid.addWidget(btn, row, col)
            grid.setColumnStretch(col, 1)
            self._sci_buttons[obj_name] = btn

        for r in range(3):
            grid.setRowStretch(r, 1)

        return container

    # ─── Signal Connections ────────────────────────────────────

    def _setup_connections(self) -> None:
        """Kết nối tất cả signals với slots."""

        # ── Toolbar buttons ──────────────────────────────────
        self._btn_theme_toggle.clicked.connect(self._on_theme_toggle)
        self._btn_history_toggle.toggled.connect(self._on_history_toggle)
        self._btn_sci_toggle.toggled.connect(self._on_scientific_toggle)

        # ── Memory buttons ────────────────────────────────────
        self._memory_btns["btn_mc"].clicked.connect(self._on_mc)
        self._memory_btns["btn_mr"].clicked.connect(self._on_mr)
        self._memory_btns["btn_mplus"].clicked.connect(self._on_mplus)
        self._memory_btns["btn_mminus"].clicked.connect(self._on_mminus)
        self._memory_btns["btn_ms"].clicked.connect(self._on_ms)

        # ── Standard grid buttons ─────────────────────────────
        b = self._standard_buttons
        for digit in "0123456789":
            b[digit].clicked.connect(
                lambda checked, d=digit: self._on_digit(d)
            )
        b["dot"].clicked.connect(self._on_dot)
        b["add"].clicked.connect(lambda: self._on_operator("+"))
        b["sub"].clicked.connect(lambda: self._on_operator("−"))
        b["mul"].clicked.connect(lambda: self._on_operator("×"))
        b["div"].clicked.connect(lambda: self._on_operator("÷"))
        b["equals"].clicked.connect(self._on_equals)
        b["clear"].clicked.connect(self._on_clear)
        b["ce"].clicked.connect(self._on_ce)
        b["backspace"].clicked.connect(self._on_backspace)
        b["sqrt"].clicked.connect(lambda: self._on_function("sqrt"))
        b["sqr"].clicked.connect(lambda: self._on_function("sqr"))
        b["inv"].clicked.connect(lambda: self._on_function("inv"))
        b["percent"].clicked.connect(lambda: self._on_function("percent"))
        b["negate"].clicked.connect(self._on_negate)

        # ── Scientific buttons ────────────────────────────────
        sci_map = {
            "btn_sin":     "sin",
            "btn_cos":     "cos",
            "btn_tan":     "tan",
            "btn_log":     "log",
            "btn_ln":      "ln",
            "btn_asin":    "asin",
            "btn_acos":    "acos",
            "btn_atan":    "atan",
            "btn_factorial": "factorial",
        }
        for obj_name, func_name in sci_map.items():
            self._sci_buttons[obj_name].clicked.connect(
                lambda checked, fn=func_name: self._on_function(fn)
            )

        self._sci_buttons["btn_paren_open"].clicked.connect(lambda: self._on_paren("("))
        self._sci_buttons["btn_paren_close"].clicked.connect(lambda: self._on_paren(")"))

        self._sci_buttons["btn_pi"].clicked.connect(
            lambda: self._on_constant("pi", "3.14159265358979")
        )
        self._sci_buttons["btn_e_const"].clicked.connect(
            lambda: self._on_constant("e", "2.71828182845905")
        )

        # ── History panel ─────────────────────────────────────
        self._history_panel.entry_selected.connect(self._on_history_entry_selected)
        self._history_panel.clear_requested.connect(self._on_history_clear)

        # ── History manager callback ───────────────────────────
        self._history_manager.add_callback(self._history_panel.update_entries)

    # ─── Display Update ────────────────────────────────────────

    def _update_display(self) -> None:
        """Cập nhật các label hiển thị từ state hiện tại."""
        # Expression label (nhỏ, phía trên)
        self._expression_label.setText(self._expression)
        self._expression_label.setCursorPosition(len(self._expression))

        # Result label (to, phía dưới)
        result_text = self._current_result
        self._result_label.setText(result_text)
        self._result_label.setCursorPosition(len(result_text))

        # Điều chỉnh cỡ chữ tự động theo độ dài kết quả
        length = len(result_text.replace(",", ""))
        if length <= 9:
            font_size = 52
        elif length <= 12:
            font_size = 44
        elif length <= 16:
            font_size = 36
        else:
            font_size = 28

        # Chỉ update font nếu thay đổi để tránh flicker
        current_size = self._result_label.font().pointSize()
        if current_size != font_size:
            font = self._result_label.font()
            font.setPointSize(font_size)
            self._result_label.setFont(font)

        # Set thuộc tính error để CSS selector hoạt động
        is_error = self._error_state
        # Cập nhật property cho QSS
        if PYQT_VERSION == 6:
            self._result_label.setProperty("error", "true" if is_error else "false")
        else:
            self._result_label.setProperty("error", "true" if is_error else "false")
        self._result_label.style().unpolish(self._result_label)
        self._result_label.style().polish(self._result_label)

    def _show_error(self, message: str) -> None:
        """Hiển thị thông báo lỗi trên màn hình.

        Args:
            message: Thông báo lỗi thân thiện.
        """
        self._error_state = True
        self._current_result = message
        self._expression = ""
        self._update_display()
        logger.debug("Error displayed: %s", message)

    def _reset_after_error(self) -> None:
        """Reset trạng thái sau khi có lỗi."""
        self._error_state = False
        self._expression = ""
        self._current_result = "0"
        self._just_calculated = False
        self._open_paren_count = 0
        self._raw_current_value = None
        self._update_display()

    # ─── Input Handlers ────────────────────────────────────────

    def _on_digit(self, digit: str) -> None:
        """Xử lý khi người dùng nhập chữ số.

        Args:
            digit: Chữ số "0"-"9".
        """
        # Nếu đang ở trạng thái lỗi → reset
        if self._error_state:
            self._reset_after_error()

        # Nếu vừa nhấn = và nhập số mới → bắt đầu biểu thức mới
        if self._just_calculated:
            self._expression = ""
            self._current_result = digit if digit != "0" else "0"
            self._just_calculated = False
            self._open_paren_count = 0
            self._update_display()
            return

        # Kiểm tra nếu hiện tại là "0" đơn → thay thế (không cho nhập "007")
        if self._current_result == "0" and digit == "0":
            # Vẫn giữ "0", không thêm nữa
            return
        if self._current_result == "0" and digit != "0":
            self._current_result = digit
        else:
            # Validate độ dài
            current_segment = self._validator.get_current_number_segment(
                self._expression + self._current_result
            )
            result = self._validator.can_append_digit(current_segment, digit)
            if not result.is_valid:
                return  # Bỏ qua nếu số quá dài
            self._current_result += digit

        self._update_display()

    def _on_dot(self) -> None:
        """Xử lý khi người dùng nhập dấu chấm thập phân."""
        if self._error_state:
            self._reset_after_error()
            self._current_result = "0."
            self._update_display()
            return

        if self._just_calculated:
            self._expression = ""
            self._current_result = "0."
            self._just_calculated = False
            self._update_display()
            return

        result = self._validator.can_append_dot(self._current_result)
        if result.is_valid:
            self._current_result = result.sanitized
            self._update_display()
        # Nếu không hợp lệ (đã có dấu chấm), bỏ qua

    def _on_operator(self, operator: str) -> None:
        """Xử lý khi người dùng nhập toán tử.

        Args:
            operator: Ký hiệu toán tử dạng display (+, −, ×, ÷).
        """
        if self._error_state:
            self._reset_after_error()
            return

        # Nếu vừa nhấn =, dùng kết quả làm đầu biểu thức mới
        if self._just_calculated:
            self._expression = self._current_result + " " + operator + " "
            self._current_result = ""
            self._just_calculated = False
            self._open_paren_count = 0
            self._update_display()
            return

        # Nếu đang nhập số và expression rỗng: bắt đầu biểu thức
        if self._current_result and not self._expression:
            self._expression = self._current_result + " " + operator + " "
            self._current_result = ""
            self._update_display()
            return

        # Nếu đang nhập số giữa biểu thức: commit số hiện tại
        if self._current_result:
            result = self._validator.can_append_operator(
                self._expression + self._current_result, operator
            )
        else:
            result = self._validator.can_append_operator(
                self._expression.rstrip(), operator
            )

        if result.is_valid:
            if self._current_result:
                self._expression = self._expression + self._current_result + " " + operator + " "
                self._current_result = ""
            else:
                # Thay thế toán tử cuối (nếu expression kết thúc bằng toán tử)
                expr = self._expression.rstrip()
                last_word = expr.split()[-1] if expr.split() else ""
                if last_word in DISPLAY_OPERATORS or last_word in ("+", "-", "*", "/", "%", "^"):
                    self._expression = " ".join(expr.split()[:-1]) + " " + operator + " "
                else:
                    self._expression = expr + " " + operator + " "
        elif result.message:
            # Thông báo lỗi nhẹ (không crash)
            logger.debug("Operator blocked: %s", result.message)

        self._update_display()

    def _on_equals(self) -> None:
        """Xử lý khi người dùng nhấn '=' (tính kết quả)."""
        if self._error_state:
            self._reset_after_error()
            return

        # Xây dựng biểu thức hoàn chỉnh
        full_expr = self._expression
        if self._current_result:
            full_expr += self._current_result

        # Tự đóng các dấu ngoặc còn thiếu
        if self._open_paren_count > 0:
            full_expr += ")" * self._open_paren_count

        full_expr = full_expr.strip()

        if not full_expr or full_expr == "0":
            return

        # Chuyển về dạng tính toán
        compute_expr = self._validator.display_to_compute(full_expr)

        logger.debug("Evaluating: %s → %s", full_expr, compute_expr)

        # Tính toán
        result = self._engine.evaluate(compute_expr)

        if result.success:
            # Lưu vào lịch sử
            self._history_manager.add_entry(
                expression=full_expr,
                result=result.display_value,
                raw_value=result.value,
            )
            # Cập nhật state
            self._expression = full_expr + " ="
            self._current_result = result.display_value
            self._raw_current_value = result.value
            self._just_calculated = True
            self._open_paren_count = 0
            self._error_state = False
            self._update_display()
        else:
            self._show_error(result.error_message or "Lỗi không xác định")

    def _on_clear(self) -> None:
        """Xử lý nút C (Clear All)."""
        self._reset_after_error()
        self._expression = ""
        self._current_result = "0"
        self._just_calculated = False
        self._open_paren_count = 0
        self._error_state = False
        self._raw_current_value = None
        self._update_display()

    def _on_ce(self) -> None:
        """Xử lý nút CE (Clear Entry - xóa số đang nhập)."""
        if self._error_state:
            self._reset_after_error()
            return

        if self._current_result and self._current_result != "0":
            self._current_result = "0"
        else:
            # Không có số đang nhập → xóa số cuối trong expression
            if self._expression:
                parts = self._expression.rstrip().split()
                if parts:
                    # Kiểm tra phần cuối có phải toán tử không
                    last = parts[-1]
                    if last in DISPLAY_OPERATORS or last in ("+", "-", "*", "/"):
                        # Xóa toán tử
                        self._expression = " ".join(parts[:-1]) + " "
                    else:
                        # Xóa số
                        self._expression = " ".join(parts[:-1])
                        if self._expression:
                            self._expression += " "
                    # Đếm lại dấu ngoặc
                    self._open_paren_count = self._validator.count_open_parens(
                        self._expression
                    )

        self._just_calculated = False
        self._update_display()

    def _on_backspace(self) -> None:
        """Xử lý nút ⌫ (Backspace - xóa từng ký tự)."""
        if self._error_state:
            self._reset_after_error()
            return

        if self._just_calculated:
            # Sau khi tính, backspace → xóa kết quả
            self._on_clear()
            return

        if self._current_result and self._current_result != "0":
            if len(self._current_result) == 1:
                self._current_result = "0"
            elif self._current_result == "-0" or self._current_result == "−0":
                self._current_result = "0"
            else:
                self._current_result = self._current_result[:-1]
                # Nếu xóa hết phần thập phân, xóa luôn dấu chấm
                if self._current_result.endswith("."):
                    pass  # Cho phép "2." để tiếp tục nhập
        elif self._expression:
            # Xóa ký tự cuối trong expression
            expr_stripped = self._expression.rstrip()
            if expr_stripped:
                self._expression = expr_stripped[:-1]
                if self._expression and not self._expression.endswith(" "):
                    self._expression += ""
                # Đếm lại dấu ngoặc
                self._open_paren_count = self._validator.count_open_parens(
                    self._expression
                )

        self._update_display()

    def _on_function(self, func_name: str) -> None:
        """Xử lý các hàm toán học (sqrt, sqr, sin, cos, ...).

        Nếu đang có số đang nhập → tính ngay trên số đó.
        Nếu không có số → thêm tên hàm vào expression.

        Args:
            func_name: Tên hàm (sqrt, sqr, sin, cos, ...).
        """
        if self._error_state:
            self._reset_after_error()
            return

        # Lấy số hiện tại để tính
        if self._current_result and self._current_result not in ("0", ""):
            # Có số đang nhập → tính ngay
            try:
                value = float(self._validator.display_to_compute(self._current_result))
            except ValueError:
                self._show_error("Lỗi: Số không hợp lệ")
                return

            result = self._engine.evaluate_single_function(func_name, value)

            if result.success:
                # Hiển thị kết quả và thêm vào expression
                expr_entry = f"{func_name}({self._current_result})"
                if self._expression:
                    self._expression = self._expression + expr_entry
                else:
                    self._expression = expr_entry + " ="
                    self._just_calculated = True

                self._current_result = result.display_value
                self._raw_current_value = result.value
                self._update_display()

                # Nếu đứng độc lập (không có expression), lưu vào history
                if self._just_calculated:
                    self._history_manager.add_entry(
                        expression=expr_entry,
                        result=result.display_value,
                        raw_value=result.value,
                    )
            else:
                self._show_error(result.error_message or "Lỗi tính toán")

        elif self._just_calculated and self._raw_current_value is not None:
            # Sau khi đã tính → áp dụng hàm lên kết quả
            result = self._engine.evaluate_single_function(
                func_name, self._raw_current_value
            )
            if result.success:
                expr_entry = f"{func_name}({self._current_result})"
                self._history_manager.add_entry(
                    expression=expr_entry,
                    result=result.display_value,
                    raw_value=result.value,
                )
                self._expression = expr_entry + " ="
                self._current_result = result.display_value
                self._raw_current_value = result.value
                self._update_display()
            else:
                self._show_error(result.error_message or "Lỗi tính toán")
        else:
            # Không có số → thêm tên hàm vào expression (mode expression)
            self._expression += f"{func_name}("
            self._open_paren_count += 1
            self._update_display()

    def _on_negate(self) -> None:
        """Xử lý nút ± (đổi dấu số hiện tại)."""
        if self._error_state:
            return

        if self._current_result and self._current_result not in ("0", ""):
            # Đổi dấu số hiện tại
            compute_str = self._validator.display_to_compute(self._current_result)
            try:
                val = float(compute_str)
                val = -val
                self._current_result = self._engine._format_number(val)
                self._raw_current_value = val
            except ValueError:
                return
        elif self._just_calculated and self._raw_current_value is not None:
            val = -self._raw_current_value
            self._current_result = self._engine._format_number(val)
            self._raw_current_value = val

        self._update_display()

    def _on_paren(self, paren: str) -> None:
        """Xử lý khi người dùng nhập dấu ngoặc.

        Args:
            paren: '(' hoặc ')'.
        """
        if self._error_state:
            self._reset_after_error()
            return

        result = self._validator.can_append_paren(
            self._expression + self._current_result,
            paren,  # type: ignore
            self._open_paren_count,
        )

        if result.is_valid:
            if paren == "(":
                # Nếu đang có số → thêm nhân ngầm rồi mở ngoặc
                if self._current_result and self._current_result != "0":
                    self._expression += self._current_result + " × ("
                    self._current_result = ""
                elif self._expression and self._expression.rstrip()[-1:].isdigit():
                    self._expression = self._expression.rstrip() + " × ("
                else:
                    self._expression += "("
                self._open_paren_count += 1
            else:  # ')'
                if self._current_result:
                    self._expression += self._current_result + ")"
                    self._current_result = ""
                else:
                    self._expression = self._expression.rstrip() + ")"
                self._open_paren_count = max(0, self._open_paren_count - 1)

        self._update_display()

    def _on_constant(self, name: str, display_value: str) -> None:
        """Xử lý khi người dùng nhập hằng số (π, e).

        Args:
            name: Tên hằng số ("pi", "e").
            display_value: Giá trị hiển thị rút gọn.
        """
        if self._error_state:
            self._reset_after_error()

        if self._just_calculated:
            self._expression = ""
            self._just_calculated = False

        # Nếu đang có số → thêm nhân ngầm
        if self._current_result and self._current_result != "0":
            self._expression += self._current_result + " × "
            self._current_result = ""

        self._expression += display_value
        self._update_display()

    # ─── Memory Handlers ───────────────────────────────────────

    def _get_current_float_value(self) -> float | None:
        """Lấy giá trị số thực của số đang hiển thị.

        Returns:
            float hoặc None nếu không parse được.
        """
        if self._raw_current_value is not None and self._just_calculated:
            return self._raw_current_value

        compute_str = self._validator.display_to_compute(
            self._current_result.replace(",", "")
        )
        try:
            return float(compute_str)
        except (ValueError, AttributeError):
            return None

    @pyqtSlot()
    def _on_mc(self) -> None:
        """MC: Xóa bộ nhớ."""
        self._memory = 0.0
        self._memory_indicator.setVisible(False)
        self._update_memory_button_states()

    @pyqtSlot()
    def _on_mr(self) -> None:
        """MR: Đọc bộ nhớ và hiển thị."""
        if self._memory != 0.0 or True:  # Cho phép đọc ngay cả khi = 0
            display = self._engine._format_number(self._memory)
            if self._just_calculated or not self._expression:
                self._expression = ""
                self._current_result = display
                self._raw_current_value = self._memory
                self._just_calculated = False
            else:
                self._expression += display
            self._update_display()

    @pyqtSlot()
    def _on_mplus(self) -> None:
        """M+: Cộng giá trị hiện tại vào bộ nhớ."""
        val = self._get_current_float_value()
        if val is not None:
            self._memory += val
            self._memory_indicator.setVisible(True)
            self._update_memory_button_states()

    @pyqtSlot()
    def _on_mminus(self) -> None:
        """M-: Trừ giá trị hiện tại khỏi bộ nhớ."""
        val = self._get_current_float_value()
        if val is not None:
            self._memory -= val
            self._memory_indicator.setVisible(True)
            self._update_memory_button_states()

    @pyqtSlot()
    def _on_ms(self) -> None:
        """MS: Lưu giá trị hiện tại vào bộ nhớ."""
        val = self._get_current_float_value()
        if val is not None:
            self._memory = val
            self._memory_indicator.setVisible(True)
            self._update_memory_button_states()

    def _update_memory_button_states(self) -> None:
        """Cập nhật trạng thái enabled/disabled của nút memory."""
        has_memory = self._memory != 0.0
        self._memory_btns["btn_mc"].setEnabled(has_memory)
        self._memory_btns["btn_mr"].setEnabled(has_memory)

    # ─── History Handlers ──────────────────────────────────────

    @pyqtSlot(object)
    def _on_history_entry_selected(self, entry: HistoryEntry) -> None:
        """Xử lý khi người dùng click vào mục lịch sử.

        Args:
            entry: Mục lịch sử được chọn.
        """
        self._expression = ""
        self._current_result = entry.result
        self._raw_current_value = entry.raw_value
        self._just_calculated = True
        self._error_state = False
        self._open_paren_count = 0
        self._update_display()

    @pyqtSlot()
    def _on_history_clear(self) -> None:
        """Xử lý khi người dùng xóa lịch sử."""
        self._history_manager.clear()

    # ─── Theme & Mode Handlers ─────────────────────────────────

    @pyqtSlot()
    def _on_theme_toggle(self) -> None:
        """Toggle giữa Dark và Light mode."""
        self._is_dark_mode = not self._is_dark_mode
        self._btn_theme_toggle.setText("🌙" if self._is_dark_mode else "☀️")
        self._apply_theme()

    @pyqtSlot(bool)
    def _on_history_toggle(self, checked: bool) -> None:
        """Ẩn/hiện history panel.

        Args:
            checked: True nếu đang bật.
        """
        self._history_visible = checked
        self._animate_history_panel(checked)

    @pyqtSlot(bool)
    def _on_scientific_toggle(self, checked: bool) -> None:
        """Ẩn/hiện chế độ Scientific.

        Args:
            checked: True nếu bật Scientific.
        """
        self._is_scientific_mode = checked
        self._sci_grid_widget.setVisible(checked)
        self._mode_label.setText("SCIENTIFIC" if checked else "STANDARD")

    # ─── Animation ─────────────────────────────────────────────

    def _animate_history_panel(self, show: bool) -> None:
        """Animate hiện/ẩn history panel.

        Args:
            show: True để hiển thị, False để ẩn.
        """
        target_width = 260 if show else 0
        self._history_panel.setVisible(True)  # Phải visible để animation hoạt động

        animation = QPropertyAnimation(self._history_panel, b"maximumWidth")
        animation.setDuration(250)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.setStartValue(self._history_panel.maximumWidth())
        animation.setEndValue(target_width)

        if not show:
            animation.finished.connect(lambda: self._history_panel.setVisible(False))

        animation.start()

        # Giữ reference để animation không bị garbage collected
        self._history_animation = animation

    # ─── Theme Application ─────────────────────────────────────

    def _apply_theme(self) -> None:
        """Áp dụng theme (Dark/Light) lên toàn bộ ứng dụng.

        Đọc file QSS, thay thế các placeholder THEME_* bằng màu thực,
        sau đó set stylesheet cho QApplication.
        """
        theme = DARK_THEME if self._is_dark_mode else LIGHT_THEME

        qss_path = Path(__file__).parent / "styles.qss"
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                qss_template = f.read()
        except FileNotFoundError:
            logger.error("styles.qss not found at %s", qss_path)
            return

        # Thay thế tất cả placeholder bằng màu thực, ưu tiên chuỗi dài trước
        qss = qss_template
        for placeholder in sorted(theme.keys(), key=len, reverse=True):
            qss = qss.replace(placeholder, theme[placeholder])

        # Áp dụng cho toàn bộ ứng dụng
        app = QApplication.instance()
        if app:
            app.setStyleSheet(qss)

    # ─── Keyboard Input ────────────────────────────────────────

    def keyPressEvent(self, event: QKeyEvent) -> None:  # type: ignore[override]
        """Xử lý keyboard input.

        Phím tắt được hỗ trợ:
        - 0-9, .: nhập số
        - +, -, *, /: toán tử
        - Enter, =: tính kết quả
        - Backspace: xóa ký tự
        - Escape, Delete: clear
        - %: phần trăm
        - Ctrl+C: copy kết quả
        - Ctrl+H: toggle history
        - Ctrl+S: toggle scientific

        Args:
            event: Sự kiện bàn phím.
        """
        if PYQT_VERSION == 6:
            key = event.key()
            modifiers = event.modifiers()
            Mod = Qt.KeyboardModifier
            Key = Qt.Key
        else:
            key = event.key()
            modifiers = event.modifiers()
            Mod = Qt  # type: ignore
            Key = Qt  # type: ignore

        # ── Ctrl shortcuts ───────────────────────────────────
        ctrl = modifiers == Mod.ControlModifier

        if ctrl:
            if key == Key.Key_C:
                self._copy_result_to_clipboard()
                return
            if key == Key.Key_H:
                self._btn_history_toggle.setChecked(
                    not self._btn_history_toggle.isChecked()
                )
                return
            if key == Key.Key_S:
                self._btn_sci_toggle.setChecked(
                    not self._btn_sci_toggle.isChecked()
                )
                return

        # ── Digit keys ────────────────────────────────────────
        if Key.Key_0 <= key <= Key.Key_9:
            self._on_digit(str(key - Key.Key_0))
            return

        # ── Numpad digits ─────────────────────────────────────
        if Key.Key_0 <= key <= Key.Key_9:
            self._on_digit(str(key - Key.Key_0))
            return

        # Kiểm tra theo text character (hỗ trợ numpad)
        text = event.text()
        if text in "0123456789":
            self._on_digit(text)
            return

        # ── Operators ─────────────────────────────────────────
        key_to_op = {
            "+": "+", "-": "−", "*": "×", "/": "÷",
        }
        if text in key_to_op:
            self._on_operator(key_to_op[text])
            return

        # ── Special keys ──────────────────────────────────────
        if key in (Key.Key_Return, Key.Key_Enter):
            self._on_equals()
            return
        if key == Key.Key_Equal and not modifiers:
            self._on_equals()
            return
        if key == Key.Key_Backspace:
            self._on_backspace()
            return
        if key == Key.Key_Escape:
            self._on_clear()
            return
        if key == Key.Key_Delete:
            self._on_ce()
            return
        if text == ".":
            self._on_dot()
            return
        if text == "%":
            self._on_operator("%")
            return
        if text == "(":
            self._on_paren("(")
            return
        if text == ")":
            self._on_paren(")")
            return

        # Chặn tất cả ký tự không hợp lệ khác
        super().keyPressEvent(event)

    # ─── Clipboard ─────────────────────────────────────────────

    def _copy_result_to_clipboard(self) -> None:
        """Copy kết quả hiện tại vào clipboard (Ctrl+C)."""
        app = QApplication.instance()
        if app:
            clipboard = app.clipboard()
            # Loại bỏ dấu phân cách hàng nghìn trước khi copy
            text = self._current_result.replace(",", "")
            clipboard.setText(text)
            logger.debug("Copied to clipboard: %s", text)

            # Flash effect: đổi màu label ngắn rồi phục hồi
            original_style = self._result_label.styleSheet()
            self._result_label.setStyleSheet("color: #0A84FF;")
            QTimer.singleShot(
                150,
                lambda: self._result_label.setStyleSheet(original_style)
            )

    # ─── Resize Event ──────────────────────────────────────────

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        """Xử lý khi cửa sổ thay đổi kích thước.

        Args:
            event: Sự kiện resize.
        """
        super().resizeEvent(event)
        # Điều chỉnh font size của expression label tùy theo chiều rộng
        width = self.width()
        if width < 380:
            font_size = 11
        elif width < 450:
            font_size = 12
        else:
            font_size = 13

        font = self._expression_label.font()
        if font.pointSize() != font_size:
            font.setPointSize(font_size)
            self._expression_label.setFont(font)
