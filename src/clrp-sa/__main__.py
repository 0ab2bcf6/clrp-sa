#!/usr/bin/env python3
"""
This is the main entry point for your module, if it is called as a scripts,
e.g.:
python -m your_module
This file contains the primary main() function for your entire project.
"""
# from argparse import ArgumentParser, Namespace
# from . import add
import random
from typing import List, Tuple

from collections import Counter

from customer import Customer
from depot import Depot
from greedysolver import GreedySolver
from heuristicsolver import HeuristicSolver
from instance import Instance
from logger import Logger
from node import Node, NodeType
from saparameters import SimulatedAnnealingParameters
from solution import Solution
from lsoperator import *

# TODO write instance parser for instances

def test_instance(logger: Logger, depot_capacity: int = 140, vehicle_capacity: int = 70, route_setup_cost: int = 1000) -> Instance:

    customers: List[Customer] = [
        Customer("C1", 20, 35, 17),
        Customer("C2", 8, 31, 18),
        Customer("C3", 29, 43, 13),
        Customer("C4", 18, 39, 19),
        Customer("C5", 19, 47, 12),
        Customer("C6", 31, 24, 18),
        Customer("C7", 38, 50, 13),
        Customer("C8", 33, 21, 13),
        Customer("C9", 2, 27, 17),
        Customer("C10", 1, 12, 20),
        Customer("C11", 26, 20, 16),
        Customer("C12", 20, 33, 18),
        Customer("C13", 15, 46, 15),
        Customer("C14", 20, 26, 11),
        Customer("C15", 17, 19, 18),
        Customer("C16", 15, 12, 16),
        Customer("C17", 5, 30, 15),
        Customer("C18", 13, 40, 15),
        Customer("C19", 38, 5, 15),
        Customer("C20", 9, 40, 16)
    ]

    depots: List[Depot] = [
        Depot("D1", 6, 7, 10841, depot_capacity),
        Depot("D2", 19, 44, 11961, depot_capacity),
        Depot("D3", 37, 23, 6091, depot_capacity),
        Depot("D4", 35, 6, 7570, depot_capacity),
        Depot("D5", 5, 8, 7497, depot_capacity)
    ]

    instance: Instance = Instance(
        depots, customers, vehicle_capacity, route_setup_cost, logger)
    return instance


def sa_parameters(a: float = 0.90, Iiter: int = 1000, P: int = 800, K: float = 1/4, T0: float = 100, TF: float = 0.1,
                  Nnon_improving=100) -> SimulatedAnnealingParameters:
    sa_params = SimulatedAnnealingParameters(
        a, Iiter, P, K, T0, TF, Nnon_improving)
    return sa_params


if __name__ == "__main__":

        logger: Logger = Logger("CLRP Testinstance", True)
        instance: Instance = test_instance(logger)
        sa_params: SimulatedAnnealingParameters = sa_parameters()

        greedy_solver: GreedySolver = GreedySolver(logger)
        heuristic_solver: HeuristicSolver = HeuristicSolver(sa_params, logger)

        initial_solution: Solution = greedy_solver.solve(instance)
        best_solution: Solution = heuristic_solver.solve(initial_solution)

        logger.print_logs_to_file(f"{logger.name}.txt")
