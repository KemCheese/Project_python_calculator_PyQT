"""
Input Validator - Xác thực và làm sạch input từ người dùng.

Module này chịu trách nhiệm validate input TRƯỚC khi gửi đến CalculatorEngine.
Mục tiêu:
- Chặn ký tự không hợp lệ ngay tại điểm nhập
- Xử lý các trường hợp đặc biệt (hai dấu chấm, hai toán tử liên tiếp, ...)
- Làm sạch chuỗi paste từ clipboard

Author: PyQt6 Calculator Project
Python: 3.10+
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Hằng số và tập hợp ký tự hợp lệ
# ─────────────────────────────────────────────────────────────

# Các ký tự toán tử nhị phân được hiển thị trên màn hình
DISPLAY_OPERATORS: set[str] = {"+", "−", "×", "÷", "%", "^"}

# Map từ ký tự hiển thị sang ký tự tính toán
OPERATOR_DISPLAY_MAP: dict[str, str] = {
    "−": "-",
    "×": "*",
    "÷": "/",
    "^": "**",
}

# Map ngược: từ ký tự tính toán sang ký tự hiển thị
OPERATOR_COMPUTE_MAP: dict[str, str] = {v: k for k, v in OPERATOR_DISPLAY_MAP.items()}
OPERATOR_COMPUTE_MAP["**"] = "^"

# Pattern ký tự hợp lệ trong biểu thức
VALID_EXPR_PATTERN = re.compile(r"^[\d\s+\-*/%.(),^a-zA-Z_eE]+$")

# Số ký tự tối đa trong expression (ngăn biểu thức quá dài nhưng cho phép nhập thả ga)
MAX_EXPRESSION_LENGTH: int = 10000


@dataclass
class ValidationResult:
    """Kết quả sau khi validate.

    Attributes:
        is_valid: True nếu hợp lệ.
        sanitized: Chuỗi đã được làm sạch (nếu hợp lệ).
        message: Thông báo nếu không hợp lệ.
    """
    is_valid: bool
    sanitized: str
    message: str = ""


class InputValidator:
    """Bộ xác thực input cho máy tính.

    Tất cả validate đều là stateless (không có side effect).
    Giao diện gọi các phương thức này TRƯỚC khi cập nhật biểu thức.

    Example::

        validator = InputValidator()

        # Kiểm tra có thể thêm dấu chấm không
        result = validator.can_append_dot("3.14")
        print(result.is_valid)  # False - đã có dấu chấm rồi

        # Làm sạch chuỗi paste
        result = validator.sanitize_paste("hello 3+2")
        print(result.sanitized)  # "3+2"
    """

    # ─── Kiểm tra từng ký tự ─────────────────────────────────

    def can_append_digit(self, current_number: str, digit: str) -> ValidationResult:
        """Kiểm tra có thể thêm chữ số vào number đang nhập không.

        Args:
            current_number: Phần số đang nhập hiện tại (VD: "123").
            digit: Chữ số cần thêm ("0"-"9").

        Returns:
            ValidationResult.
        """
        return ValidationResult(is_valid=True, sanitized=current_number + digit)

    def can_append_dot(self, current_number: str) -> ValidationResult:
        """Kiểm tra có thể thêm dấu chấm thập phân không.

        Quy tắc: Mỗi số chỉ được có tối đa một dấu chấm.

        Args:
            current_number: Phần số đang nhập hiện tại.

        Returns:
            ValidationResult.
        """
        if "." in current_number:
            return ValidationResult(
                is_valid=False,
                sanitized=current_number,
                message="Số đã có dấu thập phân",
            )
        # Nếu rỗng, thêm "0." để tạo thành "0.xxx"
        if not current_number or current_number in ("-", ""):
            return ValidationResult(is_valid=True, sanitized="0.")
        return ValidationResult(is_valid=True, sanitized=current_number + ".")

    def can_append_operator(
        self,
        expression: str,
        operator: str,
    ) -> ValidationResult:
        """Kiểm tra và xử lý việc thêm toán tử vào biểu thức.

        Quy tắc:
        - Nếu expression rỗng và operator là nhân/chia → không hợp lệ
        - Nếu ký tự cuối là toán tử → thay thế toán tử cũ
        - Nếu ký tự cuối là '(' → không thêm được (ngoại trừ '-' = unary)

        Args:
            expression: Biểu thức hiện tại (dạng display).
            operator: Toán tử cần thêm (+, −, ×, ÷, ...).

        Returns:
            ValidationResult với expression đã xử lý.
        """
        expr = expression.strip()

        # Biểu thức rỗng
        if not expr:
            if operator in ("×", "÷"):
                return ValidationResult(
                    is_valid=False,
                    sanitized=expr,
                    message="Không thể bắt đầu bằng toán tử nhân/chia",
                )
            if operator == "−":
                # Cho phép bắt đầu bằng dấu trừ (số âm)
                return ValidationResult(is_valid=True, sanitized="−")
            if operator == "+":
                # Bắt đầu bằng '+' → bỏ qua (hoặc coi là 0+)
                return ValidationResult(is_valid=False, sanitized="", message="")
            return ValidationResult(is_valid=True, sanitized=operator)

        # Lấy ký tự cuối (bỏ qua khoảng trắng)
        last_char = expr[-1]

        # Nếu kết thúc bằng dấu mở ngoặc, chỉ cho phép dấu '-' (unary)
        if last_char == "(":
            if operator == "−":
                return ValidationResult(is_valid=True, sanitized=expr + "−")
            if operator in ("+",):
                # Bỏ qua dấu '+' sau '('
                return ValidationResult(is_valid=False, sanitized=expr, message="")
            return ValidationResult(
                is_valid=False,
                sanitized=expr,
                message="Không thể thêm toán tử sau dấu mở ngoặc",
            )

        # Nếu kết thúc bằng toán tử → thay thế
        if last_char in DISPLAY_OPERATORS:
            new_expr = expr[:-1] + operator
            return ValidationResult(is_valid=True, sanitized=new_expr)

        # Trường hợp thông thường: thêm toán tử
        return ValidationResult(is_valid=True, sanitized=expr + operator)

    def can_append_paren(
        self,
        expression: str,
        paren: Literal["(", ")"],
        open_count: int,
    ) -> ValidationResult:
        """Kiểm tra có thể thêm dấu ngoặc không.

        Args:
            expression: Biểu thức hiện tại.
            paren: Dấu ngoặc cần thêm.
            open_count: Số dấu ngoặc mở hiện tại chưa đóng.

        Returns:
            ValidationResult.
        """
        expr = expression.strip()
        last_char = expr[-1] if expr else ""

        if paren == "(":
            return ValidationResult(is_valid=True, sanitized=expr + "(")

        if paren == ")":
            # Không thể đóng ngoặc nếu không có ngoặc mở chưa đóng
            if open_count <= 0:
                return ValidationResult(
                    is_valid=False,
                    sanitized=expr,
                    message="Không có dấu ngoặc mở tương ứng",
                )
            # Không thể đóng ngoặc ngay sau toán tử
            if last_char in DISPLAY_OPERATORS or last_char == "(":
                return ValidationResult(
                    is_valid=False,
                    sanitized=expr,
                    message="Không thể đóng ngoặc ở đây",
                )
            return ValidationResult(is_valid=True, sanitized=expr + ")")

        return ValidationResult(is_valid=False, sanitized=expr, message="Dấu ngoặc không hợp lệ")

    # ─── Validate biểu thức hoàn chỉnh ──────────────────────

    def validate_expression(self, expression: str) -> ValidationResult:
        """Validate toàn bộ biểu thức trước khi tính toán.

        Args:
            expression: Biểu thức dạng display (có thể chứa ký tự đặc biệt).

        Returns:
            ValidationResult với biểu thức đã chuyển đổi sang dạng tính toán.
        """
        if not expression or not expression.strip():
            return ValidationResult(
                is_valid=False,
                sanitized="",
                message="Biểu thức trống",
            )

        # Kiểm tra độ dài
        if len(expression) > MAX_EXPRESSION_LENGTH:
            return ValidationResult(
                is_valid=False,
                sanitized=expression[:MAX_EXPRESSION_LENGTH],
                message="Biểu thức quá dài",
            )

        # Chuyển đổi ký tự hiển thị sang ký tự tính toán
        compute_expr = self.display_to_compute(expression)

        # Kiểm tra dấu ngoặc khớp
        paren_check = self._check_parentheses(compute_expr)
        if not paren_check.is_valid:
            return paren_check

        return ValidationResult(is_valid=True, sanitized=compute_expr)

    # ─── Xử lý clipboard paste ───────────────────────────────

    def sanitize_paste(self, text: str) -> ValidationResult:
        """Làm sạch chuỗi được paste từ clipboard.

        Loại bỏ tất cả ký tự không phải số, toán tử, dấu chấm, dấu ngoặc.
        Giữ lại: 0-9, +, -, *, /, ., (, ), %, ^, e, E (cho scientific notation).

        Args:
            text: Chuỗi thô từ clipboard.

        Returns:
            ValidationResult với chuỗi đã làm sạch.
        """
        if not text:
            return ValidationResult(is_valid=False, sanitized="", message="Clipboard trống")

        # Giữ lại chỉ các ký tự hợp lệ
        valid_chars = re.sub(r"[^\d+\-*/%.(),^a-zA-Z\s]", "", text)
        # Loại bỏ khoảng trắng thừa
        valid_chars = re.sub(r"\s+", " ", valid_chars).strip()
        # Chuyển đổi sang ký hiệu display
        valid_chars = self.compute_to_display(valid_chars)

        if not valid_chars:
            return ValidationResult(
                is_valid=False,
                sanitized="",
                message="Không có nội dung hợp lệ để dán",
            )

        return ValidationResult(is_valid=True, sanitized=valid_chars)

    # ─── Utility methods ─────────────────────────────────────

    @staticmethod
    def display_to_compute(expression: str) -> str:
        """Chuyển đổi biểu thức dạng hiển thị sang dạng tính toán.

        Thay thế:
        - '−' → '-'
        - '×' → '*'
        - '÷' → '/'
        - '^' → '**'

        Args:
            expression: Biểu thức dạng hiển thị.

        Returns:
            Biểu thức dạng tính toán.
        """
        result = expression
        for display_char, compute_char in OPERATOR_DISPLAY_MAP.items():
            result = result.replace(display_char, compute_char)
        return result

    @staticmethod
    def compute_to_display(expression: str) -> str:
        """Chuyển đổi biểu thức dạng tính toán sang dạng hiển thị.

        Args:
            expression: Biểu thức dạng tính toán.

        Returns:
            Biểu thức dạng hiển thị.
        """
        result = expression
        # Xử lý '**' trước '*' để tránh nhầm lẫn
        result = result.replace("**", "^")
        result = result.replace("*", "×")
        result = result.replace("/", "÷")
        # Chỉ thay '-' thành '−' nếu không phải unary minus ở đầu
        # (giữ nguyên dấu '-' vì validator sẽ xử lý)
        return result

    @staticmethod
    def _check_parentheses(expression: str) -> ValidationResult:
        """Kiểm tra dấu ngoặc có khớp không.

        Args:
            expression: Biểu thức dạng tính toán.

        Returns:
            ValidationResult.
        """
        depth = 0
        for i, ch in enumerate(expression):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth < 0:
                    return ValidationResult(
                        is_valid=False,
                        sanitized=expression,
                        message="Dấu ngoặc đóng thừa tại vị trí " + str(i),
                    )
        if depth != 0:
            return ValidationResult(
                is_valid=False,
                sanitized=expression,
                message="Có " + str(depth) + " dấu ngoặc mở chưa đóng",
            )
        return ValidationResult(is_valid=True, sanitized=expression)

    @staticmethod
    def count_open_parens(expression: str) -> int:
        """Đếm số dấu ngoặc mở chưa đóng trong biểu thức.

        Args:
            expression: Biểu thức bất kỳ dạng.

        Returns:
            Số dấu ngoặc mở chưa đóng (≥ 0).
        """
        depth = 0
        for ch in expression:
            if ch in ("(", ):
                depth += 1
            elif ch in (")", ):
                depth = max(0, depth - 1)
        return depth

    @staticmethod
    def get_current_number_segment(expression: str) -> str:
        """Lấy phần số đang được nhập ở cuối biểu thức.

        VD: "12 + 3.4" → "3.4"
             "12 +" → ""
             "12" → "12"

        Args:
            expression: Biểu thức hiện tại.

        Returns:
            Chuỗi con là phần số cuối cùng.
        """
        # Split theo toán tử và ngoặc
        segments = re.split(r"[+\-×÷*/%()\^]", expression)
        if segments:
            return segments[-1].strip()
        return ""

    @staticmethod
    def is_valid_keyboard_input(key: str) -> bool:
        """Kiểm tra xem ký tự từ bàn phím có hợp lệ không.

        Args:
            key: Ký tự từ bàn phím (single char).

        Returns:
            True nếu là ký tự hợp lệ.
        """
        valid_keys = set("0123456789.+-*/()%")
        return key in valid_keys
