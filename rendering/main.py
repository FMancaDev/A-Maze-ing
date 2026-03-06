from RenderMaze import RenderMaze
# from typing import Any

maze: RenderMaze = RenderMaze()
maze.create_image()


filename: str = 'maze.txt'
filename2: str = 'heigher_maze.txt'
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
maze.fill_rect({
    'x0': 0,
    'x1': maze.win_dim['width'],
    'y0': 0,
    'y1': maze.win_dim['height'],
}, 0xFF7b00ff)
maze.draw_frame(maze_lines)
maze.draw_maze(maze_lines, 0xFFFFFFFF)
maze.mlx.mlx_loop(maze.mlx_ptr)
