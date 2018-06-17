from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QWidget,
                             QGridLayout, QTextEdit)

class MainWindow(QWidget):
    """
    """
    def __init__(self):
        super().__init__()

if __name__ == '__main__':
    app = QApplication()
    win = MainWindow()
    
