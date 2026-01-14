You are an expert Scientific Programmer and Energy Systems Researcher, familiar with Convex Optimization (Boyd & Vandenberghe). Your task is to write and execute a Python script (`water_filling_scaling.py`) that generates a visualization for a paper on "The Thermodynamic Limit of Grid Flexibility."

### **Project Setup Context**
This project uses **uv** for dependency management. The environment is at `$HOME/uv_envs/scaling-laws-power-grid`.
* **Code Location:** `py_src/scaling_laws_power_grid/` (Note: not `src/`).
* **Run Location:** Run this script from the `experiments/01_water_filling/` directory (create if needed).
* **Dependencies:** `numpy`, `matplotlib`, `scipy`.

### **1. The Scientific Context**
The paper proposes a "Universal Scaling Law" for grid stability using the **Reverse Water-Filling Algorithm**.
* **Concept:** We treat the Load Curve as a "terrain" and Battery Capacity as a fixed "volume" that shaves the highest peaks.
* **The Physics:** We do not iterate through time steps. We solve for a scalar "Ceiling" ($\lambda$).
* **Hypothesis:** Peak Load ($P_{peak}$) decays as a power law relative to Battery Capacity ($C$): $P_{peak} \propto C^{-\alpha}$.

### **2. Implementation Requirements**
Write a robust Python script.

**Step A: Define the Data (The "Duck Curve")**
Do not fetch external data. Generate a synthetic 24-hour "Duck Curve" (1000 time points) to represent a solar-heavy grid.
* **Formula:** `Base_Load = 12000 + 6000*sin(t) - 4000*cos(2t)` (or similar superposition).
* **Goal:** Ensure a deep "Belly" (Solar Trough ~8,000 MW) and a sharp "Neck" (Evening Peak ~20,000 MW).
* **Constraints:** Clip values so min load $\ge 0$.

**Step B: The Reverse Water-Filling Logic (CRITICAL)**
Implement a function `solve_optimal_ceiling(load_curve, capacity_mwh, dt_hours)`:
1.  **The Objective:** Find a scalar $\lambda$ such that the integral of the load *above* $\lambda$ equals the `capacity_mwh`.
    * Equation: $\sum (\max(0, P(t) - \lambda) \times dt) = Capacity$
2.  **The Solver:** Use `scipy.optimize.brentq` to find the root of `(energy_above_lambda(x) - capacity)`.
    * *Note:* This guarantees the "Red Part" (discharged energy) is perfectly optimal and strictly at the top.
3.  **The New Load:** Return the new curve: `min(load_curve, lambda)`.

**Step C: The Scaling Experiment**
* Run the simulation for `Battery_Capacity` ranging from **0 MWh** to **50,000 MWh** (logarithmically spaced, 50 steps).
* For each step, record the **New Peak Load** (which is just $\lambda$).
* Fit a Power Law ($y = Ax^{-\alpha} + B$) to the results.

**Step D: Visualization (The "Boyd" Plot)**
Create a high-quality figure with two subplots:
1.  **Subplot 1 (The Mechanism):**
    * Plot the **Original Load Curve** (Black Line).
    * Select a specific "Medium" capacity (e.g., 25,000 MWh).
    * Plot the **New Load Curve** (Green Line). It must be **perfectly flat** at the peak.
    * Shade the area *between* Black and Green in Red. Label: "Optimal Peak Shaving".
2.  **Subplot 2 (The Scaling Law):**
    * X-Axis: Battery Capacity (MWh) [Log Scale].
    * Y-Axis: Peak Load (MW) [Linear Scale].
    * Plot the experimental data (Blue Dots) and the fitted Power Law (Red Dashed Line).
    * **Annotation:** Display the calculated $\alpha$ (decay exponent) clearly.

### **3. Execution & Verification**
* Save the plot as `water_filling_scaling_viz.png` (High DPI).
* The script must include a `main` block.
* **Self-Correction Check:** Verify file creation with `os.path.exists()` and print: "SUCCESS: Visualization saved to water_filling_scaling_viz.png".