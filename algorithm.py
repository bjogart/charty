from maze import Direction, Maze, Point, UInt28
from tqdm import tqdm
import random

class MazeAlgorithm:
    """
    An abstract class that defines the API of a maze-generating algorithm.

    If you feel like trying your hand at this, check out https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap.html.
    """

    def id() -> str:
        """
        A unique ID for this maze generation algorithm.
        """
        raise NotImplementedError()

    def build(self, maze: Maze, start_coordinates: Point):
        """
        Generate a maze inside `maze`.
        If the algorithm starts from a given point, that point should be `start_coordinates`.
        If not, then `start_coordinates` can be safely ignored.
        """
        raise NotImplementedError()

class RecursiveBacktracker(MazeAlgorithm):
    def __init__(self):
        super().__init__()

    def id() -> str:
        return "RecursiveBacktracker"

    def shuffled_directions() -> list[Direction]:
        """
        Return a randomly shuffled list of all directions.
        The recursive backtracking algorithm does not necessarily require direction shuffling, but it helps prevent direction bias.
        """
        return random.sample(list(Direction.all()), k=len(Direction.all()))

    def build(self, maze: Maze, start_coordinates: Point):
        cell = maze[start_coordinates]

        if not cell:
            raise Exception(f"{start_coordinates} out of bounds for maze of size {maze.shape()}")

        # As the name implies, the recursive backtracking algorithm is supposed to be recursive.
        # Unfortunately, a 1080 x 1920 maze would require a stack size of about 2 million.
        # That's why the algorithm below uses a stack with a loop instead.

        # The recursive backtracking algorithm goes as follows.
        progress = tqdm(desc="build maze", total=maze.shape().x * maze.shape().y)
        # 1. Pick any cell (the "root").
        stack = [(cell, RecursiveBacktracker.shuffled_directions())]
        while stack:
            (cell, directions) = stack.pop()
            # 2. Pick any direction from that cell.
            for direction in directions:
                # 3. If there is a neighboring cell in that direction...
                neighbor = maze[cell.coordinates + direction.delta()]
                if neighbor:
                    # ...and that direction has not been visited yet...
                    if not neighbor.has_neighbors():
                        # 4. Open a corridor to that cell.
                        cell.open_corridor(direction)
                        # 5. Make that cell the current cell, then repeat from step 2.
                        stack.append((cell, directions))
                        stack.append((neighbor, RecursiveBacktracker.shuffled_directions()))
                        # Once all neighboring cells are visited, that cell is complete.
                        # Backtrack to a cell that still has unvisited neighbors.
                        # The algorithm terminates once all neighbors of the root are visited.
                        break
            # This construct (the "for-else") is a weird Python thing which is useful in exactly one scenario: this one.
            # The else triggers only if the for loop ends without triggering a break statement.
            # Said for loop iterates through directions that have not yet been explored.
            # If it is exhausted, then that means this cell has been explored in full.
            else:
                progress.update(1)
        progress.close()

def measure_distances(maze: Maze, start_coordinates: Point):
    cell = maze[start_coordinates]

    if not cell:
            raise Exception(f"{start_coordinates} out of bounds for maze of size {maze.shape()}")
    # This algorithm is just depth-first search, but with manual tracking because the call stack would overflow if the algorithm were recursive.
    progress = tqdm(desc="measure distance", total=maze.shape().x * maze.shape().y)
    # While the distance of a cell to itself is by definition always 0, we also need cells to store a value to denote they have not been visited yet.
    # Right now, all cells have a value of 0, making that the perfect sentinel.
    # So use 1 as the minimum distance instead, and we'll compensate for that during painting.
    stack = [(cell, 1)]
    while stack:
        # Grab the current cell.
        (cell, distance) = stack.pop()
        # Set the value of that cell to the distance from the root.
        cell.set_value(UInt28.clamped(distance))

        for neighbor in cell.reachable_neighbors():
            if neighbor.value() == 0:
                # Grab all neighbors that have not been visited yet and put them on the todo stack.
                stack.append((neighbor, distance + 1))
        progress.update()
    progress.close()

# This list has all the algorithms so the command-line parser knows about them.
# If you write a new algorithm, make sure to add it here!
ALGORITHMS = [RecursiveBacktracker]
