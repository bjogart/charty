import random
from maze import Maze, UInt28
from tqdm import tqdm
from typing import Self, Union
import colorsys
import re
from transmission import Transmission

class Rgb:
    """
    A color in the red-green-blue color model.
    Each component is in the range `[0.0, 1.0]`.
    """
    def __init__(self, red: float, green: float, blue: float):
        self.red = red
        self.green = green
        self.blue = blue

    def parse(text: str) -> Self:
        # It is quite common for RGB to use integer representations in the range [0, 256).
        # We, however, use [0.0, 1.0] floating point numbers instead.
        # This helper function converts the former to the latter.
        def rgb_from_int(red: int, green: int, blue: int) -> Rgb:
            return Rgb(red / 255, green / 255, blue / 255)
        # Replace uppercase characters by lowercase ones to make string matching case-insensitive.
        text = text.lower()
        # If the text is 6 hexadecimal characters, treat pairs of hexadecimals as integers in the order R -> G -> B.
        # So `ff8800` => `Rgb('ff', '88', '00')` => `Rgb(1.0, 0.53, 0.0)`.
        match = re.fullmatch("([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})", text)
        if match:
            r = int(match.group(1), 16)
            g = int(match.group(2), 16)
            b = int(match.group(3), 16)
            return rgb_from_int(r, g, b)
        # If the text is 3 hexadecimal characters, duplicate each digit, then do as the previous case.
        # So `f80` => `Rgb('ff', '88', '00')` => `Rgb(1.0, 0.53, 0.0)`.
        match = re.fullmatch("([0-9a-f])([0-9a-f])([0-9a-f])", text)
        if match:
            r = int(match.group(1) * 2, 16)
            g = int(match.group(2) * 2, 16)
            b = int(match.group(3) * 2, 16)
            return rgb_from_int(r, g, b)
        # If the text is 2 hexadecimal characters, then make this a grayscale number (red component == green component == blue component).
        # So `88` => `Rgb('88', '88', '88')` => `Rgb(0.53, 0.53, 0.53)`.
        match = re.fullmatch("[0-9a-f]{2}", text)
        if match:
            v = int(match.group(0), 16)
            return rgb_from_int(v, v, v)
        # If the text is 1 hexadecimal character, then duplicate that character then do as the previous case.
        # So `8` => `Rgb('88', '88', '88')` => `Rgb(0.53, 0.53, 0.53)`.
        match = re.fullmatch("[0-9a-f]", text)
        if match:
            v = int(match.group(0) * 2, 16)
            return rgb_from_int(v, v, v)
        # If none of these cases are valid, blame the user.
        raise Exception(f"cannot parse {text} as RGB")

    def to_hsl(self) -> "Hsl":
        (hue, lightness, saturation) = colorsys.rgb_to_hls(self.red, self.green, self.blue)
        return Hsl(hue, saturation, lightness)

    def to_int(self) -> int:
        red = int(round(255 * self.red))
        green = int(round(255 * self.green))
        blue = int(round(255 * self.blue))
        return red << 16 | green << 8 | blue

    def __repr__(self) -> str:
        return f"Rgb({self.red}, {self.green}, {self.blue})"

