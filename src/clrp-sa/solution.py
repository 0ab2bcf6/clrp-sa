#!/usr/bin/env python3
"""
This module defines the Solution class, which represents a solution for the Capacitated Location Routing Problem (CLRP).

Classes:
    Solution: A class to model a solution for the CLRP.
"""

import math
from typing import List, Tuple

from customer import Customer
from depot import Depot
from dummyzero import DummyZero
from instance import Instance
from node import Node, NodeType


class Solution:
    """Represents a Solution for the CLRP"""

    def __init__(self, instance: Instance) -> None:
        self.instance: Instance = instance
        self._sequence: List[Node] = []
        self._is_valid: bool = True
        self._cost: float = 0.0
        self._feasible: bool = True
        self.dummy_zeros: List[Node] = []
        self._create_dummy_zeros()

    def get_solution(self) -> List[Node]:
        """Returns the Solution as List of Nodes"""
        return self._sequence

    def set_solution(self, sequence: List[Node]) -> None:
        """Sets the Solution Sequence to given input sequence"""
        self._sequence = sequence
        self._calculate_cost()

    def is_valid_solution(self) -> bool:
        """Returns true if solution sequence has no customer before the first depot"""
        seen_depot: bool = False
        for node in self._sequence:
            if node.type == NodeType.DPT:
                seen_depot = True
            elif node.type == NodeType.CSTMR and not seen_depot:
                self._is_valid = False
                return self._is_valid
        self._is_valid = True
        return self._is_valid

    def get_quality(self) -> Tuple[float, bool]:
        """Returns Cost and Feasibility of Solution as Tuple"""
        return (self._cost, self._feasible)

    def append_node(self, node: Node) -> None:
        """Append node to solution sequence"""
        self._sequence.append(node)

    def append_dummy_zero(self) -> None:
        """Append dummy zero to solution sequence"""
        if self.dummy_zeros:
            dummy_zero = self.dummy_zeros.pop(0)
            self._sequence.append(dummy_zero)

    def finish_initial_solution(self) -> None:
        """Insert unused dummy zeros between DPT and CSTMR, or append to the end."""
        while self.dummy_zeros:
            inserted = False
            dummy_zero = self.dummy_zeros.pop(0)

            for i in range(len(self._sequence) - 1):
                node1 = self._sequence[i]
                node2 = self._sequence[i + 1]

                if node1.type == NodeType.DPT and node2.type == NodeType.CSTMR:
                    self._sequence.insert(i + 1, dummy_zero)
                    inserted = True
                    break

            if not inserted:
                self._sequence.append(dummy_zero)

        self._calculate_cost()

    def _create_dummy_zeros(self) -> None:
        """Creates the correct number of dummy zeros for the instance"""
        aggregate_demands: int = 0
        for customer in self.instance.customers:
            aggregate_demands += customer.demand

        number_dummy_zeros: int = math.ceil(
            aggregate_demands / self.instance.vehicle_capacity)

        for i in range(number_dummy_zeros):
            self.dummy_zeros.append(DummyZero(f"Z{i}", 0, 0))

    def _get_distance(self, node1: Node, node2: Node) -> float:
        """Returns distance between node1 and node2"""
        if node1.type != NodeType.DZR and node2.type != NodeType.DZR:
            return self.instance.get_distance(node1, node2)

    def _calculate_cost(self) -> None:
        """Calculates the cost of the current solution sequence"""

        # TODO fix cost function

        if not self._is_valid:
            self._feasible = False
            self._cost = float('inf')
            return

        cost: float = 0.0
        self._feasible = True
        sequence: List[Node] = self._reduce_list()

        # identify cost relevant subsequences in the solution sequence
        idx: int = 0
        while idx < len(sequence):
            if sequence[idx].type == NodeType.DPT and sequence[idx+1].type == NodeType.CSTMR:
                start_index = idx
                idx += 1

                if idx <= len(sequence) - 1:
                    while idx < len(sequence) and sequence[idx].type != NodeType.DPT:
                        idx += 1

                    if idx < len(sequence) and sequence[idx].type == NodeType.DPT:
                        end_index = idx
                        (partial_cost, partial_feasibility) = self._calc_cost_cap_subsequence(
                            sequence, start_index, end_index)
                        cost += partial_cost
                        self._feasible = self._feasible and partial_feasibility
                    elif idx >= len(sequence):
                        end_index = len(sequence)
                        (partial_cost, partial_feasible) = self._calc_cost_cap_subsequence(
                            sequence, start_index, end_index)
                        cost += partial_cost
                        self._feasible = self._feasible and partial_feasible
            else:
                idx += 1

        self._cost = cost

    def _calc_cost_cap_subsequence(self, sequence: List[Node], depot_idx: int, last_idx: int) -> Tuple[float, bool]:
        """Calculates the partial cost and required capacity of the subsequence in the reduced sequence from one depot to its last customer"""

        partial_cost: float = 0.0
        depot_capacity: float = sequence[depot_idx].capacity
        vehicle_capacity: float = self.instance.vehicle_capacity

        last_customer_idx: int = last_idx
        if last_idx >= len(sequence):
            last_customer_idx: int = last_idx - 1

        while sequence[last_customer_idx].type != NodeType.CSTMR:
            last_customer_idx -= 1

        previous_node: Node = None
        depot: Node = sequence[depot_idx]
        partial_cost += depot.cost
        for i in range(depot_idx, last_customer_idx+1):
            current_node: Node = sequence[i]

            if current_node.type == NodeType.CSTMR:
                if previous_node.type == NodeType.DZR:
                    # setup new route
                    partial_cost += self.instance.route_setup_cost
                    partial_cost += self._get_distance(
                        depot, current_node)
                    vehicle_capacity -= current_node.demand
                    depot_capacity -= current_node.demand
                elif previous_node.type == NodeType.CSTMR:
                    if vehicle_capacity - current_node.demand < 0:
                        # close previous route
                        partial_cost += self._get_distance(
                            previous_node, depot)
                        # setup new route
                        partial_cost += self.instance.route_setup_cost
                        partial_cost += self._get_distance(
                            depot, current_node)
                        vehicle_capacity = self.instance.vehicle_capacity - current_node.demand
                        depot_capacity -= current_node.demand
                    else:
                        partial_cost += self._get_distance(
                            previous_node, current_node)
                        vehicle_capacity -= current_node.demand
                        depot_capacity -= current_node.demand
                elif previous_node.type == NodeType.DPT:
                    # setup new route
                    partial_cost += self.instance.route_setup_cost
                    partial_cost += self._get_distance(
                        depot, current_node)
                    vehicle_capacity -= current_node.demand
                    depot_capacity -= current_node.demand
            elif current_node.type == NodeType.DZR:
                # close previous route
                partial_cost += self._get_distance(
                    previous_node, depot)
                vehicle_capacity = self.instance.vehicle_capacity

            previous_node = sequence[i]

        partial_feasible: bool = (depot_capacity >= 0)
        return (partial_cost, partial_feasible)
    
    def _reduce_list(self) -> List[Node]:
        """Create a new list in which consecutive dummy zeros are reduced to a single dummy zero,
        and remove DZR nodes directly following DPT nodes."""
        if not self._sequence:
            return []

        reduced_list: List[Node] = []
        prev_dzr: bool = False

        for node in self._sequence:
            if node.type == NodeType.DZR:
                if not prev_dzr:
                    reduced_list.append(node)
                    prev_dzr = True
            else:
                reduced_list.append(node)
                prev_dzr = False

        # Remove Zero directly following a Depot
        i: int = 0
        while i < len(reduced_list) - 1:
            if reduced_list[i].type == NodeType.DPT and reduced_list[i + 1].type == NodeType.DZR:
                reduced_list.pop(i + 1)
            else:
                i += 1

        # Remove trailing nodes until the last node is CSTMR
        while reduced_list and reduced_list[-1].type != NodeType.CSTMR:
            reduced_list.pop()

        return reduced_list
