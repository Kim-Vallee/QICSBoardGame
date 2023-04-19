import os
from typing import Callable

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QLabel, QMenu, QGridLayout, QHBoxLayout, QVBoxLayout, QFrame

from QICS_BG.constants import *
from QICS_BG.game import Game
from QICS_BG.ui import Button
from QICS_BG.utils import *
import QICS_BG.stylesheet as stylesheet


class Slot(QtWidgets.QFrame):
    def __init__(self, master: QWidget) -> None:
        super(Slot, self).__init__(master)

        self.setStyleSheet(stylesheet.SLOTS)
        self.content = None
        self.master = master
        self.content_text = ""

    def set_content(self, content: str, fontsize: int = 20):
        width, height = self.size().width(), self.size().height()
        self.content_text = content
        self.content = QLabel(self)
        self.content.setGeometry(0, 0, width, height)
        self.content.setFont(QFont("Arial", fontsize))
        self.content.setStyleSheet(stylesheet.FONT_STYLE_CONTENT)
        self.content.setAlignment(Qt.AlignCenter)
        self.content.setText(content)
        self.content.show()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        super().resizeEvent(a0)
        self.set_content(self.content_text)


class Board(QtWidgets.QFrame, AbstractObserverUI):
    def __init__(self, master: QWidget) -> None:
        super().__init__(master)

        self.setStyleSheet(stylesheet.BOARD)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

        self.slots = []
        # 4 steps to get to the end
        for i in range(NB_SLOTS):
            _slots = [Slot(self), Slot(self)]
            self.layout.addWidget(_slots[0], 0, i)
            self.layout.addWidget(_slots[1], 1, i)
            self.slots.append(tuple(_slots))

    def update_ui(self):
        game = Game()
        nb_panels = (len(game.board_content) - 1) // NB_SLOTS
        # New Panel
        if (len(game.board_content) - 1) % NB_SLOTS == 0:
            self.clean_slots()
        shown_content = game.board_content[nb_panels * NB_SLOTS:nb_panels * NB_SLOTS + 6]
        for i, (card, qubit) in enumerate(shown_content):
            self.slots[i][qubit].set_content(card)

    def clean_slots(self):
        for i in range(NB_SLOTS):
            self.slots[i][0].set_content("")
            self.slots[i][1].set_content("")


class TitleBar(QtWidgets.QFrame):
    def __init__(self, master: QWidget, window_close_fn: Callable, window: QtWidgets.QMainWindow) -> None:
        super(TitleBar, self).__init__(master)

        self.button_exit = QtWidgets.QPushButton(master)
        self.button_exit.setGeometry(QtCore.QRect(1250, 10, 20, 20))
        self.button_exit.setStyleSheet(stylesheet.EXIT_BUTTON)
        self.button_exit.clicked.connect(window_close_fn)

        self.oldPos = 0

        self.window = window

        self.setGeometry(0, 0, WINDOW_WIDTH, TITLE_BAR_HEIGHT)
        self.setStyleSheet(stylesheet.TITLE_BAR)
        self.show()

    def mousePressEvent(self, event) -> None:
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event) -> None:
        delta = QPoint(event.globalPos() - self.oldPos)
        self.window.move(self.window.x() + delta.x(), self.window.y() + delta.y())
        self.oldPos = event.globalPos()


