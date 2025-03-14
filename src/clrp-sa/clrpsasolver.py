#!/usr/bin/env python3

from typing import List, Tuple

import copy
import math
import random
import time

from clrpsolver import CLRPSolver
from logger import Logger
from lsoperator import LocalSearchOperator, InsertOperator, SwapOperator, TwoOptOperator
from saparameters import SimulatedAnnealingParameters
from hrstcsolution import HRSTCSolution


class CLRPSASolver(CLRPSolver[HRSTCSolution]):

    def __init__(self, name: str, logger: Logger, solution: HRSTCSolution) -> None:
        super().__init__(name, logger)

        self.sa_parameters: SimulatedAnnealingParameters = SimulatedAnnealingParameters(
            a=0.98,
            Iiter=5000,
            P=400,
            K=1/9,
            T0=30,
            TF=0.1,
            Nnon_improving=100
        )
        self.operators: List[LocalSearchOperator] = [
            InsertOperator(logger),
            SwapOperator(logger),
            TwoOptOperator(logger)
        ]
        self.local_search: List[LocalSearchOperator] = [
            SwapOperator(logger),
            InsertOperator(logger)
        ]
        self.inital_solution: HRSTCSolution = copy.deepcopy(solution)

    def solve(self) -> HRSTCSolution:
        """Returns the given Solution"""

        A: float = self.sa_parameters.a
        P: int = self.sa_parameters.P
        K: float = self.sa_parameters.K
        T0: float = self.sa_parameters.T0
        TF: float = self.sa_parameters.TF
        N: int = self.sa_parameters.Nnon_improving
        I: int = self.sa_parameters.Iiter * \
            len(self.inital_solution.instance.nodes)

        i_count: int = 0
        n_count: int = 0
        current_temp: float = T0
        best_solution: HRSTCSolution = self.inital_solution
        current_solution: HRSTCSolution = self.inital_solution

        start_time = time.time()
        while current_temp > TF:
            i_count += 1

            (curr_sol_cost, curr_sol_feasible) = current_solution.get_quality()
            if not curr_sol_feasible:
                curr_sol_cost += P

            random_op: int = random.randint(0, len(self.operators) - 1)
            (new_solution, new_sol_feasible) = self.operators[random_op].apply(
                current_solution)
            (new_sol_cost, new_sol_feasible) = new_solution.get_quality()
            if not new_sol_feasible:
                new_sol_cost += P

            delta: float = new_sol_cost - curr_sol_cost
            if delta <= 0:
                current_solution = new_solution
                (curr_sol_cost, curr_sol_feasible) = (
                    new_sol_cost, new_sol_feasible)
            else:
                random_r: float = random.random()
                exp_value: float = math.exp(-delta / (K * current_temp))
                if random_r < exp_value:
                    current_solution = new_solution
                    (curr_sol_cost, curr_sol_feasible) = (
                        new_sol_cost, new_sol_feasible)

            (best_sol_cost, _) = best_solution.get_quality()
            if curr_sol_cost < best_sol_cost and curr_sol_feasible:
                best_solution = current_solution
                n_count = 0

            if i_count == I:
                # update variables
                i_count = 0
                n_count += 1
                current_temp = A * current_temp

                # perform local search
                (best_sol_cost, _) = best_solution.get_quality()
                (current_solution, is_feasible) = self.local_search[0].apply(
                    best_solution)
                (curr_sol_cost, _) = current_solution.get_quality()

                if is_feasible:
                    (current_solution, is_feasible) = self.local_search[1].apply(
                        current_solution)
                    (curr_sol_cost, _) = current_solution.get_quality()

                    if is_feasible:
                        if curr_sol_cost < best_sol_cost:
                            best_solution = current_solution
                else:
                    (current_solution, is_feasible) = self.local_search[1].apply(
                        best_solution)
                    (curr_sol_cost, _) = current_solution.get_quality()

                    if is_feasible:
                        if curr_sol_cost < best_sol_cost:
                            best_solution = current_solution

            if current_temp <= TF or n_count >= N:
                return best_solution

        end_time = time.time() - start_time
        best_solution.set_time(end_time)
        return best_solution
