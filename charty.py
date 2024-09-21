import random
from algorithm import ALGORITHMS, MazeAlgorithm, measure_distances
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
    measure_distances(maze, start_coordinates)
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
