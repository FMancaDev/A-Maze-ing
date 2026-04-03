from .Renderer import Renderer
from .Window import Window
from mazegen.generator import MazeGenerator
from typing import Any, Optional, Generator, cast
import sys
import os
from time import perf_counter
from dataclasses import dataclass
import random as rd

maze_themes: dict[str, list[int]] = {
    'Los Angeles': [0xFF9933FF, 0xFFFFCC00, 0xFF33CCFF],
    'City Pop': [0xFFFF0066, 0xFF00FFEA, 0xFFFFFF66],
    'Pastel': [0xFF7E8F6A, 0xFFE9A1F2, 0xFFF2C2A1],
    'Fortune Cookie': [0xFFAF0000, 0xFFBFB05F, 0xFF000000],
}


def argb_to_rgb(argb: int) -> tuple[int, int, int]:
    r: int = (argb >> 16) & 0xFF
    g: int = (argb >> 8) & 0xFF
    b: int = argb & 0xFF
    return r, g, b


def argb_to_ansi(argb: int) -> str:
    r, g, b = argb_to_rgb(argb)
    return f'\x1b[38;2;{r};{g};{b}m'


@dataclass
class CurrentState:
    """saves the state of the program at any given time"""
    win: Window
    render: Renderer
    maze: MazeGenerator
    w: int
    h: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    maze_type: str
    algo: str
    img_stack: dict[str, Any]
    theme_names: list[str]
    starter_frame: Optional[dict[str, Any]] = None
    theme_index: int = 0
    active_theme: Optional[dict[str, Any]] = None
    last_change: Optional[float] = None
    algo_gen: Optional[Generator] = None
    algo_anim: bool = True
    base_img: bool = False
    logo: Optional[tuple] = None
    rerender_delay: float = 0.2
    last_rerender: float = 0
    animating: bool = False
    frame_index: int = 0
    last_frame_change: float = 0
    frame_delay: float = 0.05


def starter(current: CurrentState, gen_speed: float = 0.0,
            path_speed: float = 0.0) -> CurrentState:
    win = current.win
    render = current.render
    maze = current.maze
    theme_names = current.theme_names
    theme_index = current.theme_index

    bg_color = maze_themes[theme_names[theme_index]][0]
    fg_color = maze_themes[theme_names[theme_index]][1]
    path_color = maze_themes[theme_names[theme_index]][2]

    current.algo_gen = maze.generate(perfect=(current.maze_type == "perfect"),
                                     method=current.algo)

    if current.algo_gen:
        next(current.algo_gen)

    frame = win.create_img()
    render.draw_maze(maze, frame, fg_color=fg_color,
                     bg_color=bg_color, generation=True)
    current.starter_frame = frame

    if not current.maze_type:
        maze._make_imperfect()
    maze._seal_logo()

    current.img_stack = load_themes(maze, render, win, maze_themes)
    current.active_theme = current.img_stack[theme_names[theme_index]]

    # Check if active_theme is not None for MyPy
    if current.active_theme:
        bg = win.create_copy(current.active_theme['bg'])
        path_frames: list[dict[str, Any]] = [bg]

        for path_frame in render.draw_path(maze, win, bg,
                                           fg_color, path_color):
            path_frames.append(path_frame)

        current.active_theme['path'] = path_frames

    current.frame_index = 0
    current.algo_anim = True
    current.base_img = False
    return current


def print_menu(current: CurrentState) -> None:
    theme_names = current.theme_names
    theme_index = current.theme_index

    theme_color_code = argb_to_ansi(maze_themes[theme_names[theme_index]][0])
    reset, green, yellow, cyan = '\x1b[0m', '\x1b[32m', '\x1b[33m', '\x1b[36m'

    seed_val, theme_val = str(current.maze.seed), theme_names[theme_index]
    size_val, algo_val = f"{current.w}x{current.h}", current.algo

    seed_line = f"{yellow}Seed:{reset}    {seed_val:<28}"
    theme_line = (f"{yellow}Theme:{reset}   " +
                  f"{theme_color_code}{theme_val:<27}{reset}")
    size_line = f"{yellow}Size:{reset}    {size_val:<28}"
    algo_line = f"{yellow}Algo:{reset}    {algo_val:<28}"

    print(f"""
{cyan}╔══════════════════════════════════════╗
║            A-MAZE-ING MENU           ║
╠══════════════════════════════════════╣
║ {seed_line}{cyan}║
║ {theme_line}{cyan} ║
║ {size_line}{cyan}║
║ {algo_line}{cyan}║
╠══════════════════════════════════════╣
║ {green}Controls:{reset}                            {cyan}║
║  {green}R{reset}          → Regenerate maze        {cyan}║
║  {green}H{reset}          → Show/hide path         {cyan}║
║  {green}CTRL ← →{reset}   → Change theme           {cyan}║
║  {green}← →{reset}        → Change width           {cyan}║
║  {green}↑ ↓{reset}        → Change height          {cyan}║
║  {green}ESC{reset}        → Quit                   {cyan}║
╚══════════════════════════════════════╝{reset}
""")


