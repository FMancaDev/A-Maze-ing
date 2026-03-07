from RenderMaze import RenderMaze
# from typing import Any

maze: RenderMaze = RenderMaze()
maze.create_image()


filename: str = 'maze.txt'
filename2: str = 'heigher_maze.txt'
try:
    maze_text: list[str] = []
    maze_lines: list[str] = []
    path_info: list[str] = []
    empty_lines: int = 0
    with open(filename, 'r') as f:
        while True:
            line: str = f.readline()
            if not line:
                break
            maze_text.append(line)
    is_path_info: bool = False
    for line in maze_text:
        if not is_path_info:
            if line == '\n':
                is_path_info = True
                continue
            maze_lines.append(line)
        else:
            if line == '\n':
                break
            path_info.append(line)

except Exception as e:
    print(e)
maze.fill_rect({
    'x0': 0,
    'x1': maze.win_dim['width'],
    'y0': 0,
    'y1': maze.win_dim['height'],
}, 0xFF7b00ff)
maze.set_layout(maze_lines)
maze.draw_path(path_info, 0xFF4DFF4D)
maze.draw_maze(maze_lines, 0xFFFFCC00, 0xFFFFEB99)
maze.draw_frame(maze_lines, 0xFFFFCC00)
maze.mlx.mlx_loop(maze.mlx_ptr)