class Hsl:
    """
    A color in the hue-saturation-lightness color model.
    Each component is in the range `[0.0, 1.0]`.

    HSL is a different model from RGB with a major benefit: it lets you interpolate (ie. mix) colors in a way that does not look terrible.
    (See https://chrisburnell.com/article/interpolating-colours for an example.)

    In stark void of theory space, it sort-of works like this.
    RGB is a model with three axes (red, green, blue) in the range [0.0, 1.0].
    In other words, it's a cube.

    Black (`Rgb(0.0, 0.0, 0.0)`) is one corner of the cube, and white (`Rgb(1.0, 1.0, 1.0)`) is the opposite corner.
    Now turn the cube on its side, so white is directly above black.
    All the other colors are somewhere around the vertical axis between those colors.

    Use an angle to indicate where your color is relative to the central axis.
    This is Hue.
    Normally hue is measured in angles, or if you're feeling daring, radians.
    As it happens Python has built-in RGB <=> HSL functions, however, and they say hue is between 0.0 and 1.0.
    Still, since it is an angle, it wraps.
    -0.1, 0.0, and 0.1 are all equidistant from one another, in other words.

    Radial coordinates don't go well with top-down views of cubes, but they do go well with circles.
    Imagine the top-view of the cube is actually a circle with radius `1.0`.
    (And massage the numbers a bit so it makes mathematical sense.)
    Saturation is how far you go from the central axis along the hue angle to reach your desired color.

    So far we looked at the cube-circle from a top-down perspective, but cubes are actually 3D, so we need a 3rd (height) coordinate.
    Slanted cubes do poorly with height, so let's imagine it is a cylinder instead.
    (And torture the numbers a bit so it makes mathematical sense.)
    Lightness is the 3rd coordinate that says where our color is situated between the plane of black (0.0) and white (1.0).
    """
    def __init__(self, hue: float, saturation: float, lightness: float):
        self.hue = hue
        self.saturation = saturation
        self.lightness = lightness

    def random() -> Self:
        return Hsl(random.random(), random.random(), random.random())

    def to_rgb(self) -> Rgb:
        (red, green, blue) = colorsys.hls_to_rgb(self.hue, self.lightness, self.saturation)
        return Rgb(red, green, blue)

    def to_hsl(self) -> Self:
        return self

    def interpolate(a: Self, b: Self, t: float) -> Self:
        def interpolate_line(a: float, b: float, t: float) -> float:
            # Linear interpolation, or `lerp`, as it is sometimes known.
            #
            # Given two values and a coefficient `t` in the range [0.0, 1.0], linear interpolation finds the value `t`% between the two.
            # `interpolate_line(a, b, 0.5)` is the mean, `interpolate_line(a, b, 0.25)` and `interpolate_line(a, b, 0.75)` are quarts, etc.
            return t * a + (1.0 - t) * b

        def interpolate_angle(a: float, b: float, t: float) -> float:
            # Hue is an angle, and angles operate on circular algebra, not linear algebra.
            # If you go along the edge of a circle, you can get from one point to another in two ways: clockwise or counterclockwise.
            # This is relevant if you have hues of, say, 0.0 (red) and 0.66 (blue).
            # You could pass clockwise through 0.1 => 0.2 => ... => 0.6 => 0.66, but that would be a literal roundabout way of going about.
            # (Color-wise that would be something like red => orange => yellow => chartreuse => green => aqua => blue.)
            # Instead, consider you could wrap around from 0.0, which is also 1.0, to 0.9 => 0.8 => 0.7 and reach your destination in a shorter distance and with a more fitting color palette.
            # (In this case, red => purple => violet => blue.)
            delta = abs(a - b)
            min_delta = min(delta, 2 - delta)
            # Since we are on a circle, all operations are modulo 1.0: `(0.2 - 0.5 = 0.8)`.
            return (a + t * min_delta) % 1.0

        return Hsl(
            interpolate_angle(a.hue, b.hue, t),
            interpolate_line(a.saturation, b.saturation, t),
            interpolate_line(a.lightness, b.lightness, t),
        )

    def __repr__(self) -> str:
        return f"Hsl({self.hue}, {self.saturation}, {self.lightness})"

class Palette:
    def __init__(self, start_color: Hsl, end_color: Hsl, transmission: Transmission):
        self.start_color = start_color
        self.end_color = end_color
        self.transmission = transmission

    def paint(self, t: float) -> int:
        return Hsl.interpolate(self.start_color, self.end_color, self.transmission.transmit(t)).to_rgb().to_int()

def paint_maze(maze: Maze, palette: Palette):
    # Get the maximum value so we can use it to interpolate.
    # The -1 compensates for the +1 of the measuring algorithm.
    max_value = max(cell.value() for cell in maze.cells()) - 1

    for cell in tqdm(maze.cells(), desc="paint pixels", total=maze.shape().x * maze.shape().y):
        # The -1 compensates for the +1 of the measuring algorithm.
        value = cell.value() - 1
        color = palette.paint(value / max_value)
        cell.set_value(UInt28(color))
