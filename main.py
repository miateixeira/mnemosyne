import os
import sys
import json
from datetime import datetime

from PyQt6.QtCore import Qt

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
    def __init__(self, flashcard_dict):
        self.front    = flashcard_dict['front'] 
        self.back      = flashcard_dict['back'] 
        self.last_review = flashcard_dict['last_review']
        self.mem_level   = flashcard_dict['mem_level'] 

    def get_front(self):
        return self.front

    def get_back(self):
        return self.back

    def get_mem_level(self):
        return self.mem_level

    def get_last_review(self):
        return self.last_review

    def get_as_dict(self):
        """ return flashcard object as a dict """

        card_dict = {}

        card_dict['front'] = self.front 
        card_dict['back'] = self.back
        card_dict['last_review'] = self.last_review
        card_dict['mem_level'] = self.mem_level

        return card_dict

    def set_last_review(self, t):
        self.last_review = t

    def inc_mem_level(self):
        if self.mem_level < 9:
            self.mem_level += 1

    def dec_mem_level(self):
        if self.mem_level > 0:
            self.mem_level -= 1

class FlashcardDeck:
    def __init__(self, deck_name):
        # initialize deck or create new if doesn't exist
        self.deck_name = deck_name
        self.deck_file_name = DECK_DIRECTORY + self.deck_name + ".json"

        with open(self.deck_file_name, "r") as f:
            self.deck = json.load(f)

        # get srs_method and load key
        self.load_srs_method()

        # get list of flashcard objects
        self.load_flashcards()

    def load_flashcards(self):
        """ Load all the flashcard dicts are Flaschard objects """

        flashcards = self.deck.get("flashcards")
        self.flashcards = [Flashcard(x) for x in flashcards]

        self.update_pending()

    def update_pending(self):
        """ update the list of cards pending for review """
        self.pending_flashcards = [card for card in self.flashcards if self.check_pending(card)]

    def load_srs_method(self):
        """ load the key for appropriate srs method """

        self.srs_method = self.deck.get("srs_method")

        # Fibonacci: there are 9 memory levels, after which
        #            the flashcard will be shown every 21 days
        if self.srs_method == "Fibonacci":
            # keys correspond to the memory level of the flashcard
            # values correspond to the number of days that must pass
            #     before the next time the flashcard is shown
            self.srs_key = {0:0, 1:1, 2:1, 3:2, 4:3, 5:5, 6:8, 7:13, 8:21}

    def get_total_number_of_cards(self):
        """ return total number of cards in deck """
        return len(self.flashcards)

    def check_pending(self, flashcard):
        """ returns True if the flashcard is pending for review """

        curr_time = datetime.now()
        last_review_time = flashcard.get_last_review()

        # convert to datetime if needed
        if type(last_review_time) == str:
            time_format = "%Y-%m-%d %H:%M:%S.%f"
            last_review_time = datetime.strptime(last_review_time, time_format)

        delta_time = curr_time - last_review_time

        # more time has elapsed than required at current mem level
        if delta_time.days >= self.srs_key[flashcard.get_mem_level()]:
            return True

        return False

    def get_number_pending(self):
        """ return number of cards pending for review """
        return len(self.pending_flashcards)

    def get_deck_name(self):
        """ return the name of the deck """
        return self.deck_name

    def add_flashcard(self, front, back):
        """ add flashcard to deck """

        # create dict with card info
        card_info_dict = {}
        card_info_dict['front'] = front
        card_info_dict['back'] = back
        card_info_dict['last_review'] = datetime.now()
        card_info_dict['mem_level'] = 0

        # add card to deck
        new_card = Flashcard(card_info_dict)
        self.flashcards.append(new_card)

        self.update_pending()
        self.save_deck()

    def save_deck(self):
        """ write the deck as a json """
        deck_dict = {}
        deck_dict['srs_method'] = self.srs_method
        deck_dict['flashcards'] = [x.get_as_dict() for x in self.flashcards]

        # write to json file
        with open(self.deck_file_name, "w") as f:
            json.dump(deck_dict, f, indent=4, default=str, ensure_ascii=False)

    def get_next_flashcard(self):
        """ return the next available pending flashcard """

        if not self.pending_flashcards:
            return None
        
        return self.pending_flashcards.pop()

    def log_answer(self, curr_card, answer):
        """ update flashcard with time last reviewed and new mem level """

        for card in self.flashcards:
            if card == curr_card:
                card.set_last_review(datetime.now())

                if answer:
                    card.inc_mem_level()
                else:
                    card.dec_mem_level()

                self.update_pending()

                # TODO: this won't persist if app is closed before
                # eventually getting this right in the same session
                if not answer:
                    self.pending_flashcards.append(curr_card)

                self.save_deck()
                return

