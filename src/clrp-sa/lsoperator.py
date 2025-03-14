#!/usr/bin/env python3

import random

from typing import Dict, List, Optional, Tuple, Union
from enum import Enum
from abc import ABC, abstractmethod

from node import Node, NodeType
from customer import Customer
from depot import Depot
from dummyzero import DummyZero
from logger import Logger
from solution import Solution


class OperatorType(Enum):
    SWP = "SWAP"
    INSRT = "INSERT"
    TOPT = "2-OPT"


class LocalSearchOperator(ABC):

    type: OperatorType

    def __init__(self, logger: Logger) -> None:
        self.logger: Logger = logger
        self._affected_nodes: Tuple[Optional[Node], Optional[Node]] = (None, None)

    @abstractmethod
    def apply(self, solution: Solution) -> Tuple[Solution, bool]:
        """Applies the Operator-specific Operation to a given Input Solution"""
        pass

    def init_new_solution(self, solution: Solution) -> Solution:
        """initalizes new solution object"""
        new_solution: Solution = Solution(solution.instance)
        new_solution.dummy_zeros = []
        new_solution._sequence = solution.get_solution()[:]
        return new_solution

    def get_old_solution(self, solution: Solution) -> Tuple[Solution, bool]:
        (_, old_solution_feasible) = solution.get_quality()
        return (solution, old_solution_feasible)

    def set_affected_nodes(self, node1: Optional[Node], node2: Optional[Node]) -> None:
        self._affected_nodes = (node1, node2)


class TwoOptOperator(LocalSearchOperator):

    type: OperatorType = OperatorType.TOPT

    def __init__(self, logger: Logger) -> None:
        super().__init__(logger)

    def apply(self, solution: Solution) -> Tuple[Solution, bool]:
        """Applies the 2-Opt Operation to a given Input Solution"""
        super().set_affected_nodes(None, None)

        new_solution: Solution = super().init_new_solution(solution)
        candidate_depots: List[Tuple[Depot, int]] = []
        customers_of_depot: Dict[Depot, List[Tuple[Customer, int]]] = {}
        sequence = new_solution.get_solution()

        for i in range(len(sequence)):
            node: Union[Customer, Depot, DummyZero, Node] = sequence[i]
            if node.type == NodeType.DPT:
                customers_of_depot[node] = []
                count_customer = 0

                for j in range(i + 1, len(sequence)):
                    following_node: Node = sequence[j]
                    if following_node.type == NodeType.DPT or j == len(sequence) - 1:
                        if count_customer >= 2:
                            candidate_depots.append((node, i))
                        break
                    elif following_node.type == NodeType.CSTMR:
                        customers_of_depot[node].append((following_node, j))
                        count_customer += 1

        if not candidate_depots:
            return super().get_old_solution(solution)

        selected_depot, _ = candidate_depots[random.randint(
            0, len(candidate_depots) - 1)]
        customers = customers_of_depot[selected_depot]

        if len(customers) < 2:
            return super().get_old_solution(solution)

        selected_customers = sorted(
            random.sample(customers, 2), key=lambda x: x[1])
        start_idx, end_idx = selected_customers[0][1], selected_customers[1][1]
        super().set_affected_nodes(
            selected_customers[0][0], selected_customers[1][0])
        sequence[start_idx +
                 1:end_idx] = reversed(sequence[start_idx + 1:end_idx])

        new_solution.set_solution(sequence)
        (_, new_sol_feasible) = new_solution.get_quality()

        if new_solution.is_valid_solution():
            return (new_solution, new_sol_feasible)

        return super().get_old_solution(solution)


class InsertOperator(LocalSearchOperator):

    type: OperatorType = OperatorType.INSRT

    def __init__(self, logger: Logger) -> None:
        super().__init__(logger)

    def apply(self, solution: Solution) -> Tuple[Solution, bool]:
        """Applies the Insert Operation to a given Input Solution"""
        super().set_affected_nodes(None, None)

        new_solution: Solution = super().init_new_solution(solution)
        insert_candidates: List[Tuple[Node, int]] = []
        sequence: List[Node] = new_solution.get_solution()

        for i, candidate in enumerate(sequence):
            if candidate.type != NodeType.DZR:
                insert_candidates.append((candidate, i))

        if len(insert_candidates) < 2:
            return super().get_old_solution(solution)

        candidate1, candidate2 = random.sample(insert_candidates, 2)
        node1, index1 = candidate1
        node2, index2 = candidate2

        super().set_affected_nodes(node1, node2)

        sequence.pop(index1)
        if index1 < index2:
            index2 -= 1

        sequence.insert(index2, node1)
        new_solution.set_solution(sequence)
        (_, new_sol_feasible) = new_solution.get_quality()

        if new_solution.is_valid_solution():
            return (new_solution, new_sol_feasible)

        return super().get_old_solution(solution)


class SwapOperator(LocalSearchOperator):

    type: OperatorType = OperatorType.SWP

    def __init__(self, logger: Logger) -> None:
        super().__init__(logger)

    def apply(self, solution: Solution) -> Tuple[Solution, bool]:
        """Applies the Swap Operation to a given Input Solution"""
        super().set_affected_nodes(None, None)

        new_solution: Solution = super().init_new_solution(solution)
        swap_candidates_cstmr: List[Tuple[Node, int]] = []
        swap_candidates_dpt: List[Tuple[Node, int]] = []
        sequence: List[Node] = new_solution.get_solution()

        for i, candidate in enumerate(sequence):
            if candidate.type == NodeType.CSTMR or candidate.type == NodeType.DZR:
                swap_candidates_cstmr.append((candidate, i))
            elif candidate.type == NodeType.DPT:
                swap_candidates_dpt.append((candidate, i))

        # not entirely sure if this is what the paper ment
        weighted_pool = (swap_candidates_dpt + swap_candidates_cstmr * 2)

        candidate1, candidate2 = random.sample(weighted_pool, 2)
        node1, index1 = candidate1
        node2, index2 = candidate2
        sequence[index1] = node2
        sequence[index2] = node1

        super().set_affected_nodes(node1, node2)

        new_solution.set_solution(sequence)
        (_, new_sol_feasible) = new_solution.get_quality()

        if new_solution.is_valid_solution():
            return (new_solution, new_sol_feasible)

        return super().get_old_solution(solution)
