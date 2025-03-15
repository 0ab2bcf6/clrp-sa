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
from hrstcsolution import HRSTCSolution
from instance import Instance
from logger import Logger

if __name__ == "__main__":

    instances: List[Instance] = DataLoader().get_instances()
    # filter for specific instances here
    selected_instance: Instance = instances[0] # just use the first instance

    # include logger in solver classes as needed
    logger: Logger = Logger(selected_instance.name + "- Greedy", True)
    greedy_solver: GreedySolver = GreedySolver("Greedy", logger)
    initial_solution: HRSTCSolution = greedy_solver.solve(selected_instance)
    logger.print_logs_to_file()

    logger = Logger(selected_instance.name + "- SimAn", True)
    clrpsa_solver: CLRPSASolver = CLRPSASolver("SimAn", logger, initial_solution)
    best_solution: HRSTCSolution = clrpsa_solver.solve()
    logger.print_logs_to_file()
    
    logger = Logger(selected_instance.name + "- Gurobi", True)
    gurobi_solver: GurobiSolver = GurobiSolver("Gurobi", logger)
    gurobi_solution: GRBSolution = gurobi_solver.solve(selected_instance)
    logger.print_logs_to_file()

