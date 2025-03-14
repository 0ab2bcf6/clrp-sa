#!/usr/bin/env python3


from typing import List, Tuple, Dict
from abc import ABC, abstractmethod

from instance import Instance
from logger import Logger
from solution import Solution


class CLRPSolver(ABC):
    """abstract base class for CLRP Solver"""

    def __init__(self, logger: Logger) -> None:
        """init function of superclass"""
        self.logger: Logger = logger

    @abstractmethod
    def solve(self) -> Solution:
        """returns a Solution of Instance using the class-specific solving method"""
        pass
