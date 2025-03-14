#!/usr/bin/env python3
"""
This module defines the Instance class, which represents an instance of the Capacitated Location Routing Problem (CLRP).

Classes:
    Instance: A class to model an instance for the CLRP.
"""

import math
from typing import Dict, List, Optional, Tuple, Union

from customer import Customer
from depot import Depot
from node import Node


class Instance:
    """Represents an instance for a CLRP Problem."""


    def __init__(self, name: str, depots: List[Depot], customers: List[Customer], vehicle_capacity: float, route_setup_cost: float) -> None:
        self.name: str = name
        self.depots: List[Depot] = depots
        self.customers: List[Customer] = customers
        self.nodes: List[Union[Depot, Customer]] = depots + customers
        self.size: int = len(self.depots) + len(self.customers)
        self.vehicle_capacity: float = vehicle_capacity
        self.route_setup_cost: float = route_setup_cost
        self.distance_matrix: Dict[Tuple[Node, Node],
                                   float] = self._create_distance_matrix()

    def _euclidean_distance(self, node1: Node, node2: Node) -> float:
        return math.sqrt((node1.x - node2.x) ** 2 + (node1.y - node2.y) ** 2)

    def _create_distance_matrix(self) -> Dict[Tuple[Node, Node], float]:
        """Creates a distance matrix for all nodes."""
        nodes: List[Union[Depot, Customer]] = self.depots + self.customers
        distance_matrix: Dict[Tuple[Node, Node], float] = {}

        for i, node1 in enumerate(nodes):
            for j, node2 in enumerate(nodes):
                if i != j:
                    distance_matrix[(node1, node2)] = math.ceil(self._euclidean_distance(
                        node1, node2))

        return distance_matrix

    def get_distance(self, node1: Node, node2: Node) -> float:
        """Fetches the distance between two nodes from the distance matrix."""
        return self.distance_matrix.get((node1, node2), float('inf'))

    def print_distance_matrix(self) -> None:
        """Prints distance matrix to console"""
        print("Distance Matrix:")
        for (node1, node2), distance in self.distance_matrix.items():
            print(f"From {node1.name} to {node2.name}: {distance}")
    
    def get_c(self, idx1: int, idx2: int) -> float:
        """this method is only ment to be used in GurobiSolver"""
        return self.get_distance(self.nodes[idx1], self.nodes[idx2])