import sys
import random as rd
from typing import Any, Callable
from rendering.utils import (MazeConfig, parse_config,
                             load_themes, welcome_message,
                             put_logo)
from mazegen.generator import MazeGenerator
from rendering.Renderer import Renderer
from rendering.Window import Window
from rendering.constants import (H_KEYCODE as H,
                                 LEFT_ARROW_KEYCODE as LEFT,
                                 RIGHT_ARROW_KEYCODE as RIGHT,
                                 CTRL_KEYCODE as CTRL,
                                 UP_ARROW_KEYCODE as UP,
                                 DOWN_ARROW_KEYCODE as DOWN,
                                 R_KEYCODE as R)
from time import perf_counter, sleep


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

win: Window = Window(800, 800)
render: Renderer = Renderer(win.width, win.height)
w: int = cfg.width
h: int = cfg.height
entry: tuple[int, int] = cfg.entry
exit: tuple[int, int] = cfg.exit
maze = MazeGenerator(w, h, cfg.entry, cfg.exit, seed)
maze.generate(perfect=cfg.perfect, method=cfg.gen_algo)

themes: dict[str, dict[str, dict]] = load_themes(maze, render,
                                                 win, maze_themes)
theme_names: list[str] = list(themes.keys())
theme_index: int = 0
active_theme = themes[theme_names[theme_index]]
delay: float = 0.2
last_change: float = 0


welcome_message()
logo_ptr: int = 0
logo_width: int = 0
logo_height: int = 0
logo = put_logo(render, win, theme_names, theme_index)
if logo:
    logo_ptr, logo_width, logo_height = logo

# ============= Functions =============


def change_maze() -> None:
    """will randomly generate a new maze following active sizes"""
    global maze, themes, w, h, active_theme, last_change
    # win.mlx.mlx_clear_window(win.mlx_ptr, win.win_ptr)
    now = perf_counter()
    if now - last_change < delay:
        return
    last_change = now
    reset_entry_exit()
    maze = MazeGenerator(w, h, entry, exit, rd.randint(0, 999999))
    maze.generate(perfect=cfg.perfect, method=cfg.gen_algo)
    themes = load_themes(maze, render, win, maze_themes)
    active_theme = themes[theme_names[theme_index]]


def switch_theme(reverse: bool = False):
    """Will circle between themes"""
    global theme_index, active_theme, last_change
    now = perf_counter()
    if now - last_change < delay:
        return
    last_change = now
    if reverse:
        theme_index = (theme_index - 1) % len(theme_names)
    else:
        theme_index = (theme_index + 1) % len(theme_names)
    active_theme = themes[theme_names[theme_index]]
    print(f'Theme set: "{theme_names[theme_index]}"')


def key_actions(param: Any) -> None:
    """base function for key events"""
    global maze, w, h, active_theme, exit, logo_ptr, logo_width, logo_height
    if win.keys_pressed.get(CTRL) and win.keys_pressed.get(RIGHT):
        switch_theme()
        logo = put_logo(render, win, theme_names, theme_index)
        if logo:
            logo_ptr, logo_width, logo_height = logo
    if win.keys_pressed.get(CTRL) and win.keys_pressed.get(LEFT):
        switch_theme(True)
        logo = put_logo(render, win, theme_names, theme_index)
        if logo:
            logo_ptr, logo_width, logo_height = logo
    if win.keys_pressed.get(R):
        change_maze()
    if win.keys_pressed.get(UP):
        try:
            h += 1
            sleep(0.2)
            change_maze()
            print(h)
        except ValueError:
            h -= 1
    if win.keys_pressed.get(DOWN):
        h = h - 1 if h > 3 else h
        sleep(0.2)
        change_maze()

    if win.keys_pressed.get(RIGHT) and not win.keys_pressed.get(CTRL):
        try:
            w += 1
            sleep(0.2)
            change_maze()
        except ValueError:
            w -= 1
    if win.keys_pressed.get(LEFT) and not win.keys_pressed.get(CTRL):
        w = w - 1 if w > 3 else w
        sleep(0.2)
        change_maze()

    if win.keys_pressed.get(H):
        show_img(True)
    else:
        show_img(False)


def show_img(overlay: bool = False) -> None:
    global themes
    if overlay:
        if not active_theme.get('path'):
            path = []
            bg: dict[str, Any] = win.create_copy(active_theme['bg'])
            color: int = maze_themes[theme_names[theme_index]][2]
            generator: Callable = render.draw_path
            for i in generator(maze, win, bg, color):
                path.append(i)
            active_theme['path'] = path

            active_theme['path'] = path
        for img in active_theme.get('path'):
            win.mlx.mlx_put_image_to_window(win.mlx_ptr,
                                            win.win_ptr,
                                            img['ptr'],
                                            0, 0)
            if logo:
                win.mlx.mlx_put_image_to_window(win.mlx_ptr,
                                                win.win_ptr,
                                                logo_ptr,
                                                (win.width - logo_width) // 2,
                                                render.margin_tb)

            win.mlx.mlx_do_sync(win.mlx_ptr)
            sleep(0.05)

    else:
        win.mlx.mlx_put_image_to_window(win.mlx_ptr,
                                        win.win_ptr,
                                        active_theme['bg']['ptr'],
                                        0, 0)
        if logo:
            win.mlx.mlx_put_image_to_window(win.mlx_ptr,
                                            win.win_ptr,
                                            logo_ptr,
                                            (win.width - logo_width) // 2,
                                            render.margin_tb)


def reset_entry_exit() -> None:
    global entry, exit
    available_coor = []
    for y in range(h):
        for x in range(w):
            available_coor.append((x, y))
    available_coor = [x for x in available_coor if x not in maze.logo_cells]
    entry = rd.choice(available_coor)
    available_coor = [x for x in available_coor if x != entry]
    exit = rd.choice(available_coor)


# ============= First Render =============

win.mlx.mlx_put_image_to_window(win.mlx_ptr,
                                win.win_ptr,
                                active_theme['bg']['ptr'],
                                0, 0)

# ============= Loops =============

win.mlx.mlx_loop_hook(win.mlx_ptr, key_actions, None)
win.mlx.mlx_loop(win.mlx_ptr)
