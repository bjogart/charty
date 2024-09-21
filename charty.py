import random
from algorithm import ALGORITHMS, MazeAlgorithm, measure_distance
from img import save_color_data
from maze import Maze, Point
from palette import Hsl, Palette, paint_maze
from parser import select_by_id, parsed_args
from transmission import TRANSMISSIONS, Transmission

def chart(width: int, height: int, maze_algorithm_constructor: MazeAlgorithm, primary_color: Hsl, secondary_color: Hsl, transmission_constructor: Transmission, destination: str):
    # The generator was inspired by https://github.com/jamis/amazing-desktops.
    # 1. Create a maze with the same size as the resolution of the image.
    #    This maze has walls surrounding every cell, so it's not actually much of a maze, yet.
    maze = Maze(width, height)
    start_coordinates = Point.random(maze.shape())
    # 2. Use a maze algorithm to build the actual maze.
    #    The algorithm is implemented through the `MazeAlgorithm` abstract base class.
    maze_algorithm_constructor().build(maze, start_coordinates)
    # 3. Measure the distance from the starting coordinates to every cell.
    measure_distance(maze, start_coordinates)
    # 4. Color the maze by interpolating between to colors based on the relative distance to the starting coordinates.
    palette = Palette(primary_color, secondary_color, transmission_constructor())
    paint_maze(maze, palette)
    # 5. Take the maze, extract the colors of each cell, and convert them to an image file.
    save_color_data(destination, maze.cell_values())

if __name__ == "__main__":
    args = parsed_args()

    random.seed(args.seed)

    chart(
        args.width,
        args.height,
        select_by_id("algorithm", ALGORITHMS, args.algorithm),
        args.primary_color.to_hsl() if args.primary_color else Hsl.random(),
        args.secondary_color.to_hsl() if args.secondary_color else Hsl.random(),
        select_by_id("transmission", TRANSMISSIONS, args.transmission),
        args.destination,
    )

# Mind that this generator is purposefully not feature-complete.
# There's a lot of extra stuff in there to fiddle with if the urge strikes you.
# Off the top of my head:
#
# - There are lots of other maze generators.
#   Some make mazes with a completely different aesthetic from the long, winding passages of a recursive backtracker maze!
# - Multi-color gradients.
#   Right now a Palette can only handle 2 colors, but there's no real reason there can't be more.
#   An easy way would be to chain multiple 2-color palettes and delegate to one palette based on the value of `t`:
#   So if you have 3 colors, A, B, and C, make palettes A--B and B--C.
#   If t <= 0.5, use palette A--B, and B--C otherwise.
#   Then adjust t so it has the right range and delegate to the right palette.
#   That should work for pretty much any number of palettes if delegated correctly.
# - Path highlights.
#   The current color algorithm uses only 24 out of 28 bits available, so there are some fun things you might do with the rest.
#   One of them could be to put a flag in there to indicate a path of your choice (like the longest path, or the twistiest).
#   Then during painting select an accent color to highlight that specific path.
# - Partial mazes.
#   Currently there is an implicit assumption in the measuring and painting steps that every single square will be part of the maze.
#   Recursive backtracking will indeed always visit every square, but other algorithms might not.
#   (Or you could introduce a backtracker version that quits after 80% of the cells is visited. Or something.)
#   `measure_distance` is a depth-first search that will only visit cells connected to the starting cell.
#   Then you could adapt the painting algorithm to fill in the other squares with a background color just by adding an `else` statement to handle sentinel values left by `measure_distance`.
# - Wackier transmissions.
#   An easy way to get some fun color combinations is to just plug in some weird function, mathematically valid or not.
