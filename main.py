import os
import sys
import json

from PyQt6.QtCore import Qt
# from PyQt6.QtGui import *
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QFrame,
    QPushButton,
    QMessageBox,
)

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500
POP_UP_WIDTH = 400
POP_UP_HEIGHT = 250
DECK_DIRECTORY = "./decks/"

class Flashcard:
    # " needs to have a Q/A
    # " keep track of last time reviewed
    def __init__(self, question, answer, last_review):
        self.question = question
        self.answer = answer
        self.last_review = last_review

class FlashcardDeck():
    def __init__(self, deck_name):
        # " initialize deck or create new if doesn't exist
        deck_file_name = DECK_DIRECTORY + deck_name + ".json"
        print("Initializing deck at " + deck_file_name)

        with open(deck_file_name, "r") as f:
            self.deck = json.load(f)

        self.srs_method = self.deck.get("srs_method")
        self.flashcards = self.deck.get("flashcards")

    # def load_flashcards(self):
        # " read deck file

    # def save_flashcards(self):
        # " write deck to file

    # def add_flashcard(self, flashcard):
        # " add flashcard to deck

    # def get_next_flashcard(self):
        # " return a pending flashcard

class FlashcardApp(QMainWindow):
    """
    FlashcardApp Class
        Manages the GUI for the flashcard app
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """
        Initialize the GUI:
            set window size and create central widget
        """
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.generalLayout = QHBoxLayout()
        centralWidget = QWidget(self)
        centralWidget.setLayout(self.generalLayout)
        self.setCentralWidget(centralWidget)

        # Init sidebar and body
        self.init_sidebar()
        self.init_body()

    def init_sidebar(self):
        """ Creates the GUI sidebar """

        # Create a frame around the sidebar
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setFrameStyle(1)
        self.sidebar_frame.setLineWidth(1)

        # The sidebar is a vertical box layout
        self.sidebar = QVBoxLayout()

        # Init deck selector
        self.init_deck_selector()

        # add a spacer
        self.sidebar.addStretch()

        # Add sidebar to central widget's layout
        self.sidebar_frame.setLayout(self.sidebar)
        self.generalLayout.addWidget(self.sidebar_frame, 2)

    def init_body(self):
        self.body = QLabel()
        self.body.setText("Welcome!")
        self.body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.generalLayout.addWidget(self.body, 5)

    def init_deck_selector(self):
        """ Creates dropdown menu for deck selection """

        self.deck_selector = QComboBox(self)
        self.update_deck_selector()

        # deck selector signal processing
        self.deck_selector.currentTextChanged.connect(self.process_deck_selector)

        # add deck selector to sidebar
        self.sidebar.addWidget(self.deck_selector)

    def detect_existing_decks(self):
        """ returns sorted list of existing decks """

        files_found = os.listdir(DECK_DIRECTORY)
        decks = [f.split('.')[0] for f in files_found]
        return sorted(decks)

    def update_deck_selector(self):
        """ get list of existing decks and add to combo box """

        self.decks = self.detect_existing_decks()
        self.deck_selector.clear()
        self.deck_selector.addItems(["Choose a deck..."] + self.decks + ["Create new deck"])

    def process_deck_selector(self, deck_selection):
        """ Load an existing deck or create a new one """

        if deck_selection == "Create new deck":
            self.new_deck_pop_up()

        if deck_selection in self.decks:
            self.active_deck = FlashcardDeck(deck_selection)

    def new_deck_pop_up(self):
        """ create pop up form for creating new deck """

        # Create pop-up widget
        self.pop_up = QWidget()
        self.pop_up.setFixedSize(POP_UP_WIDTH, POP_UP_HEIGHT)
        self.pop_up_layout = QVBoxLayout()
        self.pop_up.setLayout(self.pop_up_layout)

        # Add pop-up header
        self.pop_up_header = QLabel("Create a new deck")
        self.pop_up_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pop_up_layout.addWidget(self.pop_up_header)

        # Add vertical spacing
        self.pop_up_layout.addStretch()

        # Create input form for new deck
        self.new_deck_form = QWidget()
        self.new_deck_form_layout = QFormLayout()
        self.new_deck_form.setLayout(self.new_deck_form_layout)
        self.pop_up_layout.addWidget(self.new_deck_form)
        
        # Input for new deck name
        self.deck_name_line_edit = QLineEdit()
        self.new_deck_form_layout.addRow("Deck name:", self.deck_name_line_edit)

        # Input for SRS method
        self.srs_method_selector = QComboBox()
        self.srs_method_selector.addItem("Fibonacci")
        self.new_deck_form_layout.addRow("SRS Method:", self.srs_method_selector)
        self.srs_warning = QLabel("Note: you can't change the SRS method after\ndeck creation.")
        self.new_deck_form_layout.addRow("", self.srs_warning)

        # Add vertical spacing
        self.pop_up_layout.addStretch()

        # Navigation buttons
        self.pop_up_nav = QWidget()
        self.pop_up_nav_layout = QHBoxLayout()
        self.cancel_deck_creation = QPushButton("Cancel")
        self.confirm_deck_creation = QPushButton("Create deck")
        self.pop_up_nav_layout.addWidget(self.cancel_deck_creation)
        self.pop_up_nav_layout.addWidget(self.confirm_deck_creation)
        self.pop_up_nav.setLayout(self.pop_up_nav_layout)
        self.pop_up_layout.addWidget(self.pop_up_nav)

        # Button push signals
        self.cancel_deck_creation.clicked.connect(self.pop_up_cancel_clicked)
        self.confirm_deck_creation.clicked.connect(self.pop_up_confirm_clicked)

        # Render the pop up
        self.pop_up.show()

    def pop_up_cancel_clicked(self):
        """ Cancel deck creation """

        self.pop_up.close()
        self.deck_selector.setCurrentText("Choose a deck...")

    def pop_up_confirm_clicked(self):
        """ Deck creation confirmed """

        # Get user input
        deck_name = self.deck_name_line_edit.text()
        srs_method = self.srs_method_selector.currentText()
        
        # Create new deck structure
        deck_file_name = DECK_DIRECTORY + deck_name + ".json"

        # Write to json
        if os.path.exists(deck_file_name):
            self.pop_up.close()
            self.deck_exists = QMessageBox()
            self.deck_exists.setText("A deck with this name already exists, loading it now!")
            self.deck_exists.exec()

            self.deck_selector.setCurrentText(deck_name)
        else:
            new_deck = {"srs_method":srs_method,"flashcards":[]}
            json_object = json.dumps(new_deck, indent=4, ensure_ascii=False)

            with open(deck_file_name, "w") as f:
                f.write(json_object)

            self.update_deck_selector()
            self.deck_selector.setCurrentText(deck_name)
            self.pop_up.close()

def main():
    """PyCard's main function"""
    app = QApplication([])
    window = FlashcardApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
