# Capacitated Location-Routing Problem (CLRP) Solver

This repository provides a framework for solving the Capacitated Location-Routing Problem (CLRP) using different interfaces and solver methods. It includes instance data, a data loader, and implemented solvers such as a simple greedy algorithm, a solver using the gurobi optimizer and a simulated annealing (SA) approach.

# TODOs
- as for now, the code is largely untested.
- fix cost function in `solution.py`: there's a bug in the cost function that causes travel cost from depot to first customer in secondary routes to not be calculated 
- implement `gurobisolver.py`: as for now, the code is untested
- meaningful and consistent integration of `Logger` in solver classes

## Features
- **DataLoader**: Loads problem instances from predefined files.
- **Greedy Solver**: Provides an initial feasible solution.
- **Simulated Annealing (CLRP-SA) Solver**: Optimizes the initial solution using simulated annealing.
- **Extensible Solver Framework**: Custom solvers can be implemented by extending the `CLRPsolver` abstract base class.
- **Logging**: Each solver class should include a logger for tracking steps or results.

## Installation
Ensure you have Python installed and the required dependencies. Install dependencies using:

```sh
pip install -r requirements.txt
```

## Usage
Run the main script to solve a CLRP instance:

```sh
python __main__.py
```

### Example Workflow in `__main__.py`
```python
from typing import List


from clrpsasolver import CLRPSASolver
from dataloader import DataLoader
from grbsolution import GRBSolution
from greedysolver import GreedySolver
from gurobisolver import GurobiSolver
from hrstcsolution import HRSTCSolution
from instance import Instance
from logger import Logger

if __name__ == "__main__":

    instances: List[Instance] = DataLoader().get_instances()
    # filter for specific instances here
    selected_instance: Instance = instances[0] # just use the first instance

    # include logger in solver classes as needed
    # use the Greedy Solver
    logger: Logger = Logger(selected_instance.name + "- Greedy", True)
    greedy_solver: GreedySolver = GreedySolver("Greedy", logger)
    initial_solution: HRSTCSolution = greedy_solver.solve(selected_instance)
    logger.print_logs_to_file()

    # use the Simulated Annealing Solver
    logger = Logger(selected_instance.name + "- SimAn", True)
    clrpsa_solver: CLRPSASolver = CLRPSASolver("SimAn", logger, initial_solution)
    best_solution: HRSTCSolution = clrpsa_solver.solve()
    logger.print_logs_to_file()
    
    # use the Gurobi Solver
    logger = Logger(selected_instance.name + "- Gurobi", True)
    gurobi_solver: GurobiSolver = GurobiSolver("Gurobi", logger)
    gurobi_solution: GRBSolution = gurobi_solver.solve(selected_instance)
    logger.print_logs_to_file()
```

## Implementing a Custom Solver
To add a new solver, create a class that implements the `CLRPsolver` abstract base class and the `Solution` abstract base class. Ensure that:
1. The solver follows the interface defined in `CLRPsolver`.
2. The solution following the interface defined in `Solution`
3. Logging is implemented as needed.

### Example Custom Solver
```python
from clrpsolver import CLRPsolver
from hrstcsolution import HRSTCSolution # or implement own solution class
from logger import Logger

class MyHeuristicSolver(CLRPsolver[HRSTCSolution]):
    def __init__(self, name: str, logger: Logger) -> None:
        super().__init__(name, logger)

    def solve(self, instance: Instance) -> HRSTCSolution:
        solution: HRSTCSolution = HRSTCSolution(instance)
        self.logger.info(f"Starting {self.name} solver")
        start_time = time()

        # Implement solver logic here

        runtime = time() - start_time
        self.logger.info(f"Solver completed in {runtime:.2f} seconds")
        return solution
```

## Logging
Each solver should integrate logging to track progress. Use the `Logger` class to store and export logs.

## License
This project is licensed under the 0BSD license License.

## Contact
For issues or contributions, feel free to open an issue or submit a pull request!

