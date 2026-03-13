from typing import Any
from ctypes import c_uint
from mazegen.generator import MazeGenerator
from .constants import DEC_TO_WALLS as WALLS


class Renderer():

    def __init__(self, win_width: int, win_height: int) -> None:
        self.win_width: int = win_width
        self.win_height: int = win_height

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

    def draw_line(self, start: tuple[int], end: tuple[int],
                  thickness: int, color: int, img: dict[str, Any]) -> None:

        half: int = 1 if thickness < 2 else thickness // 2

        x0, y0 = start
        x1, y1 = end

        dx: int = x1 - x0
        dy: int = y1 - y0

        if abs(dx) >= abs(dy):
            for i in range(x0, x1 + 1, thickness):
                self.fill_rect((i - half, y0 - half),
                               (i + half, y0 + half),
                               color, img)
        else:
            for i in range(y0, y1 + 1, thickness):
                self.fill_rect((x0 - half, i - half),
                               (x0 + half, i + half),
                               color, img)

    def draw_frame(self, coor: dict[str, int],
                   thickness: int, color: int, img: dict[str, Any]) -> None:

        self.draw_line(coor['tl'], coor['tr'], thickness, color, img)
        self.draw_line(coor['tl'], coor['bl'], thickness, color, img)
        self.draw_line(coor['bl'], coor['br'], thickness, color, img)
        self.draw_line(coor['tr'], coor['br'], thickness, color, img)

    def fill_rect(self, start: tuple[int], end: tuple[int],
                  color: int, img: dict[str, Any]) -> None:
        for y in range(start[1], end[1]):
            for x in range(start[0], end[0]):
                self.put_pixel(img['data'], x, y,
                               color, img['size_line'], img['bpp'])

    def fill_circle(self, start: tuple[int, int], end: tuple[int, int],
                    color: int, img: dict[str, Any]) -> None:
        radius: int = (end[0] - start[0]) // 2
        cx: int = start[0] + radius
        cy: int = start[1] + radius

        for y in range(cy - radius, cy + radius + 1):
            dy: int = y - cy
            dx_limit: int = int((radius**2 - dy**2)**0.5)
            for x in range(cx - dx_limit, cx + dx_limit + 1):
                self.put_pixel(img['data'], x, y, color,
                               img['size_line'], img['bpp'])

    def draw_maze(self, maze: MazeGenerator,
                  img: dict[str, Any], color: int) -> None:
        margin: float = 0.9
        active_w: int = round(self.win_width * margin)
        # sets base margin for maze
        active_h: int = round(self.win_height * margin)

        self.cell_size: int = 0  # cell size in px

        self.cell_size = active_w // maze.width
        if self.cell_size * maze.height > active_h:
            self.cell_size = active_h // maze.height
        if self.cell_size < 3:
            raise ValueError('Active width isn\'t enough '
                             'to acomodate maze width')

        maze_px_width: int = self.cell_size * maze.width
        maze_px_height: int = self.cell_size * maze.height

        padding_left: int = (self.win_width - maze_px_width) // 2
        padding_top: int = (self.win_height - maze_px_height) // 2

        self.coor: dict[str, tuple] = {
            'tl': (padding_left, padding_top),
            'tr': (padding_left + maze_px_width, padding_top),
            'bl': (padding_left, padding_top + maze_px_height),
            'br': (padding_left + maze_px_width, padding_top + maze_px_height),
        }

        self.border_thickness: int = (1 if self.cell_size < 5 else
                                      self.cell_size // 5)

        self.draw_frame(self.coor,
                        self.border_thickness, color, img)

        self.fill_42(maze.logo_cells, color, img)

        self.draw_walls(maze.grid, color, img)

        self.draw_start_end_points(maze, img, color)

    def draw_walls(self, maze_grid: list[list[int]],
                   color: int, img: dict[str, Any]) -> None:
        start: tuple[int] = self.coor['tl']
        curr: tuple[int] = start
        thickness: int = (1 if self.border_thickness < 2 else
                          self.border_thickness // 2)
        for row in maze_grid:
            for cell in row:
                walls: tuple[str] = WALLS[cell]
                if walls:
                    for wall in walls:
                        x, y = curr
                        match wall:
                            case 'N':
                                self.draw_line((x, y),
                                               (x + self.cell_size, y),
                                               thickness,
                                               color,
                                               img)
                            case 'E':
                                self.draw_line((x + self.cell_size, y),
                                               (x + self.cell_size,
                                                y + self.cell_size),
                                               thickness,
                                               color,
                                               img)
                            case 'W':
                                self.draw_line((x, y),
                                               (x, y + self.cell_size),
                                               thickness,
                                               color,
                                               img)
                            case 'S':
                                self.draw_line((x, y + self.cell_size),
                                               (x + self.cell_size,
                                                y + self.cell_size),
                                               thickness,
                                               color,
                                               img)

                curr = (curr[0] + self.cell_size, curr[1])
            curr = (start[0], curr[1] + self.cell_size)

    def fill_42(self, coors_42: set[tuple[int]],
                color: int, img: dict[str, Any]) -> None:
        for cell in coors_42:
            x0: int = cell[0] * self.cell_size + self.coor['tl'][0]
            y0: int = cell[1] * self.cell_size + self.coor['tl'][1]
            x1: int = x0 + self.cell_size
            y1: int = y0 + self.cell_size
            self.fill_rect((x0, y0), (x1, y1), color, img)

    def draw_path(self, maze: MazeGenerator,
                  img: dict[str, Any], color: int) -> None:
        path: list[tuple[int, int]] = maze.solve(maze.entry, maze.exit)
        path_t: int = round(self.border_thickness * 1.2)

        for i, square in enumerate(path):
            center_p: tuple = (square[0] * self.cell_size + self.coor['tl'][0]
                               + self.cell_size // 2,
                               square[1] * self.cell_size + self.coor['tl'][1]
                               + self.cell_size // 2,)
            x0: int = center_p[0] - path_t
            y0: int = center_p[1] - path_t
            x1: int = center_p[0] + path_t
            y1: int = center_p[1] + path_t
            self.fill_circle((x0, y0), (x1, y1), color, img)

    def draw_start_end_points(self, maze: MazeGenerator,
                              img: dict[str, Any], color: int) -> None:
        start: tuple[int, int] = (maze.entry[0] * self.cell_size
                                  + self.coor['tl'][0],
                                  maze.entry[1] * self.cell_size
                                  + self.coor['tl'][1])

        end: tuple[int, int] = (maze.exit[0] * self.cell_size
                                + self.coor['tl'][0],
                                maze.exit[1] * self.cell_size
                                + self.coor['tl'][1])

        tri_size: int = round(self.cell_size * 0.5)
        padding: int = (self.cell_size - tri_size) // 2
        i: int = 0

        for x in range(start[0] + padding, start[0] + padding + tri_size):
            for y in range(start[1] + padding + i,
                           start[1] + padding + tri_size - i):
                self.put_pixel(img['data'], x, y, color,
                               img['size_line'], img['bpp'])
            i += 1

        i = 0

        for x in range(end[0] + padding + tri_size, end[0] + padding, -1):
            for y in range(end[1] + padding + i,
                           end[1] + padding + tri_size - i):
                self.put_pixel(img['data'], x, y, color,
                               img['size_line'], img['bpp'])
            i += 1
