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
        <td><code>Window.py</code> Deals with the initialization of the window by setting the needed attributes, starting the window display and setting up main event hooks. The constructor will take the window's width, height and name as parameters. The attributes set during instantiation are used to later call any <b>minilibx</b> methods (<code>mlx_new_image</code>, <code>mlx_put_image_to_window</code>, <code>mlx_xpm_file_to_image</code>).<br>
        This class also provides useful methods to create new images, create copies of previously created images, quit the program safely and keep track of key presses and releases.</td>
    </tr>
        <tr>
        <td><b>Renderer.py</b></td>
        <td><code>Renderer.py</code> Deals with any type of drawing event, often by picking up coordinates from a MazeGenerator object and operating on the <code>[memoryview]</code> of an image dictionary. It's constructor only takes the window width and height as parameters, just so it doesn't mistakenly write pixels off of the windows bounds.</td>
    </tr>
    <tr>
        <td><b>Window.py</b></td>
        <td><code>Window.py</code> Deals with the initialization of the window by setting the needed attributes, starting the window display and setting up main event hooks. The constructor will take the window's width, height and name as parameters. The attributes set during instantiation are used to later call any <b>minilibx</b> methods (<code>mlx_new_image</code>, <code>mlx_put_image_to_window</code>, <code>mlx_xpm_file_to_image</code>).<br>
        This class also provides useful methods to create new images, create copies of previously created images, quit the program safely and keep track of key presses and releases.</td>
    </tr>

</table>



## Instructions



## Resources



### AI usage

