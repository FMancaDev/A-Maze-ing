from mlx import Mlx
from typing import Any
from ctypes import c_void_p, c_uint
import os


class RenderMaze():
    def __init__(self, w: int = 800, h: int = 600,
                 name: str = 'A_Maze_Ing') -> None:
        self.mlx: Mlx = Mlx()
        self.mlx_ptr: c_void_p = self.mlx.mlx_init()
        self.win_dim: dict[str | int] = {}

        try:
            if not isinstance(w, int):
                raise TypeError('w')
            if not isinstance(h, int):
                raise TypeError('h')
            if not isinstance(name, str):
                raise TypeError('name')
            self.win_dim['width'] = w
            self.win_dim['height'] = h
            self.name: str = name

        except TypeError as e:
            match e:
                case 'w':
                    print('[ERROR]: Wrong w type entered.')
                    print('w set to 800')
                    self.win_dim['width'] = 800
                case 'h':
                    print('[ERROR]: Wrong h type entered.')
                    print('h set to 600')
                    self.win_dim['height'] = 600
                case 'name':
                    print('[ERROR]: Wrong name type entered.')
                    print('name set to "A_Maze_Ing"')
                    self.name: str = "A_Maze_Ing"

        self.win_ptr: c_void_p = self.mlx.mlx_new_window(
                                                self.mlx_ptr,
                                                self.win_dim['width'],
                                                self.win_dim['height'],
                                                self.name)
        self.keys_pressed: dict[str, bool] = {}
        self.mlx.mlx_hook(self.win_ptr, 2, 1, self.on_keypress, None)
        self.mlx.mlx_hook(self.win_ptr, 3, 2, self.on_release, None)
        self.mlx.mlx_hook(self.win_ptr, 33, 0, self.quit_prg, None)
        self.img: dict[str | Any] = {}

    def create_image(self) -> None:
        self.img_ptr: c_void_p = self.mlx.mlx_new_image(self.mlx_ptr,
                                                        self.win_dim['width'],
                                                        self.win_dim['height'])
        data: memoryview
        bpp: c_uint
        size_line: c_uint
        fmt: c_uint
        data, bpp, size_line, fmt = self.mlx.mlx_get_data_addr(self.img_ptr)
        self.mlx.mlx_hook(self.win_ptr, 12, 0x8000, self.expose_handler, None)
        self.mlx.mlx_put_image_to_window(self.mlx_ptr,
                                         self.win_ptr,
                                         self.img_ptr, 0, 0)
        self.img = {
            'data': data,
            'bpp': bpp,
            'size_line': size_line,
            'fmt': fmt,
        }

    def put_pixel(self, data: memoryview,
                  x: c_uint, y: c_uint,
                  color: c_uint,
                  size_line: c_uint,
                  bpp: c_uint) -> None:
        """draws pixel to img buffer"""
        if (x < 0 or x >= self.win_dim['width'] or
           y < 0 or y >= self.win_dim['height']):
            return
        offset: c_uint = y * size_line + x * (bpp // 8)
        data[offset] = color & 0xFF
        data[offset + 1] = (color >> 8) & 0xFF
        data[offset + 2] = (color >> 16) & 0xFF
        data[offset + 3] = (color >> 24) & 0xFF

    def expose_handler(self, param: Any) -> None:
        """handler passed to hook in order to display img"""
        self.mlx.mlx_put_image_to_window(self.mlx_ptr,
                                         self.win_ptr,
                                         self.img_ptr, 0, 0)

    def quit_prg(self, param: Any = None) -> None:
        """destroys window, the loop and exits program"""
        self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        self.mlx.mlx_loop_exit(self.mlx_ptr)
        os._exit(0)

    def on_keypress(self, keycode: int, param: Any) -> None:
        """checks and stores pressed keys, and checks for combos
        that can kill the program"""
        print("Key:", keycode)
        if keycode == 65307:
            print('<ESC> pressed. Quitting...')
            self.quit_prg()
        self.keys_pressed[keycode] = True
        self.check_combo()

    def check_combo(self) -> None:
        """checks for pressed key combinations"""
        if self.keys_pressed.get(65507) and self.keys_pressed.get(99):
            print('<Ctr+C> pressed. Quitting...')
            self.quit_prg()
        if self.keys_pressed.get(65507) and self.keys_pressed.get(100):
            print('<Ctrl+D> pressed. Quitting...')
            self.quit_prg()

    def on_release(self, keycode: int, param: Any) -> None:
        """sets the key state as False upon release"""
        self.keys_pressed[keycode] = False

    def set_layout(self, maze_lines: list) -> None:
        columns: int = len(maze_lines[0])
        rows: int = len(maze_lines)

        margin: float = 0.8
        active_w: int = round(self.win_dim['width'] * margin)
        active_h: int = round(self.win_dim['height'] * margin)

        cell_size: int = 0

        if columns >= rows:
            if active_w // columns < 3:
                raise ValueError('Active area isn\'t '
                                 'big enough for maze height')
            cell_size = active_w // columns

        else:
            if active_h // rows < 3:
                raise ValueError('Active area isn\'t '
                                 'big enough for maze height')
            cell_size = active_h // rows

        self.maze_grid: dict[str, int] = {
            'width': active_w,
            'height': active_h,
            'cell_size': cell_size,
            'margin': (self.win_dim['width'] - active_w) // 2 if (
                columns >= rows) else (self.win_dim['height'] - active_h) // 2,
            'border_thickness': 1 if cell_size < 5 else cell_size // 5
        }

    def draw_line(self, start: tuple, end: tuple, color: int) -> None:
        """using Bresenham\'s algorithm to draw lines"""
        x0: int = start[0]
        x1: int = end[0]
        y0: int = start[1]
        y1: int = end[1]

        dx: int = abs(x1 - x0)
        dy: int = -abs(y1 - y0)
        sx: int = 1 if x0 < x1 else -1
        sy: int = 1 if y0 < y1 else -1
        error: int = dx + dy

        while True:
            self.put_pixel(self.img['data'],
                           x0, y0, color,
                           self.img['size_line'], self.img['bpp'])
            if x0 == x1 and y0 == y1:
                break
            e2: int = 2 * error
            if e2 >= dy:
                error += dy
                x0 += sx
            if e2 <= dx:
                error += dx
                y0 += sy

    def draw_thick_line(self, start: tuple, end: tuple, color: int,
                        thickness: int) -> None:
        dx: int = end[0] - start[0]
        dy: int = end[1] - start[1]
        half: int = thickness // 2

        if abs(dx) >= abs(dy):
            for i in range(-half, half + 1):
                self.draw_line((start[0] - half, start[1] + i),
                               (end[0] + half, end[1] + i), color)
        else:
            for i in range(-half, half + 1):
                self.draw_line((start[0] + i, start[1] - half),
                               (end[0] + i, end[1] + half), color)

    def draw_frame(self, maze_lines: list):
        self.set_layout(maze_lines)
        cor: dict[str | tuple] = {
            'tl': (self.maze_grid['margin'],
                   self.maze_grid['margin']),

            'tr': (self.maze_grid['margin'] + self.maze_grid['width'],
                   self.maze_grid['margin']),

            'bl': (self.maze_grid['margin'],
                   self.maze_grid['margin'] + self.maze_grid['height']),

            'br': (self.maze_grid['margin'] + self.maze_grid['width'],
                   self.maze_grid['margin'] + self.maze_grid['height']),
        }
        self.draw_thick_line(cor['tl'], cor['tr'],
                             0xFFFFFFFF, self.maze_grid['border_thickness'])
        self.draw_thick_line(cor['tl'], cor['bl'],
                             0xFFFFFFFF, self.maze_grid['border_thickness'])
        self.draw_thick_line(cor['bl'], cor['br'],
                             0xFFFFFFFF, self.maze_grid['border_thickness'])
        self.draw_thick_line(cor['br'], cor['tr'],
                             0xFFFFFFFF, self.maze_grid['border_thickness'])
