import numpy as np

def get_wavefunction(x):
    """
    Generates the complex-valued wavefunction f(x).
    The evaluator handles normalization, so this function
    just needs to return the shape.
    """
    
    # EVOLVE-BLOCK-START
    # Initial guess: A simple rectangular box function (Boxcar)
    # This is far from optimal (sharp edges = high frequency components)
    
    width = 2.0
    # Initialize with zeros
    y = np.zeros_like(x, dtype=np.complex128)
    
    # Replace boxcar with a Gaussian
    sigma = width / 4.0 # Adjust sigma to control the width of the Gaussian
    y = np.exp(-x**2 / (2 * sigma**2)) + 0.0j
    
    # EVOLVE-BLOCK-END
    
    return y