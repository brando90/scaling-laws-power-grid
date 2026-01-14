You are an expert in Convex Optimization and Energy Systems, familiar with the Boyd & Vandenberghe "Water-Filling" algorithms. Your task is to write and execute a Python script (`water_filling_scaling.py`) that generates a visualization for a research paper on "Universal Energy Scaling Laws."

### **Project Setup Context**
This project uses **uv** for dependency management with environment at `$HOME/uv_envs/scaling-laws-power-grid`. Code goes in `py_src/scaling_laws_power_grid/` (not standard `src/`). Run this script from the `experiments/01_water_filling/` directory (create if needed).

### **1. The Scientific Context**
The paper proposes a "Universal Scaling Law" for grid stability. We reject region-specific supply stacks and instead model the grid as a **Physics Problem** using the **Reverse Water-Filling Algorithm**.
* **Core Idea:** To minimize grid strain, we treat the Load Curve as a "terrain" and Battery Capacity as a fixed "volume" of water.
* **The Algorithm:** We strictly minimize the **Peak Load** by finding a horizontal "ceiling" ($\lambda$). All load above this ceiling is "chopped" (discharged) until the battery is empty.
* **Hypothesis:** Peak Load ($P_{peak}$) decays as a power law relative to Battery Capacity ($C$): $P_{peak} \propto C^{-\alpha}$.

### **2. Implementation Requirements**
Write a robust Python script using `matplotlib`, `numpy`, and `scipy.optimize`.

**Step A: Define the Data (The "Duck Curve")**
Do not fetch external data. Generate a synthetic 24-hour "Duck Curve" (1000 time points) that clearly shows a "Belly" (Solar Trough) and a "Neck" (Evening Peak).
* **Formula Suggestion:** Use a superposition of sinusoids + gaussian noise:
  `Base_Load = 12000 + 6000*sin(t) - 4000*cos(2t)`
* **Normalization:** Clip the minimum to 0. Ensure the Peak is ~20,000 MW and the Trough is ~8,000 MW.

**Step B: The Reverse Water-Filling Logic (Crucial)**
Do NOT use a time-step loop. Implement a function `solve_optimal_ceiling(load_curve, battery_capacity_mwh, time_resolution_hours)`:
1.  **The Objective:** Find a scalar value `lambda` (the ceiling) such that the area between the Load Curve and `lambda` equals `battery_capacity_mwh`.
    * Equation: $\sum (\max(0, P(t) - \lambda) \times \Delta t) = Capacity$
2.  **The Solver:** Use `scipy.optimize.brentq` (root finding) to solve for `lambda` efficiently.
    * *Note:* The "New Load" at any time $t$ is simply $\min(P(t), \lambda)$.
3.  **Power Constraint:** For this theoretical "Limit" paper, assume the battery has sufficient power rating (MW) to discharge the required energy.

**Step C: The Scaling Experiment**
* Run the simulation for `Battery_Capacity` ranging from **0 MWh** to **50,000 MWh** (logarithmically spaced, 50 steps).
* For each step, calculate the **New Peak Load** (which is just equal to the calculated `lambda`).
* Fit a Power Law ($y = Ax^{-\alpha} + B$) to this data.

**Step D: Visualization (The "Boyd" Plot)**
Create a high-quality figure with two subplots:
1.  **Subplot 1 (The Mechanism):** * Show the original Load Curve (Black Line).
    * Select a specific capacity (e.g., 25,000 MWh) and plot the New Load Curve (Green Line).
    * **Crucial:** The Green line must be perfectly flat at the peak.
    * Shade the area *between* Black and Green in Red (Label: "Peak Shaving / Discharged Energy").
2.  **Subplot 2 (The Scaling Law):**
    * X-Axis: Battery Capacity (MWh) [Log Scale].
    * Y-Axis: Peak Load (MW) [Linear Scale].
    * Plot the experimental data (Blue Dots) and the fitted Power Law (Red Dashed Line).
    * **Annotation:** Print the scaling exponent $\alpha$ clearly on the plot.

### **3. Execution & Verification**
* Save the plot as `water_filling_scaling_viz.png` (High DPI).
* The script must include a `main` block.
* **Self-Correction Check:** Verify file creation with `os.path.exists()` and print: "SUCCESS: Visualization saved to water_filling_scaling_viz.png".