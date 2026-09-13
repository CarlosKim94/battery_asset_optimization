from dataclasses import dataclass

@dataclass(frozen=True)
class BatteryConfig:
    capacity_mwh: float = 100.0
    initial_soc_mwh: float = 50.0

    min_soc_mwh: float = 10.0
    max_soc_mwh: float = 90.0

    max_charge_mw: float = 25.0
    max_discharge_mw: float = 25.0

    charge_efficiency: float = 0.95
    discharge_efficiency: float = 0.95

    degradation_cost_eur_mwh: float = 5.0

    timestep_hours: float = 1.0