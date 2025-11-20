# evaluator.py
import numpy as np
import math

# -----------------------------
# Numerical grid parameters
# -----------------------------
L = 5          # domain: x in [-L, L]
N = 512         # number of points
xs = np.linspace(-L, L, N)
dx = xs[1] - xs[0]

# FFT frequency grid
xis = np.fft.fftfreq(N, d=dx) * 2 * np.pi

# Theoretical lower bound (Heisenberg uncertainty principle)
TARGET = 0.25
MAX_PENALTY = 50   # cap for unstable or invalid candidates


def evaluate(candidate_module):
    """
    Evaluate a candidate module defining f(x) for the functional optimization:
        Q = | ∫ x^2 |f(x)|^2 dx * ∫ ξ^2 |f̂(ξ)|^2 dξ - TARGET |

    Returns a dictionary with at least "combined_score" for OpenEvolve evolution guidance.
    """

    # -----------------------------
    # 1. Extract f(x)
    # -----------------------------
    try:
        f = candidate_module.f
    except Exception:
        return {"combined_score": MAX_PENALTY, "I1": MAX_PENALTY, "I2": MAX_PENALTY}

    # -----------------------------
    # 2. Evaluate f on the grid
    # -----------------------------
    try:
        vals = np.array([f(float(x)) for x in xs], dtype=np.complex128)
    except Exception:
        return {"combined_score": MAX_PENALTY, "I1": MAX_PENALTY, "I2": MAX_PENALTY}

    if np.any(np.isnan(vals)) or np.any(np.isinf(vals)) or np.max(np.abs(vals)) > 1e6:
        return {"combined_score": MAX_PENALTY, "I1": MAX_PENALTY, "I2": MAX_PENALTY}

    # -----------------------------
    # 3. Normalize L^2 norm for fairness
    # -----------------------------
    norm = np.sum(np.abs(vals)**2) * dx
    if not np.isfinite(norm) or norm <= 1e-15:
        return {"combined_score": MAX_PENALTY, "I1": MAX_PENALTY, "I2": MAX_PENALTY}

    vals /= math.sqrt(norm)

    # -----------------------------
    # 4. Compute integrals
    # -----------------------------
    try:
        I1 = float(np.sum(xs**2 * np.abs(vals)**2) * dx)
    except Exception:
        I1 = MAX_PENALTY

    try:
        fhat = np.fft.fft(vals)
        I2 = float(np.sum((xis**2) * np.abs(fhat)**2) * (2*np.pi / (N*dx)))
    except Exception:
        I2 = MAX_PENALTY

    # Cap excessively large integrals
    I1 = min(I1, MAX_PENALTY)
    I2 = min(I2, MAX_PENALTY)

    # -----------------------------
    # 5. Objective score
    # -----------------------------
    Q = abs(I1 * I2 - TARGET)
    Q = min(Q, MAX_PENALTY)

    # -----------------------------
    # 6. Return as dictionary
    # -----------------------------
    return {
        "combined_score": Q,   # used internally by OpenEvolve for evolution guidance
        "I1": I1,              # optional metrics for logging/debugging
        "I2": I2
    }
