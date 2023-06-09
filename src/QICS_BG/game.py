import random
from typing import Callable, List

from QICS_BG.constants import *
from QICS_BG.utils import *

OPERATIONS = ["X", "Y", "Z", "SX", "SY", "SZ", "E"]
OPERATIONS_WEIGHTS = [1, 1, 1, 2, 2, 2, 1]
STATES = ["0", "1", "+", "-", "-i", "+i"]
BASIS = {
    "X": ["+", "-"],
    "Y": ["-i", "+i"],
    "Z": ["0", "1"],
    "SX": ["+", "-"],
    "SY": ["-i", "+i"],
    "SZ": ["0", "1"],
}
OPPOSITE_STATE = {
    "0": "1",
    "1": "0",
    "+": "-",
    "-": "+",
    "-i": "+i",
    "+i": "-i",
}
STATE_TO_AXIS = {
    "0": "Z",
    "1": "Z",
    "+": "X",
    "-": "X",
    "-i": "Y",
    "+i": "Y",
}


class State:
    """
    Class implementing the state of a qubit.
    """

    def __init__(self, init_state=None):
        self.state = init_state

    def rotate(self, rotation):
        if self.is_empty():
            return

        # If it is in the basis nothing happens
        if self.state in BASIS[rotation]:
            return

        # If it isn't we apply the rotation
        if rotation in ["X", "Y", "Z"]:
            self.state = OPPOSITE_STATE[self.state]
            return

        # Otherwise we do a half rotation
        curr_axis = STATE_TO_AXIS[self.state]
        rotation_axis = rotation if len(rotation) == 1 else rotation[1]

        for axis in ["X", "Y", "Z"]:
            if axis not in [curr_axis, rotation_axis]:
                self.state = BASIS[axis][BASIS[curr_axis].index(self.state)]

    def set_state(self, new_state):
        if new_state == "/":
            self.state = None
            return
        self.state = new_state

    def oppposite(self):
        return OPPOSITE_STATE[self.state]

    def is_empty(self):
        return self.state is None

    def axis(self):
        return STATE_TO_AXIS[self.state]

    def __str__(self):
        return self.state if self.state else ""


class Game(metaclass=Singleton):
    def __init__(self):
        self.hands = [[], []]

        self.board_content = []

        self.state = [
            State("0"),
            State("0"),
            State(),
            State()
        ]

        self.turn = 0
        self.scores = [0, 0]
        self.objectives = []
        self.entangled = False
        self.setup()

    def setup(self):
        # Prepare hands
        self.hands[0] = random.choices(OPERATIONS, k=NB_CARDS_HAND, weights=OPERATIONS_WEIGHTS)
        self.hands[1] = random.choices(OPERATIONS, k=NB_CARDS_HAND, weights=OPERATIONS_WEIGHTS)

        # Prepare objectives
        allowed_states_obj = STATES[1:]
        self.objectives.append(
            [
                random.choices(allowed_states_obj, k=2) for _ in range(NB_OBJECTIVES)
            ]
        )
        self.objectives.append(
            [
                random.choices(allowed_states_obj, k=2) for _ in range(NB_OBJECTIVES)
            ]
        )

    def get_hand(self, player: int) -> List[str]:
        return self.hands[player - 1]

    def replace_card(self, pos: int, player: int):
        self.hands[player - 1][pos] = random.choices(OPERATIONS, k=1, weights=OPERATIONS_WEIGHTS)[0]

    def entangle(self):
        if not self.entangled:
            self.state[2].set_state(self.state[0].oppposite())
            self.state[3].set_state(self.state[1].oppposite())
            self.entangled = True
        else:
            self.state[2].set_state("/")
            self.state[3].set_state("/")
            self.entangled = False

    def apply_rotation(self, rotation: str, qubit: int):
        if rotation == "E":
            self.entangle()
            return

        self.state[qubit].rotate(rotation)
        self.state[qubit + 2].rotate(rotation)

    def play_turn(self, player: int, card_pos: int, qubit: int, callback: Callable):
        # Get the player's hand and card
        card = self.get_hand(player)[card_pos]

        # Play the card and increase the turn
        self.board_content.append((card, qubit))
        self.turn += 1

        # Update the hand
        self.replace_card(card_pos, player)

        # Update the state
        self.apply_rotation(card, qubit)

        callback()

    def check_win(self) -> int:
        """
        Check if the game is won
        :return: 0 if not, 1 if player 1 won, 2 if player 2 won
        """
        state_str_1 = [str(state) for state in self.state[:2]]
        state_str_2 = [str(state) for state in self.state[2:]]
        if state_str_1 in self.objectives[0]:
            self.scores[0] += 1

            if state_str_2 in self.objectives[0]:
                self.scores[0] += 1
                self.objectives[0][self.objectives[0].index(state_str_2)] = random.choices(STATES[1:], k=2)

            self.objectives[0][self.objectives[0].index(state_str_1)] = random.choices(STATES[1:], k=2)

            # If there is a win, we disentangle the qubits
            if self.entangled:
                self.entangle()

            return 1
        elif state_str_1 in self.objectives[1]:
            self.scores[1] += 1
            if state_str_2 in self.objectives[1]:
                self.scores[1] += 1
                self.objectives[1][self.objectives[1].index(state_str_2)] = random.choices(STATES[1:], k=2)

            self.objectives[1][self.objectives[1].index(state_str_1)] = random.choices(STATES[1:], k=2)

            # If there is a win, we disentangle the qubits
            if self.entangled:
                self.entangle()

            return 2
        return 0
