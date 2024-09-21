from enum import IntFlag, auto
from typing import Callable, Iterator, Optional, Self
import numpy as np
import random

class UInt28(int):
    """
    A 28-bit integer.

    Mazes are implemented as a numpy array of 32-bit integers.
    Each integer denotes a cell; 4 bits are reserved for corridors (1 per direction).
    That leaves 28 bits to store arbitrary values.

    This class is used once: as an argument to `Cell.set_value`.
    Values belonging to this type can only be made through a constructor which will raise an exception if bits other than the first 28 are set.
    Though Python's lack of typing makes total safety difficult, this construction at least, makes it difficult to cause weird bit-twiddling errors happen.
    """

    # 28 set bits.
    MASK = 0xfffffff

    def __init__(self, value: int):
        if value & ~UInt28.MASK != 0:
            raise Exception(f"{value} does not fit in a 28-bit integer")
        self.value = value

    def clamped(value: int) -> Self:
        return UInt28(value & UInt28.MASK)

    def to_int(self) -> int:
        return self.value

    def __repr__(self) -> str:
        return f"UInt28({self.value})"

class Point:
    """
    An x--y coordinate.
    Not technically necessary (just use a Python tuple), but between `point.y` and `point[1]` I know my preference.
    """

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def random(bound: Self) -> Self:
        """
        Creates a random point in the range [0, {x, y}].
        """
        return Point(random.randrange(bound.x), random.randrange(bound.y))

    def from_tuple(coordinates: tuple[int, int]) -> Self:
        x, y = coordinates
        return Point(x ,y)

    def to_tuple(self) -> tuple[int, int]:
        return (self.x, self.y)

    def __add__(self, rhs: Self) -> Self:
        return Point(self.x + rhs.x, self.y + rhs.y)

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"

# Maze corridors are stored in the lowest 4 bits of a cell.
CORRIDORS_MASK = 0xf
# Length of the bit mask. (ie. 4 bits.)
CORRIDORS_WIDTH = 4

class Direction(IntFlag):
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()

    def all() -> Iterator[Self]:
        return Direction.__members__.values()

    def delta(self) -> Point:
        """
        Returns the unit vector corresponding to a direction.
        In other words, the vector that, if added to another vector, creates a new vector one step into the direction of `self`.
        """
        match self:
            case Direction.NORTH:
                return Point(0, -1)
            case Direction.EAST:
                return Point(1, 0)
            case Direction.SOUTH:
                return Point(0, 1)
            case Direction.WEST:
                return Point(-1, 0)

    def opposite(self) -> Self:
        match self:
            case Direction.NORTH:
                return Direction.SOUTH
            case Direction.EAST:
                return Direction.WEST
            case Direction.SOUTH:
                return Direction.NORTH
            case Direction.WEST:
                return Direction.EAST

    def __invert__(self) -> Self:
        """
        This function is mainly here because my Python is lacking.
        `Direction` subclasses IntFlag, meaning that all directions are also bit-flag integers.
        Unfortunately it seems that the invert operation is capped to the number of bits actually used.
        In other words, ~0x1 is 0xe, not 0xfffffffe.
        The difference is important because, as part of some operations, the inverted value will be AND-ed together with a 32-bit integer.
        If limited to 4 bits, that means we'd lose data.
        The fix is simple though: convert the bit-flag to a bare integer and inverting that one.
        """
        return ~int(self)

class Maze:
    def __init__(self, width: int, height: int):
        """
        Initialize a maze of the given `width` and `height`.

        All cells are initialized with a value of `0` and with no connections to other cells.
        """
        self.data = np.zeros((width, height), dtype=np.uint32)

    def shape(self) -> Point:
        """
        The shape of this maze.

        Technically a `Point` and a `Size` are different things, but since they are implemented much the same way a `Point` will have to do.
        This is not a game engine.
        """
        return Point.from_tuple(self.data.shape)

    def in_bounds(self, coordinates: Point) -> bool:
        return coordinates.x >= 0 and coordinates.x < self.shape().x and coordinates.y >= 0 and coordinates.y < self.shape().y

    def __getitem__(self, coordinates: Point) -> Optional["Cell"]:
        """
        Returns the cell at `coordinates`, or `None` if the coordinates lie outside the maze.
        """
        if self.in_bounds(coordinates):
            return Cell(self, coordinates)
        else:
            return None

    def _get_and_maybe_mutate_cell(self, coordinates: Point, mutate_cell: Callable[[int], Optional[int]]) -> int:
        """
        Gets the cell stored at `coordinates` and feeds its integer representation to `mutate_cell`.
        The return value depends on the result:

        - If `mutate_cell` returns `None`, this method returns the cell's integer value.
        - Otherwise update the cell's value to be the result of `mutate_cell`, then return that value.

        Admittedly this is probably the dumbest thing in the whole codebase.
        There is only one reason it is here and that reason is that I wanted only one access point to the inner data field rather than two.
        (One for reading, one for writing.)
        Fewer accesses == fewer chances for bugs to sneak in.

        Waaaayyy over-engineered, though.
        """
        coordinates = coordinates.to_tuple()
        value = self.data[coordinates]

        mutated_value = mutate_cell(value)
        if mutated_value:
            self.data[coordinates] = mutated_value
            return mutated_value
        else:
            return value

    def cells(self) -> Iterator["Cell"]:
        for y in range(self.shape().y):
            for x in range(self.shape().x):
                yield Cell(self, Point(x, y))

    def cell_values(self) -> np.ndarray:
        # The right-shift removes the 4 corridor bits.
        return self.data >> CORRIDORS_WIDTH

    def __repr__(self) -> str:
        display = " " + ("_" * (2 * self.shape().x - 1)) + "\n"

        for y in range(self.shape().y):
            display += "|"

            for x in range(self.shape().x):
                cell = self[Point(x, y)]

                display += " " if cell.has_corridor(Direction.SOUTH) else "_"
                if cell.has_corridor(Direction.EAST):
                    next_cell = self[Point(x + 1, y)]
                    display += " " if (cell.has_corridor(Direction.SOUTH) or next_cell.has_corridor(Direction.SOUTH)) else "_"
                else:
                    display += "|"

            display += "\n"
        return display