def change_maze(current: CurrentState) -> CurrentState:
    now = perf_counter()
    if current.last_rerender != 0 and now - (current.last_rerender <
                                             current.rerender_delay):
        return current
    current.last_rerender = now

    en_x, en_y = current.entry
    ex_x, ex_y = current.exit

    current.entry = (min(en_x, current.w - 1), min(en_y, current.h - 1))
    current.exit = (min(ex_x, current.w - 1), min(ex_y, current.h - 1))

    if current.entry == current.exit:
        current = reset_entry_exit(current)

    logo_cells = get_logo_coords(current.w, current.h)

    if current.entry in logo_cells or current.exit in logo_cells:
        print("\033[0;31m\nError: Entry/Exit hit logo during resize\033[0m")
        os._exit(0)

    current.maze = MazeGenerator(
        current.w, current.h, current.entry, current.exit)

    current = starter(current)
    print_menu(current)
    return current


def reset_entry_exit(current: CurrentState) -> CurrentState:
    available_coor = [(x, y) for y in range(current.h)
                      for x in range(current.w)]
    available_coor = [
        c for c in available_coor if c not in current.maze.logo_cells]
    current.entry = rd.choice(available_coor)
    available_coor = [c for c in available_coor if c != current.entry]
    current.exit = rd.choice(available_coor)
    return current


def load_themes(maze: MazeGenerator, render: Renderer, win: Window,
                themes: dict[str, list[int]] = maze_themes) -> dict[str, Any]:
    img_stack: dict[str, Any] = {}
    for name, colors in themes.items():
        bg = win.create_img()
        render.fill_rect((0, 0), (win.width, win.height), colors[0], bg)
        render.draw_maze(maze, bg, colors[1], colors[0])
        img_stack[name] = {'bg': bg}
    return img_stack


def switch_theme(current: CurrentState, reverse: bool = False) -> CurrentState:
    now = perf_counter()
    if now - current.last_rerender < current.rerender_delay:
        return current
    current.last_rerender = now

    idx_mod = -1 if reverse else 1
    current.theme_index = (current.theme_index +
                           idx_mod) % len(current.theme_names)
    current.active_theme = (current.img_stack[current.theme_names
                            [current.theme_index]])
    current.logo = put_logo(current)
    print_menu(current)
    return current


def get_logo_coords(w: int, h: int) -> list[tuple[int, int]]:
    if w < 10 or h < 8:
        return []
    atual_x, atual_y = w // 2, h // 2
    pattern = ["X X XXX", "X X   X", "XXX XXX", "  X X  ", "  X XXX"]
    coords = []
    start_x = atual_x - len(pattern[0]) // 2
    start_y = atual_y - len(pattern) // 2
    for index_y, row in enumerate(pattern):
        for index_x, c in enumerate(row):
            if c == "X":
                x, y = start_x + index_x, start_y + index_y
                if 0 <= x < w and 0 <= y < h:
                    coords.append((x, y))
    return coords


def parse_config(filename: str) -> (tuple[int, int, tuple[int, int],
                                    tuple[int, int], str, bool, str]):
    conf: dict[str, Any] = {}
    required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = [x.strip() for x in line.split("=", 1)]
            conf[k] = v

    for r in required:
        if r not in conf:
            sys.exit(f"Missing {r}")

    w, h = int(conf["WIDTH"]), int(conf["HEIGHT"])
    en = tuple(int(x) for x in conf["ENTRY"].split(","))
    ex = tuple(int(x) for x in conf["EXIT"].split(","))

    # Cast para garantir o tipo da tupla para o MyPy
    entry_tpl = cast(tuple[int, int], tuple(en))
    exit_tpl = cast(tuple[int, int], tuple(ex))

    perfect = conf["PERFECT"].lower() == "true"
    gen_algo = conf.get("GEN_ALGO", "backtracking").strip().lower()

    return w, h, entry_tpl, exit_tpl, conf["OUTPUT_FILE"], perfect, gen_algo


