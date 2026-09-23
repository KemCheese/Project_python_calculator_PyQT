"""
Calculator Engine - Bộ tính toán lõi của ứng dụng.

Sử dụng thuật toán Shunting-Yard (Edsger Dijkstra) để chuyển đổi biểu thức
infix sang Reverse Polish Notation (RPN), sau đó evaluate bằng stack.

Lý do KHÔNG dùng eval() trực tiếp:
  - eval() thực thi bất kỳ Python code nào → rủi ro bảo mật nghiêm trọng
    (VD: người dùng nhập "__import__('os').system('rm -rf /')" sẽ bị execute)
  - Thay vào đó, chúng ta parse biểu thức thành token, validate từng token,
    rồi evaluate theo quy tắc toán học - hoàn toàn an toàn.

Luồng xử lý:
  Input string → tokenize() → shunting_yard() → evaluate_rpn() → kết quả

Author: PyQt6 Calculator Project
Python: 3.10+
"""

from __future__ import annotations

import math
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Union

# Cấu hình logger để dev có thể xem lỗi chi tiết trên console
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Data Classes & Enums
# ─────────────────────────────────────────────────────────────

class TokenType(Enum):
    """Loại token trong biểu thức toán học."""
    NUMBER = auto()
    OPERATOR = auto()
    FUNCTION = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()


@dataclass
class Token:
    """Đại diện cho một token trong biểu thức."""
    type: TokenType
    value: str

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r})"


@dataclass
class CalculationResult:
    """Kết quả trả về từ CalculatorEngine.

    Attributes:
        success: True nếu tính toán thành công.
        value: Giá trị số kết quả (None nếu có lỗi).
        display_value: Chuỗi hiển thị kết quả (đã được format).
        error_message: Thông báo lỗi thân thiện (None nếu thành công).
        expression: Biểu thức đã tính.
    """
    success: bool
    value: float | None
    display_value: str
    error_message: str | None
    expression: str = ""


class CalculationError(Exception):
    """Custom exception cho các lỗi tính toán.

    Attributes:
        message: Thông báo lỗi thân thiện cho người dùng.
        detail: Chi tiết kỹ thuật cho developer (ghi vào log).
    """
    def __init__(self, message: str, detail: str = ""):
        super().__init__(message)
        self.message = message
        self.detail = detail or message


# ─────────────────────────────────────────────────────────────
# Operator Definitions
# ─────────────────────────────────────────────────────────────

# Định nghĩa ưu tiên và tính kết hợp của từng toán tử.
# precedence: số càng cao → ưu tiên càng cao (tính trước)
# right_assoc: True nếu kết hợp phải (VD: 2^3^4 = 2^(3^4))
OPERATOR_PROPS: dict[str, dict] = {
    "+":  {"precedence": 1, "right_assoc": False, "args": 2},
    "-":  {"precedence": 1, "right_assoc": False, "args": 2},
    "*":  {"precedence": 2, "right_assoc": False, "args": 2},
    "/":  {"precedence": 2, "right_assoc": False, "args": 2},
    "%":  {"precedence": 2, "right_assoc": False, "args": 2},
    "**": {"precedence": 3, "right_assoc": True,  "args": 2},
    "~":  {"precedence": 4, "right_assoc": True,  "args": 1},  # unary minus
}

# Danh sách tên hàm được hỗ trợ (luôn nhận 1 argument sau dấu ngoặc)
SUPPORTED_FUNCTIONS: set[str] = {
    "sqrt", "sin", "cos", "tan", "log", "ln",
    "abs", "factorial", "inv", "sqr",
    "asin", "acos", "atan",
    "sinh", "cosh", "tanh",
    "ceil", "floor",
}

# Hằng số được hỗ trợ
SUPPORTED_CONSTANTS: dict[str, float] = {
    "pi": math.pi,
    "e": math.e,
}


# ─────────────────────────────────────────────────────────────
# CalculatorEngine
# ─────────────────────────────────────────────────────────────

