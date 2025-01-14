#!/usr/bin/env python3

from node import NodeType, Node


class DummyZero(Node):
    """Represents a DummyZero in the Solution"""
    type: NodeType = NodeType.DZR

    def __init__(self, name, x, y):
        super().__init__(name, x, y)
