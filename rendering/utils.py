from mazegen.generator import MazeGenerator
from .constants import ESC_KEYCODE, CTRL_KEYCODE, C_KEYCODE, D_KEYCODE
from .Renderer import Renderer
from . Window import Window
from typing import Any, Optional, Callable
import sys
from time import perf_counter
from dataclasses import dataclass
import random as rd


maze_themes: dict[str, list[int, int, int]] = {
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
    img_stack: dict[str, dict[str, dict]]
    theme_names: list[str]
    theme_index: int
    active_theme: dict[str, Any]
    last_change: float
    algo_stack: Optional[list] = None
    algo_anim: bool = True
    algo_index: int = 0
    logo: tuple | None = None
    rerender_delay: float = 0.2
    last_rerender: float = 0
    animating: bool = False
    frame_index: int = 0
    last_frame_change: float = 0
    frame_delay: float = 0.05


def starter(current: CurrentState, gen_speed: float = 0.0,
            path_speed: float = 0.0) -> CurrentState:
    """loads all the needed frames and starts by animating the wall breaks"""

    win: Window = current.win
    render: Renderer = current.render
    maze: MazeGenerator = current.maze
    theme_names: list[str] = current.theme_names
    theme_index: int = current.theme_index
    bg_color: int = maze_themes[theme_names[theme_index]][0]
    fg_color: int = maze_themes[theme_names[theme_index]][1]
    path_color: int = maze_themes[theme_names[theme_index]][2]

    # mesma imagem em todos os frames
    frame: dict[str, Any] = win.create_img()
    render.set_layout(maze)
    render.border_thickness = (1 if render.cell_size < 5
                               else render.cell_size // 5)
    anim_stack: list[dict[str, Any]] = []
    anim_stack.append(frame)
    # geracao
    runner = maze.generate(perfect=current.maze_type, method=current.algo)
    for cell in runner:

        # redesenha tudo na mesma imagem
        frame = win.create_copy(frame)
        render.draw_maze(maze, frame, fg_color=fg_color,
                         bg_color=bg_color, generation=True)
        # cursor na celula atual
        cs = render.cell_size
        tlx, tly = render.coor['tl']
        cx = cell[0] * cs + tlx
        cy = cell[1] * cs + tly

        render.fill_rect((cx + 2, cy + 2),
                         (cx + cs - 2, cy + cs - 2),
                         path_color, frame)

        anim_stack.append(frame)

    if not current.maze_type:
        maze._make_imperfect()
    maze._seal_logo()

    # frame final
    render.draw_maze(maze, frame, fg_color, bg_color)
    anim_stack.append(frame)
    current.algo_stack = anim_stack

    # guarda resultado final
    current.img_stack = load_themes(maze, render, win, maze_themes)
    current.active_theme = current.img_stack[theme_names[theme_index]]
    bg: dict[str, Any] = win.create_copy(current.active_theme['bg'])
    path_frames: list = [bg]

    for path_frame in render.draw_path(maze, win, bg, fg_color, path_color):
        path_frames.append(path_frame)
    current.active_theme['path'] = path_frames
    current.frame_index = 0
    current.algo_anim = True
    current.algo_index = 0
    return current


def print_menu(current: CurrentState) -> None:
    theme_names: list[str] = current.theme_names
    theme_index: int = current.theme_index

    # cores
    theme_color_code: str = argb_to_ansi(
        maze_themes[theme_names[theme_index]][0]
    )
    reset: str = '\x1b[0m'
    green: str = '\x1b[32m'
    yellow: str = '\x1b[33m'
    cyan: str = '\x1b[36m'

    seed_val = f"{current.maze.seed}"
    theme_val = f"{theme_names[theme_index]}"
    size_val = f"{current.w}x{current.h}"
    algo_val = f"{current.algo}"

    seed_line = f"{yellow}Seed:{reset}    {seed_val:<28}"
    theme_line = f"{yellow}Theme:{reset}   {theme_color_code}{theme_val:<27}{reset}"
    size_line = f"{yellow}Size:{reset}    {size_val:<28}"
    algo_line = f"{yellow}Algo:{reset}    {algo_val:<28}"

    print(f"""
{cyan}╔══════════════════════════════════════╗
║           A-MAZE-ING MENU            ║
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
║  {green}ESC{reset}        → Quit                   {cyan}║
╚══════════════════════════════════════╝{reset}
""")


def change_maze(current: CurrentState) -> CurrentState:
    """will randomly generate a new maze following active sizes"""

    now: float = perf_counter()
    if now - current.last_change < current.rerender_delay:
        return current
    current.last_rerender = now
    current.maze = MazeGenerator(current.w, current.h,
                                 current.entry, current.exit,
                                 rd.randint(0, 999999))
    current = starter(current)
    print_menu(current)
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
        render.draw_maze(maze, bg, colors[1], colors[0])
        img_stack[name] = {'bg': bg}

    return img_stack


def switch_theme(current: CurrentState,
                 reverse: bool = False) -> CurrentState:
    """Will circle between themes"""
    now: float = perf_counter()
    if now - current.last_rerender < current.rerender_delay:
        return current
    current.last_rerender = now

    theme_names: list[str] = current.theme_names
    theme_index: int = current.theme_index
    img_stack: dict = current.img_stack

    if reverse:
        current.theme_index = (theme_index - 1) % len(theme_names)
    else:
        current.theme_index = (theme_index + 1) % len(theme_names)

    current.active_theme = img_stack[theme_names[current.theme_index]]
    current.logo = put_logo(current)
    print_menu(current)
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

    now: float = perf_counter()
    if now - current.last_frame_change < current.frame_delay:
        return
    current.last_frame_change = now

    if current.algo_anim:
        stack = current.algo_stack
        index = current.algo_index
        if (current.algo_index < len(current.algo_stack)):
            win.mlx.mlx_put_image_to_window(win.mlx_ptr,
                                            win.win_ptr,
                                            stack[index]['ptr'],
                                            0, 0)
            current.algo_index += 1
        else:
            current.algo_index = 0
            current.algo_anim = False

    elif overlay:
        if not active_theme.get('path'):
            print('Generating path...')
            path: list = []
            bg: dict[str, Any] = current.win.create_copy(active_theme['bg'])
            maze_color: int = maze_themes[theme_names[theme_index]][1]
            path_color: int = maze_themes[theme_names[theme_index]][2]
            generator: Callable = current.render.draw_path
            path.append(bg)
            for frame in generator(maze, win, bg, maze_color, path_color):
                bg = win.create_copy(frame)
                path.append(frame)
            current.active_theme['path'] = path
            active_theme = current.active_theme

        frames = active_theme.get('path')
        current.animating = True
        current_frame = frames[current.frame_index]
        if current.frame_index < len(frames) - 1:
            current.frame_index += 1
        win.mlx.mlx_put_image_to_window(win.mlx_ptr,
                                        win.win_ptr,
                                        current_frame['ptr'],
                                        0, 0)
    else:
        if current.animating:
            if current.frame_index == 0:
                current.animating = False
        if current.animating and current.active_theme.get('path'):
            current_frame = current.active_theme['path'][current.frame_index]
            current.frame_index -= 1 if current.frame_index > 0 else 0
            win.mlx.mlx_put_image_to_window(win.mlx_ptr,
                                            win.win_ptr,
                                            current_frame['ptr'],
                                            0, 0)
        else:
            win.mlx.mlx_put_image_to_window(win.mlx_ptr,
                                            win.win_ptr,
                                            active_theme['bg']['ptr'],
                                            0, 0)
    if current.render.logo_area:
        if not current.logo:
            current.logo = put_logo(current)
        logo_ptr, logo_width, logo_height = current.logo
        win.mlx.mlx_put_image_to_window(win.mlx_ptr,
                                        win.win_ptr,
                                        logo_ptr,
                                        (win.width - logo_width) // 2,
                                        current.render.margin_tb)


def welcome_message(current: CurrentState) -> None:
    print("""
 █████╗       ███╗   ███╗ █████╗ ███████╗███████╗    ██╗███╗   ██╗ ██████╗
██╔══██╗      ████╗ ████║██╔══██╗╚══███╔╝██╔════╝    ██║████╗  ██║██╔════╝
███████║█████╗██╔████╔██║███████║  ███╔╝ █████╗█████╗██║██╔██╗ ██║██║  ███╗
██╔══██║╚════╝██║╚██╔╝██║██╔══██║ ███╔╝  ██╔══╝╚════╝██║██║╚██╗██║██║   ██║
██║  ██║      ██║ ╚═╝ ██║██║  ██║███████╗███████╗    ██║██║ ╚████║╚██████╔╝
╚═╝  ╚═╝      ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝    ╚═╝╚═╝  ╚═══╝ ╚═════╝
""")
    print_menu(current)
