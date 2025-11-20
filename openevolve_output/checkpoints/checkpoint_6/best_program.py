# initial_program.py

def f(x, a=1.0):
    # Parametric Gaussian family: always safe, finite
    return math.exp(-a*x*x)

def search_algorithm():
    # For this problem, return f itself.
    # OpenEvolve will mutate the f() body, not this function.
    return f
