```markdown
# OpenEvolve Function Minimization: x^x

## Overview
This repository demonstrates the use of **OpenEvolve** to automatically evolve Python programs that minimize the function:

$$f(x) = x^x, \quad x > 0$$

We tested the workflow using the **Gemini API** for LLM-assisted code generation, combined with a custom evaluator that considers both accuracy and runtime.

---

## Structure

```

.
├── config.yaml           # OpenEvolve configuration
├── initial_program.py    # Baseline random search algorithm
├── evaluator.py          # Evaluator scoring accuracy and runtime
├── run.py                # Script to launch OpenEvolve
└── .open_evolve/         # Auto-generated folder storing best programs and checkpoints

````

---

## Key Steps

1. **Initial Program**  
   - A naive random search over `[0.2, 0.5]`, refined with local search around the current best candidate.

2. **Evaluator**  
   - Computes `score = -(error + runtime_weight * runtime)`  
   - Tracks accuracy (`error`) and execution speed (`runtime`).

3. **OpenEvolve Run**  
   - Evolved candidate programs via the Gemini LLM API.  
   - Iterative generations with MAP-Elites to maintain diversity.  
   - Checkpoints saved for potential intermediate program inspection.

---

## Results

- **Best program metrics:**
  - Score: `-0.0000`
  - Error: `0.0000` (accurate minimum found)
  - Runtime: `0.0009 s` (fast execution)

- The program converged to the **global minimum \(x = 1/e\)** already in the first iteration.

---

## Notes

- Gemini API does **not support seeding**, so exact reproducibility may vary.  
- Intermediate candidates can be extracted from `.open_evolve/checkpoints/` if needed.  
- The example shows that even a simple baseline program can achieve the exact solution quickly with OpenEvolve’s evolutionary framework.

---

## Usage

Run the evolution:

```bash
python run.py
````

The best evolved program is saved in:

```
.open_evolve/best/best_program.py
```

Metrics for each candidate are available in `.open_evolve/checkpoints/`.

```

---

If you want, I can also draft a **shorter “one-page” version** suitable for including in a GitHub repo that highlights just the workflow and results for quick reading. Do you want me to do that?
```
