from mlx import Mlx
from typing import Any
import sys

mlx: Mlx = Mlx()
mlx_ptr = mlx.mlx_init()
win_ptr = mlx.mlx_new_window(mlx_ptr, 800, 600, "A_Maze_Ing")


def quit_app(param: Any = None) -> None:
    """destroys window, the loop and exits program"""
    mlx.mlx_destroy_window(mlx_ptr, win_ptr)
    mlx.mlx_loop_exit(mlx_ptr)
    sys.exit(0)


keys_pressed: dict = {}


def on_keypress(keycode: int, param: Any) -> None:
    """checks and stores pressed keys, and checks for combos
    that can kill the program"""
    print("Key:", keycode)
    if keycode == 65307:
        quit_app()
    keys_pressed[keycode] = True
    check_combo()


def check_combo() -> None:
    """checks for pressed key combinations"""
    if keys_pressed.get(65507) and (keys_pressed.get(99) or
                                    keys_pressed.get(100)):
        quit_app()


def on_release(keycode: int, param: Any) -> None:
    """sets the key state as False upon release"""
    keys_pressed[keycode] = False


img_ptr = mlx.mlx_new_image(mlx_ptr, 800, 600)
data, bpp, size_line, fmt = mlx.mlx_get_data_addr(img_ptr)


def put_pixel(data, size_line, bpp, x, y, color):
    bytes_per_pixel = bpp // 8
    offset = y * size_line + x * bytes_per_pixel
    data[offset + 0] = color & 0xFF
    data[offset + 1] = (color >> 8) & 0xFF
    data[offset + 2] = (color >> 16) & 0xFF
    data[offset + 3] = 0


for y in range(100, 200):
    for x in range(100, 200):
        put_pixel(data, size_line, bpp, x, y, 0xFF0000)
mlx.mlx_pixel_put(mlx_ptr, win_ptr, 100, 100, 0xFF0000)
# mlx.mlx_string_put(mlx_ptr, win_ptr, 200, 200, 0xFFFFFF, "Hello MLX!")

mlx.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 0, 0)
mlx.mlx_hook(win_ptr, 2, 1, on_keypress, None)
mlx.mlx_hook(win_ptr, 3, 2, on_release, None)
mlx.mlx_hook(win_ptr, 33, 0, quit_app, None)

mlx.mlx_loop(mlx_ptr)
