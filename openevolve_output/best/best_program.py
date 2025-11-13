# initial_program.py
import random
import math

def search_algorithm():
    # naive random search
    # Improved search:  Combines random search with a refined interval search.
    best_x = 1.0
    best_val = best_x ** best_x

    # Initial random search (as before, but with more iterations)
    for _ in range(100):
        x = random.uniform(0.01, 1.5) # Broader initial search range
        val = x ** x
        if val < best_val:
            best_x, best_val = x, val

    # Refine the search near the best found value using a smaller interval and a more focused search
    # This uses a shrinking interval and a higher number of iterations.
    for _ in range(100):
        interval = 0.1 * (0.95 ** _) # Shrinking interval
        x = random.uniform(max(1e-5, best_x - interval), best_x + interval)
        val = x ** x
        if val < best_val:
            best_x, best_val = x, val

    return best_x