class CalculatorEngine:
    """Bộ máy tính toán sử dụng thuật toán Shunting-Yard.

    Không dùng eval() để đảm bảo an toàn. Thay vào đó:
    1. Tokenize biểu thức thành danh sách Token
    2. Shunting-Yard: chuyển infix → RPN (Reverse Polish Notation)
    3. Evaluate RPN bằng stack

    Example::

        engine = CalculatorEngine()
        result = engine.evaluate("12 + 8 * 2 - 5 / 2")
        print(result.display_value)  # "25.5"
    """

    # Số chữ số thập phân tối đa khi hiển thị
    MAX_DECIMAL_DIGITS: int = 12
    # Ngưỡng chuyển sang ký hiệu khoa học
    SCIENTIFIC_THRESHOLD_HIGH: float = 1e15
    SCIENTIFIC_THRESHOLD_LOW: float = 1e-10

    def evaluate(self, expression: str) -> CalculationResult:
        """Evaluate một biểu thức toán học.

        Args:
            expression: Chuỗi biểu thức toán học (VD: "12 + 8 * 2").

        Returns:
            CalculationResult với kết quả hoặc thông báo lỗi.
        """
        expr = expression.strip()
        if not expr:
            return CalculationResult(
                success=False,
                value=None,
                display_value="0",
                error_message="Biểu thức trống",
                expression=expression,
            )

        try:
            # Bước 1: Tokenize
            tokens = self._tokenize(expr)
            logger.debug("Tokens: %s", tokens)

            # Bước 2: Validate tokens
            self._validate_tokens(tokens)

            # Bước 3: Shunting-Yard → RPN
            rpn = self._shunting_yard(tokens)
            logger.debug("RPN: %s", [t.value for t in rpn])

            # Bước 4: Evaluate RPN
            raw_value = self._evaluate_rpn(rpn)
            logger.debug("Raw result: %s", raw_value)

            # Bước 5: Kiểm tra kết quả đặc biệt
            if math.isnan(raw_value):
                raise CalculationError(
                    "Lỗi: Kết quả không xác định",
                    "Result is NaN"
                )
            if math.isinf(raw_value):
                if raw_value > 0:
                    raise CalculationError(
                        "Lỗi: Kết quả quá lớn",
                        "Result is +Infinity"
                    )
                else:
                    raise CalculationError(
                        "Lỗi: Kết quả quá nhỏ",
                        "Result is -Infinity"
                    )

            # Bước 6: Format kết quả để hiển thị
            display = self._format_number(raw_value)

            return CalculationResult(
                success=True,
                value=raw_value,
                display_value=display,
                error_message=None,
                expression=expression,
            )

        except CalculationError as exc:
            logger.warning("Calculation error: %s | Detail: %s", exc.message, exc.detail)
            return CalculationResult(
                success=False,
                value=None,
                display_value=exc.message,
                error_message=exc.message,
                expression=expression,
            )
        except OverflowError as exc:
            logger.error("Overflow error: %s", exc)
            return CalculationResult(
                success=False,
                value=None,
                display_value="Lỗi: Kết quả quá lớn",
                error_message="Lỗi: Kết quả quá lớn",
                expression=expression,
            )
        except RecursionError as exc:
            logger.error("Recursion error: %s", exc)
            return CalculationResult(
                success=False,
                value=None,
                display_value="Lỗi: Biểu thức quá phức tạp",
                error_message="Lỗi: Biểu thức quá phức tạp",
                expression=expression,
            )

    def evaluate_single_function(
        self, func_name: str, value: float
    ) -> CalculationResult:
        """Tính toán một hàm đơn lẻ (VD: sqrt, sqr, factorial).

        Args:
            func_name: Tên hàm (sqrt, sqr, factorial, inv, ...).
            value: Giá trị đầu vào.

        Returns:
            CalculationResult với kết quả.
        """
        expression = f"{func_name}({value})"
        try:
            result = self._apply_function(func_name, value)
            display = self._format_number(result)
            return CalculationResult(
                success=True,
                value=result,
                display_value=display,
                error_message=None,
                expression=expression,
            )
        except CalculationError as exc:
            logger.warning("Function error: %s", exc.message)
            return CalculationResult(
                success=False,
                value=None,
                display_value=exc.message,
                error_message=exc.message,
                expression=expression,
            )
        except OverflowError:
            return CalculationResult(
                success=False,
                value=None,
                display_value="Lỗi: Kết quả quá lớn",
                error_message="Lỗi: Kết quả quá lớn",
                expression=expression,
            )

    # ─── Tokenizer ───────────────────────────────────────────

    def _tokenize(self, expression: str) -> list[Token]:
        """Tách biểu thức thành danh sách Token.

        Hỗ trợ:
        - Số nguyên và thập phân (VD: 3.14, 1000)
        - Toán tử: +, -, *, /, **, %, ~
        - Hàm: sqrt, sin, cos, ...
        - Hằng số: pi, e
        - Dấu ngoặc: (, )

        Args:
            expression: Chuỗi biểu thức cần tokenize.

        Returns:
            Danh sách Token theo thứ tự.

        Raises:
            CalculationError: Nếu gặp ký tự không hợp lệ.
        """
        tokens: list[Token] = []
        i = 0
        n = len(expression)

        # Loại bỏ dấu phân cách hàng nghìn (dấu phẩy) và khoảng trắng
        # Lưu ý: chỉ loại bỏ dấu phẩy dạng thousands separator, không phải
        # dấu chấm thập phân. Chúng ta chuẩn hóa về dạng không có dấu phẩy
        # trước khi parse để tránh nhầm lẫn.
        expression_clean = expression.replace(",", "")
        i = 0
        n = len(expression_clean)

        while i < n:
            ch = expression_clean[i]

            # Bỏ qua khoảng trắng
            if ch.isspace():
                i += 1
                continue

            # ── Số (integer hoặc float) ──
            if ch.isdigit() or (ch == "." and i + 1 < n and expression_clean[i + 1].isdigit()):
                j = i
                has_dot = False
                while j < n and (expression_clean[j].isdigit() or
                                  (expression_clean[j] == "." and not has_dot)):
                    if expression_clean[j] == ".":
                        has_dot = True
                    j += 1
                # Hỗ trợ ký hiệu khoa học: 1.5e+10, 2e-3
                if j < n and expression_clean[j] in ("e", "E"):
                    j += 1
                    if j < n and expression_clean[j] in ("+", "-"):
                        j += 1
                    while j < n and expression_clean[j].isdigit():
                        j += 1
                num_str = expression_clean[i:j]
                tokens.append(Token(TokenType.NUMBER, num_str))
                i = j
                continue

            # ── Toán tử ** (lũy thừa phải đứng trước *) ──
            if ch == "*" and i + 1 < n and expression_clean[i + 1] == "*":
                tokens.append(Token(TokenType.OPERATOR, "**"))
                i += 2
                continue

            # ── Toán tử đơn lẻ ──
            if ch in ("+", "-", "*", "/", "%"):
                # Xác định unary minus: nếu là '-' ở đầu hoặc sau toán tử/ngoặc mở
                if ch == "-" and (
                    not tokens
                    or tokens[-1].type == TokenType.OPERATOR
                    or tokens[-1].type == TokenType.FUNCTION
                    or (tokens[-1].type == TokenType.LEFT_PAREN)
                ):
                    tokens.append(Token(TokenType.OPERATOR, "~"))  # unary minus
                else:
                    tokens.append(Token(TokenType.OPERATOR, ch))
                i += 1
                continue

            # ── Dấu ngoặc ──
            if ch == "(":
                tokens.append(Token(TokenType.LEFT_PAREN, "("))
                i += 1
                continue
            if ch == ")":
                tokens.append(Token(TokenType.RIGHT_PAREN, ")"))
                i += 1
                continue

            # ── Tên hàm hoặc hằng số (chỉ chứa chữ cái) ──
            if ch.isalpha() or ch == "_":
                j = i
                while j < n and (expression_clean[j].isalnum() or expression_clean[j] == "_"):
                    j += 1
                name = expression_clean[i:j]

                # Kiểm tra xem có phải hằng số không
                if name in SUPPORTED_CONSTANTS:
                    tokens.append(Token(TokenType.NUMBER, str(SUPPORTED_CONSTANTS[name])))
                elif name in SUPPORTED_FUNCTIONS:
                    tokens.append(Token(TokenType.FUNCTION, name))
                else:
                    raise CalculationError(
                        f"Lỗi: Biểu thức không hợp lệ",
                        f"Unknown identifier: {name!r}"
                    )
                i = j
                continue

            # ── Ký tự không hợp lệ ──
            raise CalculationError(
                "Lỗi: Biểu thức không hợp lệ",
                f"Unexpected character: {ch!r} at position {i}"
            )

        return tokens

    # ─── Validator ───────────────────────────────────────────

    def _validate_tokens(self, tokens: list[Token]) -> None:
        """Kiểm tra tính hợp lệ của danh sách token.

        Kiểm tra:
        - Dấu ngoặc phải khớp và đúng thứ tự
        - Không có hai toán tử nhị phân liên tiếp
        - Biểu thức không rỗng

        Args:
            tokens: Danh sách token cần validate.

        Raises:
            CalculationError: Nếu biểu thức không hợp lệ.
        """
        if not tokens:
            raise CalculationError("Lỗi: Biểu thức trống")

        # Đếm dấu ngoặc
        paren_depth = 0
        for tok in tokens:
            if tok.type == TokenType.LEFT_PAREN:
                paren_depth += 1
            elif tok.type == TokenType.RIGHT_PAREN:
                paren_depth -= 1
                if paren_depth < 0:
                    raise CalculationError(
                        "Lỗi: Biểu thức không hợp lệ",
                        "Unexpected closing parenthesis"
                    )
        if paren_depth != 0:
            raise CalculationError(
                "Lỗi: Biểu thức không hợp lệ",
                f"Unclosed parentheses: {paren_depth} not closed"
            )

        # Kiểm tra cuối biểu thức không phải toán tử nhị phân
        last = tokens[-1]
        if last.type == TokenType.OPERATOR and last.value != "~":
            if OPERATOR_PROPS.get(last.value, {}).get("args", 2) == 2:
                raise CalculationError(
                    "Lỗi: Biểu thức không hợp lệ",
                    f"Expression ends with operator: {last.value!r}"
                )

        # Kiểm tra bắt đầu bằng toán tử nhị phân (ngoại trừ unary minus)
        first = tokens[0]
        if (first.type == TokenType.OPERATOR
                and first.value not in ("~",)
                and OPERATOR_PROPS.get(first.value, {}).get("args", 2) == 2):
            raise CalculationError(
                "Lỗi: Không thể bắt đầu bằng toán tử",
                f"Expression starts with binary operator: {first.value!r}"
            )

    # ─── Shunting-Yard Algorithm ─────────────────────────────

    def _shunting_yard(self, tokens: list[Token]) -> list[Token]:
        """Chuyển đổi infix sang RPN bằng thuật toán Shunting-Yard.

        Thuật toán của Edsger Dijkstra (1961) - O(n) time/space.
        Xử lý: số, toán tử nhị phân, toán tử đơn, hàm, dấu ngoặc.

        Args:
            tokens: Danh sách token theo thứ tự infix.

        Returns:
            Danh sách token theo thứ tự RPN (postfix).

        Raises:
            CalculationError: Nếu biểu thức không hợp lệ.
        """
        output: list[Token] = []   # Output queue (kết quả RPN)
        op_stack: list[Token] = []  # Operator stack

        for token in tokens:
            if token.type == TokenType.NUMBER:
                # Số luôn đẩy thẳng vào output
                output.append(token)

            elif token.type == TokenType.FUNCTION:
                # Hàm luôn đẩy lên stack, chờ dấu ngoặc
                op_stack.append(token)

            elif token.type == TokenType.OPERATOR:
                op = token.value
                props = OPERATOR_PROPS[op]

                # Pop toán tử có ưu tiên cao hơn hoặc bằng (nếu kết hợp trái)
                while op_stack:
                    top = op_stack[-1]
                    if top.type == TokenType.LEFT_PAREN:
                        break
                    top_is_op = top.type in (TokenType.OPERATOR, TokenType.FUNCTION)
                    if not top_is_op:
                        break

                    top_precedence = OPERATOR_PROPS.get(top.value, {}).get("precedence", 10)
                    cur_precedence = props["precedence"]

                    if top_precedence > cur_precedence or (
                        top_precedence == cur_precedence and not props["right_assoc"]
                    ):
                        output.append(op_stack.pop())
                    else:
                        break

                op_stack.append(token)

            elif token.type == TokenType.LEFT_PAREN:
                op_stack.append(token)

            elif token.type == TokenType.RIGHT_PAREN:
                # Pop cho đến khi gặp dấu ngoặc mở tương ứng
                found_left = False
                while op_stack:
                    top = op_stack.pop()
                    if top.type == TokenType.LEFT_PAREN:
                        found_left = True
                        break
                    output.append(top)

                if not found_left:
                    raise CalculationError(
                        "Lỗi: Biểu thức không hợp lệ",
                        "Mismatched parentheses (extra closing paren)"
                    )

                # Nếu trên đỉnh stack là hàm → pop luôn
                if op_stack and op_stack[-1].type == TokenType.FUNCTION:
                    output.append(op_stack.pop())

        # Pop tất cả toán tử còn lại
        while op_stack:
            top = op_stack.pop()
            if top.type == TokenType.LEFT_PAREN:
                raise CalculationError(
                    "Lỗi: Biểu thức không hợp lệ",
                    "Mismatched parentheses (unclosed)"
                )
            output.append(top)

        return output

    # ─── RPN Evaluator ───────────────────────────────────────

    def _evaluate_rpn(self, rpn: list[Token]) -> float:
        """Tính giá trị của biểu thức đã ở dạng RPN.

        Args:
            rpn: Danh sách token theo thứ tự postfix (RPN).

        Returns:
            Giá trị số kết quả.

        Raises:
            CalculationError: Nếu tính toán gặp lỗi (chia 0, ...).
        """
        stack: list[float] = []

        for token in rpn:
            if token.type == TokenType.NUMBER:
                try:
                    stack.append(float(token.value))
                except ValueError as exc:
                    raise CalculationError(
                        "Lỗi: Số không hợp lệ",
                        f"Cannot parse number: {token.value!r}"
                    ) from exc

            elif token.type == TokenType.OPERATOR:
                op = token.value
                props = OPERATOR_PROPS[op]

                if props["args"] == 1:
                    # Toán tử đơn (unary minus ~)
                    if not stack:
                        raise CalculationError(
                            "Lỗi: Biểu thức không hợp lệ",
                            "Not enough operands for unary operator"
                        )
                    a = stack.pop()
                    if op == "~":
                        stack.append(-a)
                    else:
                        raise CalculationError(
                            "Lỗi: Toán tử không xác định",
                            f"Unknown unary operator: {op!r}"
                        )

                else:
                    # Toán tử nhị phân
                    if len(stack) < 2:
                        raise CalculationError(
                            "Lỗi: Biểu thức không hợp lệ",
                            "Not enough operands for binary operator"
                        )
                    b = stack.pop()
                    a = stack.pop()
                    result = self._apply_binary_op(op, a, b)
                    stack.append(result)

            elif token.type == TokenType.FUNCTION:
                if not stack:
                    raise CalculationError(
                        "Lỗi: Biểu thức không hợp lệ",
                        f"No argument for function {token.value!r}"
                    )
                a = stack.pop()
                result = self._apply_function(token.value, a)
                stack.append(result)

        if len(stack) != 1:
            raise CalculationError(
                "Lỗi: Biểu thức không hợp lệ",
                f"RPN evaluation left {len(stack)} values on stack (expected 1)"
            )

        return stack[0]

    # ─── Binary Operator Evaluation ──────────────────────────

    def _apply_binary_op(self, op: str, a: float, b: float) -> float:
        """Áp dụng toán tử nhị phân lên hai số.

        Args:
            op: Ký hiệu toán tử.
            a: Toán hạng bên trái.
            b: Toán hạng bên phải.

        Returns:
            Kết quả phép tính.

        Raises:
            CalculationError: Cho các trường hợp đặc biệt (chia 0, ...).
        """
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            if b == 0:
                raise CalculationError(
                    "Lỗi: Không thể chia cho 0",
                    f"Division by zero: {a} / {b}"
                )
            return a / b
        if op == "%":
            if b == 0:
                raise CalculationError(
                    "Lỗi: Không thể chia cho 0 (modulo)",
                    f"Modulo by zero: {a} % {b}"
                )
            return math.fmod(a, b)
        if op == "**":
            # Kiểm tra các trường hợp đặc biệt của lũy thừa
            if a == 0 and b < 0:
                raise CalculationError(
                    "Lỗi: Không thể chia cho 0",
                    f"0 raised to negative power: {a}^{b}"
                )
            try:
                result = a ** b
            except (ValueError, ZeroDivisionError) as exc:
                raise CalculationError(
                    "Lỗi: Phép tính không hợp lệ",
                    f"Power error: {a}^{b}: {exc}"
                ) from exc

            if isinstance(result, complex):
                raise CalculationError(
                    "Lỗi: Kết quả phức số không được hỗ trợ",
                    f"Complex result for {a}^{b}"
                )
            return float(result)

        raise CalculationError(
            "Lỗi: Toán tử không xác định",
            f"Unknown binary operator: {op!r}"
        )

    # ─── Function Evaluation ─────────────────────────────────

    def _apply_function(self, func: str, x: float) -> float:
        """Áp dụng hàm toán học lên một số.

        Args:
            func: Tên hàm (sqrt, sin, cos, ...).
            x: Đối số của hàm.

        Returns:
            Kết quả của hàm.

        Raises:
            CalculationError: Nếu đối số không hợp lệ cho hàm đó.
        """
        if func == "sqrt":
            if x < 0:
                raise CalculationError(
                    "Lỗi: Không thể căn bậc hai của số âm",
                    f"sqrt of negative: {x}"
                )
            return math.sqrt(x)

        if func == "sqr":
            # Bình phương
            return x * x

        if func == "inv":
            # Nghịch đảo 1/x
            if x == 0:
                raise CalculationError(
                    "Lỗi: Không thể chia cho 0",
                    "inv(0): division by zero"
                )
            return 1.0 / x

        if func == "factorial":
            if x < 0:
                raise CalculationError(
                    "Lỗi: Giai thừa không xác định với số âm",
                    f"factorial of negative: {x}"
                )
            if x != int(x):
                raise CalculationError(
                    "Lỗi: Giai thừa chỉ áp dụng cho số nguyên",
                    f"factorial of non-integer: {x}"
                )
            n = int(x)
            if n > 170:
                raise CalculationError(
                    "Lỗi: Kết quả quá lớn",
                    f"factorial({n}) would overflow float64"
                )
            return float(math.factorial(n))

        if func == "abs":
            return abs(x)

        if func == "sin":
            return math.sin(math.radians(x))  # Nhận degree, không phải radian

        if func == "cos":
            return math.cos(math.radians(x))

        if func == "tan":
            # tan(90) và tan(270) không xác định
            deg_mod = x % 360
            if abs(deg_mod - 90) < 1e-10 or abs(deg_mod - 270) < 1e-10:
                raise CalculationError(
                    "Lỗi: tan không xác định tại góc này",
                    f"tan({x}°) is undefined"
                )
            return math.tan(math.radians(x))

        if func == "asin":
            if not -1 <= x <= 1:
                raise CalculationError(
                    "Lỗi: arcsin chỉ nhận giá trị trong [-1, 1]",
                    f"asin({x}) out of range"
                )
            return math.degrees(math.asin(x))

        if func == "acos":
            if not -1 <= x <= 1:
                raise CalculationError(
                    "Lỗi: arccos chỉ nhận giá trị trong [-1, 1]",
                    f"acos({x}) out of range"
                )
            return math.degrees(math.acos(x))

        if func == "atan":
            return math.degrees(math.atan(x))

        if func == "sinh":
            return math.sinh(x)

        if func == "cosh":
            return math.cosh(x)

        if func == "tanh":
            return math.tanh(x)

        if func == "log":
            if x <= 0:
                raise CalculationError(
                    "Lỗi: log chỉ xác định với số dương",
                    f"log({x}) is undefined"
                )
            return math.log10(x)

        if func == "ln":
            if x <= 0:
                raise CalculationError(
                    "Lỗi: ln chỉ xác định với số dương",
                    f"ln({x}) is undefined"
                )
            return math.log(x)

        if func == "ceil":
            return float(math.ceil(x))

        if func == "floor":
            return float(math.floor(x))

        raise CalculationError(
            "Lỗi: Hàm không xác định",
            f"Unknown function: {func!r}"
        )

    # ─── Number Formatter ────────────────────────────────────

    def _format_number(self, value: float) -> str:
        """Format số để hiển thị trên màn hình máy tính.

        Quy tắc:
        1. Nếu là số nguyên → hiển thị không có phần thập phân
        2. Nếu có phần thập phân → tối đa MAX_DECIMAL_DIGITS chữ số
        3. Số quá lớn/nhỏ → ký hiệu khoa học
        4. Có dấu phân cách hàng nghìn

        Args:
            value: Giá trị số cần format.

        Returns:
            Chuỗi hiển thị đã được format.
        """
        # Xử lý số nguyên (hoặc gần nguyên do floating point error)
        # Dùng round() để tránh hiển thị 0.9999999999999 thay vì 1
        if abs(value) >= self.SCIENTIFIC_THRESHOLD_HIGH:
            # Ký hiệu khoa học cho số rất lớn
            return f"{value:.6e}"

        if abs(value) < self.SCIENTIFIC_THRESHOLD_LOW and value != 0:
            # Ký hiệu khoa học cho số rất nhỏ
            return f"{value:.6e}"

        # Làm tròn để loại bỏ floating point noise
        # VD: 0.1 + 0.2 = 0.30000000000000004 → round → 0.3
        rounded = round(value, self.MAX_DECIMAL_DIGITS)

        if rounded == int(rounded) and abs(rounded) < self.SCIENTIFIC_THRESHOLD_HIGH:
            # Số nguyên: hiển thị có dấu phẩy hàng nghìn
            int_val = int(rounded)
            return f"{int_val:,}"

        # Số thập phân: loại bỏ trailing zeros
        # Định dạng tối đa MAX_DECIMAL_DIGITS chữ số thập phân
        formatted = f"{rounded:.{self.MAX_DECIMAL_DIGITS}f}"
        # Loại bỏ trailing zeros
        formatted = formatted.rstrip("0").rstrip(".")

        # Thêm dấu phân cách hàng nghìn cho phần nguyên
        if "." in formatted:
            int_part, dec_part = formatted.split(".")
            # Xử lý dấu âm
            if int_part.startswith("-"):
                int_part = "-" + f"{int(int_part):,}".replace("-", "")
            else:
                try:
                    int_part = f"{int(int_part):,}"
                except ValueError:
                    pass
            return f"{int_part}.{dec_part}"

        try:
            return f"{int(formatted):,}"
        except ValueError:
            return formatted

    @staticmethod
    def format_number_static(value: float) -> str:
        """Static version của _format_number để dùng từ ngoài class."""
        engine = CalculatorEngine()
        return engine._format_number(value)
