from typing import Any, Optional
from ctypes import c_uint
from .Window import Window
from .constants import HEX_TO_WALLS
from .Maze import Maze


class Renderer():
    def __init__(self, window: Window) -> None:
        self.win_width: int = window.width
        self.win_height: int = window.height

    def put_pixel(self, data: memoryview,
                  x: c_uint, y: c_uint,
                  color: c_uint,
                  size_line: c_uint,
                  bpp: c_uint) -> None:
        """draws pixel to img buffer"""
        if (x < 0 or x >= self.win_width or
           y < 0 or y >= self.win_height):
            return
        offset: c_uint = y * size_line + x * (bpp // 8)
        data[offset] = color & 0xFF
        data[offset + 1] = (color >> 8) & 0xFF
        data[offset + 2] = (color >> 16) & 0xFF
        data[offset + 3] = (color >> 24) & 0xFF

    def draw_line(self, start: tuple, end: tuple,
                  color: int, img: dict[str, Any]) -> None:
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
            self.put_pixel(img['data'],
                           x0, y0, color,
                           img['size_line'],
                           img['bpp'])
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
                        thickness: int, img: dict[str, Any]) -> None:
        dx: int = end[0] - start[0]
        dy: int = end[1] - start[1]
        half: int = thickness // 2
        ex = half if dx >= 0 else -half  # extension on x axis
        ey = half if dy >= 0 else -half  # extension on y axis

        if abs(dx) >= abs(dy):
            for i in range(-half, half + 1):
                self.draw_line((start[0] - ex, start[1] + i),
                               (end[0] + ex, end[1] + i), color, img)
        else:
            for i in range(-half, half + 1):
                self.draw_line((start[0] + i, start[1] - ey),
                               (end[0] + i, end[1] + ey), color, img)

    def draw_frame(self, coor: dict[str, tuple],
                   thickness: int, color: int, img: dict[str, Any]) -> None:

        self.draw_thick_line(coor['tl'], coor['tr'],
                             color, thickness, img)
        self.draw_thick_line(coor['tl'], coor['bl'],
                             color, thickness, img)
        self.draw_thick_line(coor['bl'], coor['br'],
                             color, thickness, img)
        self.draw_thick_line(coor['br'], coor['tr'],
                             color, thickness, img)

    def fill_rect(self, coor: dict, color: int, img) -> None:
        for y in range(coor['y0'], coor['y1']):
            for x in range(coor['x0'], coor['x1']):
                self.put_pixel(img['data'], x, y,
                               color, img['size_line'], img['bpp'])

    def draw_maze(self, maze: Maze, color: int, fill_color: int,
                  img: dict[str, Any]) -> None:

        start: tuple = maze.coordinates['tl']
        cell_thickness: int = maze.border_thickness // 2

        start_x: int = start[0]
        stripped_maze: list[str] = [x.strip('\n') for x in maze.maze_lines]
        for line in stripped_maze:
            for cell in line:
                walls: Optional[tuple] = HEX_TO_WALLS[cell]
                if walls == ('W', 'S', 'E', 'N'):
                    self.fill_rect(
                        {'x0': start[0], 'x1': start[0] + maze.cell_size,
                         'y0': start[1], 'y1': start[1] + maze.cell_size},
                        fill_color, img
                    )
                if walls:
                    for wall in walls:
                        match wall:
                            case 'N':
                                self.draw_thick_line(start,
                                                     (start[0] + maze.cell_size,
                                                      start[1]),
                                                     color, cell_thickness, img)
                            case 'E':
                                self.draw_thick_line((start[0] + maze.cell_size,
                                                     start[1]),
                                                     (start[0] + maze.cell_size,
                                                     start[1] + maze.cell_size),
                                                     color, cell_thickness, img)
                            case 'S':
                                self.draw_thick_line((start[0],
                                                     start[1] + maze.cell_size),
                                                     (start[0] + maze.cell_size,
                                                     start[1] + maze.cell_size),
                                                     color, cell_thickness, img)
                            case 'W':
                                self.draw_thick_line((start[0], start[1]),
                                                     (start[0],
                                                     start[1] + maze.cell_size),
                                                     color, cell_thickness, img)
                start = (start[0] + maze.cell_size, start[1])

            start = (start_x, start[1] + maze.cell_size)

    def draw_path(self, maze: Maze, color: int, img: dict[str, Any]) -> None:

        tl: tuple[int] = maze.coordinates['tl']
        start = (maze.path_start[0] + tl[0] + maze.cell_size // 2,
                 maze.path_start[1] + tl[1] + maze.cell_size // 2)
        self.path_start: tuple[int] = start

        end: tuple = (0, 0)

        for move in maze.path_moves:
            match move:
                case 'N':
                    end = (start[0], start[1] - maze.cell_size)
                case 'E':
                    end = (start[0] + maze.cell_size, start[1])
                case 'S':
                    end = (start[0], start[1] + maze.cell_size)
                case 'W':
                    end = (start[0] - maze.cell_size, start[1])
            self.draw_thick_line(start, end, color, maze.border_thickness, img)
            start = end

        self.path_end: tuple[int] = end
