import random
import sys
from typing import Callable, List

import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QWidget, QLabel, QMenu

import stylesheet
from ui import Button

WINDOW_HEIGHT = 720
WINDOW_WIDTH = 1280

BOARD_MARGIN = int(5 * WINDOW_WIDTH / 100)  # 5% margin
BOARD_WIDTH = WINDOW_WIDTH - 2 * BOARD_MARGIN
BOARD_HEIGHT = int(50 * WINDOW_HEIGHT / 100)  # 50% height

NB_SLOTS = 6
SLOT_MARGIN = int(5 * BOARD_HEIGHT // 100)
SLOT_WIDTH = int((BOARD_WIDTH - (NB_SLOTS + 1) * SLOT_MARGIN) / NB_SLOTS)
SLOT_HEIGHT = int((BOARD_HEIGHT - 3 * SLOT_MARGIN) / 2)

TITLE_BAR_HEIGHT = int(5 * WINDOW_HEIGHT // 100)  # 5% height

UI_BUTTONS_HEIGHT = int(25 * WINDOW_HEIGHT // 100)  # 10% height
UI_BUTTONS_MARGIN = BOARD_MARGIN
UI_BUTTONS_WIDTH = BOARD_WIDTH

NB_CARDS_HAND = 5


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Game(metaclass=Singleton):
    def __init__(self):
        self.player1_hand = []
        self.player2_hand = []

        self.board_content = []

        self.state = ["0", "0"]

        self.operations = ["X", "Y", "Z", "SX", "SY", "SZ"]
        self.basis = {
            "X": ["+", "-"],
            "Y": ["-i", "+i"],
            "Z": ["0", "1"],
            "SX": ["+", "-"],
            "SY": ["-i", "+i"],
            "SZ": ["0", "1"],
        }
        self.opposite_state = {
            "0": "1",
            "1": "0",
            "+": "-",
            "-": "+",
            "-i": "+i",
            "+i": "-i",
        }
        self.state_to_axis = {
            "0": "Z",
            "1": "Z",
            "+": "X",
            "-": "X",
            "-i": "Y",
            "+i": "Y",
        }

        self.turn = 0

    def get_hand(self, player: int) -> List[str]:
        if player == 1:
            if not self.player1_hand:
                self.player1_hand = random.choices(self.operations, k=NB_CARDS_HAND)
            return self.player1_hand

        elif player == 2:
            if not self.player2_hand:
                self.player2_hand = random.choices(self.operations, k=NB_CARDS_HAND)
            return self.player2_hand

    def replace_card(self, pos: int, player: int):
        if player == 1:
            self.player1_hand[pos] = random.choice(self.operations)
        elif player == 2:
            self.player2_hand[pos] = random.choice(self.operations)

    def apply_rotation(self, rotation: str, qubit: int):
        qubit_state = self.state[qubit]

        # If it is in the basis nothing happens
        if qubit_state in self.basis[rotation]:
            return

        # If it isn't we apply the rotation
        if rotation in ["X", "Y", "Z"]:
            self.state[qubit] = self.opposite_state[qubit_state]
            return

        # Otherwise we do a half rotation
        curr_axis = self.state_to_axis[qubit_state]
        rotation_axis = rotation if len(rotation) == 1 else rotation[1]

        for axis in ["X", "Y", "Z"]:
            if axis not in [curr_axis, rotation_axis]:
                self.state[qubit] = self.basis[axis][self.basis[curr_axis].index(qubit_state)]


class Slot(QtWidgets.QFrame):
    def __init__(self, master: QWidget, x: int, y: int, width: int, height: int) -> None:
        super(Slot, self).__init__(master)

        self.setGeometry(QtCore.QRect(x, y, width, height))
        self.setStyleSheet(stylesheet.SLOTS)
        self.content = None
        self.master = master

    def set_content(self, content: str):
        self.content = QLabel(self)
        self.content.setGeometry(0, 0, SLOT_WIDTH, SLOT_HEIGHT)
        self.content.setFont(stylesheet.CONTENT_FONT)
        self.content.setStyleSheet(stylesheet.FONT_STYLE_CONTENT)
        self.content.setAlignment(Qt.AlignCenter)
        self.content.setText(content)
        self.content.show()


class Board(QtWidgets.QFrame):
    def __init__(self, master: QWidget) -> None:
        super().__init__(master)

        game = Game()

        self.setGeometry(QtCore.QRect(BOARD_MARGIN, WINDOW_HEIGHT - BOARD_HEIGHT - BOARD_MARGIN,
                                      BOARD_WIDTH, BOARD_HEIGHT))
        self.setStyleSheet(stylesheet.BOARD)

        # 4 steps to get to the end
        self.slots = []
        for i in range(NB_SLOTS):
            self.slots.append(
                (Slot(self, i * (SLOT_WIDTH + SLOT_MARGIN) + SLOT_MARGIN, SLOT_MARGIN, SLOT_WIDTH, SLOT_HEIGHT),
                 Slot(self, i * (SLOT_WIDTH + SLOT_MARGIN) + SLOT_MARGIN, SLOT_HEIGHT + 2 * SLOT_MARGIN, SLOT_WIDTH,
                      SLOT_HEIGHT)))

        self.qubits = self.slots[-1]
        self.slots = self.slots[:-1]

        for i, qbit in enumerate(self.qubits):
            qbit.set_content(game.state[i])

    def update_board(self):
        game = Game()
        for i, (card, qubit) in enumerate(game.board_content):
            self.slots[i][qubit].set_content(card)

        for i, qbit in enumerate(self.qubits):
            qbit.set_content(game.state[i])




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


class HandFrame(QtWidgets.QFrame):
    """Class for the hand of the player"""

    def __init__(self, master: QWidget, player: int) -> None:
        super(HandFrame, self).__init__(master)
        self.hand_slots = []

        # Computing the center
        width = NB_CARDS_HAND * (SLOT_WIDTH + SLOT_MARGIN) + SLOT_MARGIN
        offset = (master.width() - width) // 2

        self.player = player

        for i in range(NB_CARDS_HAND):
            self.hand_slots.append(
                Button(self, "", lambda *args: self.play_card(i, *args),
                       offset + i * (SLOT_WIDTH + SLOT_MARGIN) + SLOT_MARGIN,
                       SLOT_MARGIN,
                       SLOT_WIDTH,
                       SLOT_HEIGHT))
            menu = QMenu(f'Card {i}, player {player}')
            fc = lambda i=i: self.play_card(0, i)
            fc2 = lambda i=i: self.play_card(1, i)
            menu.addAction("Play on 1st qubit", fc)
            menu.addAction("Play on 2nd qubit", fc2)
            self.hand_slots[i].setMenu(menu)

    def show(self) -> None:
        super(HandFrame, self).show()
        self.update_hand()

    def update_hand(self):
        game = Game()
        hand = game.get_hand(self.player)
        for i, card in enumerate(self.hand_slots):
            card.setText(hand[i])

    def play_card(self, qubit: int, slot: int):
        game = Game()

        # Get the player's hand and card
        hand = game.get_hand(self.player)
        card = hand[slot]

        # Play the card and increase the turn
        game.board_content.append((card, qubit))
        game.turn += 1

        # Update the hand
        game.replace_card(slot, self.player)

        # Update the state
        game.apply_rotation(card, qubit)

        # Update ui
        win = UiMainWindow.instance
        self.update_hand()
        win.board.update_board()





class PlayerChoiceFrame(QtWidgets.QFrame):
    """Class for the player choice frame"""

    def __init__(self, master: QWidget, callback_player1, callback_player2) -> None:
        super(PlayerChoiceFrame, self).__init__(master)
        button_width = int(UI_BUTTONS_WIDTH / 6)
        button_height = 50

        Button(self, "Player 1", callback_player1, button_width,
               UI_BUTTONS_HEIGHT // 2 - button_height // 2, button_width,
               button_height)
        Button(self, "Player 2", callback_player2, 4 * button_width,
               UI_BUTTONS_HEIGHT // 2 - button_height // 2, button_width,
               button_height)


class UiButtonsPlayer(QtWidgets.QFrame):
    def __init__(self, master: QWidget) -> None:
        super().__init__(master)

        self.setGeometry(UI_BUTTONS_MARGIN, UI_BUTTONS_MARGIN // 2 + TITLE_BAR_HEIGHT, UI_BUTTONS_WIDTH,
                         UI_BUTTONS_HEIGHT)
        # self.setStyleSheet("border: 1px solid white;")

        self.frames = {}

        self.player1_frame()
        self.player2_frame()
        self.player_choice_frame()

    def hide_all_frames(self):
        for frame in self.frames.values():
            frame.hide()

    def player_choice_frame(self):

        if "player_choice" in self.frames.keys():
            self.hide_all_frames()
            self.frames["player_choice"].show()
            return

        self.frames["player_choice"] = PlayerChoiceFrame(self, self.player1_frame, self.player2_frame)
        self.hide_all_frames()
        self.frames["player_choice"].show()

    def player2_frame(self):
        if "player2" in self.frames.keys():
            self.hide_all_frames()
            self.frames["player2"].show()
            return

        self.frames["player2"] = HandFrame(self, 2)

        frame = self.frames["player2"]
        button_back = QtWidgets.QPushButton(frame)
        button_back.setGeometry(QtCore.QRect(5, 5, 40, 20))
        button_back.clicked.connect(self.player_choice_frame)
        button_back.setIcon(QtGui.QIcon(QtGui.QPixmap("img/back.svg")))
        button_back.setStyleSheet(stylesheet.DEFAULT_BUTTON)

    def player1_frame(self):
        if "player1" in self.frames.keys():
            self.hide_all_frames()
            self.frames["player1"].show()
            return

        self.frames["player1"] = HandFrame(self, 1)

        frame = self.frames["player1"]
        button_back = QtWidgets.QPushButton(frame)
        button_back.setGeometry(QtCore.QRect(5, 5, 40, 20))
        button_back.clicked.connect(self.player_choice_frame)
        button_back.setIcon(QtGui.QIcon(QtGui.QPixmap("img/back.svg")))
        button_back.setStyleSheet(stylesheet.DEFAULT_BUTTON)


class UiMainWindow(QtWidgets.QMainWindow):
    instance = None

    def __init__(self) -> None:
        super().__init__()
        UiMainWindow.instance = self

        self.setup()
        TitleBar(self.centralWidget, lambda: self.close(), self)
        UiButtonsPlayer(self.centralWidget)
        self.board = Board(self.centralWidget)

    def setup(self):
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet(stylesheet.WINDOW)
        self.centralWidget = QtWidgets.QWidget(self)
        self.centralWidget.setStyleSheet(stylesheet.GLOBAL_STYLES)
        self.setCentralWidget(self.centralWidget)
        self.setWindowTitle("QICS Quantum board game")
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = UiMainWindow()
    win.show()
    sys.exit(app.exec_())
