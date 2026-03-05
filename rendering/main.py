from RenderMaze import RenderMaze
from typing import Any

maze: RenderMaze = RenderMaze()
maze.create_image()


filename: str = 'maze.txt'
try:
    maze_lines: list[str] = []
    with open(filename, 'r') as f:
        while True:
            line: str = f.readline()
            if line == '\n':
                break
            maze_lines.append(line)
except Exception as e:
    print(e)

maze.draw_frame(maze_lines)
maze.mlx.mlx_loop(maze.mlx_ptr)
