import sys

from PyQt6.QtCore import Qt
# from PyQt6.QtGui import *
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    # QToolBar,
    # QStatusBar,
)

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500
SIDEBAR_WIDTH = 200

" use dialog for adding new cards to the deck

class PyCardWindow(QMainWindow):
    """PyCard's main window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyCard")
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.generalLayout = QHBoxLayout()
        centralWidget = QWidget(self)
        centralWidget.setLayout(self.generalLayout)
        self.setCentralWidget(centralWidget)
        self._createSidebar()
        self._createCard()

    def _createSidebar(self):
        self.sidebar = QVBoxLayout()
        self.sidebar.addWidget(QLabel("Sidebar Test"), 0, Qt.AlignmentFlag.AlignCenter)
        self.sidebar.addWidget(QLabel("Sidebar Test 2"), 0, Qt.AlignmentFlag.AlignCenter)
        self.sidebar.addWidget(QLabel("Sidebar Test 3"), 0, Qt.AlignmentFlag.AlignCenter)
        self.generalLayout.addLayout(self.sidebar, 1)

    def _createCard(self):
        self.card = QLabel()
        self.card.setText("Card Test")
        self.card.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.generalLayout.addWidget(self.card, 3)

def main():
    """PyCard's main function"""
    pycardApp = QApplication([])
    pycardWindow = PyCardWindow()
    pycardWindow.show()
    sys.exit(pycardApp.exec())

if __name__ == "__main__":
    main()
