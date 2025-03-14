#!/usr/bin/env python3


from typing import List

from clrpsolver import CLRPSolver
from logger import Logger
from solution import Solution


class GurboiSolver(CLRPSolver):

    def __init__(self, logger: Logger) -> None:
        super().__init__(logger)
    
    def solve(self) -> Solution:
        """Solves the given Instance using the Gurobi Optimizer"""
        pass
