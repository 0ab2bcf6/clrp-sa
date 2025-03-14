#!/usr/bin/env python3
"""
This module defines the GurobiSolver class, which extends CLRPSolver to solve the Capacitated Location Routing Problem (CLRP) using Gurobi.

Classes:
    GurobiSolver: A solver for the CLRP utilizing the Gurobi optimization engine.
"""

import math
from itertools import combinations
import time
from typing import List

import gurobipy as gp
from gurobipy import GRB, Var, LinExpr

from clrpsolver import CLRPSolver
from customer import Customer
from depot import Depot
from grbsolution import GRBSolution
from instance import Instance
from logger import Logger


class GurobiSolver(CLRPSolver[GRBSolution]):
    """A solver for the CLRP utilizing the Gurobi optimization engine."""

    def __init__(self, logger: Logger) -> None:
        super().__init__(logger)

    def solve(self, instance: Instance, time_limit: int = 600) -> GRBSolution:
        """Solves the given Instance using the Gurobi Optimizer"""
        self._instance = instance
        model = gp.Model(f"CLRP_{instance.name}")
        model.setParam('TimeLimit', time_limit)

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
        # x[i][j][k] = 1, if arc from node i to node j is traversed by vehicle k, =0 otherwise

        y: List[Var] = []
        for i in I:
            y.append(model.addVar(vtype=GRB.BINARY, name=f"y_i{i}"))
        # y[i] =1 if depot i gets opened, =0 otherwise

        f: List[List[Var]] = []
        for i in I:
            f.append([])
            for j in V:
                f[i].append(model.addVar(
                    vtype=GRB.BINARY, name=f"f_i{i}_j{j}"))
        # f[i][j] = 1, if customer(node) j is assigned to depot(node) i, =0 otherwise

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
        J_in_V = range(len(I), len(V))
        for k in K:
            for r in range(1, len(J_in_V) + 1):  # r is the size of the subset
                for S in combinations(J_in_V, r):
                    S_l: List[int] = list(S)
                    if len(S_l) >= 2:
                        model.addConstr(gp.quicksum(x[i][j][k] for i in S_l for j in S_l if i != j) <= len(
                            S_l) - 1, name=f"c7_k{k}_S{tuple(S_l)}")

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
        start_time = time.time()
        model.optimize()
        end_time = time.time() - start_time
        solution = GRBSolution(instance)

        # Check the optimization status
        if model.status == gp.GRB.OPTIMAL:
            print("Optimal solution found!")
            obj_value = model.ObjVal
            solution.set_solution(True, obj_value)
        elif model.SolCount > 0:
            # Handle cases where a feasible solution was found but the time limit elapsed
            print("Time limit reached. Best feasible solution used.")
            obj_value = model.ObjVal
            solution.set_solution(False, obj_value)
        else:
            # Handle cases where no feasible solution was found
            print("No feasible solution found within the time limit.")
            solution.set_solution(False, -1.0)

        solution.set_time(end_time)
        return solution

    def _c(self, node1: int, node2: int) -> float:
        return self._instance.get_c(node1, node2)