class FlashcardApp(QMainWindow):
    """
    FlashcardApp Class
        Manages the GUI for the flashcard app
    """

    def __init__(self):
        super().__init__()
        self.add_button_exists = 0
        self.init_ui()

    def init_ui(self):
        """
        Initialize the GUI:
            set window size and create central widget
        """
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.generalLayout = QHBoxLayout()
        centralWidget = QWidget(self)
        # centralWidget.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled)
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

        # create widgets for sidebar deck info
        self.sidebar_card_total = QLabel()
        self.sidebar.addWidget(self.sidebar_card_total)
        self.sidebar_number_pending = QLabel()
        self.sidebar.addWidget(self.sidebar_number_pending)

        # add a spacer
        self.sidebar.addStretch()

        # Add sidebar to central widget's layout
        self.sidebar_frame.setLayout(self.sidebar)
        self.generalLayout.addWidget(self.sidebar_frame, 2)

    def init_body(self):
        """ Initialize the body of the GUI """

        # create body widget and layout
        self.body = QWidget()
        self.body_layout = QVBoxLayout()
        self.body.setLayout(self.body_layout)

        # vertical spacing
        self.body_layout.addStretch()

        # the top of the body
        self.body_top = QLabel()
        self.body_top.setText("Welcome!")
        self.body_top.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.body_layout.addWidget(self.body_top)

        # bottom row of the body
        self.body_bottom = QLabel()
        self.body_bottom.setText("Select a deck to get started")
        self.body_bottom.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.body_layout.addWidget(self.body_bottom)

        # vertical spacing
        self.body_layout.addStretch()

        # create body navigation widget
        self.body_nav = QWidget()
        self.body_nav_layout = QHBoxLayout()
        self.body_nav.setLayout(self.body_nav_layout)
        self.body_layout.addWidget(self.body_nav)

        # vertical spacing
        self.body_layout.addStretch()

        # add body to GUI
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
            self.update_sidebar()
            self.update_body()
            if not self.add_button_exists:
                self.init_add_button()

    def update_sidebar(self):
        """ Update the sidebar with total number of cards and number pending """
        # Display total number of cards
        card_total = self.active_deck.get_total_number_of_cards()
        card_total_text = str(card_total) + " cards in this deck"
        self.sidebar_card_total.setText(card_total_text)

        # Display number of cards pending for review
        number_pending = self.active_deck.get_number_pending()
        number_pending_text = str(number_pending) + " cards pending for review"
        self.sidebar_number_pending.setText(number_pending_text)

    def init_add_button(self):
        self.add_button_exists = 1
        self.add_card_button = QPushButton("Add card to deck")
        self.sidebar.addWidget(self.add_card_button)
        self.add_card_button.clicked.connect(self.add_card_button_clicked)

    def add_card_button_clicked(self):
        """ create pop up form for creating new card """

        # create popup widget
        self.new_card_pop_up = QWidget()
        self.new_card_pop_up.setFixedSize(POP_UP_WIDTH, POP_UP_HEIGHT)

        self.new_card_pop_up_layout = QVBoxLayout()
        self.new_card_pop_up.setLayout(self.new_card_pop_up_layout)

        # popup header
        self.new_card_header = QLabel("Create new card for " + self.active_deck.get_deck_name())
        self.new_card_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.new_card_pop_up_layout.addWidget(self.new_card_header)

        # add spacing
        self.new_card_pop_up_layout.addStretch()

        # create input form for new card
        self.new_card_form = QWidget()
        self.new_card_form_layout = QFormLayout()
        self.new_card_form.setLayout(self.new_card_form_layout)
        self.new_card_pop_up_layout.addWidget(self.new_card_form)

        # input for card front
        self.card_front_line_edit = QLineEdit()
        self.new_card_form_layout.addRow("Front:", self.card_front_line_edit)

        # input for card back
        self.card_back_line_edit = QLineEdit()
        self.new_card_form_layout.addRow("Back:", self.card_back_line_edit)

        # vertical spacing
        self.new_card_pop_up_layout.addStretch()

        # card creation confirmation
        self.new_card_success = QLabel()
        self.new_card_pop_up_layout.addWidget(self.new_card_success)

        # vertical spacing
        self.new_card_pop_up_layout.addStretch()

        # new card navigation buttons
        self.new_card_nav = QWidget()
        self.new_card_nav_layout = QHBoxLayout()
        self.new_card_nav.setLayout(self.new_card_nav_layout)
        self.new_card_exit = QPushButton("Exit")
        self.new_card_confirm = QPushButton("Confirm")
        self.new_card_nav_layout.addWidget(self.new_card_exit)
        self.new_card_nav_layout.addWidget(self.new_card_confirm)
        self.new_card_pop_up_layout.addWidget(self.new_card_nav)

        # button push signals
        self.new_card_exit.clicked.connect(self.new_card_exit_clicked)
        self.new_card_confirm.clicked.connect(self.new_card_confirm_clicked)

        # render the popup
        self.new_card_pop_up.show()

    def new_card_exit_clicked(self):
        """ close new card creation pop up """
        self.new_card_pop_up.close()
        self.update_sidebar()
        self.update_body()

    def new_card_confirm_clicked(self):
        """ confirm card creation and prompt for another """

        # get user input
        front = self.card_front_line_edit.text()
        back = self.card_back_line_edit.text()

        # create new card
        self.active_deck.add_flashcard(front, back)

        # clear line edit input
        self.card_front_line_edit.clear()
        self.card_back_line_edit.clear()

        # show confirmation text
        self.new_card_success.setText("New card created! Add another or exit.")

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

    def update_body(self):   
        """ Present user with a flashcard if available """

        self.next_card = self.active_deck.get_next_flashcard()

        # all caught up!
        if not self.next_card:
            self.body_top.setText("All caught up!")
            self.body_bottom.setText("")
            self.clear_layout(self.body_nav_layout)
            return

        # present next flashcard
        self.body_top.setText(self.next_card.get_front())
        self.body_bottom.setText("")

        # reset nav buttons
        self.clear_layout(self.body_nav_layout)

        # create flip button
        self.flip_button = QPushButton("Flip")
        self.flip_button.setMaximumWidth(100)
        self.flip_button.clicked.connect(self.flip_button_clicked)
        self.body_nav_layout.addWidget(self.flip_button)

    def clear_layout(self, layout):
        """ clear all widgets from a layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def flip_button_clicked(self):
        """ flip to back of flashcard """
        
        # reveal back of flashcard
        self.body_bottom.setText(self.next_card.get_back())

        # clear the nav layout of buttons
        self.clear_layout(self.body_nav_layout)

        # wrong answer :(
        self.wrong_button = QPushButton("Needs more review")
        self.wrong_button.setMaximumWidth(200)
        self.wrong_button.clicked.connect(self.wrong_button_clicked)
        self.body_nav_layout.addWidget(self.wrong_button)
        
        # right answer!
        self.right_button = QPushButton("Got it!")
        self.right_button.setMaximumWidth(200)
        self.right_button.clicked.connect(self.right_button_clicked)
        self.body_nav_layout.addWidget(self.right_button)

    def right_button_clicked(self):
        self.active_deck.log_answer(self.next_card, True)
        self.update_body()
        self.update_sidebar()

    def wrong_button_clicked(self):
        self.active_deck.log_answer(self.next_card, False)
        self.update_body()
        self.update_sidebar()

def main():
    """PyCard's main function"""
    app = QApplication([])
    window = FlashcardApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
