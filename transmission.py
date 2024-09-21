from math import pi, cos

class Transmission:
    """
    The code responsible for coloring is largely contained in the `Palette` class.
    It takes two colors as input and linearly interpolates between them based on a parameter `t` in the range [0.0, 1.0].

    Changing this code can be fairly involved, because color interpolation is fairly involved.
    A lot simpler is to mess with `t`, which is a lot easier.

    Enter `Transmission`s: classes with a single function `transmit` that takes a single `t` as an argument and returns a replacement `t` within the same range.
    Now you can interpolate non-linearly by interpolating linearly by messing with the arguments!
    """

    def id() -> str:
        """
        A unique ID for this transmission.
        """
        raise NotImplementedError()

    def transmit(self, t: float) -> float:
        raise NotImplementedError()

class Linear(Transmission):
    """
    A linear transmission.

    `f(x) = x`.
    """
    def __init__(self):
        super().__init__()

    def id() -> str:
        return "Linear"

    def transmit(self, t: float) -> float:
        return t

class Wave(Transmission):
    """
    A waveform scaled and translated so it passes through (0.0, 0.0) and (1.0, 1.0).
    """
    def __init__(self):
        super().__init__()

    def id() -> str:
        return "Wave"

    def transmit(self, t: float) -> float:
        return cos(pi * t + pi) / 2 + 0.5

class Quadratic(Transmission):
    """
    A quadratic transmission.

    `f(x) = x ** 2`.

    Compared to the linear transmission, quadratic transmission makes images that go from one color in the palette to the other much quicker, with fewer in betweens.
    """
    def __init__(self):
        super().__init__()

    def id() -> str:
        return "Quadratic"

    def transmit(self, t: float) -> float:
        return t ** 2

class Pow10(Transmission):
    """
    A deca-quadratic? transmission.

    `f(x) = x ** 10`.

    Like the quadratic transmission on steroids.
    `Pow10` is less "two colors sharing equal space" and more "a sea of the starting color with highlights of the secondary color."
    """
    def __init__(self):
        super().__init__()

    def id() -> str:
        return "Pow10"

    def transmit(self, t: float) -> float:
        return t ** 10

class InversePow10(Transmission):
    """
    Like `Pow10`, but with the colors reversed.
    """
    def __init__(self):
        super().__init__()

    def id() -> str:
        return "InversePow10"

    def transmit(self, t: float) -> float:
        return 1.0 - t ** 10

class Round(Transmission):
    """
    Just the primary and secondary colors.
    """
    def __init__(self):
        super().__init__()

    def id() -> str:
        return "Round"

    def transmit(self, t: float) -> float:
        return round(t)

class Piecewise10(Transmission):
    """
    A linearly interpolated palette composed of 10 equidistant colors.
    """
    def __init__(self):
        super().__init__()

    def id() -> str:
        return "Piecewise10"

    def transmit(self, t: float) -> float:
        return round(t, 1)

# This list has all the transmissions so the command-line parser knows about them.
# If you write a new transmission, make sure to add it here!
TRANSMISSIONS = [Linear, Wave, Quadratic, Pow10, InversePow10, Round, Piecewise10]
