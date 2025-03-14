#!/usr/bin/env python3
"""
This module defines the GurobiSolver class, which extends CLRPSolver to solve the Capacitated Location Routing Problem (CLRP) using Gurobi.

Classes:
    GurobiSolver: A solver for the CLRP utilizing the Gurobi optimization engine.
"""

import math
from itertools import combinations
from typing import List, Union

import gurobipy as gp
from gurobipy import GRB, Var, LinExpr

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
        self._instance = instance
        model = gp.Model(f"CLRP_{instance.name}")

        # Sets, be very careful with the indexes when using variables in J
        I = range(len(instance.depots))  # Depots
        J = range(len(instance.customers))  # Customers
        V = range(len([instance.depots + instance.customers]))  # Nodes
        # some max number of Vehicles
        K = range(math.ceil(len(instance.customers)/2))

        # Parameters
        F: List[float] = [instance.route_setup_cost for _ in instance.depots]
        Q: float = instance.vehicle_capacity
        W: List[float] = [depot.capacity for depot in instance.depots]
        O: List[float] = [depot.cost for depot in instance.depots]

        # Decision Variables
        x: List[List[List[Var]]] = []
        for i in V:
            x.append([])
            for j in V:
                x[i].append([])
                for k in K:
                    x[i][j].append(model.addVar(
                        vtype=GRB.BINARY, name=f"x_i{i}_j{j}_k{k}"))

        y: List[Var] = []
        for i in I:
            y.append(model.addVar(vtype=GRB.BINARY, name=f"y_i{i}"))

        f: List[List[Var]] = []
        for i in I:
            f.append([])
            for j in V:
                f[i].append(model.addVar(
                    vtype=GRB.BINARY, name=f"f_i{i}_j{j}"))

        # Objective Function
        opening_cost: LinExpr = gp.quicksum(O[i]*y[i] for i in I)
        travel_cost: LinExpr = gp.quicksum(
            x[i][j][k] * self._c(i, j) for k in K for j in V for i in I)
        route_setup_cost: LinExpr = gp.quicksum(
            x[i][j + len(I)][k] * F[i] for j in J for i in I for k in K)
        model.setObjective(opening_cost + travel_cost +
                           route_setup_cost, GRB.MINIMIZE)

        # Constraints
        # Each customer must be assigned to exactly one depot
        for j in J:
            model.addConstr(gp.quicksum(x[i][j][k]
                            for i in I for k in K) <= Q, name=f"c2_j{j}")

        # Vehicle capacity constraint
        for k in K:
            model.addConstr(gp.quicksum(x[i][j + len(I)][k] * instance.customers[j].demand
                            for i in I for j in J) == 1, name=f"c3_k{k}")

        # Customer assignment depends on depot opening
        for i in I:
            model.addConstr(gp.quicksum(f[i][j + len(I)] * instance.customers[j].demand for j in J) <= W[i] * y[i],
                            name=f"c4_i{i}_j{j}")

        # Flow conservation constraint
        for i in V:
            for k in K:
                model.addConstr(gp.quicksum(x[i][j][k] for j in V) == gp.quicksum(x[j][i][k] for j in V),
                                name=f"c5_i{i}_k{k}"
                                )

        for k in K:
            model.addConstr(gp.quicksum(x[i][j + len(I)][k]
                            for j in J for i in I) <= 1, name=f"c6_k{k}")

        # Subtour elimination
        for k in K:
            for r in range(1, len(J) + 1):
                for S in combinations(J, r):
                    S = list(S)
                    if len(S) >= 2:
                        S_in_V = [i + len(I) for i in S]
                        model.addConstr(
                            gp.quicksum(
                                x[i][j][k] for i in S_in_V for j in S_in_V if i != j) <= len(S) - 1, name=f"subtour_elim_k{k}_S{tuple(S)}")

        # only include customer into same routes if customers are assigned to the same depot
        for k in K:
            for j in J:
                customer_index = j + len(I)
                V_noj = [v for v in V if v != customer_index]
                for i in I:
                    model.addConstr(
                        gp.quicksum(x[i][u + len(I)][k] for u in J) +
                        gp.quicksum(x[u if u < customer_index else u - 1]
                                    [customer_index][k] for u in V_noj)
                        <= (1 + f[i][customer_index]),
                        name=f"c8_i{i}_j{j}_k{k}"
                    )

        # Solve the model
        model.optimize()

        # Extract the solution
        solution = Solution(instance)
        if model.status == GRB.OPTIMAL:
            solution.depots_opened = [i for i in I if y[i].x > 0.5]
            solution.customer_assignment = {
                (i, j): f[i, j].x for i in I for j in J}
            solution.routes = {
                (i, j, k): x[i, j, k].x for i in I for j in J for k in K}

        return solution

    def _c(self, node1: int, node2: int) -> float:
        return self._instance.get_c(node1, node2)
