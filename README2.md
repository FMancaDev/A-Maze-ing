<i>This project has been created as part of the 42 curriculum by mnogueir, fomanca. </i>

# A-Maze-ing

## Description
<b>A-Maze-Ing</b> is a program that reads a configuration file, generates a maze based on the specified parameters, and outputs it to a file using a hexadecimal representation of walls. Additionally, it provides a visual representation of the generated maze.<br>
If the maze happens to be set as "PERFECT" only one pathway from the entry to the exit coordinates must be available.<br>
A typical maze configuration file would look like this:
```
# Maze Configuration

WIDTH=x
HEIGHT=y
ENTRY=x1,y1
EXIT=x2,y2
OUTPUT_FILE=maze.txt
PERFECT=True
GEN_ALGO=backtracking
```

A typical <code>maze.txt</code> file would look like this:
```
B9393
C6C6A
93956
AAA93
EC46E

0,0
4,4
SENESENESSWWSSENES
```
The last three lines on the <code>maze.txt</code> file give us information on the entry coordinates, the exit coordinates and the pathway from entry to exit respectivelly.

### The Generator

The `Generator` is the core of the project, responsible for the mathematical creation of the maze grid. It uses a **Depth-First Search (DFS)** algorithm with **Recursive Backtracking** to ensure that every cell is reachable and that the maze has no loops (when set to `PERFECT=True`).

* **Matrix Representation:** The maze is stored as a 2D grid where each cell is a 4-bit integer. Each bit represents a wall (North, South, East, West).
* **Hexadecimal Export:** The generator converts these bitmask values into a hexadecimal string, following the project's specific output format.
* **Solver:** It includes a pathfinding logic that calculates the unique solution from the entry point to the exit point, which is then used by the renderer to display the solution path.


### Rendering
<table>
    <tr>
        <td><b>Window.py</b></td>
        <td><code>Window.py</code> Deals with the initialization of the window by setting the needed attributes, starting the window display and setting up main event hooks. The constructor will take the window's width, height and name as parameters. The attributes set during instantiation are used to later call any <b>minilibx</b> methods (<code>mlx_new_image</code>, <code>mlx_put_image_to_window</code>, <code>mlx_xpm_file_to_image</code>, etc.).<br>
        This class also provides useful methods to create new images, create copies of previously created images, quit the program safely and keep track of key presses and releases.</td>
    </tr>
        <tr>
        <td><b>Renderer.py</b></td>
        <td><code>Renderer.py</code> Deals with any type of drawing event, often by picking up coordinates from a MazeGenerator object and operating on the <code>[memoryview]</code> of an image dictionary. It's constructor only takes the window width and height as parameters, just so it doesn't mistakenly write pixels off of the windows bounds.</td>
    </tr>
    <tr>
        <td><b>constants.py</b></td>
        <td><code>constants.py</code> provides useful aliases and shortcuts for difficult to memorize or lengthy data like keycodes or the active walls in a maze cell.
    </tr>
        <tr>
        <td><b>utils.py</b></td>
        <td><code>utils.py</code> deals with the main tasks that are activated following user input (changing the maze, changing maze colors, displaying static or animated images, etc.). This is the bulk of the program, where the <code>Window</code>, <code>Renderer</code> and <code>MazeGenerator</code> objects are called and acted upon to deliver the fastest and most memory efficient way to display graphics.</td>
    </tr>
</table>

### a_maze_ing.py | the main file
The <code>a_maze_ing.py</code> file starts off by parsing the configuration file and then feeding those inputs to our <code>MazeGenerator</code>, while also instantiating <code>Window</code> and <code>Renderer</code>. <code>key_actions()</code> is later hooked to the event loop started at the end of this file so that, at each frame, the program will check wether a given key was pressed or released and act accordingly by calling the respective function at <code>utils.py</code>.
<br>The loop is then started, waiting for the <code>quit_prg()</code> function to eventually be called.


### Generator
<tr>
    <td><b>generator.py</b></td>
    <td>
        <code>MazeGenerator</code> is the core engine of the project.
        It manages the maze's lifecycle from initialization to file export.
        It stores the maze as a 1D list (optimized for performance) and uses
        bitwise operations (<code>1, 2, 4, 8</code>) to represent walls in each cell.
        <br><br>
        <b>Key features include:</b><br>
        • <b>Algorithm Selection:</b> Supports both <code>Iterative DFS (Backtracking)</code> and <code>Randomized Prim's</code>.<br>
        • <b>Logo Integration:</b> Dynamically calculates the "42" logo's position and seals it.<br>
        • <b>Imperfect Mode:</b> Removes extra walls to create loops.
    </td>
</tr>

## Instructions

### 1. Requirements

This project is designed to run on **Linux (Ubuntu/Fedora)** and requires `python3` and the `venv` module.

### 2. Installation & Running

The project includes a `Makefile` to automate the setup process:

* **To setup and run:**
    ```bash
    make install & make run
    ```
    *This will create a virtual environment and install the local MiniLibX wheels and start the program.*

* **To clean the environment:**
    ```bash
    make clean   # Removes the virtual environment and all the extra files
    ```

### 3. Controls
| Key | Action |
| :--- | :--- |
| `R` | Regenerate the maze with a new seed |
| `H` | Toggle the solution path (Hide/Show) |
| `Arrows` | Change Maze Width/Height in real-time |
| `CTRL + Arrows` | Cycle through different color themes |
| `ESC` | Exit the program safely |


## Reproducibility

The A-Maze-Ing generator is designed to be fully deterministic. By providing a specific seed, the same maze structure and solution path will be generated every time, regardless of the system.

You can verify the consistency of the MazeGenerator using the following Python snippet:
 ```python
from mazegen.generator import MazeGenerator

# Setup parameters
width, height = 25, 25
entry, exit_p = (0, 0), (24, 8)
seed = 42

# Initialize and generate
gen = MazeGenerator(width, height, entry, exit_p, seed)
for _ in gen.generate(perfect=True, method="backtracking"):
    pass # Consumes the generation generator

# Solve and Verify
path = gen.solve(entry, exit_p)
path_str = gen.get_path_string(path)
first_row = "".join(f"{gen.grid[x]:X}" for x in range(width))

print(f"--- Maze Verification (Seed: {seed}) ---")
print(f"First Row Hex: {first_row}")
print(f"Total Path Length: {len(path_str)} steps")

```
<br>Expected Output for Seed 42 (25x25):

  - First Row Hex: B9393955553D1555393D15553

  - Total Path Length: 264 steps


## Resources

 - Minilibx documentation helper: <a href="https://harm-smits.github.io/42docs/libs/minilibx">42 Docs | Minilibx</a><i> by harm-smits;</i>

 - Backtracking Algorithm explained: <a href="https://medium.com/@andreaiacono/backtracking-explained-7450d6ef9e1a">Medium | Backtracking</a><i> by Andrea Iacono;</i>

 - Collection of Maze Generation Algorithms: <a href="https://professor-l.github.io/mazes/">Maze Generation Algorithms</a><i> by Professor L;</i>

 - Prim's Algorithm for MST: <a href="https://vishalrana9915.medium.com/understanding-prims-algorithm-e6514a6e483c">Medium | Prim's Algorithm</a><i> by Vishal Rana;</i>


### AI usage

- Summarizing and clarifying the documentation regarding the <b>minilibx</b>;

- Checking for the most efficient ways to write pixels to memory following the mlx library.

- Brainstorming about ways to save up on memory and keeping the program fast.

- Exploring ways to manipulate pixels in memory for rendering.

- Learning bitmasking manipulations for efficient maze storage and manipulation.

