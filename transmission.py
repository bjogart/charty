from math import pi, cos

class Transmission:
    def id() -> str:
        raise NotImplementedError()

    def transmit(self, t: float) -> float:
        raise NotImplementedError()

class Linear(Transmission):
    def __init__(self):
        super().__init__()

    def id() -> str:
        return "Linear"

    def transmit(self, t: float) -> float:
        return t

class Wave(Transmission):
    def __init__(self):
        super().__init__()

    def id() -> str:
        return "Wave"

    def transmit(self, t: float) -> float:
        return cos(pi * t + pi) / 2 + 0.5

class Quadratic(Transmission):
    def __init__(self):
        super().__init__()

    def id() -> str:
        return "Quadratic"

    def transmit(self, t: float) -> float:
        return t ** 2

class Pow10(Transmission):
    def __init__(self):
        super().__init__()

    def id() -> str:
        return "Pow10"

    def transmit(self, t: float) -> float:
        return t ** 10

class Round(Transmission):
    def __init__(self):
        super().__init__()

    def id() -> str:
        return "Round"

    def transmit(self, t: float) -> float:
        return round(t)

# This list has all the transmissions so the command-line parser knows about them.
# If you write a new transmission, make sure to add it here!
TRANSMISSIONS = [Linear, Wave, Quadratic, Pow10, Round]
