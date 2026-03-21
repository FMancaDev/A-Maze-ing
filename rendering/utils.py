from mazegen.generator import MazeGenerator
from .Renderer import Renderer
from . Window import Window
from typing import Any, Optional, Callable
import sys
from dataclasses import dataclass
from time import perf_counter, sleep
import random as rd


maze_themes: dict[str, list[int, int, int]] = {
    'Los Angeles': [0xFF9933FF, 0xFFFFCC00, 0xFF33CCFF],
    'City Pop': [0xFFFF0066, 0xFF00FFEA, 0xFFFFFF66],
    'Pastel': [0xFF7E8F6A, 0xFFE9A1F2, 0xFFF2C2A1],
    'Fortune Cookie': [0xFFAF0000, 0xFFBFB05F, 0xFF000000],
}


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
    img_stack: dict[str, dict[str, dict]]
    theme_names: list[str]
    theme_index: int
    active_theme: dict[str, Any]
    last_change: float


def change_maze(current: CurrentState, delay: float) -> Optional[CurrentState]:
    """will randomly generate a new maze following active sizes"""
    # win.mlx.mlx_clear_window(win.mlx_ptr, win.win_ptr)
    now: float = perf_counter()
    last_change: float = current.last_change
    if now - last_change < delay:
        return current
    current.last_change = now

    current: CurrentState = reset_entry_exit(current)
    w: int = current.w
    h: int = current.h
    maze_type: str = current.maze_type
    algo: str = current.algo
    entry: tuple[int, int] = current.entry
    exit: tuple[int, int] = current.exit
    render: Renderer = current.render
    win: Window = current.win
    theme_names: list[str] = current.theme_names
    theme_index: int = current.theme_index

    current.maze = MazeGenerator(w, h, entry, exit, rd.randint(0, 999999))
    current.maze.generate(perfect=maze_type, method=algo)
    current.img_stack = load_themes(current.maze, render, win, maze_themes)
    current.active_theme = current.img_stack[theme_names[theme_index]]
    return current


def reset_entry_exit(current: CurrentState) -> CurrentState:
    """resets entry/ exit points"""
    available_coor = []
    for y in range(current.h):
        for x in range(current.w):
            available_coor.append((x, y))
    available_coor = [x for x in available_coor if
                      x not in current.maze.logo_cells]
    current.entry = rd.choice(available_coor)
    available_coor = [x for x in available_coor if x != current.entry]
    current.exit = rd.choice(available_coor)
    return current


def load_themes(maze: MazeGenerator,
                render: Renderer,
                win: Window,
                maze_themes: dict[str, list[int, int, int]] =
                maze_themes) -> dict[str, dict]:
    img_stack: dict[str, dict] = {}
    for name, colors in maze_themes.items():
        bg: dict[str, Any] = win.create_img()
        render.fill_rect((0, 0), (win.width, win.height), colors[0], bg)
        render.draw_maze(maze, bg, colors[1])
        img_stack[name] = {'bg': bg}

    return img_stack


def switch_theme(current: CurrentState, delay: float,
                 reverse: bool = False) -> CurrentState:
    """Will circle between themes"""
    now: float = perf_counter()
    if now - current.last_change < delay:
        return current
    current.last_change = now

    theme_names: list[str] = current.theme_names
    theme_index: int = current.theme_index
    img_stack: dict = current.img_stack

    if reverse:
        current.theme_index = (theme_index - 1) % len(theme_names)
    else:
        current.theme_index = (theme_index + 1) % len(theme_names)
    current.active_theme = img_stack[theme_names[theme_index]]
    print(f'Theme set: "{theme_names[theme_index]}"')
    return current


# =================================


