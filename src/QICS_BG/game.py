import random
from typing import Callable, List

from QICS_BG.constants import *
from QICS_BG.utils import *

OPERATIONS = ["X", "Y", "Z", "SX", "SY", "SZ", "E"]
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
        self.setup()

    def setup(self):
        # Prepare hands
        self.hands[0] = random.choices(OPERATIONS, k=NB_CARDS_HAND)
        self.hands[1] = random.choices(OPERATIONS, k=NB_CARDS_HAND)

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
        self.hands[player - 1][pos] = random.choice(OPERATIONS)

    def apply_rotation(self, rotation: str, qubit: int):
        if self.state[2].is_empty():
            # They are not entangled
            if rotation == "E":
                self.state[2].set_state(self.state[0].oppposite())
                self.state[3].set_state(self.state[1].oppposite())
            else:
                self.state[qubit].rotate(rotation)
        else:
            # They are entangled
            if rotation == "E":
                self.state[2].set_state("/")
                self.state[3].set_state("/")
            else:
                self.state[qubit].rotate(rotation)
                self.state[qubit + 2].rotate(rotation)

    def _apply_rotation_separated(self, rotation: str, qubit: int):
        qubit_state = self.state[qubit]

        # Implementing the entanglement rotation
        if rotation == "E":
            self.state[2].set_state(self.state[0].oppposite())
            self.state[3].set_state(self.state[1].oppposite())
            return

        # If it is in the basis nothing happens
        if str(qubit_state) in BASIS[rotation]:
            return

        # If it isn't we apply the rotation
        if rotation in ["X", "Y", "Z"]:
            self.state[qubit].set_state(qubit_state.oppposite())
            return

        self.state[qubit].rotate(rotation)

    def _apply_rotation_entangled(self, rotation: str, qubit: int):
        qubit_state = self.state[qubit]

        # Implementing the entanglement rotation
        if rotation == "E":
            self.state[2].set_state("/")
            self.state[3].set_state("/")
            return

        # If it is in the basis nothing happens
        if str(qubit_state) in BASIS[rotation]:
            return

        # If it isn't we apply the rotation
        if rotation in ["X", "Y", "Z"]:
            self.state[qubit].set_state(qubit_state.oppposite())
            self.state[qubit + 2].set_state(self.state[qubit].oppposite())
            return

        self.q

        # Otherwise we do a half rotation
        curr_axis = qubit_state.axis()
        rotation_axis = rotation if len(rotation) == 1 else rotation[1]

        for axis in ["X", "Y", "Z"]:
            if axis not in [curr_axis, rotation_axis]:
                self.state[qubit] = BASIS[axis][BASIS[curr_axis].index(qubit_state)]
                self.state[qubit + 2] = OPPOSITE_STATE[self.state[qubit]]

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
        state_str = [str(state) for state in self.state]
        if state_str in self.objectives[0]:
            self.scores[0] += 1
            return 1
        elif state_str in self.objectives[1]:
            self.scores[1] += 1
            return 2
        return 0
