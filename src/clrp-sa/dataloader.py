#!/usr/bin/env python3

from typing import Dict, List, Optional, Tuple
from pathlib import Path

from customer import Customer
from depot import Depot
from instance import Instance

# Absolute Path of current file
# pylint: disable=invalid-name
SCRIPT_DIR = Path(__file__).resolve().parent


class DataLoader:
    """A class to load and manage LRP instances from a directory structure."""

    def __init__(self) -> None:
        """
        Initialize the DataLoader by parsing all instance files in the given directory.
        """
        # self.data_dir = Path(data_dir)  # Convert to Path object
        self.data_dir: Path = Path(SCRIPT_DIR, "instances")
        # Maps dataset name to list of instances
        self.instances: Dict[str, List[Instance]] = {}
        self.instances_by_name: Dict[str, Instance] = {}
        # Check if directory exists
        if not self.data_dir.is_dir():
            raise ValueError(f"Directory '{self.data_dir}' does not exist.")

        # Parse all instances on initialization
        self._load_instances()

    def _load_instances(self) -> None:
        """Scan the data directory and load all instances into the dictionary."""
        # Iterate over subdirectories (e.g., prodhon, tuzun)
        for dataset_path in self.data_dir.iterdir():
            if not dataset_path.is_dir():
                continue

            dataset_name = dataset_path.name  # e.g., 'prodhon'
            self.instances[dataset_name] = []

            # Iterate over files in the dataset folder
            for file_path in dataset_path.glob("*.dat"):
                instance = self._parse_instance_file(file_path)
                if instance:
                    self.instances[dataset_name].append(instance)

    def _parse_instance_file(self, file_path: Path) -> Optional[Instance]:
        """
        Parse a single instance file and return an Instance object.
        Args:
            file_path (Path): Path to the instance file.
        Returns:
            Instance: Parsed instance, or None if parsing fails.
        """
        try:
            with file_path.open('r') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]  # Remove empty lines

                # Parse number of customers and depots
                n_customers = int(lines[0])
                n_depots = int(lines[1])

                # Parse depot coordinates
                depot_start = 2
                depot_coords: List[Tuple[float, float]] = []
                for i in range(depot_start, depot_start + n_depots):
                    x, y = map(float, lines[i].split())
                    depot_coords.append((float(x), float(y)))

                # Parse customer coordinates
                customer_start = depot_start + n_depots
                customer_coords:  List[Tuple[float, float]] = []
                for i in range(customer_start, customer_start + n_customers):
                    x, y = map(float, lines[i].split())
                    customer_coords.append((float(x), float(y)))

                # Parse vehicle capacity
                vehicle_capacity_idx = customer_start + n_customers
                vehicle_capacity = float(lines[vehicle_capacity_idx])

                # Parse route setup costs
                depot_capacity_idx = vehicle_capacity_idx + 1
                depot_capacities = []
                for i in range(depot_capacity_idx, depot_capacity_idx + n_depots):
                    depot_capacities.append(float(lines[i]))

                # Parse customer demands
                demand_start = depot_capacity_idx + n_depots
                customer_demands = []
                for i in range(demand_start, demand_start + n_customers):
                    customer_demands.append(float(lines[i]))

                # Parse depot opening costs
                opening_cost_start = demand_start + n_customers
                depot_opening_costs = []
                for i in range(opening_cost_start, opening_cost_start + n_depots):
                    depot_opening_costs.append(float(lines[i]))

                # Parse vehicle value and terminator
                route_setup_cost_idx = opening_cost_start + n_depots
                route_setup_cost = float(lines[route_setup_cost_idx])
                terminator_idx = route_setup_cost_idx + 1
                terminator = int(lines[terminator_idx]
                                 ) if terminator_idx < len(lines) else 0

                depots: List[Depot] = []
                for i in range(0, n_depots):
                    depots.append(Depot(
                        f"D{i+1}", depot_coords[i][0], depot_coords[i][1], depot_opening_costs[i], depot_capacities[i], route_setup_cost))

                customers: List[Customer] = []
                for i in range(0, n_customers):
                    customers.append(
                        Customer(f"C{i+1}", customer_coords[i][0], customer_coords[i][1], customer_demands[i]))

                name: Path = Path(
                    *file_path.parts[file_path.parts.index("instances") + 1:]).with_suffix("")
                instance: Instance = Instance(
                    str(name.as_posix()), depots, customers, vehicle_capacity, route_setup_cost)
                self.instances_by_name[str(name.as_posix())] = instance
                return instance

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    def get_instances(self, dataset_name: Optional[str] = None) -> List[Instance]:
        """
        Retrieve a list of instances, optionally filtered by dataset name.
        Args:
            dataset_name (str, optional): Name of the dataset (e.g., 'prodhon').
                                         If None, return all instances.
        Returns:
            List[Instance]: List of instances.
        """
        if dataset_name:
            return self.instances.get(dataset_name, [])
        else:
            return [instance for instances in self.instances.values() for instance in instances]

    # def get_instances_by_max_size(self, max_size: Optional[int] = None) -> List[Instance]:
    #     """
    #     Retrieve a list of instances, optionally filtered by instance size.
    #     Args:
    #         max_size (int, optional): Maximum Number of Nodes per Instance.
    #                                      If None, return all instances.
    #     Returns:
    #         List[Instance]: List of instances.
    #     """
    #     if max_size:
    #         # TODO logic here to filter for instance size
    #         return [instance for instances in self.instances.values() for instance in instances]
    #     else:
    #         return [instance for instances in self.instances.values() for instance in instances]

    def get_dataset_names(self) -> List[str]:
        """Return a list of available dataset names."""
        return list(self.instances.keys())
    
    def get_dataset_by_name(self, dataset_name:str) -> Optional[Instance]:
        """Returns an instance matching the instance dataset_name"""
        return self.instances_by_name.get(dataset_name, None)

    def __len__(self) -> int:
        """Return the total number of instances."""
        return sum(len(instances) for instances in self.instances.values())


# Example usage
if __name__ == "__main__":

    loader = DataLoader()

    # Get all instances
    all_instances = loader.get_instances()
    print(f"Total instances: {len(loader)}")

    # Get instances from a specific dataset
    prodhon_instances = loader.get_instances(dataset_name="prodhon")
    print(f"Prodhon instances: {len(prodhon_instances)}")

    # Get instance by name
    name = "tuzun/coordP133222"
    instance_by_name = loader.get_dataset_by_name(name)
    print(f"Instance by name: {instance_by_name.name}")

    # List available datasets
    print(f"Available datasets: {loader.get_dataset_names()}")
