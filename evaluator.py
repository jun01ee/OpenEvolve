# evaluator.py
import numpy as np
import math
import inspect

# numerical grid (conservative)
L = 6.0
N = 1024   # small enough for speed, increase later for validation
xs = np.linspace(-L, L, N)
dx = xs[1] - xs[0]
# frequency grid for FFT (angular frequency)
xis = np.fft.fftfreq(N, d=dx) * 2.0 * math.pi

TARGET = 0.25
SOFT_MAX = 1e4   # large-but-finite cap for bad candidates
BAD_PENALTY = 100.0  # initial penalty for mildly bad candidates

def build_f_from_candidate(candidate_module):
    """
    Accept either:
      - candidate_module.params (dict) describing a parametric family, OR
      - candidate_module.f function (callable) that accepts a float and optional params.
    Return a callable f(x).
    """
    # Case 1: params dict
    params = getattr(candidate_module, "params", None)
    if isinstance(params, dict):
        # re-use the helper from initial_program if present; otherwise, define safe families
        if hasattr(candidate_module, "build_parametric_f"):
            return candidate_module.build_parametric_f(params)
        else:
            t = params.get("type", "supergauss")
            if t == "supergauss":
                a = float(params.get("a", 1.0)); p = float(params.get("p", 4.0))
                return lambda x: math.exp(- (abs(x)/a)**p )
            elif t == "lorentz":
                b = float(params.get("b", 1.0))
                return lambda x: 1.0 / (1.0 + (x/b)**2)
            elif t == "mixed":
                a = float(params.get("a", 1.0)); r = float(params.get("r", 0.5))
                return lambda x: (1-r)*math.exp(-a*x*x) + r/(1.0 + x*x)
    # Case 2: f function provided
    f = getattr(candidate_module, "f", None)
    if callable(f):
        # Accept f(x) or f(x, **kwargs). We'll wrap to single-arg call if needed.
        try:
            # test call
            _ = f(0.0)
            return f
        except TypeError:
            # try call with default params
            return (lambda x: f(x))
    # Nothing usable
    return None

def complexity_penalty(candidate_module):
    # simple code-length penalty
    try:
        src = inspect.getsource(candidate_module)
        return 0.001 * len(src)   # tuneable
    except Exception:
        return 1.0

def smoothness_penalty(vals):
    # second-derivative energy as smoothness measure
    try:
        d2 = np.gradient(np.gradient(np.real(vals), dx), dx)
        return 0.001 * np.sum(d2**2) * dx  # tuneable
    except Exception:
        return 0.0

def evaluate(candidate_module):
    if not hasattr(candidate_module, "__dict__"):
        print("[ERROR] Candidate is not a valid module:", repr(candidate_module))
        return BAD_PENALTY
    print("[DEBUG] candidate_module.search_algorithm =", 
      getattr(candidate_module, "search_algorithm", None))

    """
    Returns dict with keys:
      - combined_score: lower is better (distance from theoretical optimal TARGET)
      - I1, I2 (for debugging)
      - extras: complexity_penalty, smoothness_penalty
    """
    # build f
    f_callable = build_f_from_candidate(candidate_module)
    if f_callable is None:
        print("[DEBUG] FAILED: no valid function or params found in candidate module")
        return {"combined_score": BAD_PENALTY, "I1": BAD_PENALTY, "I2": BAD_PENALTY,
                "complexity_penalty": 1.0, "smoothness_penalty": 1.0}

    # evaluate on grid
    try:
        vals = np.array([f_callable(float(x)) for x in xs], dtype=np.complex128)
    except Exception as e:
        print("[DEBUG] FAILED: evaluating f(x) threw exception", e)
        return {"combined_score": BAD_PENALTY, "I1": BAD_PENALTY, "I2": BAD_PENALTY,
                "complexity_penalty": 1.0, "smoothness_penalty": 1.0}

    # basic sanity checks
    if np.any(np.isnan(vals)) or np.any(np.isinf(vals)) or np.max(np.abs(vals)) > 1e6:
        print("[DEBUG] FAILED: values invalid (NaN/Inf or too large)")
        return {"combined_score": BAD_PENALTY, "I1": BAD_PENALTY, "I2": BAD_PENALTY,
                "complexity_penalty": 1.0, "smoothness_penalty": 1.0}

    # normalization (we keep normalization to make I1/I2 comparable)
    norm = np.sum(np.abs(vals)**2) * dx
    if not np.isfinite(norm) or norm <= 1e-16:
        print("[DEBUG] FAILED: normalization invalid:", norm)
        return {"combined_score": BAD_PENALTY, "I1": BAD_PENALTY, "I2": BAD_PENALTY,
                "complexity_penalty": 1.0, "smoothness_penalty": 1.0}
    vals = vals / math.sqrt(norm)

    # integrals
    try:
        I1 = float(np.sum((xs**2) * (np.abs(vals)**2)) * dx)
    except Exception:
        I1 = SOFT_MAX
    try:
        fhat = np.fft.fft(vals)
        I2 = float(np.sum((xis**2) * (np.abs(fhat)**2)) * (2.0*math.pi / (N * dx)))
    except Exception as e:
        print("[DEBUG] FAILED: FFT/I2 computation exception", e)
        I2 = SOFT_MAX

    # main objective (distance from analytic minimum)
    Q = abs(I1 * I2 - TARGET)

    # regularizers
    cpen = complexity_penalty(candidate_module)
    spen = smoothness_penalty(vals)

    combined = Q + 0.1 * cpen + 0.1 * spen   # weights tuneable

    # clip to finite range
    if not np.isfinite(combined):
        combined = SOFT_MAX

    return {
        "combined_score": float(min(combined, SOFT_MAX)),
        "I1": float(min(I1, SOFT_MAX)),
        "I2": float(min(I2, SOFT_MAX)),
        "complexity_penalty": float(cpen),
        "smoothness_penalty": float(spen)
    }