def parse_config(filename) -> tuple:
    """Parses and validates the maze configuration file robustly."""
    conf = {}
    required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]

    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = [x.strip() for x in line.split("=", 1)]
                if k in conf:
                    sys.exit(f"\nError: Duplicate key '{k}'")
                conf[k] = v

        for r in required:
            if r not in conf:
                sys.exit(f"\nError: Missing mandatory key '{r}'")

        # Validacao de WIDTH e HEIGHT
        try:
            w = int(conf["WIDTH"])
            h = int(conf["HEIGHT"])
        except ValueError:
            sys.exit("\nError: WIDTH and HEIGHT must be integers")

        if w < 1 or h < 1:
            sys.exit("\nError: WIDTH and HEIGHT must be positive integers")
        elif w < 3 or h < 3:
            sys.exit("\nError: Minimum dimensions are 3x3")

        # Validacao de ENTRY e EXIT
        for key_name in ["ENTRY", "EXIT"]:
            parts = conf[key_name].split(",")
            if len(parts) != 2:
                sys.exit(f"\nError: {key_name} must have exactly X,Y")
            try:
                coords = tuple(int(x.strip()) for x in parts)
            except ValueError:
                sys.exit(f"\nError: {key_name} coordinates must be integers")
            conf[key_name] = coords

        en = conf["ENTRY"]
        ex = conf["EXIT"]

        for coord, name in [(en, "ENTRY"), (ex, "EXIT")]:
            if not (0 <= coord[0] < w and 0 <= coord[1] < h):
                sys.exit(
                    f"\nError: {name} {coord} is outside maze bounds ({w}x{h})"
                )
        if en == ex:
            sys.exit("\nError: ENTRY and EXIT cannot be the same")

        perfect_val = conf["PERFECT"].strip().lower()
        if perfect_val not in ["true", "false"]:
            sys.exit("\nError: PERFECT must be True or False")
        perfect = (perfect_val == "true")

        gen_algo = conf.get("GEN_ALGO", "backtracking").strip().lower()

        return w, h, en, ex, conf["OUTPUT_FILE"], perfect, gen_algo

    except Exception as e:
        sys.exit(f"\nConfig Error: {e}")


def put_logo(current: CurrentState) -> Optional[tuple]:
    render: Renderer = current.render
    win: Window = current.win
    theme_names: list[str] = current.theme_names
    theme_index: int = current.theme_index
    if not render.logo_area:
        return None
    theme_name: str = 'rendering/logo/' + theme_names[theme_index].lower()
    if render.logo_size == 'small':
        return win.mlx.mlx_xpm_file_to_image(win.mlx_ptr,
                                             (f'{theme_name}_small.xpm'))
    if render.logo_size == 'medium':
        return win.mlx.mlx_xpm_file_to_image(win.mlx_ptr,
                                             (f'{theme_name}_medium.xpm'))
    if render.logo_size == 'big':
        return win.mlx.mlx_xpm_file_to_image(win.mlx_ptr,
                                             (f'{theme_name}_big.xpm'))


def show_img(current: CurrentState, overlay: bool = False) -> None:

    active_theme: dict[str, Any] = current.active_theme
    theme_names: list[str] = current.theme_names
    theme_index: int = current.theme_index
    maze: MazeGenerator = current.maze
    win: Window = current.win

    if overlay:
        if not active_theme.get('path'):
            path: list = []
            bg: dict[str, Any] = current.win.create_copy(active_theme['bg'])
            color: int = maze_themes[theme_names[theme_index]][2]
            generator: Callable = current.render.draw_path
            for i in generator(maze, win, bg, color):
                path.append(i)
            current.active_theme['path'] = path

        for img in current.active_theme.get('path'):
            win.mlx.mlx_put_image_to_window(win.mlx_ptr,
                                            win.win_ptr,
                                            img['ptr'],
                                            0, 0)
            if current.render.logo_area:
                logo_ptr, logo_width, logo_height = put_logo(current)
                win.mlx.mlx_put_image_to_window(win.mlx_ptr,
                                                win.win_ptr,
                                                logo_ptr,
                                                (win.width - logo_width) // 2,
                                                current.render.margin_tb)

            win.mlx.mlx_do_sync(win.mlx_ptr)
            sleep(0.05)

    else:
        win.mlx.mlx_put_image_to_window(win.mlx_ptr,
                                        win.win_ptr,
                                        active_theme['bg']['ptr'],
                                        0, 0)
        if current.render.logo_area:
            logo_ptr, logo_width, logo_height = put_logo(current)
            win.mlx.mlx_put_image_to_window(win.mlx_ptr,
                                            win.win_ptr,
                                            logo_ptr,
                                            (win.width - logo_width) // 2,
                                            current.render.margin_tb)


def welcome_message() -> None:
    print("""
 █████╗       ███╗   ███╗ █████╗ ███████╗███████╗    ██╗███╗   ██╗ ██████╗
██╔══██╗      ████╗ ████║██╔══██╗╚══███╔╝██╔════╝    ██║████╗  ██║██╔════╝
███████║█████╗██╔████╔██║███████║  ███╔╝ █████╗█████╗██║██╔██╗ ██║██║  ███╗
██╔══██║╚════╝██║╚██╔╝██║██╔══██║ ███╔╝  ██╔══╝╚════╝██║██║╚██╗██║██║   ██║
██║  ██║      ██║ ╚═╝ ██║██║  ██║███████╗███████╗    ██║██║ ╚████║╚██████╔╝
╚═╝  ╚═╝      ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝    ╚═╝╚═╝  ╚═══╝ ╚═════╝
""")
