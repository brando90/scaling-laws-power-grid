# Scaling Laws Power Grid - Agent Setup Summary

## **Project Context for AI Agents**

This is a minimal Python research project for energy scaling laws. The project uses **uv** for dependency management and has a **py_src/** structure (not the standard src/).

### **Environment Setup**
- **uv environment**: `$HOME/uv_envs/scaling-laws-power-grid`
- **Activation**: `source $HOME/uv_envs/scaling-laws-power-grid/bin/activate`
- **Package installation**: `uv pip install -e .` (editable mode)
- **Code location**: `py_src/scaling_laws_power_grid/` (not src/)

### **Current Project Structure**
```
scaling-laws-power-grid/
├── py_src/scaling_laws_power_grid/  # ← Your code goes here
│   ├── __init__.py
│   └── core.py                     # ← Basic merit order functions
├── experiments/
│   └── 00_toy_experiment/
│       ├── codex_prompt.md         # ← Current task specification
│       └── merit_order_toy.py      # ← Script you'll create
├── pyproject.toml
├── README.md
└── uv.lock
```

### **Key Points for Implementation**
- Import from: `from scaling_laws_power_grid.core import ...`
- Run scripts from: `experiments/00_toy_experiment/`
- Output files go in the experiment directory
- Use the existing GENERATORS dict in core.py for the toy fleet data

---

## **Setup Instructions (for reference)**

## **1. Create pyproject.toml**
```toml
[project]
name = "scaling-laws-power-grid"
version = "0.1.0"
description = "Energy Scaling Laws Research"
readme = "README.md"
authors = [
    { name = "Brando Miranda", email = "brandojazz@gmail.com" },
]
requires-python = ">=3.11,<3.12"
dependencies = [
    "numpy>=1.21.0",
    "matplotlib>=3.6.0",
    "pandas>=1.5.0",
]

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["py_src"]

[tool.hatch.build.targets.wheel]
packages = ["py_src/scaling_laws_power_grid"]
```

## **2. Create Basic Package Structure**
Create `py_src/scaling_laws_power_grid/__init__.py`:
```python
"""Energy Scaling Laws Research."""

__version__ = "0.1.0"
```

Create `py_src/scaling_laws_power_grid/core.py`:
```python
"""Core merit order implementation."""

import numpy as np

# Toy Fleet Data
GENERATORS = {
    'Solar/Wind': {'capacity': 5000, 'cost': 0, 'color': 'green'},
    'Nuclear': {'capacity': 3000, 'cost': 10, 'color': 'blue'},
    'Coal': {'capacity': 4000, 'cost': 35, 'color': 'black'},
    'Gas (CC)': {'capacity': 6000, 'cost': 45, 'color': 'orange'},
    'Gas (Peaker)': {'capacity': 2500, 'cost': 90, 'color': 'red'},
    'Oil': {'capacity': 500, 'cost': 300, 'color': 'purple'}
}

def create_supply_curve():
    """Create step function supply curve."""
    capacities = []
    costs = []

    cumulative_capacity = 0
    for gen_name, gen_data in GENERATORS.items():
        capacities.extend([cumulative_capacity, cumulative_capacity + gen_data['capacity']])
        costs.extend([gen_data['cost'], gen_data['cost']])
        cumulative_capacity += gen_data['capacity']

    return np.array(capacities), np.array(costs)
```

## **3. Create Simple Experiment Script**
Create `experiments/00_toy_experiment/merit_order_toy.py`:
```python
"""Toy experiment for merit order effect."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from scaling_laws_power_grid.core import create_supply_curve
import matplotlib.pyplot as plt

def main():
    print("Creating merit order visualization...")

    capacities, costs = create_supply_curve()

    plt.figure(figsize=(10, 6))
    plt.step(capacities, costs, where='post', linewidth=2)
    plt.xlabel('Cumulative Capacity (MW)')
    plt.ylabel('Marginal Cost ($/MWh)')
    plt.title('Merit Order Supply Curve')
    plt.grid(True, alpha=0.3)
    plt.savefig('merit_order_toy_viz.png', dpi=150, bbox_inches='tight')
    plt.show()

    print("SUCCESS: Visualization saved to merit_order_toy_viz.png")
    return 0

if __name__ == "__main__":
    exit(main())
```

## **4. Basic Setup Commands**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Create uv env
mkdir -p $HOME/uv_envs
uv venv $HOME/uv_envs/scaling-laws-power-grid

# Activate and install
source $HOME/uv_envs/scaling-laws-power-grid/bin/activate
uv sync
uv pip install -e .

# Test
python -c "import scaling_laws_power_grid; print('✓ Import works')"
cd experiments/00_toy_experiment && python merit_order_toy.py
```