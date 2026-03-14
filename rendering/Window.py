from mlx import Mlx
from ctypes import c_void_p, c_uint
from typing import Any
import os
from .constants import (ESC_KEYCODE, CTRL_KEYCODE,
                        C_KEYCODE, D_KEYCODE)


class Window():
    def __init__(self, w: int = 800, h: int = 600,
                 name: str = 'A_Maze_Ing') -> None:
        self.mlx: Mlx = Mlx()
        self.mlx_ptr: c_void_p = self.mlx.mlx_init()

        try:
            if not isinstance(w, int):
                raise TypeError('w')
            if not isinstance(h, int):
                raise TypeError('h')
            if not isinstance(name, str):
                raise TypeError('name')
            self.width: int = w
            self.height: int = h
            self.name: str = name

        except TypeError as e:
            match e:
                case 'w':
                    print('[ERROR]: Wrong w type entered.')
                    print('w set to 800')
                    self.width = 800
                case 'h':
                    print('[ERROR]: Wrong h type entered.')
                    print('h set to 600')
                    self.height = 600
                case 'name':
                    print('[ERROR]: Wrong name type entered.')
                    print('name set to "A_Maze_Ing"')
                    self.name: str = "A_Maze_Ing"

        self.win_ptr: c_void_p = self.mlx.mlx_new_window(
            self.mlx_ptr,
            self.width,
            self.height,
            self.name)
        if hasattr(self.mlx, "mlx_do_key_autorepeatoff"):
            try:
                self.mlx.mlx_do_key_autorepeatoff(self.mlx_ptr)
            except Exception:
                pass
        self.keys_pressed: dict[str, bool] = {}
        self.mlx.mlx_hook(self.win_ptr, 2, 1, self.on_keypress, None)
        self.mlx.mlx_hook(self.win_ptr, 3, 2, self.on_release, None)
        self.mlx.mlx_hook(self.win_ptr, 33, 0, self.quit_prg, None)

    def quit_prg(self, param: Any = None) -> None:
        """destroys window, the loop and exits program"""
        self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        self.mlx.mlx_loop_exit(self.mlx_ptr)
        os._exit(0)

    def on_keypress(self, keycode: int, param: Any) -> None:
        """checks and stores pressed keys, and checks for combos
        that can kill the program"""
        print("Key:", keycode)
        if keycode == ESC_KEYCODE:
            print('<ESC> pressed. Quitting...')
            self.quit_prg()
        self.keys_pressed[keycode] = True
        self.check_combo()

    def check_combo(self) -> None:
        """checks for pressed key combinations"""
        if (self.keys_pressed.get(CTRL_KEYCODE) and
           self.keys_pressed.get(C_KEYCODE)):
            print('<Ctr+C> pressed. Quitting...')
            self.quit_prg()
        if (self.keys_pressed.get(CTRL_KEYCODE) and
           self.keys_pressed.get(D_KEYCODE)):
            print('<Ctrl+D> pressed. Quitting...')
            self.quit_prg()

    def on_release(self, keycode: int, param: Any) -> None:
        """sets the key state as False upon release"""
        if keycode in self.keys_pressed:
            self.keys_pressed[keycode] = False
            print('Key released:', keycode)

    def create_img(self) -> dict[str, Any]:
        img_ptr: c_void_p = self.mlx.mlx_new_image(
            self.mlx_ptr,
            self.width,
            self.height
        )

        data: memoryview
        bpp: c_uint
        size_line: c_uint
        fmt: c_uint
        data, bpp, size_line, fmt = self.mlx.mlx_get_data_addr(img_ptr)

        return {
            'ptr': img_ptr,
            'data': data,
            'bpp': bpp,
            'size_line': size_line,
            'fmt': fmt,
        }

    def create_copy(self, img: dict[str, Any]) -> dict:

        overlay: dict[str, Any] = self.create_img()
        overlay['data'][:] = img['data'][:]
        return overlay
