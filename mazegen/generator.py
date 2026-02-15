from typing import List, Tuple


class MazeGenerator():

    NORTH = 1  # 0001
    EAST = 2  # 0010
    SOUTH = 4  # 0100
    WEST = 8  # 1000

    def __init__(self, width: int, height: int, seed: int = 42) -> None:
        self.width: int = width
        self.height: int = height
        self.seed: int = seed

        self.grid: List[List[int]] = [
            [15 for _ in range(width)] for _ in range(height)]

    def generate(self, perfect: bool = True) -> None:
        """aqui vai o algoritmo de backtracking por recursao"""
        pass

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
