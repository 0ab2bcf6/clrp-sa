# Capacitated Location-Routing Problem (CLRP) Solver

This repository provides a framework for solving the Capacitated Location-Routing Problem (CLRP) using different solver methods. It includes instance data, a data loader, and implemented solvers such as a simple greedy algorithm and a simulated annealing (SA) approach.

# TODOs
- fix cost function in `solution.py`: there's a bug in the cost function that causes travel cost from depot to first customer in secondary routes to not be calculated 
- implement `gurobisolver.py`: as for now, the code is gpt generated and in parts just wrong and not functional
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
if __name__ == "__main__":
    instances: List[Instance] = DataLoader().get_instances()
    # Filter for specific instances if needed
    selected_instance: Instance = instances[0]

    # Initialize logger
    logger: Logger = Logger(selected_instance.name, True)

    # Solve using the greedy solver
    greedy_solver: GreedySolver = GreedySolver(logger)
    initial_solution: Solution = greedy_solver.solve(selected_instance)

    # Solve using CLRP-SA solver
    clrpsa_solver: CLRPSASolver = CLRPSASolver(logger, initial_solution)
    best_solution: Solution = clrpsa_solver.solve()

    # Save logs
    logger.print_logs_to_file()
```

## Implementing a Custom Solver
To add a new solver, create a class that implements the `CLRPsolver` abstract base class. Ensure that:
1. The solver follows the interface defined in `CLRPsolver`.
2. Logging is implemented as needed.

### Example Custom Solver
```python
from clrpsolver import CLRPsolver
from logger import Logger

class MySolver(CLRPsolver):
    def __init__(self, logger: Logger) -> None:
        super().__init__(logger)

    def solve(self, instance: Instance) -> Solution:
        self.logger.log("Solving instance: " + instance.name)
        # Implement solver logic here
        return Solution()
```

## Logging
Each solver should integrate logging to track progress. Use the `Logger` class to store and export logs.

## License
This project is licensed under the 0BSD license License.

## Contact
For issues or contributions, feel free to open an issue or submit a pull request!

