# initial_program.py
import random
import math

def search_algorithm():
    # naive random search
    best_x = 1.0
    best_val = best_x ** best_x
    for _ in range(50):
        x = random.uniform(1e-5, 2.0)
        val = x ** x
        if val < best_val:
            best_x, best_val = x, val
    return best_x
