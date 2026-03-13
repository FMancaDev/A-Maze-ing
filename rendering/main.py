import sys
import random as rd
from typing import Any
from .utils import MazeConfig, parse_config, load_themes
from mazegen.generator import MazeGenerator
from .Renderer import Renderer
from .Window import Window
from .constants import (H_KEYCODE as H,
                        LEFT_ARROW_KEYCODE as LEFT,
                        RIGHT_ARROW_KEYCODE as RIGHT,
                        CTRL_KEYCODE as CTRL,
                        UP_ARROW_KEYCODE as UP,
                        DOWN_ARROW_KEYCODE as DOWN,
                        R_KEYCODE as R)
from time import perf_counter


maze_themes: dict[str] = {
    'Los Angeles': [0xFF9933FF, 0xFFFFCC00, 0xFF33CCFF],
    'City Pop': [0xFFFF0066, 0xFF00FFEA, 0xFFFFFF66],
    'Pastel': [0xFF7E8F6A, 0xFFE9A1F2, 0xFFF2C2A1],
    'Fortune Cookie': [0xFFAF0000, 0xFFBFB05F, 0xFF000000],
}

# ============= Grabing config =============

if len(sys.argv) < 2 or len(sys.argv) > 3:
    sys.exit("\nUsage: a-maze-ing config.txt [seed]")

cfg: MazeConfig = parse_config(sys.argv[1])
seed: int = int(sys.argv[2] if len(sys.argv) == 3 else rd.randint(0, 999999))

# ============= Initialization =============

win: Window = Window()
render: Renderer = Renderer(win.width, win.height)
w: int = cfg.width
h: int = cfg.height
entry: tuple[int, int] = cfg.entry
exit: tuple[int, int] = cfg.exit
maze = MazeGenerator(w, h, cfg.entry, cfg.exit, seed)
maze.generate()

themes: dict[str, dict[str, dict]] = load_themes(maze, render,
                                                 win, maze_themes)
theme_names: list[str] = list(themes.keys())
theme_index: int = 0
active_theme = themes[theme_names[theme_index]]
theme_delay: float = 0.2
last_theme_change: float = 0

# ============= Functions =============


def change_maze() -> None:
    """will randomly generate a new maze following active sizes"""
    global maze, themes, w, h, active_theme
    win.mlx.mlx_clear_window(win.mlx_ptr, win.win_ptr)
    maze = MazeGenerator(w, h, entry, exit, rd.randint(0, 999999))
    maze.generate()
    themes = load_themes(maze, render, win, maze_themes)
    active_theme = themes[theme_names[theme_index]]


def switch_theme(reverse: bool = False):
    """Will circle between themes"""
    global theme_index, active_theme, last_theme_change
    now = perf_counter()
    if now - last_theme_change < theme_delay:
        return
    last_theme_change = now
    if reverse:
        theme_index = (theme_index - 1) % len(theme_names)
    else:
        theme_index = (theme_index + 1) % len(theme_names)
    active_theme = themes[theme_names[theme_index]]
    print(f'Theme set: "{theme_names[theme_index]}"')


def key_actions(param: Any) -> None:
    """base function for key events"""
    global maze, w, h, active_theme, exit
    if win.keys_pressed.get(CTRL) and win.keys_pressed.get(RIGHT):
        switch_theme()
    if win.keys_pressed.get(CTRL) and win.keys_pressed.get(LEFT):
        switch_theme(True)
    if win.keys_pressed.get(R):
        change_maze()
    if win.keys_pressed.get(UP):
        h += 1
        change_maze()
    if win.keys_pressed.get(DOWN):
        h -= 1
        exit = (exit[0], exit[1] - 1) if exit[1] >= h else exit
        change_maze()
    if win.keys_pressed.get(RIGHT) and not win.keys_pressed.get(CTRL):
        w += 1
        change_maze()
    if win.keys_pressed.get(LEFT) and not win.keys_pressed.get(CTRL):
        w -= 1
        exit = (exit[0] - 1, exit[1]) if exit[0] >= w else exit
        change_maze()
    if win.keys_pressed.get(H):
        show_img(True)
    else:
        show_img(False)



def show_img(overlay: bool = False) -> None:
    global themes
    if overlay:
        if not active_theme.get('path'):
            path: dict[str, Any] = win.create_copy(active_theme['bg'])
            color: int = maze_themes[theme_names[theme_index]][2]
            render.draw_path(maze, path, color)
            active_theme['path'] = path
        win.mlx.mlx_put_image_to_window(win.mlx_ptr,
                                        win.win_ptr,
                                        active_theme['path']['ptr'],
                                        0, 0)
    else:
        win.mlx.mlx_put_image_to_window(win.mlx_ptr,
                                        win.win_ptr,
                                        active_theme['bg']['ptr'],
                                        0, 0)


# ============= First Render =============

win.mlx.mlx_put_image_to_window(win.mlx_ptr,
                                win.win_ptr,
                                active_theme['bg']['ptr'],
                                0, 0)

# ============= Loops =============

win.mlx.mlx_loop_hook(win.mlx_ptr, key_actions, None)
win.mlx.mlx_loop(win.mlx_ptr)
