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



## Instructions



## Resources

 - Minilibx documentation helper: <a href="https://harm-smits.github.io/42docs/libs/minilibx">42 Docs | Minilibx</a><i> by harm-smits;</i>


### AI usage

- Summarizing and clarifying the documentation regarding the <b>minilibx</b>;

- Checking for the most efficient ways to write pixels to memory following the mlx library.

- Brainstorming about ways to save up on memory and keeping the program fast.

