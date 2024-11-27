"""Defines :obj:`~osmg.model_objects.node.Node` objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import total_ordering
from typing import Self

from osmg.core.uid_object import UIDObject
from osmg.graphics.visibility import NodeVisibility


@total_ordering
@dataclass()
class Node(UIDObject):
    """
    OpenSees node.

    https://openseespydoc.readthedocs.io/en/latest/src/node.html?highlight=node

    Attributes:
    ----------
        uid_generator: Unique ID generator object.
        coordinates: List of node coordinates.
        uid: Unique ID of the node, assigned using the generator object.
        restraint: List of boolean values identifying whether the
          corresponding DOF is restrained.
    """

    coordinates: tuple[float, ...]
    visibility: NodeVisibility = field(default_factory=NodeVisibility)

    def __post_init__(self) -> None:
        """Post-initialization."""
        self.uid = self.uid_generator.new(self)

    def __le__(self, other: Self) -> bool:
        """
        Less or equal determination rule.

        Returns:
          The outcome of the less or equal operation.
        """
        return self.uid <= other.uid

    def __repr__(self) -> str:
        """
        Get string representation.

        Returns:
          The string representation of the object.
        """
        res = ''
        res += 'Node object\n'
        res += f'  uid: {self.uid}\n'
        res += f'  coordinates: {self.coordinates}\n'
        return res