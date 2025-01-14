#!/usr/bin/env python3

from dataclasses import dataclass


@dataclass
class SimulatedAnnealingParameters:
    a: float          # Cooling rate
    Iiter: int        # Iterations
    P: int            # Parameter P
    K: float          # Parameter K
    T0: float         # Initial temperature
    TF: float         # Final temperature
    Nnon_improving: int  # Number of non-improving iterations


if __name__ == "__main__":
    sa_params = SimulatedAnnealingParameters(
        a=0.98,
        Iiter=5000,
        P=400,
        K=1/9,
        T0=30,
        TF=0.1,
        Nnon_improving=100
    )

    print(sa_params)
