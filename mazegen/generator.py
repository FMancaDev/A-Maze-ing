import random
from typing import List, Tuple, Set
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
        """Initialize the maze generator"""
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit_coords
        self.seed = seed

        self.logo_cells: Set[Tuple[int, int]] = set()

        self.grid = [[15 for _ in range(width)] for _ in range(height)]

    def _get_42_coords(self) -> List[Tuple[int, int]]:
        """draw 42 logo in center of maze"""

        cx = self.width // 2
        cy = self.height // 2

        pattern = [
            "X X  XXX",
            "X X    X",
            "XXX  XXX",
            "  X  X  ",
            "  X  XXX",
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
        """Generate the maze using the selected algorithm"""
        random.seed(self.seed)
        visited: Set[Tuple[int, int]] = set()

        # define logo
        if self.width >= 10 and self.height >= 8:
            self.logo_cells = set(self._get_42_coords())

            for x, y in self.logo_cells:
                if (x, y) != self.entry and (x, y) != self.exit:
                    visited.add((x, y))
        else:
            print(
                f"[Notice] Maze {self.width}x{self.height} "
                f"too small for '42' logo."
            )

        # algoritmo
        if method.lower() == "prim":
            self._run_prim(visited)
        else:
            self._run_backtracking(visited)

        if not perfect:
            self._make_imperfect()

        self._seal_logo()

    def _run_backtracking(self, visited: Set[Tuple[int, int]]) -> None:
        """"Generte the maze using the recursive backtraking (dfs) algorithm"""
        stack = [self.entry]
        visited.add(self.entry)

        while stack:
            cx, cy = stack[-1]
            neighbors = []

            for dx, dy, wall, opp_wall in self.DIRECTIONS.values():
                nx, ny = cx + dx, cy + dy

                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and (nx, ny) not in visited
                    and (nx, ny) not in self.logo_cells
                ):
                    neighbors.append((nx, ny, wall, opp_wall))

            if neighbors:
                nx, ny, wall, opp_wall = random.choice(neighbors)

                self.grid[cy][cx] &= ~wall
                self.grid[ny][nx] &= ~opp_wall

                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

    def _run_prim(self, visited: Set[Tuple[int, int]]) -> None:
        """Generate the maze using a randomized version of Prim's algorithm"""
        walls = []

        def add_walls(x: int, y: int) -> None:
            for dx, dy, w, ow in self.DIRECTIONS.values():
                nx, ny = x + dx, y + dy

                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and (nx, ny) not in visited
                    and (nx, ny) not in self.logo_cells
                ):
                    walls.append((x, y, nx, ny, w, ow))

        if self.entry not in visited:
            visited.add(self.entry)

        add_walls(*self.entry)

        while walls:
            idx = random.randrange(len(walls))
            x1, y1, x2, y2, w, ow = walls.pop(idx)

            if (x2, y2) not in visited:
                self.grid[y1][x1] &= ~w
                self.grid[y2][x2] &= ~ow

                visited.add((x2, y2))
                add_walls(x2, y2)

    def _make_imperfect(self) -> None:
        """Randomly remove walls to create loops in the maze"""
        num_extra = (self.width * self.height) // 20
        count = 0

        while count < num_extra:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)

            d = random.choice(list(self.DIRECTIONS.values()))
            nx, ny = x + d[0], y + d[1]

            if (
                0 <= nx < self.width
                and 0 <= ny < self.height
                and (x, y) not in self.logo_cells
                and (nx, ny) not in self.logo_cells
            ):
                if self.grid[y][x] & d[2]:
                    self.grid[y][x] &= ~d[2]
                    self.grid[ny][nx] &= ~d[3]
                    count += 1

    def _seal_logo(self) -> None:
        """force the 42 logo to stay closed"""
        for x, y in self.logo_cells:
            self.grid[y][x] = 15

            # fecha também vizinhos que possam ter aberto
            for dx, dy, wall, opp_wall in self.DIRECTIONS.values():
                nx, ny = x + dx, y + dy

                if 0 <= nx < self.width and 0 <= ny < self.height:
                    self.grid[ny][nx] |= opp_wall

    def solve(
        self, start: Tuple[int, int], end: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """algoriyhm to find the shortest path"""
        parent = {start: None}
        queue = deque([start])

        while queue:
            curr = queue.popleft()

            if curr == end:
                break

            cx, cy = curr

            for dx, dy, wall, _ in self.DIRECTIONS.values():
                nx, ny = cx + dx, cy + dy

                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if not (self.grid[cy][cx] & wall) and (nx, ny) not in parent:
                        parent[(nx, ny)] = curr
                        queue.append((nx, ny))

        if end not in parent:
            return []

        path = []
        curr = end

        while curr is not None:
            path.append(curr)
            curr = parent[curr]

        return path[::-1]

    def get_path_string(self, path: List[Tuple[int, int]]) -> str:
        """covert a list of path coordinates int a string of movement """
        res = ""

        for i in range(len(path) - 1):
            dx = path[i + 1][0] - path[i][0]
            dy = path[i + 1][1] - path[i][1]

            if dx == 1:
                res += "E"
            elif dx == -1:
                res += "W"
            elif dy == 1:
                res += "S"
            elif dy == -1:
                res += "N"

        return res

    def export_to_file(
        self,
        filename: str,
        entry: Tuple[int, int],
        exit_coords: Tuple[int, int],
        path: List[Tuple[int, int]],
    ) -> None:
        """Write the maze grid and coordinates and slution path to a file"""

        with open(filename, "w") as f:
            for row in self.grid:
                f.write("".join(f"{c:X}" for c in row) + "\n")

            f.write(
                f"\n{entry[0]},{entry[1]}\n{exit_coords[0]},{exit_coords[1]}\n"
            )

            f.write(self.get_path_string(path) + "\n")
