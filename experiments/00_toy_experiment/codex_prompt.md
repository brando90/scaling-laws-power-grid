You are an expert Scientific Programmer and Energy Systems Researcher. Your task is to write and execute a Python script (`water_filling_scaling.py`) that generates a visualization for a research paper on "Universal Energy Scaling Laws."

### **Project Setup Context**
This project uses **uv** for dependency management with environment at `$HOME/uv_envs/scaling-laws-power-grid`. Code goes in `py_src/scaling_laws_power_grid/` (not standard `src/`). Run this script from the `experiments/01_water_filling/` directory (create if needed).

### **1. The Scientific Context**
The paper proposes a "Universal Scaling Law" for grid stability. We reject region-specific supply stacks and instead model the grid as a **Physics Problem** using the **Water-Filling Algorithm**.
* **Core Idea:** Treat the grid load curve like a terrain. Batteries are "water" that fills the valleys (Trough/Charging) and shaves the peaks (Peak/Discharging).
* **Hypothesis:** Peak Load ($P_{peak}$) decays as a power law relative to Battery Capacity ($C$): $P_{peak} \propto C^{-\alpha}$.

### **2. Implementation Requirements**
Write a robust Python script using `matplotlib`, `numpy`, and `scipy.optimize` (if needed for curve fitting).

**Step A: Define the Data (The "Duck Curve")**
Do not fetch external data. Generate a synthetic 24-hour "Duck Curve" using `numpy` to represent the two key periods:
* **Time:** 0 to 24 hours (resolution: 100 points).
* **Base Formula:** A combination of sine waves to create a deep midday trough (solar) and a high evening peak.
    * *Suggestion:* `Load = 10000 + 4000*sin(t) - 3000*cos(2t)` (Adjust coefficients to ensure a clear Peak ~15,000 MW and Trough ~6,000 MW).
* **Constraints:** T1 (Abundance) is roughly 10am-2pm. T2 (Scarcity) is roughly 6pm-9pm.

**Step B: The Water-Filling Algorithm (The Logic)**
Implement a function `apply_water_filling(load_curve, battery_capacity_mwh, power_rating_mw)`:
1.  **Valley Filling:** Identify the lowest points. "Pour" the battery capacity into these points to raise the floor (simulating charging).
2.  **Peak Shaving:** Identify the highest points. "Drain" the stored capacity to lower the ceiling (simulating discharging).
3.  **Constraint:** You cannot move more energy than `battery_capacity_mwh`.
4.  **Constraint:** You cannot change the load at any single time step by more than `power_rating_mw`.

**Step C: The Scaling Experiment**
* Run the simulation for `Battery_Capacity` ranging from **0 MWh** to **50,000 MWh** (logarithmically spaced steps).
* For each step, record the **New Peak Load**.
* Fit a Power Law ($y = ax^{-b} + c$) to this data.

**Step D: Visualization (Dual Plot)**
Create a figure with two subplots:
1.  **Subplot 1 (The Mechanism):** Show the original Load Curve (Black) vs. the Flattened Load Curve (Green) for a specific "Medium" battery size (e.g., 20,000 MWh). Shade the "Charged" and "Discharged" areas.
2.  **Subplot 2 (The Scaling Law):**
    * X-Axis: Battery Capacity (MWh) [Log Scale].
    * Y-Axis: Peak Load (MW) [Linear Scale].
    * Plot the experimental data (dots) and the fitted Power Law line (dashed red).
    * **Annotation:** Display the calculated $\alpha$ (decay rate) on the plot.

### **3. Execution & Verification**
* Save the plot as `water_filling_scaling_viz.png` (High DPI).
* The script must include a `main` block.
* **Self-Correction Check:** Verify file creation with `os.path.exists()` and print: "SUCCESS: Visualization saved to water_filling_scaling_viz.png".