class Cell:
    def __init__(self, maze: Maze, coordinates: Point):
        # Cells do not actually store their own data.
        # Rather, they have a reference to their maze and their coordinates.
        # This lets them change their own value by accessing the maze and changing it on demand through various functions.
        self.maze = maze
        self.coordinates = coordinates

    def _data(self) -> int:
        """
        Gets the full 32-bit integer associated with this cell.

        Each cell has a 32-bit integer associated with it.
        This integer stores whether this cell has open corridors (lowest 4 bits), and an arbitrary 28-bit value set by the user.
        In binary, that looks like so:

        ```text
        0b0000 0000 0000 0000 0000 0000 0000 0000
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ^^^^
          |                                  +--- Corridor bits (4 bits, Direction values can be used as bit-flags for indexing)
          +-------------------------------------- Arbitrary 28-bit value
        ```
        """
        return int(self.maze._get_and_maybe_mutate_cell(self.coordinates, lambda _: None))

    def set_value(self, value: UInt28):
        # See the description of `UInt28` for why this check is here.
        if not isinstance(value, UInt28):
            raise Exception(f"{value} is not of type UInt28")
        # Brief explanation of bit-twiddling.
        # We want to set remove the previous value and then set the new one.
        # However, we do need to keep the current corridor status.
        # By AND-ing the previous value (which has the corridors) with a bit mask that has 1s for just the corridor bits, we keep those and get 0s for the other 28.
        # Then we take the new 28-bit value and shift it left 4 bits.
        # Now it has 0s for the 4 lower bits.
        # OR them together and you get the new value.
        self.maze._get_and_maybe_mutate_cell(self.coordinates, lambda previous_value: (previous_value & CORRIDORS_MASK) | (value.to_int() << CORRIDORS_WIDTH))

    def value(self) -> int:
        return self._data() >> CORRIDORS_WIDTH

    def _mutate_corridor(self, direction: Direction, mutate: Callable[[int, Direction], int]):
        """
        Adjusts the status of a corridor bit as directed by `mutate`.

        `mutate` takes the current integer and a direction and it returns the new integer.

        This construction is not really necessary, but it means I don't have to duplicate (mostly the same code) for `{open, close}_corridor`.
        """
        # Get the coordinates of the neighboring cell.
        neighbor_coordinates = self.coordinates + direction.delta()
        # Only mutate if a cell exists in that direction.
        # Can't make corridors on the edges of the maze!
        if self.maze[neighbor_coordinates]:
            # Mutate the corridor from this cell to the neighboring cell.
            self.maze._get_and_maybe_mutate_cell(self.coordinates, lambda value: mutate(value, direction))
            # Mutate the corridor from neighboring cell to this cell.
            #
            # Mazes are a-directional graphs, technically.
            # Still, this representation is directional.
            # It could be made a-directional by storing only 2 directions (like east & south) per cell.
            # However, that would make some checks more difficult.
            # For example, you would need to query neighboring cells if you want to know if this cell has a corridor connecting to the west or north.
            # That's more trouble than I thought it's worth (saving 2 bits per cell).
            self.maze._get_and_maybe_mutate_cell(neighbor_coordinates, lambda value: mutate(value, direction.opposite()))

    def open_corridor(self, direction: Direction):
        # Open a corridor if it is not already open by OR-ing with the relevant direction bit-flag.
        self._mutate_corridor(direction, lambda value, direction: value | direction)

    def close_corridor(self, direction: Direction):
        # Close a corridor by AND-ing with a bit-mask that has all bits except the bit for that corridor set.
        self._mutate_corridor(direction, lambda value, direction: value & ~direction)

    def has_corridor(self, direction: Direction) -> bool:
        return self._data() & direction

    def has_neighbors(self) -> bool:
        return self._data() & CORRIDORS_MASK != 0

    def reachable_neighbors(self) -> Iterator[Self]:
        for direction in Direction.all():
            if self.has_corridor(direction):
                neighbor = self.maze[self.coordinates + direction.delta()]
                if neighbor:
                    yield neighbor
