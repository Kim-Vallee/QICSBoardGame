import os
from typing import Callable

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QLabel, QMenu, QGridLayout

from QICS_BG.constants import *
from QICS_BG.game import Game
from QICS_BG.ui import Button
from QICS_BG.utils import *
import QICS_BG.stylesheet as stylesheet


class Slot(QtWidgets.QFrame):
    def __init__(self, master: QWidget, x: int, y: int, width: int, height: int) -> None:
        super(Slot, self).__init__(master)

        self.setGeometry(QtCore.QRect(x, y, width, height))
        self.width = width
        self.height = height

        self.setStyleSheet(stylesheet.SLOTS)
        self.content = None
        self.master = master

    def set_content(self, content: str, fontsize: int = 20):
        self.content = QLabel(self)
        self.content.setGeometry(0, 0, self.width, self.height)
        self.content.setFont(QFont("Arial", fontsize))
        self.content.setStyleSheet(stylesheet.FONT_STYLE_CONTENT)
        self.content.setAlignment(Qt.AlignCenter)
        self.content.setText(content)
        self.content.show()


class Board(QtWidgets.QFrame, AbstractObserverUI):
    def __init__(self, master: QWidget) -> None:
        super().__init__(master)

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


class HandFrame(QtWidgets.QFrame, AbstractObserverUI):
    """Class for the hand of the player"""

    def __init__(self, master: QWidget, player: int) -> None:
        super(HandFrame, self).__init__(master)
        self.hand_slots = []
        self.master = master
        self.player = player

        # Computing the center
        width = NB_CARDS_HAND * (SLOT_WIDTH + SLOT_MARGIN) + SLOT_MARGIN
        offset = (master.width() - width) // 2

        self.setGeometry(master.rect())
        self.setStyleSheet("border: 1px solid white;")

        game = Game()
        win = UiMainWindow.instance

        for i in range(NB_CARDS_HAND):
            self.hand_slots.append(
                Button(self, "", lambda: 0,
                       offset + i * (SLOT_WIDTH + SLOT_MARGIN) + SLOT_MARGIN,
                       SLOT_MARGIN,
                       SLOT_WIDTH,
                       SLOT_HEIGHT))
            menu = QMenu(f'Card {i}, player {player}')
            fc = lambda i=i: game.play_turn(self.player, i, 0, win.send_signal)
            fc2 = lambda i=i: game.play_turn(self.player, i, 1, win.send_signal)
            menu.addAction("Play on 1st qubit", fc)
            menu.addAction("Play on 2nd qubit", fc2)
            self.hand_slots[i].setMenu(menu)

        # Adding the objective below
        self.objectives_frames = [
            QtWidgets.QFrame(self)
        ]

        frame_width = int(width / 6)

        # for i, frame in enumerate(self.objectives_frames):
        #     frame.setGeometry()

        self.objectives = [
            Slot(self, offset + width + SLOT_MARGIN, 0, SLOT_HEIGHT // 2, SLOT_HEIGHT // 2),
            Slot(self, offset + width + SLOT_MARGIN, SLOT_MARGIN + SLOT_HEIGHT // 2, SLOT_HEIGHT // 2, SLOT_HEIGHT // 2)
        ]

    def show(self) -> None:
        super(HandFrame, self).show()
        self.update_ui()

    def update_ui(self):
        game = Game()

        # Update the hand
        hand = game.get_hand(self.player)
        for i, card in enumerate(self.hand_slots):
            card.setText(hand[i])

        # # Update the objectives
        # for i, obj in enumerate(game.objectives[self.player - 1]):
        #     self.objectives[i].set_content(obj)


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


class UiButtonsPlayer(QtWidgets.QFrame, AbstractObserverUI):
    def __init__(self, master: QWidget) -> None:
        super().__init__(master)

        self.setGeometry(UI_BUTTONS_MARGIN, UI_BUTTONS_MARGIN // 2 + TITLE_BAR_HEIGHT, UI_BUTTONS_WIDTH,
                         UI_BUTTONS_HEIGHT)

        # self.setStyleSheet("border: 1px solid white;")

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

        win = UiMainWindow.instance
        win.add_observer(self.frames["player2"])

        frame = self.frames["player2"]
        self._setup_button(frame)

    def player1_frame(self):
        if "player1" in self.frames.keys():
            self.hide_all_frames()
            self.frames["player1"].show()
            return

        self.frames["player1"] = HandFrame(self, 1)

        win = UiMainWindow.instance
        win.add_observer(self.frames["player1"])

        frame = self.frames["player1"]
        self._setup_button(frame)

    def _setup_button(self, frame):
        button = QtWidgets.QPushButton(frame)
        button.setGeometry(QtCore.QRect(5, 5, 40, 20))
        button.clicked.connect(self.player_choice_frame)
        button.setIcon(QtGui.QIcon(QtGui.QPixmap(self.image_path)))
        button.setStyleSheet(stylesheet.DEFAULT_BUTTON)

    def update_ui(self):
        self.player_choice_frame()


class CurrentStateFrame(QtWidgets.QFrame, AbstractObserverUI):
    def __init__(self, master: QWidget) -> None:
        super().__init__(master)
        self.master = master

        self.setGeometry(2 * BOARD_MARGIN + BOARD_WIDTH, WINDOW_HEIGHT - BOARD_HEIGHT - BOARD_MARGIN,
                         SLOT_WIDTH + SLOT_MARGIN * 2, SLOT_HEIGHT * 2 + SLOT_MARGIN * 3)

        self.setStyleSheet(stylesheet.BOARD)

        self.qubits = []

        self.qubits.append(Slot(master, 2 * BOARD_MARGIN + BOARD_WIDTH + SLOT_MARGIN,
                                WINDOW_HEIGHT - BOARD_HEIGHT - BOARD_MARGIN + SLOT_MARGIN,
                                SLOT_WIDTH,
                                SLOT_HEIGHT))

        self.qubits.append(Slot(master, 2 * BOARD_MARGIN + BOARD_WIDTH + SLOT_MARGIN,
                                WINDOW_HEIGHT - BOARD_HEIGHT - BOARD_MARGIN + SLOT_HEIGHT + 2 * SLOT_MARGIN,
                                SLOT_WIDTH,
                                SLOT_HEIGHT))

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
        uiButtonPlayer = UiButtonsPlayer(self.centralWidget)
        self.add_observer(uiButtonPlayer)
        self.board = Board(self.centralWidget)
        self.add_observer(self.board)
        self.states_ui = CurrentStateFrame(self.centralWidget)
        self.add_observer(self.states_ui)

    def setup(self):
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet(stylesheet.WINDOW)
        self.centralWidget = QtWidgets.QWidget(self)
        self.centralWidget.setStyleSheet(stylesheet.GLOBAL_STYLES)
        self.setCentralWidget(self.centralWidget)
        self.setWindowTitle("QICS Quantum board game")
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)

    def add_observer(self, observer: AbstractObserverUI):
        self.update_observers.append(observer)

    def send_signal(self):
        for observer in self.update_observers:
            observer.update_ui()