class UiButtonsPlayer(QtWidgets.QFrame, AbstractObserverUI):
    def __init__(self, master: QWidget) -> None:
        super().__init__(master)

        self.master = master
        self.layout = QtWidgets.QHBoxLayout(self)
        self.setLayout(self.layout)

        # self.setStyleSheet("border: 1px solid green;")

        self.frames = {}
        self.image_path = os.path.join(os.path.dirname(__file__), "img/back.svg")

        self.player1_frame()
        self.player2_frame()
        self.player_choice_frame()

    def hide_all_frames(self):
        for frame in self.frames.values():
            frame.hide()

    def player_choice_frame(self):

        if "player_choice" not in self.frames.keys():
            self.frames["player_choice"] = PlayerChoiceFrame(self, self.player1_frame, self.player2_frame)
            self.layout.addWidget(self.frames["player_choice"])

        self.hide_all_frames()
        self.frames["player_choice"].show()

        # Check winning condition
        game = Game()
        winning = game.check_win()
        if winning > 0:
            if winning == 1:
                print("Player 1 wins")
            elif winning == 2:
                print("Player 2 wins")

    def player2_frame(self):
        if "player2" in self.frames.keys():
            self.hide_all_frames()
            self.frames["player2"].show()
            return

        self.frames["player2"] = HandFrame(self, 2)

        self.layout.addWidget(self.frames["player2"])

        win = UiMainWindow.instance
        win.add_observer(self.frames["player2"])

    def player1_frame(self):
        if "player1" in self.frames.keys():
            self.hide_all_frames()
            self.frames["player1"].show()
            return

        self.frames["player1"] = HandFrame(self, 1)

        self.layout.addWidget(self.frames["player1"])

        win = UiMainWindow.instance
        win.add_observer(self.frames["player1"])

    def update_ui(self):
        self.player_choice_frame()


class HandFrame(QtWidgets.QFrame, AbstractObserverUI):
    """Class for the hand of the player"""

    def __init__(self, master: UiButtonsPlayer, player: int) -> None:
        super(HandFrame, self).__init__(master)
        self.hand_slots = []
        self.master = master
        self.player = player

        # First layout corresponds to return button and states
        self.layout = QVBoxLayout(self)

        self.upper_part = QtWidgets.QFrame(self)
        self.lower_part = QtWidgets.QFrame(self)

        self.layout.addWidget(self.upper_part, 2)
        self.layout.addWidget(self.lower_part, 1)

        self.setLayout(self.layout)

        upper_layout = QHBoxLayout(self.upper_part)
        lower_layout = QHBoxLayout(self.lower_part)

        game = Game()
        win = UiMainWindow.instance

        # Return button
        exit_button = QtWidgets.QPushButton(self)
        exit_button.setGeometry(QtCore.QRect(0, 0, 40, 20))
        exit_button.clicked.connect(master.player_choice_frame)
        exit_button.setIcon(QtGui.QIcon(QtGui.QPixmap(master.image_path)))
        exit_button.setStyleSheet(stylesheet.DEFAULT_BUTTON)
        exit_button.setMaximumWidth(40)
        upper_layout.addWidget(exit_button, 1, alignment=Qt.AlignLeft | Qt.AlignTop)

        for i in range(NB_CARDS_HAND):
            button = Button(self, "", lambda: 0)
            button.setMaximumWidth(100)
            button.setMaximumHeight(100)
            button.setMinimumWidth(100)
            button.setMinimumHeight(100)

            self.hand_slots.append(button)
            upper_layout.addWidget(button, 3, alignment=Qt.AlignCenter)

            menu = QMenu(f'Card {i}, player {player}')
            fc = lambda i=i: game.play_turn(self.player, i, 0, win.send_signal)
            fc2 = lambda i=i: game.play_turn(self.player, i, 1, win.send_signal)
            menu.addAction("Play on 1st qubit", fc)
            menu.addAction("Play on 2nd qubit", fc2)

            self.hand_slots[i].setMenu(menu)

        self.upper_part.setLayout(upper_layout)

        self.objectives = []

        # Adding the objectives below
        for i in range(len(game.objectives[player - 1])):
            slots = [QLabel(self), QLabel(self)]
            for slot in slots:
                slot.setFont(QFont("Arial", 12))
                slot.setStyleSheet(stylesheet.FONT_STYLE_CONTENT)
                slot.setAlignment(Qt.AlignCenter)
                slot.show()
            container = QFrame(self)
            objective_layout = QHBoxLayout()
            objective_layout.addWidget(slots[0], 1)
            objective_layout.addWidget(slots[1], 1)
            container.setLayout(objective_layout)
            container.setObjectName(f"container_{i}_{player}")
            container.setStyleSheet(f"""
            #container_{i}_{player} {{
                border: 1px solid white;
                background-color: #2d2d2d;
            }}
            
            QFrame {{
                border-radius: 5px;
            }}
            """)
            lower_layout.addWidget(container, 1)
            self.objectives.append(tuple(slots))

        self.lower_part.setLayout(lower_layout)

    def show(self) -> None:
        super(HandFrame, self).show()
        self.update_ui()

    def update_ui(self):
        game = Game()

        # Update the hand
        hand = game.get_hand(self.player)
        for i, card in enumerate(self.hand_slots):
            card.setText(hand[i])

        # Update the objectives
        for i, obj in enumerate(game.objectives[self.player - 1]):
            for j in range(2):
                self.objectives[i][j].setText(obj[j])


