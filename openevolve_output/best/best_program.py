# initial_program.py
import math
import random

# Parametric family factory: returns a function f(x) built from parameters.
# Candidate modules can either provide `params` (dict) or a function `f(x, **kwargs)`.
def build_parametric_f(params):
    # params expected keys: "type" and numeric parameters
    t = params.get("type", "supergauss")
    if t == "supergauss":
        a = float(params.get("a", 1.0))
        p = float(params.get("p", 4.0))   # p=2 is Gaussian, p>2 super-gauss
        def f(x):
            return math.exp(- (abs(x)/a)**p )
        return f
    elif t == "lorentz":
        b = float(params.get("b", 1.0))
        def f(x):
            return 1.0 / (1.0 + (x/b)**2)
        return f
    elif t == "mixed":
        a = float(params.get("a", 1.0))
        r = float(params.get("r", 0.5))
        def f(x):
            return (1-r)*math.exp(-a*x*x) + r/(1.0 + x*x)
        return f
    else:
        # fallback safe Gaussian
        a = float(params.get("a", 1.0))
        def f(x):
            return math.exp(-a*x*x)
        return f

# This search_algorithm returns a small parameter dictionary.
def search_algorithm():
    # Provide a diverse starting sample (avoid p=2 exactly to not be Gaussian-first)
    seed_types = ["supergauss", "lorentz", "mixed"]
    choice = random.choice(seed_types)
    if choice == "supergauss":
        params = {"type":"supergauss", "a": random.uniform(0.5, 2.0), "p": random.uniform(3.0, 6.0)}
    elif choice == "lorentz":
        params = {"type":"lorentz", "b": random.uniform(0.5, 3.0)}
    else:
        params = {"type":"mixed", "a": random.uniform(0.5, 2.0), "r": random.uniform(0.2, 0.8)}
    # OpenEvolve can mutate the `params` dict or replace it with other dicts. Return it.
    return params
