class Maze():
    def __init__(self, filename: str) -> None:
        """parses maze upon initialization"""
        try:
            with open(filename, 'r') as f:
                file_lines: list[str] = []
                self.maze_lines: list[str] = []
                path_info: list[str] = []

                while True:
                    line: str = f.readline()
                    if not line:
                        break
                    file_lines.append(line)
        except FileNotFoundError as e:
            print(e)
            return

        is_path_info: bool = False

        for line in file_lines:
            if line == '\n':
                is_path_info = True
                continue
            if not is_path_info:
                self.maze_lines.append(line)
            else:
                path_info.append(line)

        self.path_start: tuple[int] = (int(path_info[0].strip().split(',')[0]),
                                       int(path_info[0].strip().split(',')[1]))
        self.path_end: tuple[int] = (int(path_info[1].strip().split(',')[0]),
                                     int(path_info[1].strip().split(',')[1]))
        self.path_moves: str = path_info[2].strip()

    def set_maze_dim(self, win_width: int, win_height: int) -> None:
        """Sets maze properties and dimensions"""
        columns: int = len(self.maze_lines[0].strip('\n'))
        rows: int = len(self.maze_lines)

        margin: float = 0.9
        self.active_w: int = round(win_width * margin)
        self.active_h: int = round(win_height * margin)

        self.cell_size: int = 0
        try:
            if columns >= rows:
                self.cell_size = self.active_w // columns
                if self.cell_size * rows > self.active_h:
                    self.cell_size = self.active_h // rows
                if self.cell_size < 3:
                    raise ValueError('Active area isn\'t '
                                     'big enough for maze width')
            else:
                self.cell_size = self.active_h // rows
                if self.cell_size * columns > self.active_w:
                    self.cell_size = self.active_w // columns
                if self.cell_size < 3:
                    raise ValueError('Active area isn\'t '
                                     'big enough for maze height')

        except ValueError as e:
            print(f'[ERROR]: {e}')

        self.width: int = self.cell_size * columns
        self.height: int = self.cell_size * rows
        self.x_offset: int = (win_width - self.width) // 2
        self.y_offset: int = (win_height - self.height) // 2
        self.coordinates: dict[str, int] = {
            'tl': (self.x_offset, self.y_offset),
            'tr': (self.x_offset + self.width, self.y_offset),
            'bl': (self.x_offset, self.y_offset + self.height),
            'br': (self.x_offset + self.width, self.y_offset + self.height),
        }
        self.border_thickness: int = (1 if self.cell_size < 5 else
                                      self.cell_size // 5)
