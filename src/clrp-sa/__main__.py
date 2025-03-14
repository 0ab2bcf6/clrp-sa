#!/usr/bin/env python3
"""
This is the main entry point for your module, if it is called as a scripts,
e.g.:
python -m your_module
This file contains the primary main() function for your entire project.
"""

from typing import List


from clrpsasolver import CLRPSASolver
from dataloader import DataLoader
from greedysolver import GreedySolver
from instance import Instance
from logger import Logger
from solution import Solution

if __name__ == "__main__":

    instances: List[Instance] = DataLoader().get_instances()

    # filter for specific instances here
    selected_instance: Instance = instances[0]
    # include logger in solver classes as needed
    logger: Logger = Logger(selected_instance.name, True)

    greedy_solver: GreedySolver = GreedySolver(logger)
    initial_solution: Solution = greedy_solver.solve(selected_instance)
    clrpsa_solver: CLRPSASolver = CLRPSASolver(logger, initial_solution)
    best_solution: Solution = clrpsa_solver.solve()

    logger.print_logs_to_file()
