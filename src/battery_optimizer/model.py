import pyomo.environ as pyo

from .config import BatteryConfig


def build_battery_model(
    prices: list[float],
    config: BatteryConfig,
) -> pyo.ConcreteModel:

    model = pyo.ConcreteModel()

    n_periods = len(prices)

    model.T = pyo.RangeSet(0, n_periods - 1)

    model.price = pyo.Param(
        model.T,
        initialize={i: prices[i] for i in range(n_periods)},
    )

    # Decision variables

    model.charge = pyo.Var(
        model.T,
        domain=pyo.NonNegativeReals,
    )

    model.discharge = pyo.Var(
        model.T,
        domain=pyo.NonNegativeReals,
    )

    model.soc = pyo.Var(
        model.T,
        bounds=(
            config.min_soc_mwh,
            config.max_soc_mwh,
        ),
    )

    model.charge_mode = pyo.Var(
        model.T,
        domain=pyo.Binary,
    )

    # Objective

    def objective_rule(model):
        return sum(
            model.price[t] * model.discharge[t]
            - model.price[t] * model.charge[t]
            - config.degradation_cost_eur_mwh
            * model.discharge[t]
            for t in model.T
        )

    model.objective = pyo.Objective(
        rule=objective_rule,
        sense=pyo.maximize,
    )

    # SOC constraint

    def soc_rule(model, t):

        if t == 0:
            previous_soc = config.initial_soc_mwh
        else:
            previous_soc = model.soc[t - 1]

        return model.soc[t] == (
            previous_soc
            + config.charge_efficiency * model.charge[t]
            - model.discharge[t]
            / config.discharge_efficiency
        )

    model.soc_constraint = pyo.Constraint(
        model.T,
        rule=soc_rule,
    )

    # Charging limit

    def charge_limit_rule(model, t):
        return model.charge[t] <= (
            config.max_charge_mw
            * model.charge_mode[t]
        )

    model.charge_limit = pyo.Constraint(
        model.T,
        rule=charge_limit_rule,
    )

    # Discharging limit

    def discharge_limit_rule(model, t):
        return model.discharge[t] <= (
            config.max_discharge_mw
            * (1 - model.charge_mode[t])
        )

    model.discharge_limit = pyo.Constraint(
        model.T,
        rule=discharge_limit_rule,
    )

    # Terminal SOC

    model.terminal_soc = pyo.Constraint(
        expr=model.soc[n_periods - 1]
        == config.initial_soc_mwh
    )

    return model