def put_logo(current: CurrentState) -> Optional[tuple]:
    render, win = current.render, current.win
    if not render.logo_area:
        return None

    path = f'rendering/logo/{current.theme_names[current.theme_index].lower()}'
    size = render.logo_size
    return win.mlx.mlx_xpm_file_to_image(win.mlx_ptr, f'{path}_{size}.xpm')


def show_img(current: CurrentState, overlay: bool = False) -> None:
    if not current.active_theme:
        return

    active_theme = current.active_theme
    render, win, maze = current.render, current.win, current.maze
    theme_colors = maze_themes[current.theme_names[current.theme_index]]
    bg_color, fg_color, path_color = (theme_colors[0],
                                      theme_colors[1], theme_colors[2])

    now = perf_counter()
    if now - current.last_frame_change < current.frame_delay:
        return
    current.last_frame_change = now

    if current.algo_anim:
        if current.algo_gen and current.starter_frame:
            try:
                cell = next(current.algo_gen)
                frame = current.starter_frame
                render.draw_maze(maze, frame, fg_color, bg_color, True)
                cs = render.cell_size
                tlx, tly = render.coor['tl']
                cx, cy = cell[0] * cs + tlx, cell[1] * cs + tly
                render.fill_rect((cx + 2, cy + 2),
                                 (cx + cs - 2, cy + cs - 2), path_color, frame)
                win.mlx.mlx_put_image_to_window(
                    win.mlx_ptr, win.win_ptr, frame['ptr'], 0, 0)
            except StopIteration:
                current.algo_anim = False
                import __main__
                if hasattr(__main__, 'save_maze_now'):
                    getattr(__main__, 'save_maze_now')(
                        current, getattr(__main__, 'output_file', 'out.png'))

    elif not current.base_img:
        current.base_img = True
        current.img_stack = load_themes(maze, render, win)
        current.active_theme = (current.img_stack[current.theme_names
                                [current.theme_index]])
        # Recarregar referência após update
        active_theme = current.active_theme
        bg = win.create_copy(active_theme['bg'])
        path_frames: list[dict[str, Any]] = []
        path_frames.append(bg)
        for p_frame in render.draw_path(maze, win, bg, fg_color, path_color):
            if p_frame is not None:
                path_frames.append(p_frame)
        active_theme['path'] = path_frames
        current.frame_index = 0

    elif overlay:
        if not active_theme.get('path'):
            bg_copy = win.create_copy(active_theme['bg'])
            path_list = [bg_copy]
            for f in render.draw_path(maze, win, bg_copy,
                                      fg_color, path_color):
                path_list.append(f)
            active_theme['path'] = path_list

        frames = active_theme['path']
        current.animating = True
        current_frame = frames[current.frame_index]
        if current.frame_index < len(frames) - 1:
            current.frame_index += 1
        win.mlx.mlx_put_image_to_window(
            win.mlx_ptr, win.win_ptr, current_frame['ptr'], 0, 0)

    else:
        if current.animating and current.frame_index == 0:
            current.animating = False

        tmp: None | Any = active_theme.get('path')
        if tmp:
            path_frames = tmp
        # path_frames = active_theme.get('path')
        if current.animating and path_frames:
            current_frame = path_frames[current.frame_index]
            current.frame_index -= 1 if current.frame_index > 0 else 0
            win.mlx.mlx_put_image_to_window(
                win.mlx_ptr, win.win_ptr, current_frame['ptr'], 0, 0)
        else:
            win.mlx.mlx_put_image_to_window(
                win.mlx_ptr, win.win_ptr, active_theme['bg']['ptr'], 0, 0)

    if render.logo_area and current.logo:
        logo_ptr, logo_w, _ = current.logo
        win.mlx.mlx_put_image_to_window(
            win.mlx_ptr, win.win_ptr, logo_ptr, (win.width - logo_w) // 2,
            render.margin_tb)


def welcome_message(current: CurrentState) -> None:
    print("\n A-MAZE-ING GENERATOR LOADED \n")
    print_menu(current)
