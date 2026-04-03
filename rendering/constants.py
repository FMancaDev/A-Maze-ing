from typing import Any

C_KEYCODE: int = 99
D_KEYCODE: int = 100
H_KEYCODE: int = 104
ESC_KEYCODE: int = 65307
CTRL_KEYCODE: int = 65507
LEFT_ARROW_KEYCODE: int = 65361
RIGHT_ARROW_KEYCODE: int = 65363
UP_ARROW_KEYCODE: int = 65362
DOWN_ARROW_KEYCODE: int = 65364
R_KEYCODE: int = 114


DEC_TO_WALLS: dict[int, None | Any] = {
    0: None,
    1: ('N'),
    2: ('E'),
    3: ('E', 'N'),
    4: ('S'),
    5: ('S', 'N'),
    6: ('S', 'E'),
    7: ('S', 'E', 'N'),
    8: ('W'),
    9: ('W', 'N'),
    10: ('W', 'E'),
    11: ('W', 'E', 'N'),
    12: ('W', 'S'),
    13: ('W', 'S', 'N'),
    14: ('W', 'S', 'E'),
    15: ('W', 'S', 'E', 'N')
}
