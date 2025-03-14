#!/usr/bin/env python3

from node import Node, NodeType


class Depot(Node):
    """Represents a Depot in the CLRP"""

    type: NodeType = NodeType.DPT

    def __init__(self, name: str, x: float, y: float, cost: float, capacity: float, route_setup: float) -> None:
        super().__init__(name, x, y)
        self.cost: float = cost
        self.capacity: float = capacity
        self.route_setup: float = route_setup
        self.open: bool = False
