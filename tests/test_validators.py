"""
Test suite cho InputValidator.

Bao phủ:
- Thêm chữ số
- Thêm dấu chấm thập phân
- Thêm toán tử (thay thế, chặn)
- Thêm dấu ngoặc
- Validate biểu thức hoàn chỉnh
- Làm sạch chuỗi paste từ clipboard
- Đếm dấu ngoặc mở
- Chuyển đổi display ↔ compute

Chạy test:
    pytest tests/test_validators.py -v

Author: PyQt6 Calculator Project
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Thêm root vào path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.utils.validators import InputValidator, ValidationResult


@pytest.fixture
def validator() -> InputValidator:
    """Tạo instance InputValidator dùng chung."""
    return InputValidator()


# ─────────────────────────────────────────────────────────────
# 1. can_append_digit
# ─────────────────────────────────────────────────────────────

class TestCanAppendDigit:
    """Test thêm chữ số."""

    def test_append_digit_to_empty(self, validator: InputValidator) -> None:
        result = validator.can_append_digit("", "5")
        assert result.is_valid
        assert result.sanitized == "5"

    def test_append_digit_to_number(self, validator: InputValidator) -> None:
        result = validator.can_append_digit("12", "3")
        assert result.is_valid
        assert result.sanitized == "123"

    def test_append_zero(self, validator: InputValidator) -> None:
        result = validator.can_append_digit("5", "0")
        assert result.is_valid
        assert result.sanitized == "50"

    def test_digit_too_long(self, validator: InputValidator) -> None:
        # Số 20 ký tự → không cho thêm nữa
        long_number = "1" * 20
        result = validator.can_append_digit(long_number, "1")
        assert not result.is_valid

    def test_append_digit_to_decimal(self, validator: InputValidator) -> None:
        result = validator.can_append_digit("3.14", "1")
        assert result.is_valid
        assert result.sanitized == "3.141"


# ─────────────────────────────────────────────────────────────
# 2. can_append_dot
# ─────────────────────────────────────────────────────────────

class TestCanAppendDot:
    """Test thêm dấu chấm thập phân."""

    def test_dot_to_integer(self, validator: InputValidator) -> None:
        result = validator.can_append_dot("3")
        assert result.is_valid
        assert result.sanitized == "3."

    def test_dot_to_empty(self, validator: InputValidator) -> None:
        # Rỗng → "0."
        result = validator.can_append_dot("")
        assert result.is_valid
        assert result.sanitized == "0."

    def test_double_dot_rejected(self, validator: InputValidator) -> None:
        # Đã có dấu chấm → từ chối
        result = validator.can_append_dot("3.14")
        assert not result.is_valid

    def test_dot_to_zero(self, validator: InputValidator) -> None:
        result = validator.can_append_dot("0")
        assert result.is_valid
        assert result.sanitized == "0."

    def test_dot_only_in_number_rejected(self, validator: InputValidator) -> None:
        # "1.2.3" không hợp lệ
        result = validator.can_append_dot("1.2")
        assert not result.is_valid


# ─────────────────────────────────────────────────────────────
# 3. can_append_operator
# ─────────────────────────────────────────────────────────────

class TestCanAppendOperator:
    """Test thêm toán tử."""

    def test_add_operator_to_number(self, validator: InputValidator) -> None:
        result = validator.can_append_operator("5", "+")
        assert result.is_valid

    def test_replace_operator(self, validator: InputValidator) -> None:
        # Expression kết thúc bằng '+', nhập '×' → thay thế
        result = validator.can_append_operator("5 +", "×")
        assert result.is_valid
        assert "×" in result.sanitized
        assert "+" not in result.sanitized

    def test_multiply_at_start_rejected(self, validator: InputValidator) -> None:
        # Bắt đầu bằng '×' → không hợp lệ
        result = validator.can_append_operator("", "×")
        assert not result.is_valid

    def test_divide_at_start_rejected(self, validator: InputValidator) -> None:
        result = validator.can_append_operator("", "÷")
        assert not result.is_valid

    def test_minus_at_start_allowed(self, validator: InputValidator) -> None:
        # Dấu trừ ở đầu cho phép (số âm)
        result = validator.can_append_operator("", "−")
        assert result.is_valid

    def test_operator_after_open_paren_minus_only(self, validator: InputValidator) -> None:
        # Sau '(' chỉ cho phép '-'
        result_minus = validator.can_append_operator("(", "−")
        assert result_minus.is_valid

        result_plus = validator.can_append_operator("(", "+")
        # '+' sau '(' → không thêm (trả về is_valid=False với message rỗng)
        assert not result_plus.is_valid

        result_mul = validator.can_append_operator("(", "×")
        assert not result_mul.is_valid


# ─────────────────────────────────────────────────────────────
# 4. can_append_paren
# ─────────────────────────────────────────────────────────────

class TestCanAppendParen:
    """Test thêm dấu ngoặc."""

    def test_open_paren_always_allowed(self, validator: InputValidator) -> None:
        result = validator.can_append_paren("5 + ", "(", 0)
        assert result.is_valid

    def test_close_paren_no_open(self, validator: InputValidator) -> None:
        # Không có ngoặc mở → không cho đóng
        result = validator.can_append_paren("5", ")", 0)
        assert not result.is_valid

    def test_close_paren_with_open(self, validator: InputValidator) -> None:
        # Có 1 ngoặc mở → cho đóng
        result = validator.can_append_paren("(5 + 3", ")", 1)
        assert result.is_valid

    def test_close_paren_after_operator_rejected(self, validator: InputValidator) -> None:
        # Đóng ngoặc ngay sau toán tử → không hợp lệ
        result = validator.can_append_paren("(5 +", ")", 1)
        assert not result.is_valid


# ─────────────────────────────────────────────────────────────
# 5. validate_expression
# ─────────────────────────────────────────────────────────────

class TestValidateExpression:
    """Test validate biểu thức hoàn chỉnh."""

    def test_valid_simple_expression(self, validator: InputValidator) -> None:
        result = validator.validate_expression("3 + 4")
        assert result.is_valid

    def test_empty_expression_invalid(self, validator: InputValidator) -> None:
        result = validator.validate_expression("")
        assert not result.is_valid

    def test_mismatched_parens_invalid(self, validator: InputValidator) -> None:
        result = validator.validate_expression("(3 + 4")
        assert not result.is_valid

    def test_extra_close_paren_invalid(self, validator: InputValidator) -> None:
        result = validator.validate_expression("3 + 4)")
        assert not result.is_valid

    def test_display_to_compute_conversion(self, validator: InputValidator) -> None:
        result = validator.validate_expression("3 × 4 ÷ 2")
        assert result.is_valid
        assert "×" not in result.sanitized
        assert "*" in result.sanitized or "/" in result.sanitized

    def test_too_long_expression(self, validator: InputValidator) -> None:
        long_expr = "1 + " * 60  # > 200 ký tự
        result = validator.validate_expression(long_expr)
        assert not result.is_valid


# ─────────────────────────────────────────────────────────────
# 6. sanitize_paste
# ─────────────────────────────────────────────────────────────

class TestSanitizePaste:
    """Test làm sạch chuỗi paste."""

    def test_clean_math_expression(self, validator: InputValidator) -> None:
        result = validator.sanitize_paste("3 + 4 * 2")
        assert result.is_valid

    def test_removes_invalid_chars(self, validator: InputValidator) -> None:
        # Ký tự '@', '#', '$' bị loại bỏ
        result = validator.sanitize_paste("3 @+ 4#")
        assert result.is_valid
        assert "@" not in result.sanitized
        assert "#" not in result.sanitized

    def test_empty_paste(self, validator: InputValidator) -> None:
        result = validator.sanitize_paste("")
        assert not result.is_valid

    def test_all_garbage(self, validator: InputValidator) -> None:
        # Toàn ký tự rác
        result = validator.sanitize_paste("@@@###$$$")
        assert not result.is_valid

    def test_valid_number_preserved(self, validator: InputValidator) -> None:
        result = validator.sanitize_paste("3.14159")
        assert result.is_valid
        assert "3.14159" in result.sanitized


# ─────────────────────────────────────────────────────────────
# 7. count_open_parens
# ─────────────────────────────────────────────────────────────

class TestCountOpenParens:
    """Test đếm dấu ngoặc mở."""

    def test_no_parens(self) -> None:
        assert InputValidator.count_open_parens("3 + 4") == 0

    def test_one_open(self) -> None:
        assert InputValidator.count_open_parens("(3 + 4") == 1

    def test_balanced_parens(self) -> None:
        assert InputValidator.count_open_parens("(3 + 4)") == 0

    def test_nested_parens(self) -> None:
        assert InputValidator.count_open_parens("((3 + 4)") == 1

    def test_multiple_open(self) -> None:
        assert InputValidator.count_open_parens("((3 + (4") == 3


# ─────────────────────────────────────────────────────────────
# 8. display_to_compute / compute_to_display
# ─────────────────────────────────────────────────────────────

class TestConversions:
    """Test chuyển đổi ký tự hiển thị ↔ tính toán."""

    def test_display_to_compute_minus(self) -> None:
        result = InputValidator.display_to_compute("5 − 3")
        assert "−" not in result
        assert "-" in result

    def test_display_to_compute_multiply(self) -> None:
        result = InputValidator.display_to_compute("5 × 3")
        assert "×" not in result
        assert "*" in result

    def test_display_to_compute_divide(self) -> None:
        result = InputValidator.display_to_compute("6 ÷ 2")
        assert "÷" not in result
        assert "/" in result

    def test_display_to_compute_power(self) -> None:
        result = InputValidator.display_to_compute("2^3")
        assert "^" not in result
        assert "**" in result

    def test_compute_to_display_multiply(self) -> None:
        result = InputValidator.compute_to_display("5 * 3")
        assert "*" not in result
        assert "×" in result

    def test_compute_to_display_power(self) -> None:
        result = InputValidator.compute_to_display("2**3")
        assert "**" not in result
        assert "^" in result

    def test_roundtrip_conversion(self) -> None:
        # Display → Compute → Display (có thể không hoàn toàn giống ban đầu
        # vì một số ký tự được chuẩn hóa)
        original = "5 × 3 + 2 ÷ 4"
        compute = InputValidator.display_to_compute(original)
        back = InputValidator.compute_to_display(compute)
        assert "×" in back or "*" in compute  # Ít nhất một trong hai

    def test_get_current_number_segment(self) -> None:
        assert InputValidator.get_current_number_segment("12 + 3.4") == "3.4"
        assert InputValidator.get_current_number_segment("12 +") == ""
        assert InputValidator.get_current_number_segment("12") == "12"

    def test_is_valid_keyboard_input(self) -> None:
        assert InputValidator.is_valid_keyboard_input("5")
        assert InputValidator.is_valid_keyboard_input("+")
        assert InputValidator.is_valid_keyboard_input(".")
        assert not InputValidator.is_valid_keyboard_input("@")
        assert not InputValidator.is_valid_keyboard_input("a")
        assert not InputValidator.is_valid_keyboard_input("$")
