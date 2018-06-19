from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QWidget,
                             QGridLayout, QTextEdit)


class MainWindow(QWidget):
    """
    """
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 200, 200)
        self.show()


if __name__ == '__main__':
    app = QApplication()
    win = MainWindow()
