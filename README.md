# Battery Asset Optimization for Electricity Trading

## 📌 Overview
A Pyomo-based optimization engine that determines the economically optimal charging and discharging schedule of a battery and evaluates the strategy against imperfect electricity price forecasts.

## ❓ Problem Description
A battery is a flexible energy asset. Its value depends on when it charges and discharges.

Given hourly electricity prices, the optimization aims to:
- charge when electricity is relatively cheap;
- store energy;
- discharge when electricity is relatively expensive;
- account for efficiency losses;
- account for degradation;
- never exceed the battery's physical limits.

The optimization maximizes the expected economic value of the battery based on forecasted electricity prices.

## 🏗️ Approach
The workflow is:

Forecasted electricity prices -> Pyomo model -> HiGHS solver -> Optimized charge/discharge schedule -> Result -> Streamlit dashboard

The optimized schedule is then evaluated using realized electricity prices to measure the impact of forecast errors.

## 📝 Mathematical Formulation
### Decision Variables

For each hourly timestep:
- `charge_t` - battery charging power (MW)
- `discharge_t` - battery discharging power (MW)
- `SOC_t` - battery state of charge (MWh)
- `mode_t` - binary variable controlling whether the battery is charging or discharging

### Objective
The model maximizes expected profit:

Maximize:
    - electricity sales revenue
    − electricity charging cost
    − battery degradation cost

The objective is calculated using the **forecasted electricity prices**.

### Constraints

The optimization enforces the physical operating limits of the battery:

**State of charge**

```text
SOC_t =
    SOC_(t-1)
    + charge_t × charge_efficiency
    - discharge_t / discharge_efficiency
```

**SOC limits**

```text
minimum SOC ≤ SOC_t ≤ maximum SOC
```

**Charging limit**

```text
0 ≤ charge_t ≤ maximum charge power
```

**Discharging limit**

```text
0 ≤ discharge_t ≤ maximum discharge power
```

**Operating mode**

A binary variable prevents the battery from charging and discharging simultaneously.

## 📊 Dataset

The project uses **synthetic hourly electricity price data** representing:

- forecasted electricity prices;
- realized electricity prices.

Synthetic data was used to keep the project self-contained and reproducible while demonstrating the optimization and forecast-error evaluation workflow.

The default battery configuration is:

| Parameter | Value |
|---|---:|
| Capacity | 100 MWh |
| Initial SOC | 50 MWh |
| Minimum SOC | 10 MWh |
| Maximum SOC | 90 MWh |
| Maximum charge | 25 MW |
| Maximum discharge | 25 MW |
| Charge efficiency | 95% |
| Discharge efficiency | 95% |
| Degradation cost | €5/MWh |
| Time resolution | 1 hour |
| Optimization horizon | 24 hours |

## 🏗️ Architecture

```text
                  ┌─────────────────┐
                  │    Streamlit    │
                  │    Dashboard    │
                  └────────┬────────┘
                           │
                           │
                           ↓
                  ┌─────────────────┐
                  │     FastAPI     │
                  │      API        │
                  └────────┬────────┘
                           │
                           ↓
                  ┌─────────────────┐
                  │  Pyomo Model    │
                  │       +         │
                  │  HiGHS Solver   │
                  └────────┬────────┘
                           │
                           ↓
                    Optimized Dispatch
                           │
                           ↓
                     dispatch.csv
```

The application is containerized with Docker and deployed as separate FastAPI and Streamlit services.

## 📊 Results

### Optimized Dispatch

The optimization produces an hourly dispatch schedule containing values such as:

- electricity price;
- charging power;
- discharging power;
- state of charge.

The Streamlit dashboard visualizes the resulting battery behavior over the 24-hour optimization horizon.

### Forecast vs Realized

The optimized strategy is generated using **forecasted prices**.

The same strategy is then evaluated using **realized prices** without re-optimizing.

For the default scenario:

| Metric | Result |
|---|---:|
| Expected Profit | €6,812.04 |
| Realized Profit | €8,756.34 |
| Realized Uplift | €1,944.30 |

The realized uplift is:

```text
Realized Profit - Expected Profit
= €8,756.34 - €6,812.04
= €1,944.30
```

In this synthetic example, the realized prices were more favorable to the optimized strategy than the forecast prices.

## 🔍 Key Findings

- Mathematical optimization can determine a battery dispatch strategy based on expected electricity prices.
- Battery efficiency and degradation have a direct economic impact on the optimal strategy.
- Physical constraints significantly influence when and how much the battery can charge or discharge.
- Separating forecast-based optimization from realized-price evaluation makes the impact of forecast errors visible.
- The optimization produces a structured dispatch schedule that can be consumed by downstream applications and visualizations.

## Future Improvements

Potential extensions include:

- integration with real electricity market data;
- probabilistic or scenario-based price forecasts;
- multiple batteries or other type of assets.

## ▶️ How to Run the Project

### Prerequisites

- Python 3.13+
- uv
- Docker and Docker Compose

### Run Locally

Clone the repository:

```bash
git clone https://github.com/CarlosKim94/battery_asset_optimization.git
cd battery_asset_optimization
```

Install dependencies:

```bash
uv sync
```

Start the FastAPI backend and Streamlit dashboard:

```bash
docker compose up --build
```

Applications:

- Streamlit dashboard: http://localhost:8501
- FastAPI API: http://localhost:8000
- FastAPI health check: http://localhost:8000/health

Open the Streamlit dashboard and click **Run Optimization**.

### 🚀 Cloud Demo

The Streamlit dashboard is deployed online:

**https://battery-asset-optimization-streamlit.onrender.com**

https://github.com/user-attachments/assets/98a4dab0-844b-4f0d-9b18-ad54101f7633

The FastAPI backend is deployed as a separate service and is called by the Streamlit dashboard.
