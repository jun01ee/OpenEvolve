import importlib.util
import math
import time

def evaluate(path_to_program):
    try:
        # Dynamically import candidate
        spec = importlib.util.spec_from_file_location("candidate", path_to_program)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # Time the candidate’s execution
        start = time.perf_counter()
        best_x = mod.search_algorithm()
        elapsed = time.perf_counter() - start

        # Check domain validity
        if not isinstance(best_x, (int, float)) or best_x <= 0:
            return {"score": -9999}

        # Compute accuracy
        true_min_x = 1 / math.e
        true_min_val = true_min_x ** true_min_x
        candidate_val = best_x ** best_x
        error = abs(candidate_val - true_min_val)

        # Combine accuracy and speed into a single score
        # (lower error and shorter runtime => higher score)
        score = -(error + 0.05 * elapsed)

        return {
            "score": score,
            "error": error,
            "runtime": elapsed
        }

    except Exception:
        return {"score": -9999, "error": None, "runtime": None}
