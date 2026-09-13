from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from battery_optimizer.config import BatteryConfig
from battery_optimizer.data import load_prices
from battery_optimizer.optimizer import optimize_battery
from battery_optimizer.evaluation import calculate_profit
from battery_optimizer.validation import validate_dispatch


BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Battery Asset Optimization API",
    description=(
        "Battery dispatch optimization using Pyomo "
    ),
    version="1.0.0",
)


class OptimizationRequest(BaseModel):

    capacity_mwh: float = Field(
        default=100.0,
        gt=0,
    )

    initial_soc_mwh: float = Field(
        default=50.0,
        ge=0,
    )

    min_soc_mwh: float = Field(
        default=10.0,
        ge=0,
    )

    max_soc_mwh: float = Field(
        default=90.0,
        gt=0,
    )

    max_charge_mw: float = Field(
        default=25.0,
        gt=0,
    )

    max_discharge_mw: float = Field(
        default=25.0,
        gt=0,
    )

    charge_efficiency: float = Field(
        default=0.95,
        gt=0,
        le=1,
    )

    discharge_efficiency: float = Field(
        default=0.95,
        gt=0,
        le=1,
    )

    degradation_cost_eur_mwh: float = Field(
        default=5.0,
        ge=0,
    )


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/config")
def default_config():

    config = BatteryConfig()

    return {
        "capacity_mwh": config.capacity_mwh,
        "initial_soc_mwh": config.initial_soc_mwh,
        "min_soc_mwh": config.min_soc_mwh,
        "max_soc_mwh": config.max_soc_mwh,
        "max_charge_mw": config.max_charge_mw,
        "max_discharge_mw": config.max_discharge_mw,
        "charge_efficiency": config.charge_efficiency,
        "discharge_efficiency": config.discharge_efficiency,
        "degradation_cost_eur_mwh":
            config.degradation_cost_eur_mwh,
    }


@app.post("/optimize")
def optimize(request: OptimizationRequest):

    config = BatteryConfig(
        capacity_mwh=request.capacity_mwh,
        initial_soc_mwh=request.initial_soc_mwh,
        min_soc_mwh=request.min_soc_mwh,
        max_soc_mwh=request.max_soc_mwh,
        max_charge_mw=request.max_charge_mw,
        max_discharge_mw=request.max_discharge_mw,
        charge_efficiency=request.charge_efficiency,
        discharge_efficiency=request.discharge_efficiency,
        degradation_cost_eur_mwh=
            request.degradation_cost_eur_mwh,
    )

    forecast = load_prices(
        BASE_DIR / "data/prices_forecast.csv"
    )

    realized = load_prices(
        BASE_DIR / "data/prices_realized.csv"
    )

    dispatch, expected_profit = optimize_battery(
        forecast,
        config,
    )

    validation = validate_dispatch(
        dispatch,
        config,
    )

    realized_profit = calculate_profit(
        dispatch,
        realized["price_eur_mwh"],
        config.degradation_cost_eur_mwh,
    )

    return {
        "expected_profit_eur":
            round(expected_profit, 2),

        "realized_profit_eur":
            round(realized_profit, 2),

        "realized_uplift_eur":
            round(
                realized_profit - expected_profit,
                2,
            ),

        "validation": validation,

        "dispatch": [
            {
                "timestamp":
                    row.timestamp.isoformat(),

                "price_eur_mwh":
                    round(row.price_eur_mwh, 2),

                "charge_mwh":
                    round(row.charge_mwh, 3),

                "discharge_mwh":
                    round(row.discharge_mwh, 3),

                "soc_mwh":
                    round(row.soc_mwh, 3),
            }
            for row in dispatch.itertuples()
        ],
    }


@app.get("/")
def root():

    return {
        "name": "Battery Asset Optimization API",
        "status": "running",
        "docs_url": "/docs",
        "health_check": "/health",
    }