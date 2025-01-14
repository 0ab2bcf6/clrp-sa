
from typing import List, Tuple

import math
import random

from logger import Logger
from node import Node
from lsoperator import LocalSearchOperator, InsertOperator, SwapOperator, TwoOptOperator
from saparameters import SimulatedAnnealingParameters
from solution import Solution


class HeuristicSolver:

    def __init__(self, sa_parameters: SimulatedAnnealingParameters, logger: Logger) -> None:

        self.logger: Logger = logger
        self.sa_parameters: SimulatedAnnealingParameters = sa_parameters
        self.operators: List[LocalSearchOperator] = [
            InsertOperator(logger),
            SwapOperator(logger),
            TwoOptOperator(logger)
        ]
        self.local_search: List[LocalSearchOperator] = [
            SwapOperator(logger),
            InsertOperator(logger)
        ]
        self._edge_case_reached = False
        self._max_delta: float = 0.0

    def solve(self, solution: Solution) -> Solution:
        """Returns the given Solution"""

        A: float = self.sa_parameters.a
        P: int = self.sa_parameters.P
        K: float = self.sa_parameters.K
        T0: float = self.sa_parameters.T0
        TF: float = self.sa_parameters.TF
        N: int = self.sa_parameters.Nnon_improving
        I: int = self.sa_parameters.Iiter * len(solution.get_solution())

        i_count: int = 0
        n_count: int = 0
        current_temp: float = T0
        best_solution: Solution = solution
        current_solution: Solution = solution

        accepted_worse: Tuple[bool, int] = (False, 0)
        affected_nodes: Tuple[Node, Node] = ()

        self.logger.log("----- SA-Parameters and Variables -----")
        self.logger.log(f"--- alpha: {A}")
        self.logger.log(f"--- Temp_start: {T0}")
        self.logger.log(f"--- Temp_final: {TF}")
        self.logger.log(f"--- K: {K}")
        self.logger.log(f"--- N_non_improving: {N}")
        self.logger.log(f"--- I_iter: {I}")
        self.logger.log(f"--- Penalty: {P}")
        self.logger.log("---------------------------------------")
        self.logger.increase_indent()
        self.logger.log("--------- Start SA Algorithm ---------")

        while current_temp > TF:
            i_count += 1

            
            self.logger.log(f"┬─---------- Step {i_count} -----------")

            (curr_sol_cost, curr_sol_feasible) = current_solution.get_quality()
            if not curr_sol_feasible:
                curr_sol_cost += P
            self.logger.log(
                f"├─--- current solution: {(curr_sol_cost, curr_sol_feasible)}")
            self.logger.log(
                f"├─--- {[node.name for node in current_solution.get_solution()]}")

            random_op: int = random.randint(0, len(self.operators) - 1)
            (new_solution, new_sol_feasible) = self.operators[random_op].apply(
                current_solution)
            (new_sol_cost, new_sol_feasible) = new_solution.get_quality()
            if not new_sol_feasible:
                new_sol_cost += P

            self.logger.log(
                f"├─--- new solution: {(new_sol_cost, new_sol_feasible)}")
            self.logger.log(
                f"├─--- {[node.name for node in new_solution.get_solution()]}")

            delta: float = new_sol_cost - curr_sol_cost
            if delta <= 0:
                self.logger.log(f"├─-- better solution accepted: {delta}")
                current_solution = new_solution
                (curr_sol_cost, curr_sol_feasible) = (
                    new_sol_cost, new_sol_feasible)
            else:
                random_r: float = random.random()
                exp_value: float = math.exp(-delta / (K * current_temp))
                if random_r < exp_value:
                    self.logger.log(
                        f"├─-- worse solution accepted: r= {random_r}, exp_val= {exp_value}")
                    current_solution = new_solution
                    (curr_sol_cost, curr_sol_feasible) = (
                        new_sol_cost, new_sol_feasible)
                    accepted_worse = (True, i_count)

            (best_sol_cost, best_sol_feasible) = best_solution.get_quality()
            self.logger.log(
                f"├─--- best solution: {(best_sol_cost, best_sol_feasible)}")
            self.logger.log(
                f"├─--- {[node.name for node in best_solution.get_solution()]}")
            if curr_sol_cost < best_sol_cost and curr_sol_feasible:
                self.logger.log("└─-- new best solution found")
                if accepted_worse[0] and i_count - accepted_worse[1] <= 2:
                    self._edge_case_reached = True
                    self._max_delta = min(self._max_delta, delta)
                    accepted_worse = (False, -1)
                    self.logger.log("EDGE CASE REACHED")
                best_solution = current_solution
                n_count = 0
            else:
                self.logger.log("└─-- no improvement reached")

            if i_count == I:
                # update variables
                i_count = 0
                n_count += 1
                current_temp = A * current_temp

                self.logger.log(f"┬─----- I_iter reached {I} ------")
                self.logger.log(
                    f"├─-- n_count = {n_count}")
                self.logger.log(
                    f"├─-- current temp: {current_temp} = {A} * {current_temp/A}")

                if True:
                    # perform local search
                    (best_sol_cost, best_sol_feasible) = best_solution.get_quality()

                    self.logger.log(
                        f"├─--- best solution: {(best_sol_cost, best_sol_feasible)}")
                    self.logger.log(
                        f"├─--- {[node.name for node in best_solution.get_solution()]}")
                    self.logger.log("├─---- local search ----")

                    (current_solution, is_feasible) = self.local_search[0].apply(
                        best_solution)
                    (curr_sol_cost, _) = current_solution.get_quality()

                    if is_feasible:
                        self.logger.log(
                            f"├─--- new local search solution: {(curr_sol_cost, is_feasible)}")
                        self.logger.log(
                            f"├─--- {[node.name for node in current_solution.get_solution()]}")
                        (current_solution, is_feasible) = self.local_search[1].apply(
                            current_solution)
                        (curr_sol_cost, _) = current_solution.get_quality()

                        if is_feasible:
                            self.logger.log(
                                f"├─--- new local search solution: {(curr_sol_cost, is_feasible)}")
                            self.logger.log(
                                f"├─--- {[node.name for node in current_solution.get_solution()]}")
                            if curr_sol_cost < best_sol_cost:
                                best_solution = current_solution
                                self.logger.log("└─-- new best solution found")
                            else:
                                self.logger.log("└─-- no improvement reached")
                    else:
                        (current_solution, is_feasible) = self.local_search[1].apply(
                            best_solution)
                        (curr_sol_cost, _) = current_solution.get_quality()

                        if is_feasible:
                            self.logger.log(
                                f"├─--- new local search solution: {(curr_sol_cost, is_feasible)}")
                            self.logger.log(
                                f"├─--- {[node.name for node in current_solution.get_solution()]}")
                            if curr_sol_cost < best_sol_cost:
                                best_solution = current_solution
                                self.logger.log("└─-- new best solution found by local search")
                            else:
                                self.logger.log("└─-- no improvement reached")

            if current_temp <= TF or n_count >= N:
                self.logger.log("---------- End SA Algorithm ----------")
                self.logger.decrease_indent()
                return best_solution

        self.logger.decrease_indent()
        return best_solution
