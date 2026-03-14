import random
from typing import Generator, List, Tuple, Set
from collections import deque


class MazeGenerator:
    NORTH = 1  # 0001
    EAST = 2   # 0010
    SOUTH = 4  # 0100
    WEST = 8   # 1000
    DIRECTIONS = {
        "N": (0, -1, NORTH, SOUTH),
        "S": (0, 1, SOUTH, NORTH),
        "E": (1, 0, EAST, WEST),
        "W": (-1, 0, WEST, EAST),
    }

    def __init__(self, width: int, height: int, entry: Tuple[int, int],
                 exit_coords: Tuple[int, int], seed: int = 42) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit_coords
        self.seed = seed

        self.logo_cells: Set[Tuple[int, int]] = set()
        self.grid: list[int] = [15] * (width * height)

    def _carve(self, x1: int, y1: int, x2: int, y2: int,
               wall: int, opp: int) -> None:
        w = self.width
        self.grid[y1 * w + x1] &= ~wall
        self.grid[y2 * w + x2] &= ~opp

    def _get_42_coords(self) -> List[Tuple[int, int]]:
        """Desenha o logo 42 no centro do labirinto."""
        cx = self.width // 2
        cy = self.height // 2
        pattern = [
            "X X XXX",
            "X X   X",
            "XXX XXX",
            "  X X  ",
            "  X XXX",
        ]
        coords = []
        start_x = cx - len(pattern[0]) // 2
        start_y = cy - len(pattern) // 2
        for dy, row in enumerate(pattern):
            for dx, c in enumerate(row):
                if c == "X":
                    x = start_x + dx
                    y = start_y + dy
                    if 0 <= x < self.width and 0 <= y < self.height:
                        coords.append((x, y))
        return coords

    def generate(self, perfect: bool = True,
                 method: str = "backtracking") -> None:
        random.seed(self.seed)
        visited: Set[Tuple[int, int]] = set()

        if self.width >= 10 and self.height >= 8:
            self.logo_cells = set(self._get_42_coords())
            for cell in self.logo_cells:
                if cell != self.entry and cell != self.exit:
                    visited.add(cell)
        else:
            print(f"[Notice] Maze {self.width}x{self.height} "
                  f"too small for '42' logo.")

        if method.lower() == "prim":
            for _ in self._run_prim(visited):
                pass
        else:
            for _ in self._run_backtracking(visited):
                pass

        if not perfect:
            self._make_imperfect()

        self._seal_logo()

    def _run_backtracking(
        self, visited: Set[Tuple[int, int]]
    ) -> Generator[Tuple[int, int], None, None]:
        """DFS iterativo com gerador. Cada yield devolve a celula atual."""
        dirs = list(self.DIRECTIONS.values())
        stack = [self.entry]
        visited.add(self.entry)
        width = self.width
        height = self.height
        logo = self.logo_cells

        while stack:
            cx, cy = stack[-1]
            neighbors = [
                (cx + dx, cy + dy, w, ow)
                for dx, dy, w, ow in dirs
                if (0 <= cx + dx < width
                    and 0 <= cy + dy < height
                    and (cx + dx, cy + dy) not in visited
                    and (cx + dx, cy + dy) not in logo)
            ]
            if neighbors:
                nx, ny, wall, opp = random.choice(neighbors)
                self._carve(cx, cy, nx, ny, wall, opp)
                visited.add((nx, ny))
                stack.append((nx, ny))
                yield (nx, ny)
            else:
                stack.pop()

    def _run_prim(
        self, visited: Set[Tuple[int, int]]
    ) -> Generator[Tuple[int, int], None, None]:
        """Prim randomizado com gerador."""
        dirs = list(self.DIRECTIONS.values())
        walls: list = []
        width = self.width
        height = self.height
        logo = self.logo_cells

        def _add_walls(x: int, y: int) -> None:
            for dx, dy, w, ow in dirs:
                nx, ny = x + dx, y + dy
                if (0 <= nx < width
                        and 0 <= ny < height
                        and (nx, ny) not in visited
                        and (nx, ny) not in logo):
                    walls.append((x, y, nx, ny, w, ow))

        if self.entry not in visited:
            visited.add(self.entry)
        _add_walls(*self.entry)

        while walls:
            idx = random.randrange(len(walls))
            walls[idx], walls[-1] = walls[-1], walls[idx]
            x1, y1, x2, y2, w, ow = walls.pop()

            if (x2, y2) not in visited:
                self._carve(x1, y1, x2, y2, w, ow)
                visited.add((x2, y2))
                _add_walls(x2, y2)
                yield (x2, y2)

    def _make_imperfect(self) -> None:
        """Remove paredes aleatorias para criar loops no labirinto."""
        dirs = list(self.DIRECTIONS.values())
        num_extra = max(1, (self.width * self.height) // 20)
        grid = self.grid
        width = self.width
        logo = self.logo_cells

        candidates = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in logo
        ]
        random.shuffle(candidates)

        count = 0
        for x, y in candidates:
            if count >= num_extra:
                break
            random.shuffle(dirs)
            for dx, dy, wall, opp in dirs:
                nx, ny = x + dx, y + dy
                if (0 <= nx < width
                        and 0 <= ny < self.height
                        and (nx, ny) not in logo
                        and grid[y * width + x] & wall):
                    self._carve(x, y, nx, ny, wall, opp)
                    count += 1
                    break

    def _seal_logo(self) -> None:
        """Forca o logo 42 a ficar fechado."""
        w = self.width
        for x, y in self.logo_cells:
            self.grid[y * w + x] = 15
            for dx, dy, _wall, opp in self.DIRECTIONS.values():
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    self.grid[ny * w + nx] |= opp

    def solve(
        self, start: Tuple[int, int], end: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """BFS — devolve o caminho mais curto."""
        parent: dict = {start: None}
        queue = deque([start])
        width = self.width
        height = self.height
        grid = self.grid
        dirs = list(self.DIRECTIONS.values())

        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == end:
                break
            cell_val = grid[cy * width + cx]
            for dx, dy, wall, _ in dirs:
                if not (cell_val & wall):
                    nx, ny = cx + dx, cy + dy
                    if (0 <= nx < width
                            and 0 <= ny < height
                            and (nx, ny) not in parent):
                        parent[(nx, ny)] = (cx, cy)
                        queue.append((nx, ny))

        if end not in parent:
            return []

        path = []
        curr: Tuple[int, int] | None = end
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
        return path[::-1]

    @property
    def grid_rows(self) -> List[List[int]]:
        """Vista 2D do grid flat. Substitui maze.grid no renderer."""
        w = self.width
        return [self.grid[y * w:(y + 1) * w] for y in range(self.height)]

    def get_path_string(self, path: List[Tuple[int, int]]) -> str:
        res = []
        for i in range(len(path) - 1):
            dx = path[i + 1][0] - path[i][0]
            dy = path[i + 1][1] - path[i][1]
            if dx == 1:
                res.append("E")
            elif dx == -1:
                res.append("W")
            elif dy == 1:
                res.append("S")
            elif dy == -1:
                res.append("N")
        return "".join(res)

    def export_to_file(
        self,
        filename: str,
        entry: Tuple[int, int],
        exit_coords: Tuple[int, int],
        path: List[Tuple[int, int]],
    ) -> None:
        w = self.width
        with open(filename, "w") as f:
            for y in range(self.height):
                f.write("".join(
                    f"{self.grid[y * w + x]:X}" for x in range(w)
                ) + "\n")
            f.write(
                f"\n{entry[0]},{entry[1]}\n"
                f"{exit_coords[0]},{exit_coords[1]}\n"
            )
            f.write(self.get_path_string(path) + "\n")
