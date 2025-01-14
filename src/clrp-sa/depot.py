#!/usr/bin/env python3

from node import Node, NodeType


class Depot(Node):
    """Represents a Depot in the CLRP"""

    type: NodeType = NodeType.DPT

    def __init__(self, name: str, x: int, y: int, cost: int, capacity: int = 10000000000) -> None:
        super().__init__(name, x, y)
        self.cost: int = cost
        self.capacity: int = capacity
        self.open: bool = False
