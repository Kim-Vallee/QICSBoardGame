import random
from typing import Callable, List

from QICS_BG.constants import *
from QICS_BG.utils import *

OPERATIONS = ["X", "Y", "Z", "SX", "SY", "SZ", "E"]
STATES = ["0", "1", "+", "-", "-i", "+i"]


class State:
    """
    Class implementing the state of a qubit.
    """

    def __init__(self, init_state=None):
        self.state = init_state

    def __str__(self):
        return self.state if self.state else ""


class Game(metaclass=Singleton):
    def __init__(self):
        self.hands = [[], []]

        self.board_content = []

        self.state = ["0", "0", "/", "/"]

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
        if self.state[2] == "/":
            self._apply_rotation_separated(rotation, qubit)
        else:
            self._apply_rotation_entangled(rotation, qubit)

    def _apply_rotation_separated(self, rotation: str, qubit: int):
        qubit_state = self.state[qubit]

        # Implementing the entanglement rotation
        if rotation == "E":
            self.state[2] = self.opposite_state[self.state[0]]
            self.state[3] = self.opposite_state[self.state[1]]
            return

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

    def _apply_rotation_entangled(self, rotation: str, qubit: int):
        qubit_state = self.state[qubit]

        # Implementing the entanglement rotation
        if rotation == "E":
            self.state[2] = self.state[3] = "/"
            return

        # If it is in the basis nothing happens
        if qubit_state in self.basis[rotation]:
            return

        # If it isn't we apply the rotation
        if rotation in ["X", "Y", "Z"]:
            self.state[qubit + 2] = qubit_state
            self.state[qubit] = self.opposite_state[qubit_state]
            return

        # Otherwise we do a half rotation
        curr_axis = self.state_to_axis[qubit_state]
        rotation_axis = rotation if len(rotation) == 1 else rotation[1]

        for axis in ["X", "Y", "Z"]:
            if axis not in [curr_axis, rotation_axis]:
                self.state[qubit] = self.basis[axis][self.basis[curr_axis].index(qubit_state)]
                self.state[qubit + 2] = self.opposite_state[self.state[qubit]]

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
        if self.state in self.objectives[0]:
            return 1
        elif self.state in self.objectives[1]:
            return 2
        return 0
