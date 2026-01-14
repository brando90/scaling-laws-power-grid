You are an expert Scientific Programmer and Energy Systems Researcher. Your task is to write and execute a Python script (`bounded_scaling_laws.py`) that generates a research visualization for "Bounded Energy Scaling Laws."

### **Project Setup**
* **Environment:** Uses **uv** at `$HOME/uv_envs/scaling-laws-power-grid`.
* **Code Path:** `py_src/scaling_laws_power_grid/` (create if needed).
* **Run Path:** Run this script from the directory: `/Users/brandomiranda/scaling-laws-power-grid/experiments/03_water_filling_bounds/` (create if needed).
* **Dependencies:** `numpy`, `matplotlib`, `scipy`.

### **1. The Scientific Goal**
We are characterizing the **Safety Corridor** of grid flexibility. Instead of a single scaling law, we want to visualize three distinct bounds on a Log-Log plot:
1.  **Lower Bound (Optimistic):** The "Physics Limit" (Perfect Foresight, Optimal Water-Filling).
2.  **Upper Bound (Pessimistic):** The "Robust Limit" (Operational Reality, Rigid Scheduling).
3.  **Expected Law:** The median behavior.

**Hypothesis:** Peak Load ($P$) scales with Battery Capacity ($C$) as $P \propto C^{-\alpha}$, but the exponent $\alpha$ degrades under uncertainty.

### **2. Implementation Requirements**

**Step A: Define the "Universal Duck Curve"**
Generate a synthetic 24-hour load curve (1000 points) representing a high-stress day:
* `True_Load = 12000 + 6000*sin(t) - 4000*cos(2t)` (Clip min to 0).
* Ensure a distinct "Peak Window" exists around roughly 6 PM - 9 PM.

**Step B: Implement Three Dispatch Strategies**
Create a function `simulate_bounds(load_curve, capacity_mwh)` that returns three values: `(peak_opt, peak_pess, peak_exp)`.

1.  **Optimistic Strategy (Reverse Water-Filling):**
    * Use `scipy.optimize.brentq` to find a scalar ceiling $\lambda$ such that the area above $\lambda$ equals `capacity_mwh`.
    * `New_Load = min(True_Load, lambda)`.
    * This is the mathematically best possible peak reduction.

2.  **Pessimistic Strategy (Fixed Block Discharge):**
    * Simulate a "dumb" or "robust" operator who lacks perfect foresight.
    * The operator simply discharges the `capacity_mwh` as a **Constant Square Block** over a fixed 4-hour window (e.g., 5 PM to 9 PM).
    * `Discharge_Power = capacity_mwh / 4 hours`.
    * `New_Load = True_Load - Discharge_Power` (during the window only).
    * *Note:* Because this is a fixed window, it might miss the exact peak second. This effectively models forecast error and rigidity.

3.  **Expected Strategy:**
    * Average the results: `(peak_opt + peak_pess) / 2`.

**Step C: The Scaling Experiment**
* Range `Battery_Capacity` from **100 MWh** to **50,000 MWh** (logarithmically spaced steps).
* Run `simulate_bounds` for each step.
* Fit a Power Law ($y = Ax^{-\alpha}$) to **each of the three curves** to get $\alpha_{opt}$, $\alpha_{pess}$, and $\alpha_{exp}$.

**Step D: Visualization (The Safety Corridor)**
Create a single Log-Log plot:
* **X-Axis:** Battery Capacity (MWh).
* **Y-Axis:** Peak Load (MW).
* **Plot 1 (Green Line):** The Optimistic Lower Bound.
* **Plot 2 (Red Line):** The Pessimistic Upper Bound.
* **Plot 3 (Blue Dashed Line):** The Expected Law.
* **Shading:** Fill the area between the Green and Red lines with light grey. Label this "Guaranteed Safety Corridor".
* **Scatter Points:** Overlay the simulation data points on the lines.

### **3. Execution & Verification**
* Include a `main` block.
* Save the plot as `bounded_scaling_viz.png`.
* Print the three calculated $\alpha$ values to the console for verification.
* **Self-Check:** Verify `peak_opt` is always <= `peak_pess`.