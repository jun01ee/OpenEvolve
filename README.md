Heisenberg Uncertainty Minimizer with OpenEvolve

This project uses OpenEvolve (an evolutionary coding agent) to numerically discover the wavefunction $f(x)$ that minimizes the Heisenberg Uncertainty Product:


$$\sigma_x^2 \sigma_\xi^2 \ge \frac{1}{16\pi^2} \approx 0.00633$$

Starting from a crude "boxcar" function (score $\approx 6.0$), the agent evolves Python code to rediscover the Gaussian wavefunction (score $\approx 0.0063$).

💡 Discussion & Future Work

Summary of Results:
The agent successfully converged on the Gaussian wavefunction ($\psi(x) \propto e^{-ax^2}$), achieving the theoretical minimum score of $\approx 0.0063$. The discovery occurred extremely rapidly (often by Iteration 2), suggesting that the LLM leveraged strong inductive bias from its training data rather than performing a "blind" evolutionary search. Since the "Heisenberg Uncertainty Principle" is a famous physics problem, the model likely "recalled" the solution rather than deriving it.

Future Directions to Test "True" Discovery:
To rigorously test the agent's optimization capabilities beyond simple recall, future experiments should:

Obfuscate the Physics: Rename variables (e.g., minimize std(u) * std(v) where v is the FFT of u) and remove all references to "Heisenberg" or "Wavefunction."

Non-Standard Functionals: Minimize functionals with no closed-form analytical solution, such as $\int |x|^4 |f|^2 dx \cdot \int |k|^2 |\hat{f}|^2 dk$.

Add Constraints: Force the solution to have compact support or specific boundary conditions that preclude the standard Gaussian.

🧪 Evolution Showcase

1. Initial Program (The "Boxcar")

Score: $\approx 6.0$ (High uncertainty due to sharp edges)

The agent starts with a discontinuous square pulse. The sharp transitions at $x = \pm 1$ introduce high-frequency components in Fourier space, blowing up the momentum variance.

import numpy as np

def get_wavefunction(x):
    """
    Initial guess: A simple rectangular box function.
    Sharp edges = High Momentum Variance.
    """
    width = 2.0
    y = np.zeros_like(x, dtype=np.complex128)
    
    # Create the box
    mask = (x > -width/2) & (x < width/2)
    y[mask] = 1.0 + 0.0j
    
    return y


2. Evolved Solution (The Gaussian)

Score: $\approx 0.0063$ (Theoretical Minimum)

After $\approx 12$ iterations, OpenEvolve converges on a Gaussian profile. This function strikes the perfect balance between localization in position space and localization in momentum space.

import numpy as np

def get_wavefunction(x):
    """
    Evolved solution: A Gaussian function.
    Smooth decay = Minimum Uncertainty Product.
    """
    # The agent discovers that a smooth exponential decay is optimal
    # Parameters like width (sigma) may vary, but the shape is Gaussian
    sigma = 0.75 
    y = np.exp(-x**2 / (2 * sigma**2))
    
    return y.astype(np.complex128)


🧠 The System Prompt

This is the exact instruction set given to the LLM (Gemini Flash) to guide the evolution. Note the specific hint about "smoothing edges" to steer the physics.

You are evolving a Python wavefunction to minimize the Heisenberg Uncertainty Product.

The evaluator computes: Integral |x|^2 |f(x)|^2 * Integral |k|^2 |f_hat(k)|^2.

Rules:
- You must define: `def get_wavefunction(x):`
- Do not change the function signature.
- Return the COMPLETE function code (no diffs).
- Focus on smoothing edges to reduce momentum variance.
- No Monte Carlo loops.


📂 Project Structure

initial_program.py: The seed program containing a boxcar implementation of get_wavefunction(x).

evaluator.py: The physics engine. It computes position/momentum variances via FFT and returns a fitness score.

config.yaml: OpenEvolve configuration tuned for the Gemini Free Tier (low concurrency).

run.py: A wrapper script to launch the evolution loop programmatically.

extract_best.py: A utility to recover the true best solution from checkpoints if the main loop crashes or maximizes incorrectly.

🐛 Key Bugs & Workarounds

This setup addresses several specific challenges encountered during development:

1. Maximization vs. Minimization

Issue: OpenEvolve is hardcoded to maximize the combined_score. It initially discarded our optimal low-uncertainty solutions ($0.0063$) in favor of high-uncertainty garbage ($6.0$).

Fix: In evaluator.py, we negated the physics output: combined_score = -product. This tricks the maximizer into seeking the numerical minimum.

2. LLM Syntax Errors (Markdown Fences)

Issue: Gemini often wraps code in ```python ... ```, causing invalid syntax errors when Python tries to execute the raw string.

Fix: evaluator.py includes a Regex cleaner (_clean_code) that aggressively strips Markdown fences and conversational preambles before execution.

3. Process Isolation & Timeouts

Issue: Evolved code often contains infinite loops or crashes, which would kill the main OpenEvolve process.

Fix: evaluator.py writes the candidate code to a temp file and executes it in a separate subprocess with a hard 10-second timeout.

4. Free Tier Rate Limits

Issue: The default population size (24) triggered immediate 429 Too Many Requests errors on the Gemini Free Tier (15 RPM limit).

Fix: config.yaml is tuned to population_size: 4, num_islands: 1, and parallel_evaluations: 1.

5. Diff-Based Evolution Failure

Issue: Small/Fast models like Gemini Flash struggled to generate valid <<<< SEARCH / >>>> REPLACE blocks, leading to "No valid diffs found" warnings.

Fix: Disabled diff_based_evolution in config.yaml. The model now rewrites the full function, which is more reliable for short scripts.