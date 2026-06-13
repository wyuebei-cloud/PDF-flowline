from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt6.QtCore import Qt

class ValueDialog(QDialog):
    def __init__(self, raw_value: str, parent=None, model_name: str = None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Elevation Value")
        self.setFixedWidth(300)
        
        layout = QVBoxLayout(self)
        
        self.label = QLabel("OCR detected the following value:")
        layout.addWidget(self.label)
        
        self.input_field = QLineEdit(raw_value)
        layout.addWidget(self.input_field)

        if model_name:
            model_label = QLabel(f"Model: {model_name}")
            model_label.setStyleSheet("color: gray; font-size: 10px;")
            layout.addWidget(model_label)
        
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("Confirm")
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)

    def get_value(self):
        try:
            return float(self.input_field.text())
        except ValueError:
            return None
