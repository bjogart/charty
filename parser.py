from argparse import ArgumentParser
from typing import List

from algorithm import ALGORITHMS, RecursiveBacktracker
from palette import Rgb
from transmission import TRANSMISSIONS, Linear

def select_by_id[T](thing: str, items: List[T], id: str) -> T:
    """
    Selects an item from `items` whose .id() static function returns `id`.

    This function is used to parse a maze building algorithm and a transmission function from a string input.
    """
    # Replace uppercase characters by lowercase ones to make string matching case-insensitive.
    lower_id = id.lower()
    # Collect all items with the right ID.
    # This should be just one item in most cases, since IDs are supposed to be unique.
    items = [item for item in items if lower_id == item.id().lower()]

    if len(items) == 0:
        raise Exception(f"unknown {thing}: {id}")

    return items[0]

def parsed_args():
    parser = ArgumentParser(prog="Charty", description="Randomly generates map-like screensavers or images.", epilog="Bottom text")

    parser.add_argument("destination", help="Image destination. The generated image will be saved here with a file format identified from the file extension.")
    parser.add_argument("-W", "--width", help="Width of the generated image in pixels. The default is an image 1920 pixels wide.", type=int, default=1920)
    parser.add_argument("-H", "--height", help="Height of the generated image in pixels. The default is an image 1080 pixels high.", type=int, default=1080)
    parser.add_argument("-a", "--algorithm", help="Algorithm used to generate the underlying maze. The default is the recursive backtracking algorithm", choices=[a.id() for a in ALGORITHMS], default=RecursiveBacktracker.id())
    parser.add_argument("-c1", "--primary_color", help="Color of the primary point. This is the point where maze exploration starts. If not set, this value will be generated randomly. Colors can be ", type=Rgb.parse)
    parser.add_argument("-c2", "--secondary_color", help="Color of the secondary point. This is the point furthest away from the starting point. If not set, this value will be generated randomly.", type=Rgb.parse)
    parser.add_argument('-s', "--seed", help="Seed for color palette randomization and maze generation.", type=int)
    parser.add_argument('-t', "--transmission", help="Color transmission function. Transmissions are functions that take a linear value between 0 and 1 and return a (possibly different) value between 0 and 1 which indicates how the generator should interpolate between the primary and secondary colors. By default, a linear transmission will be used.", choices=[t.id() for t in TRANSMISSIONS], default=Linear.id())

    return parser.parse_args()
