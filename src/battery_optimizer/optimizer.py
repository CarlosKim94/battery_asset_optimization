import pandas as pd
import pyomo.environ as pyo

from .config import BatteryConfig
from .model import build_battery_model


def optimize_battery(
    price_data: pd.DataFrame,
    config: BatteryConfig,
) -> tuple[pd.DataFrame, float]:

    prices = price_data["price_eur_mwh"].tolist()

    model = build_battery_model(
        prices=prices,
        config=config,
    )

    solver = pyo.SolverFactory("appsi_highs")

    result = solver.solve(
        model,
        tee=False,
    )

    status = result.solver.status
    termination = result.solver.termination_condition

    if termination != pyo.TerminationCondition.optimal:
        raise RuntimeError(
            f"Optimization failed: "
            f"{status}, {termination}"
        )

    rows = []

    for t in model.T:
        rows.append(
            {
                "timestamp": price_data.loc[t, "timestamp"],
                "price_eur_mwh": prices[t],
                "charge_mwh": pyo.value(model.charge[t]),
                "discharge_mwh": pyo.value(
                    model.discharge[t]
                ),
                "soc_mwh": pyo.value(model.soc[t]),
            }
        )

    dispatch = pd.DataFrame(rows)

    profit = pyo.value(model.objective)

    return dispatch, profit