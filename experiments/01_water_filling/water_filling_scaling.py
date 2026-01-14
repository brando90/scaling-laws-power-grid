#!/usr/bin/env python3
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator, StrMethodFormatter
from scipy.optimize import curve_fit

NUM_POINTS = 100
MEDIUM_BATTERY_MWH = 20000
POWER_RATING_MW = 3000
CAPACITY_MAX_MWH = 50000
LOGSPACE_POINTS = 14
ANNOTATION_BOX = dict(
    boxstyle="round,pad=0.25",
    facecolor="white",
    edgecolor="none",
    alpha=0.85,
)


def generate_duck_curve(num_points: int = NUM_POINTS) -> tuple[np.ndarray, np.ndarray]:
    time_hours = np.linspace(0, 24, num_points)
    time_rad = 2 * np.pi * time_hours / 24
    load_mw = 9500 + 3300 * np.cos(time_rad - 4.9) - 2300 * np.cos(2 * time_rad)
    return time_hours, load_mw


def apply_water_filling(
    load_curve: np.ndarray,
    battery_capacity_mwh: float,
    power_rating_mw: float,
    dt_hours: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    loads = np.asarray(load_curve, dtype=float)
    if battery_capacity_mwh <= 0 or power_rating_mw <= 0:
        return loads.copy(), np.zeros_like(loads), np.zeros_like(loads)

    power_cap = float(power_rating_mw)
    min_load = float(loads.min())
    max_load = float(loads.max())

    def charge_energy(level: float) -> float:
        deltas = np.clip(level - loads, 0, power_cap)
        return float(deltas.sum() * dt_hours)

    def discharge_energy(level: float) -> float:
        deltas = np.clip(loads - level, 0, power_cap)
        return float(deltas.sum() * dt_hours)

    low, high = min_load, max_load
    for _ in range(60):
        mid = (low + high) / 2
        if charge_energy(mid) > discharge_energy(mid):
            high = mid
        else:
            low = mid
    balance_level = (low + high) / 2

    max_transfer_mwh = charge_energy(balance_level)
    energy_to_shift = min(float(battery_capacity_mwh), max_transfer_mwh)
    if energy_to_shift <= 0:
        return loads.copy(), np.zeros_like(loads), np.zeros_like(loads)

    def solve_charge_level(target_mwh: float) -> float:
        low, high = min_load, balance_level
        for _ in range(60):
            mid = (low + high) / 2
            if charge_energy(mid) >= target_mwh:
                high = mid
            else:
                low = mid
        return (low + high) / 2

    def solve_discharge_level(target_mwh: float) -> float:
        low, high = balance_level, max_load
        for _ in range(60):
            mid = (low + high) / 2
            if discharge_energy(mid) >= target_mwh:
                low = mid
            else:
                high = mid
        return (low + high) / 2

    charge_level = solve_charge_level(energy_to_shift)
    discharge_level = solve_discharge_level(energy_to_shift)

    charge_mw = np.clip(charge_level - loads, 0, power_cap)
    discharge_mw = np.clip(loads - discharge_level, 0, power_cap)
    adjusted = loads + charge_mw - discharge_mw
    return adjusted, charge_mw, discharge_mw


def power_law(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    return a * np.power(x, -b) + c


def plot_results(
    time_hours: np.ndarray,
    load_curve: np.ndarray,
    adjusted_curve: np.ndarray,
    charge_mw: np.ndarray,
    discharge_mw: np.ndarray,
    capacities_mwh: np.ndarray,
    peak_loads_mw: np.ndarray,
    fit_params: tuple[float, float, float],
    output_path: str,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.6))
    fig.patch.set_facecolor("white")

    for ax in axes:
        ax.set_facecolor("#f7f5f0")
        ax.grid(alpha=0.35, linestyle="--", linewidth=0.6, color="#9aa0a6")
        ax.tick_params(axis="both", labelsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    ax1, ax2 = axes

    ax1.plot(time_hours, load_curve, color="black", linewidth=2, label="Original Load")
    ax1.plot(
        time_hours,
        adjusted_curve,
        color="#2a9d8f",
        linewidth=2,
        label="Flattened Load",
    )
    ax1.fill_between(
        time_hours,
        load_curve,
        adjusted_curve,
        where=adjusted_curve >= load_curve,
        color="#8ecae6",
        alpha=0.45,
        label="Charging (Valley Fill)",
    )
    ax1.fill_between(
        time_hours,
        load_curve,
        adjusted_curve,
        where=adjusted_curve < load_curve,
        color="#e76f51",
        alpha=0.45,
        label="Discharging (Peak Shave)",
    )

    y_max = max(load_curve.max(), adjusted_curve.max()) * 1.12
    ax1.set_ylim(0, y_max)
    ax1.set_title("Water-Filling Mechanism (20,000 MWh Battery)", pad=10, weight="bold")
    ax1.set_xlabel("Hour of Day")
    ax1.set_ylabel("Load (MW)")
    ax1.xaxis.set_major_locator(MaxNLocator(nbins=7, integer=True))
    ax1.yaxis.set_major_locator(MaxNLocator(nbins=6, integer=True))
    ax1.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    ax1.legend(frameon=False, fontsize=8, loc="upper left")

    fit_a, fit_b, fit_c = fit_params
    capacities_fit = capacities_mwh[capacities_mwh > 0]
    peaks_fit = peak_loads_mw[capacities_mwh > 0]
    fit_x = np.logspace(np.log10(capacities_fit.min()), np.log10(capacities_fit.max()), 200)
    fit_y = power_law(fit_x, fit_a, fit_b, fit_c)

    ax2.scatter(
        capacities_fit,
        peaks_fit,
        color="#264653",
        s=28,
        alpha=0.9,
        label="Simulation",
    )
    ax2.plot(
        fit_x,
        fit_y,
        color="#d62828",
        linestyle="--",
        linewidth=2,
        label="Power-Law Fit",
    )
    ax2.set_xscale("log")
    ax2.set_title("Scaling Law: Peak Load vs Battery Capacity", pad=10, weight="bold")
    ax2.set_xlabel("Battery Capacity (MWh)")
    ax2.set_ylabel("Peak Load (MW)")
    ax2.yaxis.set_major_locator(MaxNLocator(nbins=6, integer=True))
    ax2.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    ax2.legend(frameon=False, fontsize=8, loc="upper right")
    ax2.annotate(
        f"alpha = {fit_b:.2f}",
        xy=(0.05, 0.1),
        xycoords="axes fraction",
        fontsize=10,
        bbox=ANNOTATION_BOX,
    )

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    time_hours, load_curve = generate_duck_curve()
    dt_hours = float(time_hours[1] - time_hours[0])

    adjusted_curve, charge_mw, discharge_mw = apply_water_filling(
        load_curve,
        MEDIUM_BATTERY_MWH,
        POWER_RATING_MW,
        dt_hours,
    )

    capacities_mwh = np.concatenate(
        (
            [0.0],
            np.logspace(2, np.log10(CAPACITY_MAX_MWH), LOGSPACE_POINTS),
        )
    )
    peak_loads_mw = []
    for capacity in capacities_mwh:
        adjusted, _, _ = apply_water_filling(
            load_curve,
            capacity,
            POWER_RATING_MW,
            dt_hours,
        )
        peak_loads_mw.append(float(adjusted.max()))
    peak_loads_mw = np.array(peak_loads_mw)

    fit_mask = capacities_mwh > 0
    initial_guess = (
        peak_loads_mw[fit_mask][0] - peak_loads_mw[fit_mask][-1],
        0.6,
        peak_loads_mw[fit_mask][-1],
    )
    fit_params, _ = curve_fit(
        power_law,
        capacities_mwh[fit_mask],
        peak_loads_mw[fit_mask],
        p0=initial_guess,
        bounds=(0, [np.inf, 5, np.inf]),
        maxfev=10000,
    )

    output_path = "water_filling_scaling_viz.png"
    plot_results(
        time_hours,
        load_curve,
        adjusted_curve,
        charge_mw,
        discharge_mw,
        capacities_mwh,
        peak_loads_mw,
        tuple(fit_params),
        output_path,
    )

    if not os.path.exists(output_path):
        raise FileNotFoundError("Expected plot output was not created.")
    print("SUCCESS: Visualization saved to water_filling_scaling_viz.png")


if __name__ == "__main__":
    main()
