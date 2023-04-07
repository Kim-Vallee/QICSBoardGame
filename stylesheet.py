from PyQt5.QtGui import QFont

DEFAULT_FONT = QFont("Arial", 12)
TRANSITION_FONT = QFont("Arial", 20)

CONTENT_FONT = QFont("Arial", 30)
FONT_STYLE_CONTENT = "color: white;"

TITLE_BAR = "border-bottom: 2px solid rgb(50, 48, 57);"

WINDOW = "background-color: rgb(28, 27, 32);"

ICONS = {
    1: "img/die_face_1_T.png",
    2: "img/die_face_2_T.png",
    3: "img/die_face_3_T.png",
    4: "img/die_face_4_T.png",
    5: "img/die_face_5_T.png",
    6: "img/die_face_6_T.png",
}

GLOBAL_STYLES = """
QSpinBox {
    border: 2 solid rgb(50, 48, 57);
    border-radius: 20;
    color: #FFF;
    background-color: rgb(47, 45, 54);
}
QSpinBox:hover {
    border: 2 solid rgb(98, 94, 113);
}
QSpinBox:focus {
    border: 2 solid rgb(85, 170, 255);
    background-color: rgb(63, 60, 72);
}
QLineEdit {
    border: 2px solid rgb(50, 48, 57);
    border-radius: 20px;
    color: #FFF;
    padding-left: 20px;
    padding-right: 20px;
    background-color: rgb(47, 45, 54);
}
QLineEdit:hover {
    border: 2px solid rgb(98, 94, 113);
}
QLineEdit:focus {
    border: 2px solid rgb(85, 170, 255);
    background-color: rgb(63, 60, 72);
}
QRadioButton {
    color: #FFF;
    padding: 5;
    background-color: rgb(47, 45, 54);
    spacing: 20;
}
QRadioButton::indicator:unchecked {
    image: url(img/indicator.svg);
}
QRadioButton::indicator:unchecked:hover {
    image: url(img/indicator_hover.svg);
}
QRadioButton::indicator:checked {
    border-image: url(img/checked.svg);
}
QRadioButton::indicator:disabled {
    image: url(img/disabled.svg);
}
"""

BOARD = """
QFrame {
    border-radius: 20px;
    background-color: rgb(47, 45, 54);
}
"""

SLOTS = """
QFrame {
    border-radius: 20px;
    background-color: rgb(37, 35, 44);
}
"""

CHOICE_FRAME = """
QFrame {
    border: 2px solid rgb(50, 48, 57);
    border-radius: 20px;
    color: #FFF;
    background-color: rgb(47, 45, 54);
}
"""

EXIT_FRAME = """
QFrame {
    border-radius: 20px;
    color: #FFF;
    background-color: rgb(142, 21, 21);
}
"""

TRANSITION_BG = """
QFrame {
    color: #FFF;
    background-color: rgb(47, 45, 54);
}
"""

CROSSOUT_FRAME = """
QFrame {
    border-radius: 20px;
    color: #FFF;
    background-color: rgb(47, 45, 54);
}
"""

DEFAULT_FRAME = """
QFrame {
    border: 2px solid rgb(50, 48, 57);
    border-radius: 20px;
    color: #FFF;
    background-color: rgb(47, 45, 54);
}
"""

DICE_BUTTON = """
QPushButton {
    border: 4 solid rgb(50, 48, 57);
    border-radius: 20;
    color: #FFF;
    background-color: rgb(47, 45, 54);
}
QPushButton:hover {
    border: 4 solid rgb(98, 94, 113);
}
QPushButton:checked {
    border: 4 solid rgb(85, 170, 255);
    background-color: rgb(63, 60, 72);
}
"""

EXIT_BUTTON = """
QPushButton {
	border: none;
	border-radius: 10px;
	background-color: rgb(204, 0, 0);
}
QPushButton:hover {
	background-color: rgba(204, 0, 0, 150);
}
"""

HELP_BUTTON = """
QPushButton {
	border: none;
	border-radius: 10px;
	background-color: rgb(241, 235, 52);
    image: url(img/help.svg);
}
QPushButton:hover {
	background-color: rgba(241, 235, 52, 150);
}
"""

BACK_HELP_BUTTON = """
QPushButton {
    border: 2px solid rgb(50, 48, 57);
    border-radius: 10px;
    background-color: rgb(47, 45, 54);
}
QPushButton:hover {
    border: 2px solid rgb(98, 94, 113);
}
QPushButton:focus:hover {
    border: 2px solid rgb(85, 170, 255);
    background-color: rgb(63, 60, 72);
}
"""

DEFAULT_BUTTON = """
QPushButton {
    border: 2px solid rgb(50, 48, 57);
    border-radius: 20px;
    color: #FFF;
    padding-left: 20px;
    padding-right: 20px;
    background-color: rgb(47, 45, 54);
}
QPushButton:hover {
    border: 2px solid rgb(98, 94, 113);
}
QPushButton:focus:hover {
    border: 2px solid rgb(85, 170, 255);
    background-color: rgb(63, 60, 72);
}
"""
