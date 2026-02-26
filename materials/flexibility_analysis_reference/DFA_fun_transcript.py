import numpy as np
from scipy import stats

def DFA_fun(data, pts, order=1):
    """
    Function for the DFA analysis.
    
    Parameters:
    -----------
    data : array_like
        A one-dimensional data vector.
    pts : array_like
        Sizes of the windows/bins at which to evaluate the fluctuation.
    order : int, optional
        Order of the polynomial for the local trend correction (default is 1).
    
    Returns:
    --------
    A : ndarray
        A 2-element array. A[0] is the scaling coefficient "alpha",
        A[1] the intercept of the log-log regression, useful for plotting.
    F : ndarray
        A vector of size len(pts) containing the fluctuations corresponding to
        the windows specified in pts.
    """
    
    # Convert data to numpy array and ensure correct orientation
    data = np.asarray(data)
    if data.ndim > 1:
        if data.shape[0] == 1:
            data = data.T
    
    # Check inputs
    if min(pts) == order + 1:
        print(f'WARNING: The smallest window size is {min(pts)}. DFA order is {order}.')
        print('This severely affects the estimate of the scaling coefficient')
        print('(If order == 1, the corresponding fluctuation is zero.)')
    elif min(pts) < (order + 1):
        print(f'ERROR: The smallest window size is {min(pts)}. DFA order is {order}:')
        print(f'Aborting. The smallest window size should be of {order+1} points at least.')
        return None, None
    
    npts = len(pts)
    F = np.zeros(npts)
    N = len(data)
    
    for h in range(npts):
        w = pts[h]
        n = int(np.floor(N / w))
        Nfloor = n * w
        D = data[:Nfloor]
        
        # Integrated series
        y = np.cumsum(D - np.mean(D))
        
        # Prepare segments
        bin_edges = np.arange(0, Nfloor, w)
        vec = np.arange(1, w + 1)
        
        # Calculate local trends and detrend
        y_hat = np.zeros_like(y)
        for j in range(n):
            segment = y[bin_edges[j]:bin_edges[j]+w]
            coeff = np.polyfit(vec, segment, order)
            y_hat[bin_edges[j]:bin_edges[j]+w] = np.polyval(coeff, vec)
        
        # Calculate fluctuation for this window size
        F[h] = np.sqrt(np.mean((y - y_hat) ** 2))
    
    # Calculate scaling coefficient
    A = np.polyfit(np.log(pts), np.log(F), 1)
    
    return A, F