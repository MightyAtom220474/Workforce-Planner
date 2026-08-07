from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

#import pyworkforce
#from pyworkforce.queuing import ErlangC

def calculate_erlang(
    transactions: float,
    aht: float,
    asa: float,
    interval: int,
    service_level_target: float = 0.8,
    shrinkage: float = 0.0,
    ):
    """
    Calculate staffing requirements using Erlang C.

    Parameters
    ----------
    transactions : float
        Number of transactions/calls in the interval.
    aht : float
        Average Handle Time (seconds).
    asa : float
        Target Answer Speed (seconds).
    interval : int
        Interval length (seconds).
    service_level_target : float
        Service level target (e.g. 0.8 = 80%).
    shrinkage : float
        Shrinkage as a decimal (e.g. 0.3 = 30%).

    Returns
    -------
    dict
    """

    erlang = ErlangC(
        transactions=transactions,
        aht=aht,
        asa=asa,
        interval=interval,
        shrinkage=shrinkage,
    )

    result = erlang.required_positions(
        service_level=service_level_target
    )

    # Convert to dictionary if required
    if isinstance(result, dict):
        return result

    if hasattr(result, "to_dict"):
        return result.to_dict()

    if hasattr(result, "__dict__"):
        return dict(result.__dict__)

    return {"result": str(result)}

def summarise_result(result: dict) -> dict:
    """
    Extract key metrics from an Erlang calculation result.
    """

    return {
        "positions": result.get("positions"),
        "positions_with_shrinkage": result.get("positions_with_shrinkage"),
        "service_level": result.get("service_level"),
        "occupancy": result.get("occupancy"),
        "waiting_probability": result.get("waiting_probability"),
        "offered_load": result.get("offered_load"),
    }
    
