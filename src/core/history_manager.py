"""
History Manager - Quản lý lịch sử phép tính trong phiên làm việc.

Lưu trữ danh sách các phép tính đã thực hiện, hỗ trợ callback pattern
để thông báo cho UI khi có thay đổi.

Author: PyQt6 Calculator Project
Python: 3.10+
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

logger = logging.getLogger(__name__)


@dataclass
class HistoryEntry:
    """Đại diện cho một mục trong lịch sử phép tính.

    Attributes:
        expression: Biểu thức đã tính (VD: "12 + 8 × 2").
        result: Kết quả (VD: "28").
        timestamp: Thời điểm thực hiện phép tính.
        raw_value: Giá trị số thô để tái sử dụng.
    """
    expression: str
    result: str
    timestamp: datetime = field(default_factory=datetime.now)
    raw_value: float | None = None

    def display_text(self) -> str:
        """Trả về chuỗi hiển thị trong history panel.

        Returns:
            Chuỗi dạng "expression = result".
        """
        return f"{self.expression} = {self.result}"

    def time_label(self) -> str:
        """Trả về nhãn thời gian ngắn gọn.

        Returns:
            Chuỗi giờ:phút:giây.
        """
        return self.timestamp.strftime("%H:%M:%S")


class HistoryManager:
    """Quản lý danh sách lịch sử phép tính.

    Hỗ trợ thêm mục mới, xóa tất cả, và callback khi có thay đổi.
    Giới hạn số mục tối đa để tránh dùng quá nhiều bộ nhớ.

    Attributes:
        _entries: Danh sách các mục lịch sử (mới nhất ở cuối).
        _max_entries: Số mục tối đa được lưu.
        _callbacks: Danh sách hàm callback được gọi khi history thay đổi.

    Example::

        manager = HistoryManager(max_entries=50)
        manager.add_callback(lambda entries: print(f"Now {len(entries)} entries"))
        manager.add_entry("2 + 3", "5", 5.0)
    """

    def __init__(self, max_entries: int = 100) -> None:
        """Khởi tạo HistoryManager.

        Args:
            max_entries: Số mục lịch sử tối đa được lưu giữ.
        """
        self._entries: list[HistoryEntry] = []
        self._max_entries: int = max_entries
        self._callbacks: list[Callable[[list[HistoryEntry]], None]] = []

    # ─── Public API ──────────────────────────────────────────

    def add_entry(
        self,
        expression: str,
        result: str,
        raw_value: float | None = None,
    ) -> HistoryEntry:
        """Thêm một mục vào lịch sử.

        Nếu đạt giới hạn max_entries, mục cũ nhất sẽ bị xóa.

        Args:
            expression: Biểu thức đã tính.
            result: Kết quả dạng string.
            raw_value: Giá trị số thô (để tái sử dụng).

        Returns:
            Mục vừa được thêm vào.
        """
        entry = HistoryEntry(
            expression=expression,
            result=result,
            raw_value=raw_value,
        )
        self._entries.append(entry)

        # Xóa mục cũ nhất nếu vượt giới hạn
        if len(self._entries) > self._max_entries:
            removed = self._entries.pop(0)
            logger.debug("History limit reached, removed oldest: %s", removed.display_text())

        logger.debug("History entry added: %s", entry.display_text())
        self._notify_callbacks()
        return entry

    def clear(self) -> None:
        """Xóa toàn bộ lịch sử."""
        count = len(self._entries)
        self._entries.clear()
        logger.debug("History cleared (%d entries removed)", count)
        self._notify_callbacks()

    def get_all(self) -> list[HistoryEntry]:
        """Trả về toàn bộ danh sách lịch sử (bản sao).

        Returns:
            Danh sách HistoryEntry, mới nhất ở cuối.
        """
        return list(self._entries)

    def get_reversed(self) -> list[HistoryEntry]:
        """Trả về danh sách lịch sử đảo ngược (mới nhất trước).

        Returns:
            Danh sách HistoryEntry, mới nhất ở đầu.
        """
        return list(reversed(self._entries))

    def get_entry(self, index: int) -> HistoryEntry | None:
        """Lấy mục lịch sử theo index.

        Args:
            index: Vị trí trong danh sách (0-based, 0 = cũ nhất).

        Returns:
            HistoryEntry hoặc None nếu index không hợp lệ.
        """
        if 0 <= index < len(self._entries):
            return self._entries[index]
        return None

    def count(self) -> int:
        """Trả về số lượng mục trong lịch sử.

        Returns:
            Số nguyên.
        """
        return len(self._entries)

    def is_empty(self) -> bool:
        """Kiểm tra xem lịch sử có rỗng không.

        Returns:
            True nếu không có mục nào.
        """
        return len(self._entries) == 0

    # ─── Callback Management ─────────────────────────────────

    def add_callback(
        self, callback: Callable[[list[HistoryEntry]], None]
    ) -> None:
        """Đăng ký callback được gọi khi history thay đổi.

        Args:
            callback: Hàm nhận danh sách HistoryEntry hiện tại.
        """
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def remove_callback(
        self, callback: Callable[[list[HistoryEntry]], None]
    ) -> None:
        """Hủy đăng ký callback.

        Args:
            callback: Hàm callback cần xóa.
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _notify_callbacks(self) -> None:
        """Gọi tất cả callback đã đăng ký với danh sách hiện tại."""
        entries = self.get_all()
        for callback in self._callbacks:
            try:
                callback(entries)
            except Exception as exc:
                logger.error("History callback error: %s", exc)
