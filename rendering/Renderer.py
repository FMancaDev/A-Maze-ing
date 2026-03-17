from typing import Any, Generator
import struct
from mazegen.generator import MazeGenerator
from .Window import Window
from .constants import DEC_TO_WALLS as WALLS


class Renderer():
    def __init__(self, win_width: int, win_height: int) -> None:
        self.win_width: int = win_width
        self.win_height: int = win_height

    def put_pixel(self, data: memoryview,
                  x: int, y: int,
                  color: int,
                  size_line: int,
                  bpp: int) -> None:
        if x < 0 or x >= self.win_width or y < 0 or y >= self.win_height:
            return
        offset = y * size_line + x * (bpp // 8)
        data[offset] = color & 0xFF
        data[offset + 1] = (color >> 8) & 0xFF
        data[offset + 2] = (color >> 16) & 0xFF
        data[offset + 3] = (color >> 24) & 0xFF

    def fill_rect(self, start: tuple[int, int], end: tuple[int, int],
                  color: int, img: dict[str, Any]) -> None:
        data: memoryview = img['data']
        bpp: int = img['bpp']
        size_line: int = img['size_line']
        bpp_bytes: int = bpp // 8

        x0 = max(0, start[0])
        y0 = max(0, start[1])
        x1 = min(self.win_width,  end[0])
        y1 = min(self.win_height, end[1])
        if x0 >= x1 or y0 >= y1:
            return

        pixel = struct.pack('BBBB',
                            color & 0xFF,
                            (color >> 8) & 0xFF,
                            (color >> 16) & 0xFF,
                            (color >> 24) & 0xFF)
        row_bytes = pixel * (x1 - x0)

        for y in range(y0, y1):
            offset = y * size_line + x0 * bpp_bytes
            data[offset: offset + len(row_bytes)] = row_bytes

    def draw_line(self, start: tuple[int, int], end: tuple[int, int],
                  thickness: int, color: int, img: dict[str, Any]) -> None:

        half: int = max(1, thickness // 2)

        x0, y0 = start
        x1, y1 = end

        self.fill_rect((x0 - half, y0 - half), (x1 + half, y1 + half),
                       color, img)

    def draw_frame(self, coor: dict[str, tuple],
                   thickness: int, color: int, img: dict[str, Any]) -> None:

        self.draw_line(coor['tl'], coor['tr'], thickness, color, img)
        self.draw_line(coor['tl'], coor['bl'], thickness, color, img)
        self.draw_line(coor['bl'], coor['br'], thickness, color, img)
        self.draw_line(coor['tr'], coor['br'], thickness, color, img)

    def fill_circle(self, start: tuple[int, int], end: tuple[int, int],
                    color: int, img: dict[str, Any]) -> None:
        radius: int = (end[0] - start[0]) // 2
        cx: int = start[0] + radius
        cy: int = start[1] + radius

        for y in range(cy - radius, cy + radius + 1):
            dy = y - cy
            dx_limit = int((radius ** 2 - dy ** 2) ** 0.5)
            self.fill_rect((cx - dx_limit, y),
                           (cx + dx_limit + 1, y + 1),
                           color, img)

    def draw_maze(self, maze: MazeGenerator,
                  img: dict[str, Any], color: int) -> None:
        margin: float = 0.9
        active_w: int = round(self.win_width * margin)
        # sets base margin for maze
        active_h: int = round(self.win_height * margin)

        self.cell_size: int = (active_w // maze.width if maze.width > 0 else
                               active_w)
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
            'tr': (padding_left + maze_px_width,  padding_top),
            'bl': (padding_left, padding_top + maze_px_height),
            'br': (padding_left + maze_px_width, padding_top + maze_px_height),
        }
        self.border_thickness: int = (1 if self.cell_size < 5 else
                                      self.cell_size // 5)

        self.draw_frame(self.coor, self.border_thickness, color, img)

        self.fill_42(maze.logo_cells, color, img)

        self.draw_walls(maze.grid_rows, color, img)

        self.draw_start_end_points(maze, img, color)

    def draw_walls(self, maze_grid: list[list[int]],
                   color: int, img: dict[str, Any]) -> None:
        tl_x, tl_y = self.coor['tl']
        cs = self.cell_size
        t = (1 if self.border_thickness < 2 else self.border_thickness // 2)

        for row_idx, row in enumerate(maze_grid):
            for col_idx, cell in enumerate(row):
                walls = WALLS[cell]
                if not walls:
                    continue
                x = tl_x + col_idx * cs
                y = tl_y + row_idx * cs
                for wall in walls:
                    if wall == 'N':
                        print('N')
                        self.draw_line((x, y), (x + cs, y),
                                       t, color, img)
                    elif wall == 'S':
                        print('S')
                        self.draw_line((x, y + cs), (x + cs, y + cs),
                                       t, color, img)
                    elif wall == 'W':
                        print('W')
                        self.draw_line((x, y), (x, y + cs),
                                       t, color, img)
                    elif wall == 'E':
                        print('E')
                        self.draw_line((x + cs, y), (x + cs, y + cs),
                                       t, color, img)

    def fill_42(self, coors_42: set[tuple[int, int]],
                color: int, img: dict[str, Any]) -> None:
        cs = self.cell_size
        tlx, tly = self.coor['tl']
        for cell in coors_42:
            x0 = cell[0] * cs + tlx
            y0 = cell[1] * cs + tly
            self.fill_rect((x0, y0), (x0 + cs, y0 + cs), color, img)

    def draw_path(self, maze: MazeGenerator, win: Window,
                  img: dict[str, Any], color: int) -> Generator:

        path: list[tuple[int, int]] = maze.solve(maze.entry, maze.exit)
        path_t: int = round(self.border_thickness * 1.2)
        cs = self.cell_size
        tlx, tly = self.coor['tl']
        for square in path:
            step: dict[str, Any] = win.create_copy(img)
            cx = square[0] * cs + tlx + cs // 2
            cy = square[1] * cs + tly + cs // 2
            self.fill_circle((cx - path_t, cy - path_t),
                             (cx + path_t, cy + path_t),
                             color, step)
            yield step

    def draw_start_end_points(self, maze: MazeGenerator,
                              img: dict[str, Any], color: int) -> None:
        cs = self.cell_size
        tlx, tly = self.coor['tl']
        bpp = img['bpp']
        sl = img['size_line']
        data = img['data']

        start = (maze.entry[0] * cs + tlx, maze.entry[1] * cs + tly)
        end = (maze.exit[0] * cs + tlx, maze.exit[1] * cs + tly)

        tri_size = round(cs * 0.5)
        padding = (cs - tri_size) // 2

        i = 0
        for x in range(start[0] + padding, start[0] + padding + tri_size):
            for y in range(start[1] + padding + i,
                           start[1] + padding + tri_size - i):
                self.put_pixel(data, x, y, color, sl, bpp)
            i += 1

        i = 0
        for x in range(end[0] + padding + tri_size, end[0] + padding, -1):
            for y in range(end[1] + padding + i,
                           end[1] + padding + tri_size - i):
                self.put_pixel(data, x, y, color, sl, bpp)
            i += 1
