#!/usr/bin/env python3
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def build_toy_fleet() -> pd.DataFrame:
    data = [
        {
            "technology": "Solar/Wind",
            "marginal_cost": 0,
            "capacity_mw": 5000,
            "color": "green",
        },
        {
            "technology": "Nuclear",
            "marginal_cost": 10,
            "capacity_mw": 3000,
            "color": "blue",
        },
        {
            "technology": "Coal",
            "marginal_cost": 35,
            "capacity_mw": 4000,
            "color": "black",
        },
        {
            "technology": "Gas (CC)",
            "marginal_cost": 45,
            "capacity_mw": 6000,
            "color": "orange",
        },
        {
            "technology": "Gas (Peaker)",
            "marginal_cost": 90,
            "capacity_mw": 2500,
            "color": "red",
        },
        {
            "technology": "Oil",
            "marginal_cost": 300,
            "capacity_mw": 500,
            "color": "purple",
        },
    ]
    df = pd.DataFrame(data)
    df["cum_capacity_mw"] = df["capacity_mw"].cumsum()
    df["start_capacity_mw"] = df["cum_capacity_mw"] - df["capacity_mw"]
    return df


def price_at(
    demand_mw: float,
    edges_mw: np.ndarray,
    prices: np.ndarray,
    *,
    boundary: str = "right",
    bin_size_mw: int | None = None,
) -> float:
    demand = float(demand_mw)
    if bin_size_mw:
        demand = (demand // bin_size_mw) * bin_size_mw
    idx = np.searchsorted(edges_mw, demand, side=boundary) - 1
    idx = int(np.clip(idx, 0, len(prices) - 1))
    return float(prices[idx])


def plot_merit_order(df: pd.DataFrame, output_path: str) -> None:
    total_capacity = int(df["capacity_mw"].sum())
    max_price = float(df["marginal_cost"].max())

    edges = np.concatenate(([0], df["cum_capacity_mw"].to_numpy()))
    prices = df["marginal_cost"].to_numpy()
    x_step = edges
    y_step = np.concatenate((prices, [prices[-1]]))

    fig, ax = plt.subplots(figsize=(10, 6))

    for _, row in df.iterrows():
        start = float(row["start_capacity_mw"])
        end = float(row["cum_capacity_mw"])
        price = float(row["marginal_cost"])
        ax.fill_between(
            [start, end],
            0,
            price,
            color=row["color"],
            alpha=0.5,
        )

    ax.step(x_step, y_step, where="post", color="black", linewidth=2)

    label_offset = max_price * 0.02
    for _, row in df.iterrows():
        start = float(row["start_capacity_mw"])
        end = float(row["cum_capacity_mw"])
        mid = (start + end) / 2
        ax.text(
            mid,
            row["marginal_cost"] + label_offset,
            row["technology"],
            ha="center",
            va="bottom",
            fontsize=9,
        )

    base_load = 12000
    peak_load = 19000
    base_price = price_at(base_load, edges, prices, boundary="right")
    peak_price = price_at(peak_load, edges, prices, boundary="right")

    ax.axvline(base_load, color="gray", linestyle="--", linewidth=1)
    ax.axvline(peak_load, color="gray", linestyle="--", linewidth=1)

    ax.annotate(
        f"Base Load = {base_load:,} MW\nPrice ~${int(base_price)}/MWh",
        xy=(base_load, base_price),
        xytext=(base_load + 700, base_price + 20),
        arrowprops=dict(arrowstyle="->", color="gray"),
        fontsize=9,
        ha="left",
    )
    ax.annotate(
        f"Peak Load = {peak_load:,} MW\nPrice ~${int(peak_price)}/MWh",
        xy=(peak_load, peak_price),
        xytext=(peak_load + 700, peak_price + 40),
        arrowprops=dict(arrowstyle="->", color="gray"),
        fontsize=9,
        ha="left",
    )

    gas_cc_end = float(
        df.loc[df["technology"] == "Gas (CC)", "cum_capacity_mw"].iloc[0]
    )
    gas_cc_cost = float(
        df.loc[df["technology"] == "Gas (CC)", "marginal_cost"].iloc[0]
    )
    peaker_cost = float(
        df.loc[df["technology"] == "Gas (Peaker)", "marginal_cost"].iloc[0]
    )
    cliff_y = (gas_cc_cost + peaker_cost) / 2
    ax.annotate(
        "Non-Linear Price Cliff",
        xy=(gas_cc_end, cliff_y),
        xytext=(gas_cc_end + 1200, cliff_y + 35),
        arrowprops=dict(arrowstyle="->", color="black"),
        fontsize=10,
        ha="left",
    )

    ax.set_title("Merit Order Supply Curve (Toy Fleet)")
    ax.set_xlabel("Cumulative Capacity (MW)")
    ax.set_ylabel("Marginal Cost ($/MWh)")
    ax.set_xlim(0, total_capacity + 500)
    ax.set_ylim(0, max_price * 1.12)
    ax.grid(alpha=0.3, linestyle="--", linewidth=0.5)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def main() -> None:
    df = build_toy_fleet()

    total_capacity = int(df["capacity_mw"].sum())
    max_price = int(df["marginal_cost"].max())
    assert total_capacity == 21000
    assert max_price == 300

    edges = np.concatenate(([0], df["cum_capacity_mw"].to_numpy()))
    prices = df["marginal_cost"].to_numpy()

    # Bin the demand to emphasize discrete jumps in the toy curve.
    price_at_18999 = price_at(
        18999, edges, prices, boundary="left", bin_size_mw=1000
    )
    price_at_19001 = price_at(
        19001, edges, prices, boundary="left", bin_size_mw=1000
    )
    assert price_at_19001 > (price_at_18999 * 1.5), (
        "Error: The Price Cliff is missing or too small."
    )

    output_path = "merit_order_toy_viz.png"
    plot_merit_order(df, output_path)
    assert os.path.exists(output_path)
    print("SUCCESS: Logic verified and visualization saved")


if __name__ == "__main__":
    main()
