

# OpenEvolve Function Minimization: x^x

## Overview
This repository demonstrates the use of **OpenEvolve** to automatically evolve Python programs that minimize the function:

$$f(x) = x^x, \quad x > 0$$

We tested the workflow using the **Gemini API** for LLM-assisted code generation, combined with a custom evaluator that considers both accuracy and runtime.

---

## Project Structure

```

.
├── config.yaml           # OpenEvolve configuration
├── initial_program.py    # Baseline random search algorithm
├── evaluator.py          # Evaluator scoring accuracy and runtime
├── run.py                # Script to launch OpenEvolve
└── .openevolve_output/   openevolve_output# Auto-generated folder storing best programs and checkpoints

```

---

## Key Steps

1. **Initial Program**  
   - A naive random search over `[1e-5, 2.0]`, iterations up to 50 times.

2. **Evaluator**  
   - Computes a fitness score combining accuracy and runtime:  
     `score = -(error + runtime_weight * runtime)`  
   - Tracks both **error** (distance from true minimum) and **runtime** (speed).

3. **OpenEvolve Run**  
   - Evolved candidate programs via the Gemini LLM API.  
   - Iterative generations with **MAP-Elites** to maintain diversity.  
   - Checkpoints saved for potential inspection of intermediate candidates.

---

## Results

- **Best program metrics:**
  - Score: `-0.0000`
  - Error: `0.0000` (accurate minimum found)
  - Runtime: `0.0009 s` (very fast execution)

- The program converged near the **global minimum \(x = 1/e\)** already in the first/two iteration.  

- The evolved program uses a **two-phase random search**:
  1. Broad random sampling in `[0.2, 0.5]`
  2. Local refinement around the current best candidate

---

## Intermediate Programs

- All intermediate candidates are saved in **checkpoints**:

```

.openevolve_output/checkpoints/

```

- The final winning program is in:

```

.openevolve_output/best/best_program.py

````

---

## Notes

- Gemini API does **not support seeding**, so exact reproducibility may vary.  
- Text embedding model failed, so similarity filtering is off.
- Even simple initial programs can find the correct minimum quickly for this function.  
- For more complex functions, multiple iterations and generations will show gradual improvement.

---

## Usage

Run the evolution:

```bash
python openevolve-run.py initial_program.py evaluator.py --config config.yaml
````

Check the best program:

```bash
cat .openevolve_output/best/best_program.py
```

Inspect checkpoints (optional):

```bash
ls .openevolve_output/checkpoints/
```

---

## License

This repository is for demonstration purposes. Modify and experiment freely.