class PlayerChoiceFrame(QtWidgets.QFrame):
    """Class for the player choice frame"""

    def __init__(self, master: QWidget, callback_player1, callback_player2) -> None:
        super(PlayerChoiceFrame, self).__init__(master)
        button_width = 200
        button_height = 50

        self.setGeometry(master.rect())

        # self.setStyleSheet("border: 1px solid red;")

        self.layout = QtWidgets.QHBoxLayout(self)

        button_player1 = Button(self, "Player 1", callback_player1)
        button_player1.setMaximumWidth(button_width)
        button_player1.setMinimumHeight(50)
        button_player2 = Button(self, "Player 2", callback_player2)
        button_player2.setMaximumWidth(button_width)
        button_player2.setMinimumHeight(50)

        self.layout.addWidget(button_player1)
        self.layout.addWidget(button_player2)

        self.setLayout(self.layout)


class CurrentStateFrame(QtWidgets.QFrame, AbstractObserverUI):
    def __init__(self, master: QWidget) -> None:
        super().__init__(master)

        self.master = master

        self.setStyleSheet(stylesheet.BOARD)

        self.layout = QtWidgets.QVBoxLayout(self)

        self.qubits = [Slot(self), Slot(self)]

        self.layout.addWidget(self.qubits[0])
        self.layout.addWidget(self.qubits[1])
        self.setLayout(self.layout)

        for qbit_ui in self.qubits:
            qbit_ui.set_content("0")

    def update_ui(self):
        game = Game()

        for i, qbit in enumerate(self.qubits):
            qbit.set_content(game.state[i])


class UiMainWindow(QtWidgets.QMainWindow):
    instance = None

    def __init__(self) -> None:
        super().__init__()
        UiMainWindow.instance = self
        self.update_observers = []

        self.setup()
        TitleBar(self.centralWidget, lambda: self.close(), self)
        self.contentWidget.setGeometry(0, TITLE_BAR_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT - TITLE_BAR_HEIGHT)
        self.layout = QtWidgets.QVBoxLayout(self.contentWidget)

        self.board_widget = QtWidgets.QWidget(self.contentWidget)
        self.board_layout = QtWidgets.QHBoxLayout()

        self.uiButtonPlayer = UiButtonsPlayer(self.contentWidget)
        self.board = Board(self.contentWidget)
        self.states_ui = CurrentStateFrame(self.contentWidget)

        self.add_observer(self.uiButtonPlayer)
        self.add_observer(self.states_ui)
        self.add_observer(self.board)

        self.layout.addWidget(self.uiButtonPlayer, 5)
        self.layout.addWidget(self.board_widget, 6)

        self.board_layout.addWidget(self.board, 5)
        self.board_layout.addWidget(self.states_ui, 1)

        self.contentWidget.setLayout(self.layout)
        self.board_widget.setLayout(self.board_layout)

    def setup(self):
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet(stylesheet.WINDOW)

        self.centralWidget = QtWidgets.QWidget(self)
        self.contentWidget = QtWidgets.QWidget(self.centralWidget)

        self.centralWidget.setStyleSheet(stylesheet.GLOBAL_STYLES)
        self.setCentralWidget(self.centralWidget)
        self.setWindowTitle("QICS Quantum board game")
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)

    def add_observer(self, observer: AbstractObserverUI):
        self.update_observers.append(observer)

    def send_signal(self):
        for observer in self.update_observers:
            observer.update_ui()
