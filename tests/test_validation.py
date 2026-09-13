import pandas as pd

from battery_optimizer.config import BatteryConfig
from battery_optimizer.validation import validate_dispatch


def test_valid_dispatch():

    config = BatteryConfig()

    dispatch = pd.DataFrame({
        "soc_mwh": [50, 60, 70, 50],
        "charge_mwh": [10, 10, 0, 0],
        "discharge_mwh": [0, 0, 18, 0],
    })

    result = validate_dispatch(
        dispatch,
        config,
    )

    assert result["valid"]

def test_soc_limit_violation():

    config = BatteryConfig()

    dispatch = pd.DataFrame({
        "soc_mwh": [50, 95],
        "charge_mwh": [0, 0],
        "discharge_mwh": [0, 0],
    })

    result = validate_dispatch(
        dispatch,
        config,
    )

    assert not result["valid"]