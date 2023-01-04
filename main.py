import os
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
    QComboBox,
    QFrame,
)

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500
DECK_DIRECTORY = "./decks/"

class Flashcard:
    # " needs to have a Q/A
    # " keep track of last time reviewed
    def __init__(self, question, answer, last_review):
        self.question = question
        self.answer = answer
        self.last_review = last_review

# class FlashcardDeck(deck_name):
    # def __init__(self):
        # " initialize deck or create new if doesn't exist

    # def load_flashcards(self):
        # " read deck file

    # def save_flashcards(self):
        # " write deck to file

    # def add_flashcard(self, flashcard):
        # " add flashcard to deck

    # def get_next_flashcard(self):
        # " return a pending flashcard

class FlashcardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # initial state of the gui
        # have prompt for choosing a deck or creating a new one
        # when deck is chosen, initialize deck object
        #   display total cards & number pending
        # button for closing
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.generalLayout = QHBoxLayout()
        centralWidget = QWidget(self)
        centralWidget.setLayout(self.generalLayout)
        self.setCentralWidget(centralWidget)
        self.init_sidebar()
        self.init_body()

    def init_sidebar(self):
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setFrameStyle(1)
        self.sidebar_frame.setLineWidth(1)

        self.sidebar = QVBoxLayout()

        self.deck_selector = QComboBox(self)
        self.decks = self.detect_existing_decks()
        self.deck_selector.addItems(["Choose a deck..."] + self.decks + ["Create new deck"])
        self.sidebar.addWidget(self.deck_selector)

        # add a spacer
        self.sidebar.addStretch()

        self.sidebar_frame.setLayout(self.sidebar)
        self.generalLayout.addWidget(self.sidebar_frame, 2)

    def init_body(self):
        self.body = QLabel()
        self.body.setText("Welcome!")
        self.body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.generalLayout.addWidget(self.body, 5)

    def detect_existing_decks(self):
        files_found = os.listdir(DECK_DIRECTORY)
        decks = [f.split('.')[0] for f in files_found]
        return decks

    # def show_flashcard(self):
        # " get a pending flashcard from the deck
        # " display as QLabel
        # " buttons for right/wrong


def main():
    """PyCard's main function"""
    app = QApplication([])
    window = FlashcardApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

# WINDOW_WIDTH = 700
# WINDOW_HEIGHT = 500
# SIDEBAR_WIDTH = 200
#
# " use dialog for adding new cards to the deck
#
# class PyCardWindow(QMainWindow):
#     """PyCard's main window."""
#
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("PyCard")
#         self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
#         self.generalLayout = QHBoxLayout()
#         centralWidget = QWidget(self)
#         centralWidget.setLayout(self.generalLayout)
#         self.setCentralWidget(centralWidget)
#         self._createSidebar()
#         self._createCard()
#
#     def _createSidebar(self):
#         self.sidebar = QVBoxLayout()
#         self.sidebar.addWidget(QLabel("Sidebar Test"), 0, Qt.AlignmentFlag.AlignCenter)
#         self.sidebar.addWidget(QLabel("Sidebar Test 2"), 0, Qt.AlignmentFlag.AlignCenter)
#         self.sidebar.addWidget(QLabel("Sidebar Test 3"), 0, Qt.AlignmentFlag.AlignCenter)
#         self.generalLayout.addLayout(self.sidebar, 1)
#
#     def _createCard(self):
#         self.card = QLabel()
#         self.card.setText("Card Test")
#         self.card.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.generalLayout.addWidget(self.card, 3)
#
# def main():
#     """PyCard's main function"""
#     pycardApp = QApplication([])
#     pycardWindow = PyCardWindow()
#     pycardWindow.show()
#     sys.exit(pycardApp.exec())
#
# if __name__ == "__main__":
#     main()
