from pathlib import Path

from battery_optimizer.config import BatteryConfig
from battery_optimizer.data import load_prices
from battery_optimizer.evaluation import calculate_profit
from battery_optimizer.optimizer import optimize_battery
from battery_optimizer.validation import validate_dispatch
from battery_optimizer.visualization import plot_dispatch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"

def main():

    config = BatteryConfig()

    forecast = load_prices(
        DATA_DIR/"prices_forecast.csv"
    )

    realized = load_prices(
        DATA_DIR/"prices_realized.csv"
    )

    # Optimize against forecast prices

    dispatch, expected_profit = optimize_battery(
        forecast,
        config,
    )

    # Validate optimization result

    validation = validate_dispatch(
        dispatch,
        config,
    )

    print("\nOptimization result")
    print("===================")

    print(
        f"Expected profit: "
        f"€{expected_profit:,.2f}"
    )

    print(
        f"Valid solution: "
        f"{validation['valid']}"
    )

    print(
        f"Minimum SOC: "
        f"{validation['min_soc_mwh']:.2f} MWh"
    )

    print(
        f"Maximum SOC: "
        f"{validation['max_soc_mwh']:.2f} MWh"
    )

    # Evaluate using realized prices

    realized_profit = calculate_profit(
        dispatch,
        realized["price_eur_mwh"],
        config.degradation_cost_eur_mwh,
    )

    forecast_error_cost = (
        expected_profit - realized_profit
    )

    print(
        f"Realized profit: "
        f"€{realized_profit:,.2f}"
    )

    print(
        f"Forecast error impact: "
        f"€{forecast_error_cost:,.2f}"
    )

    # Save results

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    dispatch.to_csv(
        RESULTS_DIR / "dispatch.csv",
        index=False,
    )

    plot_dispatch(
        dispatch,
        RESULTS_DIR / "dispatch_plot.png",
    )

if __name__ == "__main__":
    main()