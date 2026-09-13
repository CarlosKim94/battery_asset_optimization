import matplotlib.pyplot as plt
import pandas as pd


def plot_dispatch(
    dispatch: pd.DataFrame,
    output_path: str,
) -> None:

    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(
        dispatch["timestamp"],
        dispatch["price_eur_mwh"],
        label="Price",
    )

    ax1.set_ylabel("Price (€/MWh)")

    ax2 = ax1.twinx()

    ax2.plot(
        dispatch["timestamp"],
        dispatch["soc_mwh"],
        label="SOC",
    )

    ax2.bar(
        dispatch["timestamp"],
        dispatch["charge_mwh"],
        alpha=0.4,
        label="Charge",
    )

    ax2.bar(
        dispatch["timestamp"],
        -dispatch["discharge_mwh"],
        alpha=0.4,
        label="Discharge",
    )

    ax2.set_ylabel("Battery energy (MWh)")

    fig.autofmt_xdate()

    plt.title("Battery Optimal Dispatch")

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=150,
    )

    plt.close()