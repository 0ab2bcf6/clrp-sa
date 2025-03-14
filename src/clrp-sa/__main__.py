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
from grbsolution import GRBSolution
from greedysolver import GreedySolver
from gurobisolver import GurobiSolver
from instance import Instance
from logger import Logger
from solution import Solution

if __name__ == "__main__":

    instances: List[Instance] = DataLoader().get_instances()

    # filter for specific instances here
    selected_instance: Instance = instances[0]
    # include logger in solver classes as needed
    logger: Logger = Logger(selected_instance.name, True)

    greedy_solver: GreedySolver = GreedySolver("Greedy", logger)
    initial_solution: Solution = greedy_solver.solve(selected_instance)
    clrpsa_solver: CLRPSASolver = CLRPSASolver("SimAn", logger, initial_solution)
    best_solution: Solution = clrpsa_solver.solve()
    gurobi_solver: GurobiSolver = GurobiSolver("Gurobi", logger)
    gurobi_solution: GRBSolution = gurobi_solver.solve(selected_instance)

    logger.print_logs_to_file()
