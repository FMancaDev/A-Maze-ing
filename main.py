import sys
import random as rand
from typing import Any
from mazegen.generator import MazeGenerator
import rendering as rend
from rendering import CTRL, LEFT, RIGHT, UP, DOWN, R, H
from time import sleep


# ============= Grabing config =============

if len(sys.argv) < 2 or len(sys.argv) > 3:
    sys.exit("\nUsage: a-maze-ing config.txt [seed]")

w: int
h: int
entry: tuple[int, int]
exit: tuple[int, int]
maze_type: str
algo: str
w, h, entry, exit, _, maze_type, algo = rend.parse_config(sys.argv[1])
seed: int = int(sys.argv[2] if len(sys.argv) == 3 else rand.randint(0, 999999))

# ============= Initialization =============

win: rend.Window = rend.Window(800, 800)
render: rend.Renderer = rend.Renderer(win.width, win.height)
maze = MazeGenerator(w, h, entry, exit, seed)
maze.generate(perfect=maze_type, method=algo)

img_stack: dict[str, dict[str, dict]] = rend.load_themes(maze, render, win)
theme_names: list[str] = list(img_stack.keys())
theme_index: int = 0
active_theme = img_stack[theme_names[theme_index]]
delay: float = 0.2
last_change: float = 0

current = rend.CurrentState(win, render, maze, w, h, entry, exit,
                            maze_type, algo, img_stack, theme_names,
                            theme_index, active_theme, last_change)
rend.welcome_message()

# ============= Functions =============


def key_actions(param: Any) -> None:
    """base function for key events"""
    global current
    if win.keys_pressed.get(CTRL) and win.keys_pressed.get(RIGHT):
        current = rend.switch_theme(current, delay)
        logo = rend.put_logo(render, win, theme_names, theme_index)
        if logo:
            logo_ptr, logo_width, logo_height = logo
    if win.keys_pressed.get(CTRL) and win.keys_pressed.get(LEFT):
        current = rend.switch_theme(True)
        logo = rend.put_logo(render, win, theme_names, theme_index)
        if logo:
            logo_ptr, logo_width, logo_height = logo
    if win.keys_pressed.get(R):
        current = rend.change_maze(current, delay)
    if win.keys_pressed.get(UP):
        try:
            current.h += 1
            sleep(0.2)
            current = rend.change_maze(current, delay)
        except ValueError:
            current.h -= 1
    if win.keys_pressed.get(DOWN):
        current.h = current.h - 1 if current.h > 3 else current.h
        sleep(0.2)
        current = rend.change_maze(current, delay)

    if win.keys_pressed.get(RIGHT) and not win.keys_pressed.get(CTRL):
        try:
            current.w += 1
            sleep(0.2)
            current = rend.change_maze(current, delay)
        except ValueError:
            current.w -= 1
    if win.keys_pressed.get(LEFT) and not win.keys_pressed.get(CTRL):
        current.w = current.w - 1 if current.w > 3 else current.w
        sleep(0.2)
        current = rend.change_maze(current, delay)

    if win.keys_pressed.get(H):
        rend.show_img(current, True)
    else:
        rend.show_img(current, False)


# ============= First Render =============

win.mlx.mlx_put_image_to_window(current.win.mlx_ptr,
                                current.win.win_ptr,
                                current.active_theme['bg']['ptr'],
                                0, 0)

# ============= Loops =============

win.mlx.mlx_loop_hook(win.mlx_ptr, key_actions, None)
win.mlx.mlx_loop(win.mlx_ptr)
