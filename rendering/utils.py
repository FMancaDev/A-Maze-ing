from dataclasses import dataclass
from mazegen.generator import MazeGenerator
from .Renderer import Renderer
from . Window import Window
from typing import Any
import sys


@dataclass
class MazeConfig:
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    gen_algo: str


def parse_config(filename) -> MazeConfig:
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

        return MazeConfig(w, h, en, ex, conf["OUTPUT_FILE"], perfect, gen_algo)

    except Exception as e:
        sys.exit(f"\nConfig Error: {e}")


def load_themes(maze: MazeGenerator,
                render: Renderer,
                win: Window,
                maze_themes: dict[str, list]) -> dict[str, dict]:
    img_stack: dict[str, dict] = {}
    for name, colors in maze_themes.items():
        bg: dict[str, Any] = win.create_img()
        render.fill_rect((0, 0), (win.width, win.height), colors[0], bg)
        render.draw_maze(maze, bg, colors[1])
        img_stack[name] = {'bg': bg}

    return img_stack


def welcome_message() -> None:
    print("""
 █████╗       ███╗   ███╗ █████╗ ███████╗███████╗    ██╗███╗   ██╗ ██████╗
██╔══██╗      ████╗ ████║██╔══██╗╚══███╔╝██╔════╝    ██║████╗  ██║██╔════╝
███████║█████╗██╔████╔██║███████║  ███╔╝ █████╗█████╗██║██╔██╗ ██║██║  ███╗
██╔══██║╚════╝██║╚██╔╝██║██╔══██║ ███╔╝  ██╔══╝╚════╝██║██║╚██╗██║██║   ██║
██║  ██║      ██║ ╚═╝ ██║██║  ██║███████╗███████╗    ██║██║ ╚████║╚██████╔╝
╚═╝  ╚═╝      ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝    ╚═╝╚═╝  ╚═══╝ ╚═════╝
""")
