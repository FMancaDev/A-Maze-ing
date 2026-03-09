from RenderMaze import RenderMaze
# from typing import Any

maze: RenderMaze = RenderMaze()
maze.create_image()


filename: str = 'maze.txt'
filename2: str = 'heigher_maze.txt'

maze.parse_maze(filename)
maze.fill_rect({
    'x0': 0,
    'x1': maze.win_dim['width'],
    'y0': 0,
    'y1': maze.win_dim['height'],
}, 0xFF7b00ff)
maze.set_layout(maze.maze_utils['maze_lines'])
maze.draw_path(maze.maze_utils['path_info'], 0xFF4DFF4D)
maze.draw_maze(maze.maze_utils['maze_lines'], 0xFFFFCC00, 0xFFFFEB99)
maze.draw_frame(maze.maze_utils['maze_lines'], 0xFFFFCC00)
maze.mlx.mlx_loop(maze.mlx_ptr)
