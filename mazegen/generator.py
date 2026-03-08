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
        """Initializes the maze grid and dimensions"""
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit_coords
        self.seed = seed

        self.grid = [[15 for _ in range(width)] for _ in range(height)]

    def _get_42_coords(self) -> List[Tuple[int, int]]:
        """Returns the centralized coordinates for the '42' pattern."""
        mid_x, mid_y = self.width // 2, self.height // 2
        four = [
            (mid_x - 2, mid_y - 1), (mid_x - 2, mid_y),
            (mid_x - 1, mid_y),
            (mid_x, mid_y - 1), (mid_x, mid_y), (mid_x, mid_y + 1)
        ]
        two = [
            (mid_x + 2, mid_y - 1), (mid_x + 3, mid_y - 1),
            (mid_x + 3, mid_y), (mid_x + 2, mid_y),
            (mid_x + 2, mid_y + 1), (mid_x + 3, mid_y + 1)
        ]
        return four + two

    def generate(self, method: str = "backtracking",
                 perfect: bool = True) -> None:
        """Generates the maze by selecting algorithms"""
        random.seed(self.seed)
        self.grid = [[15 for _ in range(self.width)]
                     for _ in range(self.height)]

        visited = set()
        # Protege o '42'
        if self.width >= 10 and self.height >= 8:
            for x, y in self._get_42_coords():
                if 0 <= x < self.width and 0 <= y < self.height:
                    if (x, y) != self.entry and (x, y) != self.exit:
                        visited.add((x, y))

        if method.lower() == "prim":
            self._run_prim(visited)
        else:
            self._run_backtracking(visited)

        if not perfect:
            self._make_imperfect()

    def _run_backtracking(self, visited: Set[Tuple[int, int]]) -> None:
        """Recursive Backtracking algorithm"""
        stack = [self.entry]
        visited.add(self.entry)

        while stack:
            cx, cy = stack[-1]
            neighbors = []
            for dx, dy, wall, opp_wall in self.DIRECTIONS.values():
                nx, ny = cx + dx, cy + dy
                if (0 <= nx < self.width and 0 <= ny < self.height
                        and (nx, ny) not in visited):
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
        """Prims algorithm"""
        walls = []

        def add_walls(x, y):
            for dx, dy, wall, opp_wall in self.DIRECTIONS.values():
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.width and 0 <= ny < self.height
                        and (nx, ny) not in visited):
                    walls.append((x, y, nx, ny, wall, opp_wall))

        visited.add(self.entry)
        add_walls(*self.entry)

        while walls:
            idx = random.randrange(len(walls))
            x1, y1, x2, y2, wall, opp_wall = walls.pop(idx)

            if (x2, y2) not in visited:
                self.grid[y1][x1] &= ~wall
                self.grid[y2][x2] &= ~opp_wall
                visited.add((x2, y2))
                add_walls(x2, y2)

    def _make_imperfect(self) -> None:
        """Creates loops by removing random walls"""
        num_extra = (self.width * self.height) // 20
        for _ in range(num_extra):
            x, y = random.randint(
                0, self.width-1), random.randint(0, self.height-1)
            d = random.choice(list(self.DIRECTIONS.values()))
            nx, ny = x + d[0], y + d[1]
            if 0 <= nx < self.width and 0 <= ny < self.height:
                self.grid[y][x] &= ~d[2]
                self.grid[ny][nx] &= ~d[3]

    def solve(self, method: str = "bfs") -> List[Tuple[int, int]]:
        """solve the maze using BFS or DFS"""
        if method.lower() == "dfs":
            return self._solve_dfs(self.entry, self.exit)
        return self._solve_bfs(self.entry, self.exit)

    def _solve_bfs(self, start, end) -> List[Tuple[int, int]]:
        """Guarantees the shortest path"""
        queue = deque([start])
        parent = {start: None}
        while queue:
            curr = queue.popleft()
            if curr == end:
                break
            cx, cy = curr
            for dx, dy, wall, _ in self.DIRECTIONS.values():
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (not (self.grid[cy][cx] & wall)
                            and (nx, ny) not in parent):
                        parent[(nx, ny)] = curr
                        queue.append((nx, ny))
        return self._reconstruct_path(parent, end)

    def _solve_dfs(self, start, end) -> List[Tuple[int, int]]:
        """Find a way(it may not be the shortest one)"""
        stack = [start]
        parent = {start: None}
        while stack:
            curr = stack.pop()
            if curr == end:
                break
            cx, cy = curr
            for dx, dy, wall, _ in self.DIRECTIONS.values():
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (not (self.grid[cy][cx] & wall)
                            and (nx, ny) not in parent):
                        parent[(nx, ny)] = curr
                        stack.append((nx, ny))
        return self._reconstruct_path(parent, end)

    def _reconstruct_path(self, parent, end) -> List[Tuple[int, int]]:
        if end not in parent:
            return []
        path, curr = [], end
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
        return path[::-1]

    def get_path_string(self, path: List[Tuple[int, int]]) -> str:
        res = ""
        for i in range(len(path)-1):
            dx = path[i+1][0] - path[i][0]
            dy = path[i+1][1] - path[i][1]
            if dx == 1:
                res += "E"
            elif dx == -1:
                res += "W"
            elif dy == 1:
                res += "S"
            elif dy == -1:
                res += "N"
        return res

    def export_to_file(self, filename: str, path: List[Tuple[int, int]]):
        with open(filename, 'w') as f:
            for row in self.grid:
                f.write("".join([f"{c:X}" for c in row]) + "\n")

            f.write(f"\n{self.entry[0]},{self.entry[1]}\n")
            f.write(f"{self.exit[0]},{self.exit[1]}\n")
            f.write(self.get_path_string(path) + "\n")
