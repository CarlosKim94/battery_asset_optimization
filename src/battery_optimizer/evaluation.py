import pandas as pd
from battery_optimizer.config import BatteryConfig

def calculate_profit(
    dispatch: pd.DataFrame,
    prices: pd.Series,
    degradation_cost: float,
) -> float:

    revenue = (
        dispatch["discharge_mwh"]
        * prices
    ).sum()

    charging_cost = (
        dispatch["charge_mwh"]
        * prices
    ).sum()

    degradation = (
        dispatch["discharge_mwh"]
        * degradation_cost
    ).sum()

    return revenue - charging_cost - degradation


def compare_forecast_realized(
    dispatch: pd.DataFrame,
    realized_prices: pd.Series,
    degradation_cost: float,
) -> float:

    return calculate_profit(
        dispatch=dispatch,
        prices=realized_prices,
        degradation_cost=degradation_cost,
    )

def rule_based_dispatch(
    price_data: pd.DataFrame,
    config: BatteryConfig,
    charge_threshold: float = 40.0,
    discharge_threshold: float = 90.0,
) -> pd.DataFrame:

    soc = config.initial_soc_mwh

    rows = []

    for _, row in price_data.iterrows():

        charge = 0.0
        discharge = 0.0

        if row["price_eur_mwh"] < charge_threshold:

            available_capacity = (
                config.max_soc_mwh - soc
            )

            charge = min(
                config.max_charge_mw,
                available_capacity
                / config.charge_efficiency,
            )

            soc += (
                charge
                * config.charge_efficiency
            )

        elif row["price_eur_mwh"] > discharge_threshold:

            available_energy = (
                soc - config.min_soc_mwh
            )

            discharge = min(
                config.max_discharge_mw,
                available_energy
                * config.discharge_efficiency,
            )

            soc -= (
                discharge
                / config.discharge_efficiency
            )

        rows.append({
            "timestamp": row["timestamp"],
            "price_eur_mwh": row["price_eur_mwh"],
            "charge_mwh": charge,
            "discharge_mwh": discharge,
            "soc_mwh": soc,
        })

    return pd.DataFrame(rows)