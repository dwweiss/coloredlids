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
      2019-11-19 DWW
"""

import numpy as np
from typing import Optional, Union
from nptyping import Array


def v_axial(v_mean: Union[float, Array[float]] = 1., 
            d_pipe: Union[float, Array[float]] = 1., 
            r: Union[float, Array[float]] = 0., 
            nu: Union[float, Array[float]] = 1e-6, 
            lambda_: Optional[int] = None, 
            n: Optional[int] = 6) -> float:
    """
    Computes the axial velocity distribution v_z(r) in a pipe

    r
    ^
    |------
    |      -----
    |           ----  v_z(r)
    |               ---
    |                  --
    |                    --
    ---------------------------> z

    Args:
        v_mean:
            mean of axial velocity component [m/s]

        d_pipe:
            inner pipe diameter [m]

        r:
            actual radius for which axial velocity is computed [m]

        nu:
            kinematic viscosity [m^2/s]

        lambda_:
            friction coefficient (0.01 <= lambda_ <= 0.1) [/]
            (n,lambda) = {(4, .06), (5, .04), ()}

        n:
            parabel coefficient (3 <= n <= 10) [/]
            (smooth pipe surface: n=6..10, rough surface: n=4)

    Returns:
        velocity component in radial direction [m/s]

    Reference:
        Bernd Glueck: Hydrodynamische und gasdynamische Rohrstroemung.
            Verlag fuer Bauwesen, Berlin 1988
            (laminar: equ. 1.6 and 1.8, turbulent: equ. 1.02, 1.21, 1.23)
    """
    Re = v_mean * d_pipe / nu
    if Re < 2300:
        v_max = 2 * v_mean
        
        return v_max * (1.0 - 4 * (r / d_pipe)**2)
    else:
        # smooth pipe surface: n=6..10, rough: n=4
        if lambda_ is None:
            if n is None:
                n = 6
            reciprocal_of_n = 1. / n
        else:
            reciprocal_of_n = np.sqrt(lambda_)
        x = (reciprocal_of_n + 2) * (reciprocal_of_n + 1)
        v_max = v_mean * x / 2
        
        return v_max * (1.0 - 2 * r / d_pipe)**reciprocal_of_n
