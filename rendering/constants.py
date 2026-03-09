C_KEYCODE: int = 99
D_KEYCODE: int = 100
H_KEYCODE: int = 104
ESC_KEYCODE: int = 65307
CTRL_KEYCODE: int = 65507
LEFT_ARROW_KEYCODE: int = 65361
RIGHT_ARROW_KEYCODE: int = 65363


HEX_TO_WALLS: dict[str, int] = {
    '0': None,
    '1': ('N'),
    '2': ('E'),
    '3': ('E', 'N'),
    '4': ('S'),
    '5': ('S', 'N'),
    '6': ('S', 'E'),
    '7': ('S', 'E', 'N'),
    '8': ('W'),
    '9': ('W', 'N'),
    'A': ('W', 'E'),  # 10
    'B': ('W', 'E', 'N'),  # 11
    'C': ('W', 'S'),  # 12
    'D': ('W', 'S', 'N'),  # 13
    'E': ('W', 'S', 'E'),  # 14
    'F': ('W', 'S', 'E', 'N')  # 15
}
