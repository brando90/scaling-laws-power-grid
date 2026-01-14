#!/usr/bin/env python3
import os

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq, curve_fit

HOURS_PER_DAY = 24.0
NUM_POINTS = 1000
CAPACITY_MIN_MWH = 100.0
CAPACITY_MAX_MWH = 50000.0
LOGSPACE_POINTS = 50
BLOCK_START_HOUR = 17.0
BLOCK_DURATION_HOURS = 4.0
OUTPUT_PATH = "bounded_scaling_viz.png"


def generate_duck_curve(num_points: int = NUM_POINTS) -> tuple[np.ndarray, np.ndarray]:
    time_hours = np.linspace(0.0, HOURS_PER_DAY, num_points, endpoint=False)
    time_rad = 2 * np.pi * (time_hours - 12.0) / HOURS_PER_DAY
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

    def energy_above(level: float) -> float:
        return float(np.maximum(loads - level, 0.0).sum() * dt_hours)

    def residual(level: float) -> float:
        return energy_above(level) - capacity_mwh

    low = min_load
    high = max_load
    if residual(low) < 0:
        total_energy = float(loads.sum() * dt_hours)
        total_time = float(len(loads) * dt_hours)
        low = (total_energy - capacity_mwh) / total_time
        if residual(low) < 0:
            low -= abs(low) * 1e-6 + 1e-6

    return float(brentq(residual, low, high))


def simulate_bounds(load_curve: np.ndarray, capacity_mwh: float) -> tuple[float, float, float]:
    dt_hours = HOURS_PER_DAY / len(load_curve)
    peak_opt = solve_optimal_ceiling(load_curve, capacity_mwh, dt_hours)

    discharge_power = capacity_mwh / BLOCK_DURATION_HOURS
    time_hours = np.linspace(0.0, HOURS_PER_DAY, len(load_curve), endpoint=False)
    block_end_hour = BLOCK_START_HOUR + BLOCK_DURATION_HOURS
    block_mask = (time_hours >= BLOCK_START_HOUR) & (time_hours < block_end_hour)
    pess_curve = load_curve.copy()
    pess_curve[block_mask] = pess_curve[block_mask] - discharge_power
    peak_pess = float(pess_curve.max())

    peak_exp = 0.5 * (peak_opt + peak_pess)
    return peak_opt, peak_pess, peak_exp


def power_law(x: np.ndarray, a: float, alpha: float) -> np.ndarray:
    return a * np.power(x, -alpha)


def fit_power_law(capacities: np.ndarray, peaks: np.ndarray) -> tuple[float, float]:
    log_x = np.log(capacities)
    log_y = np.log(peaks)
    slope, intercept = np.polyfit(log_x, log_y, 1)
    alpha_guess = -slope
    a_guess = np.exp(intercept)
    params, _ = curve_fit(
        power_law,
        capacities,
        peaks,
        p0=(a_guess, alpha_guess),
        bounds=(0, np.inf),
        maxfev=10000,
    )
    return float(params[0]), float(params[1])


def plot_safety_corridor(
    capacities: np.ndarray,
    peaks_opt: np.ndarray,
    peaks_pess: np.ndarray,
    peaks_exp: np.ndarray,
    alphas: tuple[float, float, float],
) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 6.0))
    fig.patch.set_facecolor("white")

    ax.fill_between(
        capacities,
        peaks_opt,
        peaks_pess,
        color="#d9d9d9",
        alpha=0.5,
        label="Guaranteed Safety Corridor",
    )

    ax.plot(capacities, peaks_opt, color="#2ca02c", linewidth=2.2, label="Optimistic Bound")
    ax.plot(capacities, peaks_pess, color="#d62728", linewidth=2.2, label="Pessimistic Bound")
    ax.plot(
        capacities,
        peaks_exp,
        color="#1f77b4",
        linestyle="--",
        linewidth=2.2,
        label="Expected Law",
    )

    ax.scatter(capacities, peaks_opt, color="#2ca02c", s=24, alpha=0.85)
    ax.scatter(capacities, peaks_pess, color="#d62728", s=24, alpha=0.85)
    ax.scatter(capacities, peaks_exp, color="#1f77b4", s=24, alpha=0.85)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Battery Capacity (MWh)")
    ax.set_ylabel("Peak Load (MW)")
    ax.set_title("Bounded Energy Scaling Laws", pad=10, weight="bold")
    ax.grid(alpha=0.35, linestyle="--", linewidth=0.6)

    alpha_opt, alpha_pess, alpha_exp = alphas
    annotation = (
        f"alpha_opt = {alpha_opt:.2f}\\n"
        f"alpha_pess = {alpha_pess:.2f}\\n"
        f"alpha_exp = {alpha_exp:.2f}"
    )
    ax.annotate(
        annotation,
        xy=(0.03, 0.05),
        xycoords="axes fraction",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0.85),
    )
    ax.legend(frameon=False, fontsize=9, loc="upper right")

    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    _, load_curve = generate_duck_curve()

    capacities = np.logspace(
        np.log10(CAPACITY_MIN_MWH),
        np.log10(CAPACITY_MAX_MWH),
        LOGSPACE_POINTS,
    )

    peaks_opt = []
    peaks_pess = []
    peaks_exp = []
    for capacity in capacities:
        peak_opt, peak_pess, peak_exp = simulate_bounds(load_curve, capacity)
        peaks_opt.append(peak_opt)
        peaks_pess.append(peak_pess)
        peaks_exp.append(peak_exp)

    peaks_opt = np.array(peaks_opt)
    peaks_pess = np.array(peaks_pess)
    peaks_exp = np.array(peaks_exp)

    if not np.all(peaks_opt <= peaks_pess + 1e-8):
        raise ValueError("Self-check failed: optimistic bound exceeds pessimistic bound.")

    _, alpha_opt = fit_power_law(capacities, peaks_opt)
    _, alpha_pess = fit_power_law(capacities, peaks_pess)
    _, alpha_exp = fit_power_law(capacities, peaks_exp)

    plot_safety_corridor(
        capacities,
        peaks_opt,
        peaks_pess,
        peaks_exp,
        (alpha_opt, alpha_pess, alpha_exp),
    )

    if not os.path.exists(OUTPUT_PATH):
        raise FileNotFoundError(f"Expected plot output was not created: {OUTPUT_PATH}")

    print(f"alpha_opt  = {alpha_opt:.4f}")
    print(f"alpha_pess = {alpha_pess:.4f}")
    print(f"alpha_exp  = {alpha_exp:.4f}")
    print(f"SUCCESS: Visualization saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
