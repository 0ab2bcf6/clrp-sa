#!/usr/bin/env python3
"""
This module defines the GurobiSolver class, which extends CLRPSolver to solve the Capacitated Location Routing Problem (CLRP) using Gurobi.

Classes:
    GurobiSolver: A solver for the CLRP utilizing the Gurobi optimization engine.
"""

import gurobipy as gp
from gurobipy import GRB
from typing import List, Union

from customer import Customer
from depot import Depot
from instance import Instance
from logger import Logger
from solution import Solution
from clrpsolver import CLRPSolver


class GurobiSolver(CLRPSolver):
    """A solver for the CLRP utilizing the Gurobi optimization engine."""

    def __init__(self, logger: Logger) -> None:
        super().__init__(logger)

    def solve(self, instance: Instance) -> Solution:
        """Solves the given Instance using the Gurobi Optimizer"""
        model = gp.Model(instance.name)
        self._instance = instance

        # Sets
        I = range(len(instance.depots))  # Depots
        J = range(len(instance.customers))  # Customers
        K = range(len(instance.customers))  # Vehicles

        # Parameters
        Q = instance.vehicle_capacity
        W: List[float] = [depot.capacity for depot in instance.depots]
        O: List[float] = [depot.cost for depot in instance.depots]

        # Decision Variables
        y = model.addVars(I, vtype=GRB.BINARY, name="y")  # Depot open
        f = model.addVars(I, J, vtype=GRB.BINARY,
                          name="f")  # Customer assignment
        x = model.addVars(I, J, K, vtype=GRB.BINARY,
                          name="x")  # Vehicle routing

        # Objective Function
        # TODO travel_cost for integers i and j is not easy to handle
        model.setObjective(
            gp.quicksum(O[i] * y[i] for i in I) +
            gp.quicksum(c[i][j] * x[i, j, k] for i in I for j in J for k in K),
            GRB.MINIMIZE
        )

        # Constraints
        # Each customer must be assigned to exactly one depot
        for j in J:
            model.addConstr(gp.quicksum(f[i, j]
                            for i in I) == 1, name=f"AssignCustomer_{j}")

        # Vehicle capacity constraint
        for k in K:
            model.addConstr(gp.quicksum(
                W[j] * x[i, j, k] for i in I for j in J) <= Q, name=f"VehicleCapacity_{k}")

        # Customer assignment depends on depot opening
        for i in I:
            for j in J:
                model.addConstr(f[i, j] <= W[i] * y[i],
                                name=f"DepotAssignment_{i}_{j}")

        # Flow conservation constraint
        for i in I:
            for k in K:
                model.addConstr(
                    gp.quicksum(x[i, j, k] for j in J) ==
                    gp.quicksum(x[j, i, k] for j in J),
                    name=f"FlowConservation_{i}_{k}"
                )

        # Subtour elimination (MTZ constraints)
        u = model.addVars(J, vtype=GRB.CONTINUOUS, name="u")
        for j in J:
            for k in K:
                for s in range(1, len(J)):
                    model.addConstr(
                        u[j] - u[s] + len(J) * x[j, s, k] <= len(J) - 1,
                        name=f"SubtourElimination_{j}_{s}_{k}"
                    )

        # Solve the model
        model.optimize()

        # Extract the solution
        solution = Solution()
        if model.status == GRB.OPTIMAL:
            solution.depots_opened = [i for i in I if y[i].x > 0.5]
            solution.customer_assignment = {
                (i, j): f[i, j].x for i in I for j in J}
            solution.routes = {
                (i, j, k): x[i, j, k].x for i in I for j in J for k in K}

        return solution

    def _get_c(self, node1: int, node2: int) -> float:
        return self._instance.get_distance(node1, node2)
