
from __future__ import annotations
import math
import pandas as pd


from dataclasses import dataclass
from typing import Any, Dict

#import pyworkforce
#from pyworkforce.queuing import ErlangC

import math

def calculate_erlang(
    transactions: float,
    aht: float,
    asa: float,
    interval: int,
    shrinkage: float = 0.0,
    service_level_target: float = 0.80,
    max_staff_limit: int = 500
):
    """
    Calculate minimum staffing requirement using Erlang C.

    Returns similar information to pyworkforce ErlangC.
    """

    offered_load = (transactions * aht) / interval

    required_staff = None
    achieved_service_level = None

    for staff in range(1, max_staff_limit + 1):

        service_level = erlang_service_level(
            transactions=transactions,
            aht=aht,
            asa=asa,
            interval=interval,
            staff=staff
        )

        if service_level >= service_level_target:
            required_staff = staff
            achieved_service_level = service_level
            break

    if required_staff is None:
        raise ValueError(
            f"No staffing level found up to {max_staff_limit} staff."
        )

    occupancy = offered_load / required_staff

    probability_waiting = (
        erlang_c_probability_of_waiting(
            offered_load,
            required_staff
        )
    )

    positions_with_shrinkage = math.ceil(
        required_staff / (1 - shrinkage)
    ) if shrinkage < 1 else None

    return {
        "transactions": transactions,
        "aht": aht,
        "asa": asa,
        "interval": interval,
        "offered_load": offered_load,
        "positions": required_staff,
        "positions_with_shrinkage": positions_with_shrinkage,
        "service_level": achieved_service_level,
        "occupancy": occupancy,
        "waiting_probability": probability_waiting,
        "shrinkage": shrinkage
    }

# def calculate_erlang(
#     transactions: float,
#     aht: float,
#     asa: float,
#     interval: int,
#     service_level_target: float = 0.8,
#     shrinkage: float = 0.0,
#     ):
#     """
#     Calculate staffing requirements using Erlang C.

#     Parameters
#     ----------
#     transactions : float
#         Number of transactions/calls in the interval.
#     aht : float
#         Average Handle Time (seconds).
#     asa : float
#         Target Answer Speed (seconds).
#     interval : int
#         Interval length (seconds).
#     service_level_target : float
#         Service level target (e.g. 0.8 = 80%).
#     shrinkage : float
#         Shrinkage as a decimal (e.g. 0.3 = 30%).

#     Returns
#     -------
#     dict
#     """

#     erlang = ErlangC(
#         transactions=transactions,
#         aht=aht,
#         asa=asa,
#         interval=interval,
#         shrinkage=shrinkage,
#     )

#     result = erlang.required_positions(
#         service_level=service_level_target
#     )

#     # Convert to dictionary if required
#     if isinstance(result, dict):
#         return result

#     if hasattr(result, "to_dict"):
#         return result.to_dict()

#     if hasattr(result, "__dict__"):
#         return dict(result.__dict__)

#     return {"result": str(result)}

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

def erlang_c_probability_of_waiting(traffic_intensity: float, staff: int) -> float:
    if staff <= traffic_intensity:
        return 1.0

    sum_terms = sum(
        (traffic_intensity ** n) / math.factorial(n)
        for n in range(staff)
    )

    last_term = (traffic_intensity ** staff) / (
        math.factorial(staff) * (1 - (traffic_intensity / staff))
    )

    denominator = sum_terms + last_term
    return last_term / denominator


def erlang_service_level(
    transactions: float,
    aht: float,
    asa: float,
    interval: int,
    staff: int,
) -> float:
    offered_load = (transactions * aht) / interval

    if staff <= offered_load:
        return 0.0

    p_wait = erlang_c_probability_of_waiting(offered_load, staff)

    service_level = 1 - (
        p_wait * math.exp(-((staff - offered_load) * asa / aht))
    )

    return max(0.0, min(1.0, service_level))


def calculate_staffing_curve(
    transactions: float,
    aht: float,
    asa: float,
    interval: int,
    shrinkage: float = 0.0,
    max_staff_limit: int = 500,
    flattening_threshold: float = 0.0001,
):
    rows = []
    staff = 1
    previous_service_level = None

    while staff <= max_staff_limit:
        service_level = erlang_service_level(
            transactions=transactions,
            aht=aht,
            asa=asa,
            interval=interval,
            staff=staff,
        )
        
        adjusted_staff = staff / (1 - shrinkage) if shrinkage < 1 else None

        offered_load = (transactions * aht) / interval

        p_wait = erlang_c_probability_of_waiting(
            offered_load,
            staff
        )

        occupancy_pct = (
            offered_load / staff
        ) * 100

        rows.append(
            {
                "staff": staff,
                "service_level": service_level,
                "service_level_pct": service_level * 100,
                "probability_waiting": p_wait * 100,
                "occupancy_pct": occupancy_pct,
                "offered_load": offered_load,
                "adjusted_staff_for_shrinkage": adjusted_staff,
            }
        )

        # Stop if service level is effectively 100%
        if service_level >= 0.999:
            break

        # Stop if the curve has flattened out
        if previous_service_level is not None and previous_service_level > 0:
            improvement = service_level - previous_service_level
            if improvement < flattening_threshold and staff > 1 :
                break

        previous_service_level = service_level
        staff += 1

    df = pd.DataFrame(rows)

    df["marginal_gain"] = (
        df["service_level_pct"]
        .diff()
        .fillna(0)
    )

    return df