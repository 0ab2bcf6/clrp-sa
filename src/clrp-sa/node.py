#!/usr/bin/env python3

from abc import ABC
from enum import Enum


class NodeType(Enum):
    BSC = "Basic"
    DPT = "Depot"
    CSTMR = "Customer"
    DZR = "DummyZero"


class Node(ABC):
    """Represents a Node in the CLRP"""

    type: NodeType = NodeType.BSC

    def __init__(self, name: str, x: int, y: int) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y
