"""
Model Generator for OpenSees ~ node
"""

#                          __
#   ____  ____ ___  ____ _/ /
#  / __ \/ __ `__ \/ __ `/ /
# / /_/ / / / / / / /_/ /_/
# \____/_/ /_/ /_/\__, (_)
#                /____/
#
# https://github.com/ioannis-vm/OpenSees_Model_Generator

from dataclasses import dataclass, field
from functools import total_ordering


@dataclass
@total_ordering
class Node:
    """
    OpenSees node
    https://openseespydoc.readthedocs.io/en/latest/src/node.html?highlight=node
    Attributes:
        uid (int)
        coords (list[float])
        mass (list[float])
        load (list[float])
        restraint (list[bool])
    """
    uid: int
    coords: list[float]
    restraint: list[bool] = field(init=False)

    def __post_init__(self):
        self.restraint = [False]*6
        self.mass = [0.00]*6

    def __le__(self, other):
        return self.uid < other.uid