import random
from typing import List, Tuple


class MazeGenerator():

    NORTH = 1  # 0001
    EAST = 2  # 0010
    SOUTH = 4  # 0100
    WEST = 8  # 1000

    DIRECTIONS = {
        "N": (0, -1, NORTH, SOUTH),
        "S": (0, 1, SOUTH, NORTH),
        "E": (1, 0, EAST, WEST),
        "W": (-1, 0, WEST, EAST),
    }

    def __init__(self, width: int, height: int, seed: int = 42) -> None:
        self.width: int = width
        self.height: int = height
        self.seed: int = seed

        self.grid: List[List[int]] = [
            [15 for _ in range(width)] for _ in range(height)]

    def generate(self, perfect: bool = True) -> None:
        """aqui vai o algoritmo de backtracking por recursao"""
        random.seed(self.seed)
        self._apply_42_pattern()

        start_point = (0, 0)
        stack = [start_point]  # guarda caminho atual
        visited = {start_point}

        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 15:
                    visited.add((x, y))

        while stack:
            cx, cy = stack[-1]
            neighbors = []

            # procurar locais nao visitados
            for dx, dy, wall, opp_wall in self.DIRECTIONS.values():
                nx, ny = cx + dx, cy + dy

                # garante que estamos dentro do labirinto
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in visited:
                        neighbors.append((nx, ny, wall, opp_wall))

            if neighbors:
                nx, ny, wall, opp_wall = random.choice(neighbors)

                # parte as paredes - tanforma 1 em 0
                self.grid[cy][cx] &= ~wall
                self.grid[ny][nx] &= ~opp_wall

                visited .add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()  # volta a tras se nao encontra outra saida

    def get_path_string(self, path: List[Tuple[int, int]]) -> str:
        """Converts the list of coordinates [(x,y)] into a string 'EENSS'"""

        path_str = ""
        for i in range(len(path) - 1):
            curr = path[i]
            nxt = path[i + 1]
            dx = nxt[0] - curr[0]
            dy = nxt[1] - curr[1]

            if dx == 1:
                path_str += "E"
            elif dx == -1:
                path_str += "W"
            elif dy == 1:
                path_str += "S"
            elif dy == -1:
                path_str += "N"
        return path_str

    def export_to_file(
            self, filename: str, entry: Tuple[int, int],
            exit_coords: Tuple[int, int], path: List[Tuple[int, int]]):
        """write the maze in hexadecimal format"""
        try:
            with open(filename, 'w') as file:
                for row in self.grid:
                    # converte cada int(0-15) para hexadecimal em maisculo
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
        """Find the shortest path using BFS for the exporter and viewer."""
        queue = [start]
        parent = {start: None}

        while queue:
            cx, cy = queue.pop(0)
            if (cx, cy) == end:
                break

            for dx, dy, wall, _ in self.DIRECTIONS.values():
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if not (self.grid[cy][cx] & wall):
                        if (nx, ny) not in parent:
                            parent[(nx, ny)] = (cx, cy)
                            queue.append((nx, ny))

        path = []
        curr = end
        if end not in parent:
            return []
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
        return path[::-1]

    def _apply_42_pattern(self) -> None:
        """draw number '42' with closed celules into the maze"""

        # verifica se o labirinto tem tamanho minino para o desenho ser visivel
        if self.width < 15 or self.height < 10:
            print("Warning: Maze size does not allow for for '42' pattern")
            return

        mid_x = self.width // 2
        mid_y = self.height // 2

        four = [
            (mid_x-4, mid_y-2), (mid_x-4, mid_y-1), (mid_x-4, mid_y),
            (mid_x-3, mid_y), (mid_x-2, mid_y),
            (mid_x-2, mid_y-2), (mid_x-2, mid_y-1), (mid_x-2, mid_y),
            (mid_x-2, mid_y+1), (mid_x-2, mid_y+2)
        ]

        two = [
            (mid_x+1, mid_y-2), (mid_x+2, mid_y-2), (mid_x+3, mid_y-2),
            (mid_x+3, mid_y-1), (mid_x+3, mid_y),
            (mid_x+2, mid_y), (mid_x+1, mid_y),
            (mid_x+1, mid_y+1), (mid_x+1, mid_y+2),
            (mid_x+2, mid_y+2), (mid_x+3, mid_y+2)
        ]

        # Aplicar as células fechadas (valor 15)
        for x, y in four + two:
            if 0 <= x < self.width and 0 <= y < self.height:
                self.grid[y][x] = 15
