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
theme_names: list[str] = list(rend.maze_themes.keys())
theme_index: int = 0
last_change: float = 0
img_stack: dict = {}
active_theme: dict = {}
current = rend.CurrentState(win, render, maze, w, h, entry, exit,
                            maze_type, algo, img_stack, theme_names,
                            theme_index, active_theme, last_change)
rend.welcome_message()
current = rend.animate(current)


# ============= Functions =============


def key_actions(param: Any) -> None:
    """base function for key events"""
    global current
    if win.keys_pressed.get(CTRL) and win.keys_pressed.get(RIGHT):
        current = rend.switch_theme(current)
        current.logo = rend.put_logo(current)
    if win.keys_pressed.get(CTRL) and win.keys_pressed.get(LEFT):
        current = rend.switch_theme(current, reverse=True)
        current.logo = rend.put_logo(current)
    if win.keys_pressed.get(R):
        current = rend.change_maze(current)
    if win.keys_pressed.get(UP):
        try:
            current.h += 1
            sleep(0.2)
            current = rend.change_maze(current)
        except ValueError:
            current.h -= 1
    if win.keys_pressed.get(DOWN):
        current.h = current.h - 1 if current.h > 3 else current.h
        sleep(0.2)
        current = rend.change_maze(current)

    if win.keys_pressed.get(RIGHT) and not win.keys_pressed.get(CTRL):
        try:
            current.w += 1
            sleep(0.2)
            current = rend.change_maze(current)
        except ValueError:
            current.w -= 1
    if win.keys_pressed.get(LEFT) and not win.keys_pressed.get(CTRL):
        current.w = current.w - 1 if current.w > 3 else current.w
        sleep(0.2)
        current = rend.change_maze(current)

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
