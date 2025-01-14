#!/usr/bin/env python3

from node import Node, NodeType


class Customer(Node):
    """Represents a Customer in the CLRP"""

    type: NodeType = NodeType.CSTMR

    def __init__(self, name: str, x: int, y: int, demand: int) -> None:
        super().__init__(name, x, y)
        self.demand: int = demand
