import random
from typing import List, Tuple
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
        self.width: int = width
        self.height: int = height
        self.entry: Tuple[int, int] = entry
        self.exit: Tuple[int, int] = exit_coords
        self.seed: int = seed

        self.grid: List[List[int]] = [
            [15 for _ in range(width)] for _ in range(height)]

    def _apply_42_pattern(self) -> None:
        """Draws number '42' using closed cells, avoiding entry/exit."""
        if self.width < 10 or self.height < 8:
            return

        mid_x, mid_y = self.width // 2, self.height // 2

        four = [
            (mid_x - 2, mid_y - 1), (mid_x - 2, mid_y), (mid_x - 1, mid_y),
            (mid_x, mid_y - 1), (mid_x, mid_y), (mid_x, mid_y + 1)
        ]
        two = [
            (mid_x + 2, mid_y - 1), (mid_x + 3, mid_y - 1), (mid_x + 3, mid_y),
            (mid_x + 2, mid_y), (mid_x + 2, mid_y + 1), (mid_x + 3, mid_y + 1)
        ]

        for x, y in (four + two):
            if 0 <= x < self.width and 0 <= y < self.height:
                if (x, y) != self.entry and (x, y) != self.exit:
                    self.grid[y][x] = 15

    def generate(self, perfect: bool = True) -> None:
        """Recursive backtracking algorithm with pattern protection."""
        random.seed(self.seed)
        self._apply_42_pattern()

        stack = [self.entry]
        visited = {self.entry}

        mid_x, mid_y = self.width // 2, self.height // 2
        logo = [
            (mid_x - 2, mid_y - 1), (mid_x - 2, mid_y), (mid_x - 1, mid_y),
            (mid_x, mid_y - 1), (mid_x, mid_y), (mid_x, mid_y + 1),
            (mid_x + 2, mid_y - 1), (mid_x + 3, mid_y - 1), (mid_x + 3, mid_y),
            (mid_x + 2, mid_y), (mid_x + 2, mid_y + 1), (mid_x + 3, mid_y + 1)
        ]

        for x, y in logo:
            if 0 <= x < self.width and 0 <= y < self.height:
                if (x, y) != self.entry and (x, y) != self.exit:
                    visited.add((x, y))

        while stack:
            cx, cy = stack[-1]
            neighbors = []

            # procurar locais nao visitados
            for dx, dy, wall, opp_wall in self.DIRECTIONS.values():
                nx, ny = cx + dx, cy + dy

                # garante que estamos nos limites do labirinto
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in visited:
                        neighbors.append((nx, ny, wall, opp_wall))

            if neighbors:
                nx, ny, wall, opp_wall = random.choice(neighbors)

                self.grid[cy][cx] &= ~wall
                self.grid[ny][nx] &= ~opp_wall

                # parte as paredes - tanforma 1 em 0
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

        if not perfect:
            self._make_imperfect()

    def _make_imperfect(self) -> None:
        """Removes extra walls to create cycles/multiple paths."""

        num_extra_walls = (self.width * self.height) // 20
        for _ in range(num_extra_walls):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)

            d_name = random.choice(list(self.DIRECTIONS.keys()))
            dx, dy, wall, opp_wall = self.DIRECTIONS[d_name]
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                # Quebra a parede entre (x,y) e (nx,ny)
                self.grid[y][x] &= ~wall
                self.grid[ny][nx] &= ~opp_wall

    def get_path_string(self, path: List[Tuple[int, int]]) -> str:
        """Converts the list of coordinates into a string like 'EENSS'."""
        path_str = ""
        for i in range(len(path) - 1):
            curr, nxt = path[i], path[i + 1]
            dx, dy = nxt[0] - curr[0], nxt[1] - curr[1]
            if dx == 1:
                path_str += "E"
            elif dx == -1:
                path_str += "W"
            elif dy == 1:
                path_str += "S"
            elif dy == -1:
                path_str += "N"
        return path_str

    def export_to_file(self, filename: str, entry: Tuple[int, int],
                       exit_coords: Tuple[int, int],
                       path: List[Tuple[int, int]]):
        """Writes the maze in hexadecimal format."""
        try:
            with open(filename, 'w') as file:
                for row in self.grid:
                    hex_row = "".join([f"{cell:X}" for cell in row])
                    file.write(hex_row + "\n")
                file.write("\n")

                file.write(f"{entry[0]},{entry[1]}\n")
                file.write(f"{exit_coords[0]},{exit_coords[1]}\n")
                file.write(self.get_path_string(path) + "\n")
        except Exception as erro:
            print(f"Error exporting file: {erro}")

    def solve(self, start: Tuple[int, int],
              end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Finds the shortest path using BFS with optimized deque."""
        # O uso de deque garante performance O(1) no popleft
        queue = deque([start])
        parent = {start: None}

        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == end:
                break

            for dx, dy, wall, _ in self.DIRECTIONS.values():
                nx, ny = cx + dx, cy + dy
                # 1. Verificar limites do labirinto
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    # 2. Verificar se não há parede (Bitwise AND)
                    if not (self.grid[cy][cx] & wall):
                        # 3. Evitar ciclos e redundância
                        if (nx, ny) not in parent:
                            parent[(nx, ny)] = (cx, cy)
                            queue.append((nx, ny))

        path = []
        if end not in parent:
            return []
        curr = end
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
        return path[::-1]
