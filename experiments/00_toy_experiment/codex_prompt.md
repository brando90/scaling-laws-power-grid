You are an expert Scientific Programmer and Energy Systems Researcher. Your task is to write and execute a Python script (`merit_order_toy.py`) that generates a visualization for a research paper on "Energy Scaling Laws."

### **Project Setup Context**
This project uses **uv** for dependency management with environment at `$HOME/uv_envs/scaling-laws-power-grid`. Code goes in `py_src/scaling_laws_power_grid/` (not standard `src/`). The toy fleet data is already defined in `py_src/scaling_laws_power_grid/core.py`. Run this script from the `experiments/00_toy_experiment/` directory.

### **1. The Scientific Context**
The paper challenges the assumption that energy prices scale linearly. Instead, we model the grid using the **"Merit Order Effect,"** where the supply curve is a discrete **step function** based on available technologies (Solar → Nuclear → Coal → Gas → Peakers).
* **Goal:** Visualize the "Price Cliff"—the sharp non-linear jump in price when demand crosses from one technology tier to the next.

### **2. Implementation Requirements**
Write a robust Python script using `matplotlib`, `pandas`, and `numpy`.

**Step A: Define the Data (Hardcoded)**
Do not fetch external data. Use this exact "Toy Fleet" to guarantee the visualization matches the theory:
* **Solar/Wind:** $0/MWh, 5000 MW, Green
* **Nuclear:** $10/MWh, 3000 MW, Blue
* **Coal:** $35/MWh, 4000 MW, Black
* **Gas (CC):** $45/MWh, 6000 MW, Orange
* **Gas (Peaker):** $90/MWh, 2500 MW, Red
* **Oil:** $300/MWh, 500 MW, Purple

**Step B: Construct the Step Function**
* Create an X-axis array for "Cumulative Capacity (MW)".
* Create a Y-axis array for "Marginal Cost ($/MWh)".
* *Crucial:* ensure the data is structured to plot a **STEP FUNCTION** (where the price is flat for the duration of a generator's capacity, then jumps vertically).

**Step C: Plotting**
* Use `plt.step(..., where='post')` or manually construct the vertices. **Do not use a smooth `plt.plot` line.**
* Use `plt.fill_between` to color the area under each step with the specific generator color (alpha=0.5).
* Label each step with the technology name (centered horizontally on the step).

**Step D: Annotations (The Hypothesis Proof)**
* **Base Load Line:** Vertical dashed line at **12,000 MW**. Annotate intersection price (~$45).
* **Peak Load Line:** Vertical dashed line at **19,000 MW**. Annotate intersection price (~$90).
* **The Cliff:** Add an arrow and text label pointing to the vertical jump between "Gas (CC)" and "Gas (Peaker)" labeled: **"Non-Linear Price Cliff"**.

### **3. execution & Verification**
* Save the plot as `merit_order_toy_viz.png` (High DPI).
* The script must include a `main` block that runs the generation.
* **Self-Correction Check:** After saving, use `os.path.exists()` to verify the file was created and print: "SUCCESS: Visualization saved to merit_order_toy_viz.png".