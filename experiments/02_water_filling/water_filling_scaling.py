#!/usr/bin/env python3
import os

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq, curve_fit

HOURS_PER_DAY = 24.0
NUM_POINTS = 1000
CAPACITY_MAX_MWH = 50000.0
LOGSPACE_POINTS = 50
MEDIUM_CAPACITY_MWH = 25000.0
OUTPUT_PATH = "water_filling_scaling_viz.png"


def generate_duck_curve(num_points: int = NUM_POINTS) -> tuple[np.ndarray, np.ndarray]:
    time_hours = np.linspace(0.0, HOURS_PER_DAY, num_points, endpoint=False)
    time_rad = 2 * np.pi * (time_hours + 10.0) / HOURS_PER_DAY
    load_mw = 12000 + 6000 * np.sin(time_rad) - 4000 * np.cos(2 * time_rad)
    load_mw = np.clip(load_mw, 0.0, None)
    return time_hours, load_mw


def solve_optimal_ceiling(
    load_curve: np.ndarray,
    capacity_mwh: float,
    dt_hours: float,
) -> float:
    loads = np.asarray(load_curve, dtype=float)
    max_load = float(loads.max())
    min_load = float(loads.min())

    if capacity_mwh <= 0:
        return max_load

    def energy_above_lambda(level: float) -> float:
        return float(np.maximum(loads - level, 0.0).sum() * dt_hours)

    def residual(level: float) -> float:
        return energy_above_lambda(level) - capacity_mwh

    low = min_load
    high = max_load
    if residual(low) < 0:
        total_energy = float(loads.sum() * dt_hours)
        total_time = float(len(loads) * dt_hours)
        low = (total_energy - capacity_mwh) / total_time
        if residual(low) < 0:
            low -= abs(low) * 1e-6 + 1e-6

    return float(brentq(residual, low, high))


def apply_reverse_water_filling(
    load_curve: np.ndarray,
    capacity_mwh: float,
    dt_hours: float,
) -> tuple[float, np.ndarray]:
    ceiling = solve_optimal_ceiling(load_curve, capacity_mwh, dt_hours)
    return ceiling, np.minimum(load_curve, ceiling)


def power_law(x: np.ndarray, a: float, alpha: float, b: float) -> np.ndarray:
    return a * np.power(x, -alpha) + b


def plot_results(
    time_hours: np.ndarray,
    load_curve: np.ndarray,
    medium_curve: np.ndarray,
    capacities_mwh: np.ndarray,
    peak_loads_mw: np.ndarray,
    fit_params: tuple[float, float, float],
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.6))
    fig.patch.set_facecolor("white")

    ax1, ax2 = axes

    ax1.plot(time_hours, load_curve, color="black", linewidth=2, label="Original Load")
    ax1.plot(
        time_hours,
        medium_curve,
        color="#2a9d8f",
        linewidth=2,
        label=f"Shaved Load ({MEDIUM_CAPACITY_MWH:,.0f} MWh)",
    )
    ax1.fill_between(
        time_hours,
        load_curve,
        medium_curve,
        where=load_curve > medium_curve,
        color="#d62828",
        alpha=0.35,
        label="Optimal Peak Shaving",
    )
    ax1.set_title("Reverse Water-Filling Mechanism", pad=10, weight="bold")
    ax1.set_xlabel("Hour of Day")
    ax1.set_ylabel("Load (MW)")
    ax1.set_ylim(0, load_curve.max() * 1.12)
    ax1.grid(alpha=0.35, linestyle="--", linewidth=0.6)
    ax1.legend(frameon=False, fontsize=8, loc="upper left")

    fit_a, fit_alpha, fit_b = fit_params
    fit_mask = capacities_mwh > 0
    capacities_fit = capacities_mwh[fit_mask]
    peaks_fit = peak_loads_mw[fit_mask]
    fit_x = np.logspace(np.log10(capacities_fit.min()), np.log10(capacities_fit.max()), 200)
    fit_y = power_law(fit_x, fit_a, fit_alpha, fit_b)

    ax2.scatter(
        capacities_fit,
        peaks_fit,
        color="#1d3557",
        s=28,
        alpha=0.9,
        label="Simulation",
    )
    ax2.plot(
        fit_x,
        fit_y,
        color="#e63946",
        linestyle="--",
        linewidth=2,
        label="Power-Law Fit",
    )
    ax2.set_xscale("log")
    ax2.set_title("Scaling Law: Peak Load vs Battery Capacity", pad=10, weight="bold")
    ax2.set_xlabel("Battery Capacity (MWh)")
    ax2.set_ylabel("Peak Load (MW)")
    ax2.grid(alpha=0.35, linestyle="--", linewidth=0.6)
    ax2.legend(frameon=False, fontsize=8, loc="upper right")
    ax2.annotate(
        f"alpha = {fit_alpha:.2f}",
        xy=(0.05, 0.1),
        xycoords="axes fraction",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="none", alpha=0.85),
    )

    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    time_hours, load_curve = generate_duck_curve()
    dt_hours = float(time_hours[1] - time_hours[0])

    _, medium_curve = apply_reverse_water_filling(
        load_curve,
        MEDIUM_CAPACITY_MWH,
        dt_hours,
    )

    positive_caps = np.logspace(0, np.log10(CAPACITY_MAX_MWH), LOGSPACE_POINTS - 1)
    capacities_mwh = np.concatenate(([0.0], positive_caps))

    peak_loads = []
    for capacity in capacities_mwh:
        peak_loads.append(solve_optimal_ceiling(load_curve, capacity, dt_hours))
    peak_loads_mw = np.array(peak_loads)

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

    plot_results(
        time_hours,
        load_curve,
        medium_curve,
        capacities_mwh,
        peak_loads_mw,
        tuple(fit_params),
    )

    if not os.path.exists(OUTPUT_PATH):
        raise FileNotFoundError(f"Expected plot output was not created: {OUTPUT_PATH}")
    print("SUCCESS: Visualization saved to water_filling_scaling_viz.png")


if __name__ == "__main__":
    main()
