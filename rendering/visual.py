from mlx import Mlx
from typing import Any
from ctypes import c_void_p, c_uint
import sys

mlx: Mlx = Mlx()
mlx_ptr: c_void_p = mlx.mlx_init()
win_ptr: c_void_p = mlx.mlx_new_window(mlx_ptr, 800, 600, "A_Maze_Ing")

img_ptr: int = mlx.mlx_new_image(mlx_ptr, 800, 600)
data: memoryview
bpp: c_uint
size_line: c_uint
fmt: c_uint
data, bpp, size_line, fmt = mlx.mlx_get_data_addr(img_ptr)


def put_pixel(data: memoryview,
              x: c_uint, y: c_uint,
              color: c_uint,
              size_line: c_uint,
              bpp: c_uint) -> None:
    offset: c_uint = y * size_line + x * (bpp // 8)
    data[offset] = color & 0xFF
    data[offset + 1] = (color >> 8) & 0xFF
    data[offset + 2] = (color >> 16) & 0xFF
    data[offset + 3] = (color >> 24) & 0xFF


for y in range(100, 150):
    for x in range(100, 150):
        put_pixel(data, x, y, 0xFFFFFFFF, size_line, bpp)


def expose_handler(param: Any) -> None:
    mlx.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 0, 0)


def quit_app(param: Any = None) -> None:
    """destroys window, the loop and exits program"""
    mlx.mlx_destroy_window(mlx_ptr, win_ptr)
    mlx.mlx_loop_exit(mlx_ptr)
    sys.exit(0)


keys_pressed: dict[str, bool] = {}


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


# mlx.mlx_string_put(mlx_ptr, win_ptr, 200, 200, 0xFFFFFF, "Hello MLX!")
mlx.mlx_hook(win_ptr, 2, 1, on_keypress, None)
mlx.mlx_hook(win_ptr, 3, 2, on_release, None)
mlx.mlx_hook(win_ptr, 33, 0, quit_app, None)

mlx.mlx_hook(win_ptr, 12, 0x8000, expose_handler, None)
mlx.mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, 0, 0)

mlx.mlx_loop(mlx_ptr)
