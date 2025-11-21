import numpy as np
import tempfile
import os
import subprocess
import sys
import pickle
import traceback
import importlib.util
import inspect
import re

# ==========================================
#  Robust Subprocess Evaluator (Heisenberg)
# ==========================================

class TimeoutError(Exception):
    pass

def _clean_code(code_str):
    """
    Robustly extracts code from LLM output.
    Strategies:
    1. Regex for ```python ... ``` or ``` ... ```
    2. Heuristic: Look for first 'import' or 'def' if no fences found.
    """
    if not isinstance(code_str, str):
        return code_str
    
    # 1. Try Markdown Fences
    tick = "`"
    # Regex: 3 ticks, optional language, capture content, 3 ticks
    pattern = tick * 3 + r"(?:python)?\s*(.*?)" + tick * 3
    code_block_pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
    
    match = code_block_pattern.search(code_str)
    if match:
        return match.group(1).strip()
    
    # 2. Fallback: No fences? formatting is likely loose.
    # Scan for the start of code (import or def)
    lines = code_str.splitlines()
    start_index = 0
    for i, line in enumerate(lines):
        s = line.strip()
        # Heuristic: Python usually starts with import or def in this context
        if s.startswith("import ") or s.startswith("from ") or s.startswith("def "):
            start_index = i
            break
            
    # Return from the first code line onwards
    return "\n".join(lines[start_index:]).strip()

def run_with_timeout(program_path, timeout_seconds=10):
    """
    Runs the physics evaluation in a separate subprocess.
    """
    # Create a temporary runner script
    # delete=False is required so the subprocess can read the file
    with tempfile.NamedTemporaryFile(suffix=".py", mode='w', delete=False) as temp_runner:
        
        script = f"""
import sys
import os
import numpy as np
from scipy.integrate import simpson
import pickle
import traceback
import importlib.util

def run_physics():
    try:
        # --- 1. Import the Candidate Program ---
        spec = importlib.util.spec_from_file_location("candidate", r'{program_path}')
        if spec is None:
            return {{'error': 'Could not load spec for candidate file'}}
        candidate_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(candidate_module)
        
        # --- 2. Setup Physics Grid ---
        N = 2048
        L = 20.0
        x = np.linspace(-L/2, L/2, N)
        dx = x[1] - x[0]

        # --- 3. Execute Candidate Function ---
        if not hasattr(candidate_module, 'get_wavefunction'):
            return {{'error': "Function 'get_wavefunction' not found"}}
            
        f = candidate_module.get_wavefunction(x)

        # --- 4. Validation ---
        if f.shape != x.shape:
            return {{'error': f"Shape mismatch: expected {{x.shape}}, got {{f.shape}}"}}
        
        if not np.all(np.isfinite(f)):
            return {{'error': "Wavefunction contains NaN or Inf"}}

        norm_sq = simpson(np.abs(f)**2, x)
        if norm_sq < 1e-10:
            return {{'error': "Wavefunction norm is near zero"}}

        # --- 5. Compute Physics Metrics ---
        f_norm = f / np.sqrt(norm_sq)

        # Position Variance <x^2>
        prob_density_x = np.abs(f_norm)**2
        var_x = simpson(x**2 * prob_density_x, x)

        # Momentum Variance <k^2>
        xi = np.fft.fftshift(np.fft.fftfreq(N, d=dx))
        f_hat = np.fft.fftshift(np.fft.fft(f_norm)) * dx 
        
        norm_sq_hat = simpson(np.abs(f_hat)**2, xi)
        
        if norm_sq_hat < 1e-10:
             return {{'error': "FFT norm is near zero"}}

        prob_density_xi = np.abs(f_hat)**2 / norm_sq_hat
        var_xi = simpson(xi**2 * prob_density_xi, xi)

        product = var_x * var_xi

        return {{
            'combined_score': -float(product),
            'score': -float(product),
            'var_x': float(var_x),
            'var_xi': float(var_xi)
        }}

    except Exception as e:
        return {{'error': f"Runtime Physics Error: {{str(e)}}"}}

if __name__ == "__main__":
    try:
        results = run_physics()
    except Exception as e:
        results = {{'error': f"Harness Error: {{str(e)}}"}}
    
    with open(r'{temp_runner.name}.results', 'wb') as f:
        pickle.dump(results, f)
"""
        temp_runner.write(script)
        runner_path = temp_runner.name

    results_path = runner_path + ".results"

    try:
        process = subprocess.Popen(
            [sys.executable, runner_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            raise TimeoutError(f"Execution timed out after {timeout_seconds}s")

        if process.returncode != 0:
            raise RuntimeError(f"Subprocess crashed: {stderr}")

        if os.path.exists(results_path):
            with open(results_path, "rb") as f:
                try:
                    results = pickle.load(f)
                except pickle.UnpicklingError:
                    raise RuntimeError("Failed to decode results pickle.")
            return results
        else:
            raise RuntimeError("No results file produced")

    finally:
        for p in [runner_path, results_path]:
            if os.path.exists(p):
                try: os.unlink(p)
                except: pass

def evaluate(candidate_input):
    """
    Main entry point called by OpenEvolve.
    """
    temp_candidate_path = None
    code_content = "" # Store for debug printing
    
    try:
        # 1. Handle Input (String vs File Path)
        if isinstance(candidate_input, str):
            # === CRITICAL FIX: Check if input is a file path ===
            if os.path.exists(candidate_input) and os.path.isfile(candidate_input):
                # It's a path! Read the actual code from the file.
                try:
                    with open(candidate_input, 'r') as f:
                        raw_content = f.read()
                except Exception as e:
                     return {'combined_score': float('inf'), 'error': f'Could not read candidate file: {e}'}
            else:
                # It's the raw code string
                raw_content = candidate_input
            
            # CLEANUP: Extract code from Markdown fences
            code_content = _clean_code(raw_content)
            
            # Write cleaned code to a NEW temp file for execution
            with tempfile.NamedTemporaryFile(suffix=".py", mode='w', delete=False) as f:
                f.write(code_content)
                temp_candidate_path = f.name
            target_path = temp_candidate_path
        else:
            # Module object case
            try:
                target_path = inspect.getfile(candidate_input)
            except:
                return {'combined_score': float('inf'), 'error': 'Could not determine file path'}

        # 2. Run Secure Evaluation
        results = run_with_timeout(target_path, timeout_seconds=10)
        
        # DEBUG: If error, print the code snippet to see what failed syntax
        if 'error' in results and 'invalid syntax' in str(results['error']):
            print("\n[DEBUG] Syntax Error detected! Code Snippet:")
            print("-" * 40)
            print("\n".join(code_content.splitlines()[:5])) # Print first 5 lines
            print("..." + "-" * 40)
            
        return results

    except TimeoutError:
        return {'combined_score': float('inf'), 'error': 'Timeout'}
    except Exception as e:
        return {'combined_score': float('inf'), 'error': str(e)}
    finally:
        if temp_candidate_path and os.path.exists(temp_candidate_path):
            try: os.unlink(temp_candidate_path)
            except: pass