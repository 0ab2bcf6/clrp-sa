#!/usr/bin/env python3
"""
This module defines the Solution class, which represents a solution for the Capacitated Location Routing Problem (CLRP) solved using the Gurobi Optimizer or similar software.

Classes:
    GRBSolution: A class to model a solution for the CLRP obtained using a solver.
"""

from typing import Optional

from instance import Instance
from solution import Solution


class GRBSolution(Solution):
    """Represents a Solution for the CLRP obtained using an optimizer"""

    def __init__(self, instance: Instance) -> None:
        super().__init__(instance)
        self._is_optimal: bool = False

    def set_solution(self, is_optimal: bool, cost: Optional[float]) -> None:
        """this method is ment to be accessed in the respective solver class"""
        if not cost or cost <= 0.0:
            self._feasible = False
            self._is_optimal = False
            self._cost = -1.0
            return

        self._is_optimal = is_optimal
        self._cost = cost
