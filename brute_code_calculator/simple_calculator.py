import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, 
    QLineEdit, QPushButton, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class SimpleCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Máy tính code tay ")
        self.setFixedSize(400, 500)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        self.display = QLineEdit()
        self.display.returnPressed.connect(lambda: self.calculate_result(self.display.text()))
        self.display.textEdited.connect(self.on_text_edited)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setFont(QFont("Arial", 24))
        self.display.setStyleSheet("background-color: #f0f0f0; color: black; padding: 10px; border-radius: 5px;")
        main_layout.addWidget(self.display)
        
        grid_layout = QGridLayout()
        
        buttons = [
            ('C', 0, 0, 1, 2), ('⌫', 0, 2, 1, 2),
            ('1/x', 1, 0), ('√', 1, 1), ('^', 1, 2), ('/', 1, 3),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('*', 2, 3),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('-', 3, 3),
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('+', 4, 3),
            ('%', 5, 0), ('0', 5, 1), ('.', 5, 2), ('=', 5, 3),
        ]
        
        for btn_data in buttons:
            text = btn_data[0]
            btn = QPushButton(text)
            btn.setFont(QFont("Arial", 16))
            btn.setStyleSheet("color: black;")
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setMinimumHeight(60)
            
            if len(btn_data) == 3:
                grid_layout.addWidget(btn, btn_data[1], btn_data[2])
            else:
                grid_layout.addWidget(btn, btn_data[1], btn_data[2], btn_data[3], btn_data[4])
                
            btn.clicked.connect(lambda checked, x=text: self.on_button_click(x))
                
        main_layout.addLayout(grid_layout)

    def on_text_edited(self, text):
        if text.startswith("Lỗi"):
            self.display.setText(getattr(self, 'last_input', ''))

    def on_button_click(self, char):
        current_text = self.display.text()
        
        if current_text.startswith("Lỗi"):
            current_text = getattr(self, 'last_input', '')
            self.display.setText(current_text)

        if char == 'C':
            self.display.clear()
        elif char == '⌫':
            self.display.setText(current_text[:-1])
        elif char == '=':
            self.calculate_result(current_text)
        elif char == '1/x':
            self.display.setText(current_text + '1/')
        elif char == '√':
            self.display.setText(current_text + 'sqrt(')
        else:
            self.display.setText(current_text + char)

    def calculate_result(self, expression):
        if not expression or expression.startswith("Lỗi"):
            return

        safe_expression = expression.replace('^', '**')
        
        open_brackets = safe_expression.count('(')
        close_brackets = safe_expression.count(')')
        if open_brackets > close_brackets:
            safe_expression += ')' * (open_brackets - close_brackets)

        try:
            allowed_names = {
                "__builtins__": None, 
                "sqrt": math.sqrt
            }
            
            result = eval(safe_expression, allowed_names)
            
            self.display.setText(self.format_result(result))
            
        except ZeroDivisionError:
            self.show_error("Lỗi tính toán: Không thể chia cho 0!")
        except ValueError:
            self.show_error("Lỗi tính toán: Phép tính không hợp lệ (Ví dụ: căn bậc số âm)!")
        except SyntaxError:
            self.show_error("Lỗi Input: Sai cú pháp biểu thức!")
        except TypeError:
            self.show_error("Lỗi Input: Dữ liệu nhập sai kiểu!")
        except NameError:
            self.show_error("Lỗi Input: Có chứa ký tự chữ cái không hợp lệ từ bàn phím!")
        except Exception as e:
            self.show_error(f"Lỗi không xác định: {str(e)}")

    def format_result(self, number):
        if number == 0:
            return "0"
            
        abs_num = abs(number)
        
        if abs_num >= 1e16 or abs_num < 1e-15:
            formatted = f"{number:.15e}"
            mantissa, exponent = formatted.split('e')
            
            if '.' in mantissa:
                mantissa = mantissa.rstrip('0').rstrip('.')
                
            exp_sign = exponent[0]
            exp_val = str(int(exponent[1:]))
            
            return f"{mantissa}e{exp_sign}{exp_val}"
        else:
            if isinstance(number, float) and number.is_integer():
                return str(int(number))
                
            formatted = f"{number:.15f}"
            if '.' in formatted:
                formatted = formatted.rstrip('0').rstrip('.')
                
            if not formatted:
                return "0"
            return formatted
            
    def show_error(self, message):
        self.last_input = self.display.text()
        self.display.setText(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleCalculator()
    window.show()
    sys.exit(app.exec())
