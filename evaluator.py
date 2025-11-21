import numpy as np
from scipy.integrate import simpson

def evaluate(candidate_module):
    """
    Evaluates the candidate wavefunction f(x).
    
    Args:
        candidate_module: The imported module containing the evolved 
                          'get_wavefunction' function.
                          
    Returns:
        dict: {'score': float} where score is the product of variances.
    """
    
    # 1. Setup Grid (High resolution to capture high-freq components)
    N = 2048
    L = 20.0
    x = np.linspace(-L/2, L/2, N)
    dx = x[1] - x[0]
    
    # 2. Get the candidate wavefunction
    try:
        f = candidate_module.get_wavefunction(x)
        
        # Sanity check: Shape
        if f.shape != x.shape:
            return {'score': float('inf'), 'error': 'Shape mismatch'}
            
        # Sanity check: Finite values
        if not np.all(np.isfinite(f)):
             return {'score': float('inf'), 'error': 'NaN or Inf values'}
             
        # Sanity check: Non-zero
        norm_sq = simpson(np.abs(f)**2, x)
        if norm_sq < 1e-10:
            return {'score': float('inf'), 'error': 'Zero norm'}
            
    except Exception as e:
        return {'score': float('inf'), 'error': str(e)}

    # 3. Normalize f(x) -> Integral |f|^2 = 1
    f_norm = f / np.sqrt(norm_sq)
    
    # 4. Compute Position Variance: Int x^2 |f|^2 dx
    # Note: We calculate the second moment around 0 as requested
    prob_density_x = np.abs(f_norm)**2
    var_x = simpson(x**2 * prob_density_x, x)
    
    # 5. Compute Momentum (Frequency) Variance
    # We use the standard unitary FFT convention often used in physics
    # f_hat(xi) = Integral f(x) e^{-2pi i x xi} dx
    
    xi = np.fft.fftshift(np.fft.fftfreq(N, d=dx))
    f_hat = np.fft.fftshift(np.fft.fft(f_norm)) * dx # Scaled by dx for continuous approx
    
    # Normalize f_hat (Parseval's theorem check, strictly should be 1 already if f is norm'd)
    norm_sq_hat = simpson(np.abs(f_hat)**2, xi) # Should be close to 1
    
    prob_density_xi = np.abs(f_hat)**2 / norm_sq_hat
    var_xi = simpson(xi**2 * prob_density_xi, xi)
    
    # 6. The Objective: The Uncertainty Product
    # Theoretical minimum is 1/(16*pi^2) for standard defs, or 0.5/1 depending on units.
    product = var_x * var_xi
    
    return {
        'score': float(product),
        'var_x': float(var_x),
        'var_xi': float(var_xi)
    }