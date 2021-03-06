"""
  Copyright (c) 2016- by Dietmar W Weiss

  This is free software; you can redistribute it and/or modify it
  under the terms of the GNU Lesser General Public License as
  published by the Free Software Foundation; either version 3.0 of
  the License, or (at your option) any later version.

  This software is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public
  License along with this software; if not, write to the Free
  Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
  02110-1301 USA, or see the FSF site: http://www.fsf.org.

  Version:
      2019-09-16 DWW
"""

from nptyping import Array
import numpy as np
from scipy import optimize

"""
    Example for employing minimizers from scipy.optimize for 
    1. finding minimum of a function
    2. finding optimal x satisfying minimum of difference between 
       function result f(x) and target y_trg
"""

def f1(x: Array[float]) -> float:
    return .5*(1 - x[0])**2 + (x[1] - x[0]**2)**2

def f2(x: Array[float]) -> float:
    return 1*x[0]**2 + x[1]

########################################################################

y_trg = 0.5   # target in inverse problem solution

def objective(x: Array[float]) -> float:
    """
    Objective function for inverse problem solution

    Args:
        x (1D array of float)
        
    Returns:
            L2-norm of difference between f2() and target
    """
    return np.sqrt(np.mean(f2(x) - y_trg)**2)

########################################################################

print('Find Minimum of f(x)')
result = optimize.minimize(f1, [2, -1], method="CG")
print('Minimum of f(x):', result.x)
print('Summary minimum:', result)

########################################################################

print('Find x so that (f(x) - y_trg)**2 is mimimum')
result = optimize.minimize(fun=objective, x0=[-1, 9], method="Nelder-Mead")
print('Inverse, optimal x:', result.x)
print('Summary inverse:', result)
