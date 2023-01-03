"""
Model Generator for OpenSees ~ uid generator
"""

#
#   _|_|      _|_|_|  _|      _|    _|_|_|
# _|    _|  _|        _|_|  _|_|  _|
# _|    _|    _|_|    _|  _|  _|  _|  _|_|
# _|    _|        _|  _|      _|  _|    _|
#   _|_|    _|_|_|    _|      _|    _|_|_|
#
#
# https://github.com/ioannis-vm/OpenSees_Model_Generator

from dataclasses import dataclass
from itertools import count


@dataclass
class UIDGenerator:
    """
    Generates unique identifiers (uids) for various objects.
    """

    def new(self, thing: str):
        """
        Generates a new uid for an object of the given type.

        Args:
            object_type (str): The type of object for which to generate a uid.

        Returns:
            int: A unique identifier for an object of the given type.

        Example:
            >>> from osmg.gen.uid_gen import UIDGenerator
            >>> generator = UIDGenerator()
            >>> generator.new('node')
            0
            >>> generator.new('node')
            1
            >>> generator.new('element')
            0
            >>> generator.new('element')
            1
        """
        if hasattr(self, thing):
            res = next(getattr(self, thing))
        else:
            setattr(self, thing, count(0))
            res = next(getattr(self, thing))
        return res
