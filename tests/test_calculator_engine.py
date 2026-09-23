"""
Test suite cho CalculatorEngine.

Bao phủ:
- Phép tính cơ bản (cộng, trừ, nhân, chia)
- Thứ tự ưu tiên toán tử
- Dấu ngoặc lồng nhau
- Chia cho 0
- Căn bậc hai của số âm
- Số thập phân và số âm
- Giai thừa
- Biểu thức rỗng/không hợp lệ
- Các hàm scientific
- Hằng số (pi, e)
- Kết quả overflow/NaN

Chạy test:
    pytest tests/test_calculator_engine.py -v

Author: PyQt6 Calculator Project
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

# Thêm root vào path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.core.calculator_engine import CalculatorEngine, CalculationResult


@pytest.fixture
def engine() -> CalculatorEngine:
    """Tạo instance CalculatorEngine dùng chung cho các test."""
    return CalculatorEngine()


# ─────────────────────────────────────────────────────────────
# Helper function
# ─────────────────────────────────────────────────────────────

def calc(engine: CalculatorEngine, expr: str) -> CalculationResult:
    """Shorthand để evaluate và trả về kết quả."""
    return engine.evaluate(expr)


def val(engine: CalculatorEngine, expr: str) -> float:
    """Evaluate và trả về giá trị số (float). Assert thành công."""
    result = engine.evaluate(expr)
    assert result.success, f"Expected success but got error: {result.error_message}"
    return result.value  # type: ignore


# ─────────────────────────────────────────────────────────────
# 1. Phép tính cơ bản
# ─────────────────────────────────────────────────────────────

class TestBasicOperations:
    """Test các phép tính cơ bản."""

    def test_addition_simple(self, engine: CalculatorEngine) -> None:
        assert val(engine, "2 + 3") == 5.0

    def test_addition_floats(self, engine: CalculatorEngine) -> None:
        result = val(engine, "0.1 + 0.2")
        # Phải tránh floating point error: 0.30000000000000004
        assert abs(result - 0.3) < 1e-10

    def test_subtraction_simple(self, engine: CalculatorEngine) -> None:
        assert val(engine, "10 - 4") == 6.0

    def test_subtraction_negative_result(self, engine: CalculatorEngine) -> None:
        assert val(engine, "3 - 7") == -4.0

    def test_multiplication_simple(self, engine: CalculatorEngine) -> None:
        assert val(engine, "6 * 7") == 42.0

    def test_multiplication_float(self, engine: CalculatorEngine) -> None:
        result = val(engine, "2.5 * 4")
        assert abs(result - 10.0) < 1e-10

    def test_division_simple(self, engine: CalculatorEngine) -> None:
        assert val(engine, "15 / 3") == 5.0

    def test_division_float_result(self, engine: CalculatorEngine) -> None:
        result = val(engine, "10 / 3")
        assert abs(result - 3.3333333333333335) < 1e-10

    def test_modulo(self, engine: CalculatorEngine) -> None:
        result = val(engine, "17 % 5")
        assert abs(result - 2.0) < 1e-10

    def test_zero_plus_zero(self, engine: CalculatorEngine) -> None:
        assert val(engine, "0 + 0") == 0.0

    def test_large_numbers(self, engine: CalculatorEngine) -> None:
        result = val(engine, "1000000 + 2000000")
        assert result == 3000000.0


# ─────────────────────────────────────────────────────────────
# 2. Thứ tự ưu tiên toán tử
# ─────────────────────────────────────────────────────────────

class TestOperatorPrecedence:
    """Test thứ tự ưu tiên toán tử (nhân/chia trước cộng/trừ)."""

    def test_multiplication_before_addition(self, engine: CalculatorEngine) -> None:
        # 2 + 3 * 4 = 2 + 12 = 14 (KHÔNG phải 5 * 4 = 20)
        assert val(engine, "2 + 3 * 4") == 14.0

    def test_division_before_subtraction(self, engine: CalculatorEngine) -> None:
        # 10 - 6 / 2 = 10 - 3 = 7
        assert val(engine, "10 - 6 / 2") == 7.0

    def test_mixed_operators(self, engine: CalculatorEngine) -> None:
        # 12 + 8 * 2 - 5 / 2 = 12 + 16 - 2.5 = 25.5
        result = val(engine, "12 + 8 * 2 - 5 / 2")
        assert abs(result - 25.5) < 1e-10

    def test_all_operators(self, engine: CalculatorEngine) -> None:
        # 1 + 2 * 3 - 4 / 2 + 5 % 3 = 1 + 6 - 2 + 2 = 7
        result = val(engine, "1 + 2 * 3 - 4 / 2 + 5 % 3")
        assert abs(result - 7.0) < 1e-10

    def test_power_before_multiplication(self, engine: CalculatorEngine) -> None:
        # 2 * 3 ** 2 = 2 * 9 = 18
        result = val(engine, "2 * 3 ** 2")
        assert abs(result - 18.0) < 1e-10

    def test_right_associativity_of_power(self, engine: CalculatorEngine) -> None:
        # 2 ** 3 ** 2 = 2 ** (3 ** 2) = 2 ** 9 = 512 (kết hợp phải)
        result = val(engine, "2 ** 3 ** 2")
        assert abs(result - 512.0) < 1e-10

    def test_chained_operations(self, engine: CalculatorEngine) -> None:
        # Nhiều phép tính liên tiếp
        result = val(engine, "100 / 10 / 2")  # 100/10=10, 10/2=5
        assert abs(result - 5.0) < 1e-10


# ─────────────────────────────────────────────────────────────
# 3. Dấu ngoặc
# ─────────────────────────────────────────────────────────────

class TestParentheses:
    """Test biểu thức có dấu ngoặc."""

    def test_simple_paren(self, engine: CalculatorEngine) -> None:
        # (2 + 3) * 4 = 20 (không phải 14)
        assert val(engine, "(2 + 3) * 4") == 20.0

    def test_nested_paren(self, engine: CalculatorEngine) -> None:
        # ((2 + 3) * (4 - 1)) = (5 * 3) = 15
        result = val(engine, "((2 + 3) * (4 - 1))")
        assert abs(result - 15.0) < 1e-10

    def test_deeply_nested_paren(self, engine: CalculatorEngine) -> None:
        # (((1 + 2) * 3) + 4) = (9 + 4) = 13
        result = val(engine, "(((1 + 2) * 3) + 4)")
        assert abs(result - 13.0) < 1e-10

    def test_paren_overrides_precedence(self, engine: CalculatorEngine) -> None:
        # (5 + 3) / (2 * 2) = 8 / 4 = 2
        result = val(engine, "(5 + 3) / (2 * 2)")
        assert abs(result - 2.0) < 1e-10

    def test_paren_with_negative(self, engine: CalculatorEngine) -> None:
        # 10 * (-3 + 5) = 10 * 2 = 20
        result = val(engine, "10 * (-3 + 5)")
        assert abs(result - 20.0) < 1e-10

    def test_single_number_in_paren(self, engine: CalculatorEngine) -> None:
        # (42) = 42
        result = val(engine, "(42)")
        assert abs(result - 42.0) < 1e-10


# ─────────────────────────────────────────────────────────────
# 4. Lỗi chia cho 0
# ─────────────────────────────────────────────────────────────

class TestDivisionByZero:
    """Test xử lý chia cho 0."""

    def test_divide_by_zero(self, engine: CalculatorEngine) -> None:
        result = calc(engine, "5 / 0")
        assert not result.success
        assert "0" in result.error_message  # type: ignore

    def test_divide_by_zero_in_expression(self, engine: CalculatorEngine) -> None:
        result = calc(engine, "10 + 5 / 0")
        assert not result.success

    def test_modulo_by_zero(self, engine: CalculatorEngine) -> None:
        result = calc(engine, "10 % 0")
        assert not result.success

    def test_zero_power_negative(self, engine: CalculatorEngine) -> None:
        # 0 ** -1 = division by zero
        result = calc(engine, "0 ** -1")
        assert not result.success

    def test_divide_by_very_small_not_zero(self, engine: CalculatorEngine) -> None:
        # 1 / 0.000001 là hợp lệ (không phải chia cho 0)
        result = calc(engine, "1 / 0.000001")
        assert result.success
        assert result.value == pytest.approx(1000000.0)


# ─────────────────────────────────────────────────────────────
# 5. Căn bậc hai
# ─────────────────────────────────────────────────────────────

class TestSquareRoot:
    """Test hàm căn bậc hai."""

    def test_sqrt_positive(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("sqrt", 9.0)
        assert result.success
        assert abs(result.value - 3.0) < 1e-10  # type: ignore

    def test_sqrt_of_two(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("sqrt", 2.0)
        assert result.success
        assert abs(result.value - math.sqrt(2)) < 1e-10  # type: ignore

    def test_sqrt_zero(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("sqrt", 0.0)
        assert result.success
        assert result.value == 0.0  # type: ignore

    def test_sqrt_negative(self, engine: CalculatorEngine) -> None:
        # sqrt(-1) → lỗi
        result = engine.evaluate_single_function("sqrt", -1.0)
        assert not result.success
        assert result.error_message is not None
        assert "âm" in result.error_message or "hợp lệ" in result.error_message

    def test_sqrt_large_number(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("sqrt", 1000000.0)
        assert result.success
        assert abs(result.value - 1000.0) < 1e-10  # type: ignore

    def test_sqrt_in_expression(self, engine: CalculatorEngine) -> None:
        # sqrt(16) + 2 = 6
        result = val(engine, "sqrt(16) + 2")
        assert abs(result - 6.0) < 1e-10


# ─────────────────────────────────────────────────────────────
# 6. Số thập phân
# ─────────────────────────────────────────────────────────────

class TestDecimalNumbers:
    """Test số thập phân."""

    def test_simple_decimal(self, engine: CalculatorEngine) -> None:
        result = val(engine, "3.14 + 0")
        assert abs(result - 3.14) < 1e-10

    def test_decimal_addition(self, engine: CalculatorEngine) -> None:
        result = val(engine, "1.5 + 2.5")
        assert abs(result - 4.0) < 1e-10

    def test_floating_point_precision(self, engine: CalculatorEngine) -> None:
        # Test chống floating point error kinh điển
        result = val(engine, "0.1 + 0.2")
        assert abs(result - 0.3) < 1e-10

    def test_decimal_division(self, engine: CalculatorEngine) -> None:
        result = val(engine, "7.5 / 2.5")
        assert abs(result - 3.0) < 1e-10

    def test_small_decimal(self, engine: CalculatorEngine) -> None:
        result = val(engine, "0.001 + 0.002")
        assert abs(result - 0.003) < 1e-10

    def test_decimal_multiplication(self, engine: CalculatorEngine) -> None:
        result = val(engine, "1.1 * 1.1")
        assert abs(result - 1.21) < 1e-10


# ─────────────────────────────────────────────────────────────
# 7. Số âm
# ─────────────────────────────────────────────────────────────

class TestNegativeNumbers:
    """Test số âm và unary minus."""

    def test_unary_minus(self, engine: CalculatorEngine) -> None:
        result = val(engine, "-5")
        assert result == -5.0

    def test_negative_plus_positive(self, engine: CalculatorEngine) -> None:
        result = val(engine, "-3 + 5")
        assert abs(result - 2.0) < 1e-10

    def test_negative_times_negative(self, engine: CalculatorEngine) -> None:
        result = val(engine, "-4 * -3")
        assert abs(result - 12.0) < 1e-10

    def test_negative_in_paren(self, engine: CalculatorEngine) -> None:
        result = val(engine, "(-3 + 5) * 2")
        assert abs(result - 4.0) < 1e-10

    def test_double_negative(self, engine: CalculatorEngine) -> None:
        # 5 - (-3) = 8
        result = val(engine, "5 - (-3)")
        assert abs(result - 8.0) < 1e-10

    def test_negative_exponent(self, engine: CalculatorEngine) -> None:
        # 2 ** -1 = 0.5
        result = val(engine, "2 ** -1")
        assert abs(result - 0.5) < 1e-10


# ─────────────────────────────────────────────────────────────
# 8. Biểu thức rỗng và không hợp lệ
# ─────────────────────────────────────────────────────────────

class TestInvalidExpressions:
    """Test biểu thức không hợp lệ."""

    def test_empty_expression(self, engine: CalculatorEngine) -> None:
        result = calc(engine, "")
        assert not result.success

    def test_whitespace_only(self, engine: CalculatorEngine) -> None:
        result = calc(engine, "   ")
        assert not result.success

    def test_mismatched_paren_open(self, engine: CalculatorEngine) -> None:
        # Dấu ngoặc mở chưa đóng
        result = calc(engine, "(3 + 4")
        assert not result.success

    def test_mismatched_paren_close(self, engine: CalculatorEngine) -> None:
        # Dấu ngoặc đóng thừa
        result = calc(engine, "3 + 4)")
        assert not result.success

    def test_starts_with_multiply(self, engine: CalculatorEngine) -> None:
        # Bắt đầu bằng toán tử nhân
        result = calc(engine, "* 5")
        assert not result.success

    def test_ends_with_operator(self, engine: CalculatorEngine) -> None:
        # Kết thúc bằng toán tử
        result = calc(engine, "5 +")
        assert not result.success

    def test_consecutive_operators(self, engine: CalculatorEngine) -> None:
        # Hai toán tử liên tiếp (không phải unary)
        result = calc(engine, "5 + * 3")
        assert not result.success

    def test_unknown_function(self, engine: CalculatorEngine) -> None:
        result = calc(engine, "foo(5)")
        assert not result.success

    def test_single_operator(self, engine: CalculatorEngine) -> None:
        result = calc(engine, "+")
        assert not result.success


# ─────────────────────────────────────────────────────────────
# 9. Giai thừa
# ─────────────────────────────────────────────────────────────

class TestFactorial:
    """Test hàm giai thừa."""

    def test_factorial_zero(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("factorial", 0)
        assert result.success
        assert result.value == 1.0  # type: ignore

    def test_factorial_one(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("factorial", 1)
        assert result.success
        assert result.value == 1.0  # type: ignore

    def test_factorial_five(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("factorial", 5)
        assert result.success
        assert result.value == 120.0  # type: ignore

    def test_factorial_ten(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("factorial", 10)
        assert result.success
        assert result.value == 3628800.0  # type: ignore

    def test_factorial_negative(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("factorial", -1)
        assert not result.success
        assert result.error_message is not None

    def test_factorial_decimal(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("factorial", 3.5)
        assert not result.success
        assert result.error_message is not None

    def test_factorial_too_large(self, engine: CalculatorEngine) -> None:
        # factorial(171) vượt giới hạn float64
        result = engine.evaluate_single_function("factorial", 171)
        assert not result.success


# ─────────────────────────────────────────────────────────────
# 10. Scientific Functions
# ─────────────────────────────────────────────────────────────

class TestScientificFunctions:
    """Test các hàm khoa học."""

    def test_sin_zero(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("sin", 0.0)
        assert result.success
        assert abs(result.value - 0.0) < 1e-10  # type: ignore

    def test_sin_90(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("sin", 90.0)
        assert result.success
        assert abs(result.value - 1.0) < 1e-10  # type: ignore

    def test_cos_zero(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("cos", 0.0)
        assert result.success
        assert abs(result.value - 1.0) < 1e-10  # type: ignore

    def test_cos_180(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("cos", 180.0)
        assert result.success
        assert abs(result.value - (-1.0)) < 1e-10  # type: ignore

    def test_tan_45(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("tan", 45.0)
        assert result.success
        assert abs(result.value - 1.0) < 1e-10  # type: ignore

    def test_tan_90_undefined(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("tan", 90.0)
        assert not result.success

    def test_log_10(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("log", 10.0)
        assert result.success
        assert abs(result.value - 1.0) < 1e-10  # type: ignore

    def test_log_negative(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("log", -5.0)
        assert not result.success

    def test_ln_e(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("ln", math.e)
        assert result.success
        assert abs(result.value - 1.0) < 1e-10  # type: ignore

    def test_ln_zero(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("ln", 0.0)
        assert not result.success

    def test_sqr(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("sqr", 7.0)
        assert result.success
        assert abs(result.value - 49.0) < 1e-10  # type: ignore

    def test_inv_nonzero(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("inv", 4.0)
        assert result.success
        assert abs(result.value - 0.25) < 1e-10  # type: ignore

    def test_inv_zero(self, engine: CalculatorEngine) -> None:
        result = engine.evaluate_single_function("inv", 0.0)
        assert not result.success


# ─────────────────────────────────────────────────────────────
# 11. Hằng số
# ─────────────────────────────────────────────────────────────

class TestConstants:
    """Test hằng số pi và e."""

    def test_pi_value(self, engine: CalculatorEngine) -> None:
        result = val(engine, "pi")
        assert abs(result - math.pi) < 1e-10

    def test_e_value(self, engine: CalculatorEngine) -> None:
        result = val(engine, "e")
        assert abs(result - math.e) < 1e-10

    def test_pi_in_expression(self, engine: CalculatorEngine) -> None:
        # 2 * pi ≈ 6.283185...
        result = val(engine, "2 * pi")
        assert abs(result - 2 * math.pi) < 1e-10

    def test_e_squared(self, engine: CalculatorEngine) -> None:
        result = val(engine, "e ** 2")
        assert abs(result - math.e ** 2) < 1e-10


# ─────────────────────────────────────────────────────────────
# 12. Number Formatter
# ─────────────────────────────────────────────────────────────

class TestNumberFormatter:
    """Test hàm format số."""

    def test_integer_formatting(self, engine: CalculatorEngine) -> None:
        display = engine._format_number(1234567.0)
        # Phải có dấu phân cách hàng nghìn
        assert "," in display

    def test_no_trailing_zeros(self, engine: CalculatorEngine) -> None:
        # 3.50 → "3.5" (không phải "3.50")
        display = engine._format_number(3.5)
        assert display == "3.5"

    def test_floating_point_noise_removed(self, engine: CalculatorEngine) -> None:
        # 0.30000000000000004 → "0.3"
        display = engine._format_number(0.30000000000000004)
        assert display == "0.3"

    def test_very_large_number_scientific(self, engine: CalculatorEngine) -> None:
        display = engine._format_number(1.23e16)
        assert "e" in display.lower()

    def test_very_small_number_scientific(self, engine: CalculatorEngine) -> None:
        display = engine._format_number(1.23e-11)
        assert "e" in display.lower()

    def test_zero(self, engine: CalculatorEngine) -> None:
        display = engine._format_number(0.0)
        assert display == "0"

    def test_negative_integer(self, engine: CalculatorEngine) -> None:
        display = engine._format_number(-42.0)
        assert display == "-42"


# ─────────────────────────────────────────────────────────────
# 13. Edge Cases
# ─────────────────────────────────────────────────────────────

class TestEdgeCases:
    """Test các trường hợp đặc biệt."""

    def test_single_number(self, engine: CalculatorEngine) -> None:
        result = val(engine, "42")
        assert result == 42.0

    def test_single_zero(self, engine: CalculatorEngine) -> None:
        result = val(engine, "0")
        assert result == 0.0

    def test_expression_with_spaces(self, engine: CalculatorEngine) -> None:
        result = val(engine, "  5   +   3  ")
        assert result == 8.0

    def test_thousands_separator_ignored(self, engine: CalculatorEngine) -> None:
        # Dấu phẩy phân cách hàng nghìn trong input phải bị bỏ qua
        result = val(engine, "1,234 + 1")
        assert result == 1235.0

    def test_scientific_notation_input(self, engine: CalculatorEngine) -> None:
        # Input dạng khoa học
        result = val(engine, "1.5e3 + 500")
        assert abs(result - 2000.0) < 1e-10

    def test_complex_nested_expression(self, engine: CalculatorEngine) -> None:
        # Biểu thức phức tạp
        result = val(engine, "((3 + 4) * 2) / (5 - 1)")
        assert abs(result - 3.5) < 1e-10

    def test_multiple_operations_chain(self, engine: CalculatorEngine) -> None:
        # Chuỗi phép tính dài
        result = val(engine, "1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 + 10")
        assert abs(result - 55.0) < 1e-10

    def test_power_of_zero(self, engine: CalculatorEngine) -> None:
        # x ** 0 = 1 với mọi x
        result = val(engine, "999 ** 0")
        assert abs(result - 1.0) < 1e-10

    def test_zero_power_positive(self, engine: CalculatorEngine) -> None:
        # 0 ** x = 0 với x > 0
        result = val(engine, "0 ** 5")
        assert abs(result - 0.0) < 1e-10
