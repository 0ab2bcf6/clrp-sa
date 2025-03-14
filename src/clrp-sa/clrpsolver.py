#!/usr/bin/env python3

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from instance import Instance
from logger import Logger
from solution import Solution

# Define a TypeVar constrained to Solution
TSolution = TypeVar('TSolution', bound=Solution)


class CLRPSolver(Generic[TSolution], ABC):
    """abstract base class for CLRP Solver"""

    def __init__(self, name: str, logger: Logger) -> None:
        """init function of superclass"""
        self.logger: Logger = logger
        self.name: str = name

    @abstractmethod
    def solve(self) -> TSolution:
        """Abstract method to solve the CLRP and return a Solution subclass."""
        pass
