# File: SimpleTest.py
# Path: OllamaModelEditor/SimpleTest.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-11
# Description: Simple test application to verify PySide6 is working

import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

try:
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
    from PySide6.QtCore import Qt
    print("PySide6 imported successfully")
except ImportError as e:
    print(f"Error importing PySide6: {e}")
    sys.exit(1)

class SimpleTestWindow(QWidget):
    """Simple window to test PySide6 functionality."""
    
    def __init__(self):
        """Initialize the test window."""
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("OllamaModelEditor - PySide6 Test")
        self.setGeometry(100, 100, 400, 300)
        
        # Create layout
        Layout = QVBoxLayout()
        self.setLayout(Layout)
        
        # Add widgets
        HeaderLabel = QLabel("PySide6 Test Application")
        HeaderLabel.setAlignment(Qt.AlignCenter)
        HeaderLabel.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        Layout.addWidget(HeaderLabel)
        
        SuccessLabel = QLabel("If you can see this window, PySide6 is working correctly!")
        SuccessLabel.setAlignment(Qt.AlignCenter)
        SuccessLabel.setStyleSheet("font-size: 14px; color: green;")
        Layout.addWidget(SuccessLabel)
        
        InfoLabel = QLabel(f"Python version: {sys.version}")
        InfoLabel.setAlignment(Qt.AlignCenter)
        Layout.addWidget(InfoLabel)
        
        # Add close button
        CloseButton = QPushButton("Close")
        CloseButton.clicked.connect(self.close)
        Layout.addWidget(CloseButton)

if __name__ == "__main__":
    print("Starting PySide6 test application...")
    
    # Create application
    App = QApplication(sys.argv)
    
    # Create and show window
    Window = SimpleTestWindow()
    Window.show()
    
    # Start event loop
    sys.exit(App.exec())
