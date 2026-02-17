import random
from typing import List, Tuple


class MazeGenerator():

    NORTH = 1  # 0001
    EAST = 2  # 0010
    SOUTH = 4  # 0100
    WEST = 8  # 1000

    DIRECTIONS = {
        "N": (0, -1, NORTH, SOUTH),
        "S": (0, 1, SOUTH, SOUTH),
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

        start_point = (0, 0)
        stack: List[Tuple[int, int]] = [start_point]  # guarda caminho atual
        visited = {start_point}

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
                self.grid[cx][cy] &= ~wall
                self.grid[nx][ny] &= ~opp_wall

                visited .add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()  # volta a tras se nao encontra outra saida

    def _apply_42_pattern(self) -> None:
        # verifica se ha espaco para desenhar o '42'
        if self.width < 10 or self.height < 10:
            print("Warning: Maze too small for '42' pattern")
            return

        # exemplo
        pattern_42 = [
            (3, 3), (3, 4), (3, 5), (4, 5), (5, 3), (5, 4), (5, 5)
        ]

        for x, y in pattern_42:
            self.grid[x][y] = 15
