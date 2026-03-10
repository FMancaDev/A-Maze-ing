from .Renderer import Renderer
from .Window import Window
from .Maze import Maze
from typing import Any
from .constants import (H_KEYCODE as H,
                        LEFT_ARROW_KEYCODE as L,
                        RIGHT_ARROW_KEYCODE as R,
                        CTRL_KEYCODE as CTRL)


maze_themes: dict[str] = {
    'Los Angeles': [0xFF9933FF, 0xFFFFCC00, 0xFF33CCFF],
    'City Pop': [0xFFFF0066, 0xFF00FFEA, 0xFFFFFF66],
    'Pastel': [0xFF7E8F6A, 0xFFE9A1F2, 0xFFF2C2A1],
    'Fortune Cookie': [0xFFAF0000, 0xFFBFB05F, 0xFF000000],
}

filename: str = 'maze.txt'

win: Window = Window()
render: Renderer = Renderer(win)
maze: Maze = Maze(filename)


maze.set_maze_dim(win.width, win.height)


def draw_base(img: dict[str, Any], theme: list) -> None:
    render.fill_rect({'x0': 0, 'x1':  win.width, 'y0': 0, 'y1': win.height},
                     theme[0], img)
    render.draw_frame(maze.coordinates, maze.border_thickness,
                      theme[1], img)
    render.draw_maze(maze, theme[1], theme[1], img)
    render.draw_triangle(maze, theme[1], img, reverse=False)
    render.draw_triangle(maze, theme[1], img, reverse=True)


img_stack: list[tuple] = []

for name in list(maze_themes.keys()):
    background = win.create_img()
    path = win.create_img()
    draw_base(background, maze_themes[name])
    draw_base(path, maze_themes[name])
    render.draw_path(maze, maze_themes[name][2], path)
    img_stack.append((background, path))


i: int = 0


def check_key(param: Any) -> None:
    global i, theme
    if win.keys_pressed.get(CTRL) and win.keys_pressed.get(L):
        i = (i - 1) % len(img_stack)

    if win.keys_pressed.get(CTRL) and win.keys_pressed.get(R):
        i = (i + 1) % len(img_stack)

    if win.keys_pressed.get(H, False):
        img = img_stack[i][1]
    else:
        img = img_stack[i][0]

    win.mlx.mlx_put_image_to_window(win.mlx_ptr,
                                    win.win_ptr,
                                    img['ptr'], 0, 0)


win.mlx.mlx_loop_hook(win.mlx_ptr, check_key, None)

win.mlx.mlx_loop(win.mlx_ptr)
