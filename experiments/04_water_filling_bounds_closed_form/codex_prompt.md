You are an expert Scientific Programmer and Energy Systems Researcher. Your task is to write and execute a Python script (`bounded_scaling_laws.py`) that generates a research visualization for "Bounded Energy Scaling Laws."

### **Project Setup**
* **Environment:** Uses **uv** at `$HOME/uv_envs/scaling-laws-power-grid`.
* **Code Path:** `py_src/scaling_laws_power_grid/` (create if needed).
* **Run Path:** Run this script from the directory: `$HOME/scaling-laws-power-grid/experiments/03_water_filling_bounds/` (create if needed).
* **Dependencies:** `numpy`, `matplotlib`, `scipy`.

### **1. The Scientific Goal**
We are characterizing the **Safety Corridor** of grid flexibility. Instead of a single scaling law, we want to visualize three distinct bounds on a Log-Log plot:
1.  **Lower Bound (Optimistic):** The "Physics Limit" (Perfect Foresight, Optimal Water-Filling).
2.  **Upper Bound (Pessimistic):** The "Robust Limit" (Operational Reality, Rigid Scheduling).
3.  **Expected Law (Analytic):** The behavior under human constraints (modeled via effective capacity).

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
    * Return `max(New_Load)`.

2.  **Pessimistic Strategy (Fixed Block Discharge):**
    * Simulate a "dumb" robust operator.
    * Discharge the `capacity_mwh` as a **Constant Square Block** over a fixed 4-hour window (e.g., 5 PM to 9 PM).
    * `Discharge_Power = capacity_mwh / 4 hours`.
    * `New_Load = True_Load - Discharge_Power` (during window only).
    * Return `max(New_Load)`.

3.  **Expected Strategy (Analytic Derivation):**
    * **Logic:** Do NOT use Monte Carlo. Use a closed-form heuristic.
    * **Assumption:** Due to human behavioral overrides and diversity factors (Velander’s effect), the *effective* capacity available for optimal peak shaving is only ~75% of nameplate.
    * **Method:** Run the **Reverse Water-Filling** logic (same as Optimistic), but input `capacity_mwh * 0.75`.
    * This provides a rigorous "Median" curve derived from behavioral assumptions.

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
* **Plot 3 (Blue Dashed Line):** The Expected Law (Analytic).
* **Shading:** Fill the area between the Green and Red lines with light grey. Label this "Guaranteed Safety Corridor".
* **Annotation:** Display the three $\alpha$ exponents in a legend or text box.

### **3. Execution & Verification**
* Include a `main` block.
* Save the plot as `bounded_scaling_viz.png`.
* **Self-Check:** Verify `peak_opt` <= `peak_exp` <= `peak_pess`.