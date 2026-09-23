"""
History Panel Widget - Panel hiển thị lịch sử phép tính.

Là một QWidget có thể ẩn/hiện (slide in/out), chứa QListWidget
với danh sách các phép tính đã thực hiện trong phiên.

Người dùng có thể:
- Scroll xem lịch sử
- Click vào mục để lấy lại kết quả
- Xóa toàn bộ lịch sử

Author: PyQt6 Calculator Project
Python: 3.10+
"""

from __future__ import annotations

import logging
from typing import Callable

try:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout,
        QListWidget, QListWidgetItem, QLabel,
        QPushButton, QSizePolicy,
    )
    from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize
    from PyQt6.QtGui import QFont, QColor
    PYQT_VERSION = 6
except ImportError:
    from PyQt5.QtWidgets import (  # type: ignore[no-redef]
        QWidget, QVBoxLayout, QHBoxLayout,
        QListWidget, QListWidgetItem, QLabel,
        QPushButton, QSizePolicy,
    )
    from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize  # type: ignore[no-redef]
    from PyQt5.QtGui import QFont, QColor  # type: ignore[no-redef]
    PYQT_VERSION = 5

from src.core.history_manager import HistoryEntry

logger = logging.getLogger(__name__)


class HistoryPanel(QWidget):
    """Panel hiển thị lịch sử phép tính.

    Signals:
        entry_selected: Phát ra khi người dùng click vào mục lịch sử.
                        Truyền kèm HistoryEntry được chọn.
        clear_requested: Phát ra khi người dùng nhấn nút xóa lịch sử.

    Attributes:
        _list_widget: QListWidget chứa danh sách lịch sử.
        _entries: Danh sách HistoryEntry hiện tại (đồng bộ với list widget).
    """

    entry_selected = pyqtSignal(object)   # object = HistoryEntry
    clear_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Khởi tạo HistoryPanel.

        Args:
            parent: Widget cha.
        """
        super().__init__(parent)
        self._entries: list[HistoryEntry] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Thiết lập giao diện của panel."""
        self.setObjectName("historyPanel")
        self.setMinimumWidth(220)
        self.setMaximumWidth(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header ──────────────────────────────────────────
        header = QWidget()
        header.setObjectName("historyHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 10, 12, 10)

        title_label = QLabel("Lịch sử")
        title_label.setObjectName("historyTitle")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        title_label.setFont(font)

        clear_btn = QPushButton("Xóa tất cả")
        clear_btn.setObjectName("historyClearBtn")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(self._on_clear_clicked)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(clear_btn)

        # ── List Widget ──────────────────────────────────────
        self._list_widget = QListWidget()
        self._list_widget.setObjectName("historyList")
        self._list_widget.setSpacing(2)
        self._list_widget.setVerticalScrollMode(
            QListWidget.ScrollMode.ScrollPerPixel
        )
        self._list_widget.itemClicked.connect(self._on_item_clicked)
        self._list_widget.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        # ── Empty state label ────────────────────────────────
        self._empty_label = QLabel("Chưa có phép tính nào")
        self._empty_label.setObjectName("historyEmpty")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setWordWrap(True)

        layout.addWidget(header)
        layout.addWidget(self._list_widget)
        layout.addWidget(self._empty_label)

        self._update_empty_state()

    # ─── Public Methods ──────────────────────────────────────

    def update_entries(self, entries: list[HistoryEntry]) -> None:
        """Cập nhật danh sách lịch sử hiển thị.

        Được gọi từ callback của HistoryManager.

        Args:
            entries: Danh sách HistoryEntry mới (mới nhất ở cuối).
        """
        self._entries = list(reversed(entries))  # Hiển thị mới nhất ở trên
        self._list_widget.clear()

        for entry in self._entries:
            item = self._create_list_item(entry)
            self._list_widget.addItem(item)

        self._update_empty_state()

    def add_entry(self, entry: HistoryEntry) -> None:
        """Thêm một mục vào đầu danh sách (mới nhất lên đầu).

        Args:
            entry: Mục lịch sử mới.
        """
        self._entries.insert(0, entry)
        item = self._create_list_item(entry)
        self._list_widget.insertItem(0, item)
        self._list_widget.scrollToTop()
        self._update_empty_state()

    def clear_entries(self) -> None:
        """Xóa toàn bộ hiển thị (không trigger signal)."""
        self._entries.clear()
        self._list_widget.clear()
        self._update_empty_state()

    # ─── Private Methods ─────────────────────────────────────

    def _create_list_item(self, entry: HistoryEntry) -> QListWidgetItem:
        """Tạo QListWidgetItem từ HistoryEntry.

        Args:
            entry: Mục lịch sử.

        Returns:
            QListWidgetItem đã được cấu hình.
        """
        # Text hiển thị: biểu thức trên, kết quả dưới (bold)
        display_text = f"{entry.expression}\n= {entry.result}"
        item = QListWidgetItem(display_text)
        item.setToolTip(
            f"Biểu thức: {entry.expression}\n"
            f"Kết quả: {entry.result}\n"
            f"Thời gian: {entry.time_label()}"
        )
        # Lưu entry vào item để truy xuất khi click
        item.setData(Qt.ItemDataRole.UserRole, entry)
        item.setSizeHint(QSize(0, 56))  # Chiều cao cố định cho mỗi item
        return item

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        """Xử lý khi người dùng click vào mục lịch sử.

        Args:
            item: QListWidgetItem được click.
        """
        entry = item.data(Qt.ItemDataRole.UserRole)
        if entry is not None:
            logger.debug("History item selected: %s", entry.display_text())
            self.entry_selected.emit(entry)

    def _on_clear_clicked(self) -> None:
        """Xử lý khi người dùng nhấn nút 'Xóa tất cả'."""
        logger.debug("Clear history requested")
        self.clear_requested.emit()

    def _update_empty_state(self) -> None:
        """Ẩn/hiện thông báo trống tùy theo có mục hay không."""
        has_entries = len(self._entries) > 0
        self._list_widget.setVisible(has_entries)
        self._empty_label.setVisible(not has_entries)
