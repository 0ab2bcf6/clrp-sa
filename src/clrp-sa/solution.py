#!/usr/bin/env python3

from typing import Tuple
from abc import ABC

from instance import Instance


class Solution(ABC):
    """abstract base class for CLRP Solver"""

    def __init__(self, instance: Instance) -> None:
        """init function of superclass"""
        self.instance = instance
        self._feasible: bool = True
        self._cost: float = 0.0
        self._time: float = 0.0

    def get_quality(self) -> Tuple[float, bool]:
        """Returns Cost and Feasibility of Solution as Tuple"""
        return (self._cost, self._feasible)
    
    def set_time(self, duration: float) -> None:
        self._time = duration
