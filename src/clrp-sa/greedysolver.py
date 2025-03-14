#!/usr/bin/env python3
"""
This module defines the GreedySolver class, which implements a greedy approach to solving the Capacitated Location Routing Problem (CLRP).

Classes:
    GreedySolver: A greedy algorithm-based solver for the CLRP.
"""

import time
from typing import Dict, List, Tuple, Optional

from clrpsolver import CLRPSolver
from customer import Customer
from depot import Depot
from instance import Instance
from logger import Logger
from node import Node
from hrstcsolution import HRSTCSolution


class GreedySolver(CLRPSolver[HRSTCSolution]):
    """Greedy Solver for a CLRP Instance."""

    def __init__(self, logger: Logger) -> None:
        super().__init__(logger)

    def solve(self, instance: Instance) -> HRSTCSolution:
        """Returns greedy Solution for the given Instance"""

        solution: HRSTCSolution = HRSTCSolution(instance)
        used_depots: List[Depot] = []
        assigned_customers: List[Customer] = []

        start_time = time.time()
        while len(assigned_customers) < len(instance.customers) and len(used_depots) < len(instance.depots):
            unused_depots: Dict[Depot, List[Tuple[Customer, float]]] = {
                depot: [] for depot in instance.depots if depot not in used_depots}
            unassigned_customers: List[Customer] = [
                customer for customer in instance.customers if customer not in assigned_customers
            ]

            for customer in unassigned_customers:
                closest_depot: Optional[Depot] = None
                min_distance: float = float('inf')

                for depot in unused_depots:
                    distance = instance.get_distance(customer, depot)
                    if distance < min_distance:
                        min_distance = distance
                        closest_depot = depot

                if closest_depot:
                    unused_depots[closest_depot].append((customer, min_distance))

            for depot in unused_depots:
                unused_depots[depot].sort(key=lambda x: x[1])

            selected_depot: Depot = max(unused_depots.keys(), key=lambda depot: (
                len(unused_depots[depot]), depot.capacity))

            solution.append_node(selected_depot)
            cap: float = selected_depot.capacity
            last_appended_node: Node = selected_depot
            current_route_cap: float = instance.vehicle_capacity
            is_cap_reached: bool = False
            while not is_cap_reached:
                min_distance: float = float('inf')
                selected_customer: Optional[Customer] = None
                for customer in unused_depots[selected_depot]:
                    customer_distance = instance.get_distance(
                        customer[0], last_appended_node)
                    if customer_distance < min_distance:
                        min_distance = customer_distance
                        selected_customer = customer[0]

                if not selected_customer:
                    used_depots.append(selected_depot)
                    is_cap_reached = True
                    break

                if selected_customer and cap - selected_customer.demand > 0:
                    if selected_customer and current_route_cap - selected_customer.demand < 0:
                        solution.append_dummy_zero()
                        current_route_cap = instance.vehicle_capacity
                        last_appended_node = selected_depot
                    else:
                        cap -= selected_customer.demand
                        current_route_cap -= selected_customer.demand
                        unused_depots[selected_depot] = [
                            c for c in unused_depots[selected_depot] if c[0] != selected_customer
                        ]
                        last_appended_node = selected_customer
                        solution.append_node(selected_customer)
                        assigned_customers.append(selected_customer)
                else:
                    used_depots.append(selected_depot)
                    is_cap_reached = True

        for depot in instance.depots:
            if depot not in solution.get_solution():
                solution.append_node(depot)

        solution.finish_initial_solution()
        end_time = time.time() - start_time
        solution.set_time(end_time)
        return solution
