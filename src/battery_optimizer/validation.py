import pandas as pd

from .config import BatteryConfig


def validate_dispatch(
    dispatch: pd.DataFrame,
    config: BatteryConfig,
) -> dict:

    violations = []

    if dispatch["soc_mwh"].min() < config.min_soc_mwh - 1e-6:
        violations.append("Minimum SOC violated.")

    if dispatch["soc_mwh"].max() > config.max_soc_mwh + 1e-6:
        violations.append("Maximum SOC violated.")

    if dispatch["charge_mwh"].max() > config.max_charge_mw + 1e-6:
        violations.append("Maximum charge power violated.")

    if dispatch["discharge_mwh"].max() > config.max_discharge_mw + 1e-6:
        violations.append(
            "Maximum discharge power violated."
        )

    simultaneous = (
        (dispatch["charge_mwh"] > 1e-6)
        & (dispatch["discharge_mwh"] > 1e-6)
    )

    if simultaneous.any():
        violations.append(
            "Simultaneous charge/discharge detected."
        )

    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "min_soc_mwh": dispatch["soc_mwh"].min(),
        "max_soc_mwh": dispatch["soc_mwh"].max(),
        "max_charge_mw": dispatch["charge_mwh"].max(),
        "max_discharge_mw": dispatch["discharge_mwh"].max(),
    }