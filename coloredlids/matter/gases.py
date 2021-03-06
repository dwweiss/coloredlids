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
      2020-12-20 DWW

  Acknowledgements:
      CoolProp is a contribution by Ian Bell (github.com/CoolProp/CoolProp)
"""

import numpy as np
from typing import Optional

try:
    from coloredlids.property.conversion import atm, C2K, K2C
    from coloredlids.property.matter import Gas
    from coloredlids.property.range import Range
except:
    from conversion import C2K, K2C
    from generic import Gas
    from range import Range

try:
    import CoolProp as cp
except:
    print('!!! module CoolProp not loaded')


class Air_interpolated(Gas):
    """
    Physical and chemical properties of air
    """

    def __init__(self, identifier: str = 'Air', 
                 latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        """
        Args:
            identifier:
                identifier of matter

            latex:
                Latex-version of identifier. 
                If None, latex is identical with identifier

            comment:
                comment on matter
        """
        super().__init__(identifier=identifier, latex=latex, comment=comment)
        self.version = '111220_dww'
        self.comment = 'Composition: N2: 0.78, O2: 21, Ar+CO2: 0.01'

        # reference point and operational range
        self.T._ranges['operational'] = Range(C2K(0.), C2K(100.))
        self.p._ranges['operational'] = Range(0. + atm(), 100e5 + atm())
        self.T.ref = C2K(15.)
        self.T.val = self.T.ref
        self.p.ref = atm()
        self.p.val = self.p.ref

        # constants
        self.E = 2.2e9
        self.h_melt = 334e3
        self.h_vap = 2270e3
        self.M = 29e-3
        self.T_liq = C2K(0.)
        self.T_boil = 83.

        # functions of temperature, pressure and spare parameter 'x'
        self.beta.calc = self._beta
        self.c_p.calc = self._c_p
        self.c_sound.calc = self._c_sound
        self.lambda_.calc = self._lambda
        self.mu.calc = self._mu
        self.nu.calc = self._nu
        self.rho.calc = self._rho

    def _beta(self, T, p=1e5, x=0.):
        assert T > 1e-10, str(T)
        return 1. / T

    def _c_p(self, T, p=1e5, x=0.):
        Tp = [100,   150,  200,  250,  300,  350,  400,
              450,   500,  550,  600,  650,  700,  750,
              800,   850,  900,  950, 1000, 1100, 1200,
              1300, 1400, 1500, 1600, 1700, 1800, 1900,
              2000, 2100, 2200, 2300, 2400, 2500, 3000]
        Up = [1.032e3, 1.012e3, 1.007e3, 1.006e3, 1.007e3, 1.009e3, 1.014e3,
              1.021e3, 1.030e3, 1.040e3, 1.051e3, 1.063e3, 1.075e3, 1.087e3,
              1.099e3, 1.110e3, 1.121e3, 1.131e3, 1.141e3, 1.159e3, 1.175e3,
              1.189e3, 1.207e3, 1.230e3, 1.248e3, 1.267e3, 1.286e3, 1.307e3,
              1.337e3, 1.372e3, 1.417e3, 1.478e3, 1.558e3, 1.665e3, 2.726e3]
        return np.interp(T, Tp, Up)

    def _c_sound(self, T, p=1e5, x=0.):
        return 331.3 * np.sqrt(1 + K2C(T) / 273.15)

    def _lambda(self, T, p=1e5, x=0.):
        Tp = [100,   150,  200,  250,  300,  350,  400,
              450,   500,  550,  600,  650,  700,  750,
              800,   850,  900,  950, 1000, 1100, 1200,
              1300, 1400, 1500, 1600, 1700, 1800, 1900,
              2000, 2100, 2200, 2300, 2400, 2500, 3000]
        Up = [  9.34e-3, 13.8e-3, 18.1e-3, 22.3e-3, 26.3e-3, 30.0e-3, 33.8e-3,
               37.3e-3,  40.7e-3, 43.9e-3, 46.9e-3, 49.7e-3, 52.4e-3, 54.9e-3,
               57.3e-3,  59.6e-3, 62e-3,   64.3e-3, 66.7e-3, 71.5e-3, 76.3e-3,
               82e-3,    91e-3,  100e-3,  106e-3,  113e-3,  120e-3,  128e-3,
              137e-3,   147e-3,  160e-3,  175e-3,  196e-3,  222e-3,  486e-3]
        return np.interp(T, Tp, Up)

    def _mu(self, T, p=1e5, x=0.):
        return self._nu(T, p, x) * self._rho(T, p, x)

    def _nu(self, T, p=1e5, x=0.):
        Tp = [100,   150,  200,  250,  300,  350,  400,
              450,   500,  550,  600,  650,  700,  750,
              800,   850,  900,  950, 1000, 1100, 1200,
              1300, 1400, 1500, 1600, 1700, 1800, 1900,
              2000, 2100, 2200, 2300, 2400, 2500, 3000]
        Up = [ 2e-6, 4.426e-6, 7.59e-6, 11.44e-6, 15.89e-6, 20.92e-6, 26.41e-6,
               32.39e-6, 38.79e-6, 45.57e-6, 52.69e-6, 60.21e-6, 68.10e-6,
               76.37e-6, 84.93e-6, 93.8e-6,  102.9e-6, 112.2e-6, 121.9e-6,
              141.8e-6, 162.9e-6, 185.1e-6, 213.0e-6, 240.0e-6, 268.0e-6,
              298.0e-6, 329.0e-6, 362.0e-6, 396.0e-6, 431.0e-6, 468.0e-6,
              506.0e-6, 547.0e-6, 589.0e-6, 841.0e-6]
        return np.interp(T, Tp, Up)

    def _Pr(self, T, p=1e5, x=0.):
        Tp = [100,   150,  200,  250,  300,  350,  400,
              450,   500,  550,  600,  650,  700,  750,
              800,   850,  900,  950, 1000, 1100, 1200,
              1300, 1400, 1500, 1600, 1700, 1800, 1900,
              2000, 2100, 2200, 2300, 2400, 2500, 3000]
        Up = [0.786, 0.758, 0.737, 0.720, 0.707, 0.700, 0.690,
              0.686, 0.684, 0.683, 0.685, 0.690, 0.695, 0.702,
              0.709, 0.716, 0.720, 0.723, 0.726, 0.728, 0.728,
              0.719, 0.703, 0.685, 0.688, 0.685, 0.683, 0.677,
              0.672, 0.667, 0.655, 0.647, 0.630, 0.613, 0.536]
        return np.interp(T, Tp, Up)

    def _rho(self, T, p=1e5, x=0.):
        Tp = [100,   150,  200,  250,  300,  350,  400,
              450,   500,  550,  600,  650,  700,  750,
              800,   850,  900,  950, 1000, 1100, 1200,
              1300, 1400, 1500, 1600, 1700, 1800, 1900,
              2000, 2100, 2200, 2300, 2400, 2500, 3000]
        Up = [3.5562, 2.3364, 1.7458, 1.3947, 1.1614, 0.9950, 0.8711,
              0.7740, 0.6964, 0.6329, 0.5804, 0.5356, 0.4975, 0.4643,
              0.4354, 0.4097, 0.3868, 0.3666, 0.3482, 0.3166, 0.2902,
              0.2679, 0.2488, 0.2322, 0.2177, 0.2049, 0.1935, 0.1833,
              0.1741, 0.1658, 0.1582, 0.1513, 0.1448, 0.1389, 0.1135]
        return np.interp(T, Tp, Up)


class Ar_interpolated(Gas):
    """
    Physical and chemical properties of Argon
    """

    def __init__(self, identifier: str = 'Ar', 
                 latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        """
        Args:
            identifier:
                identifier of matter

            latex:
                Latex-version of identifier. 
                If None, latex is identical with identifier

            comment:
                comment on matter
        """
        super().__init__(identifier=identifier, latex=latex, comment=comment)
        self.version = '160118_dww'

        # reference point and operational range
        self.T._ranges['operational'] = Range(C2K(0), C2K(100))
        self.T.ref = C2K(15)
        self.T.val = self.T.ref
        self.p._ranges['operational'] = Range(0. + atm(), 100e5 + atm())
        self.p.ref = atm()
        self.p.val = self.p.ref

        # constants
        self.composition['Ar'] = 100.
        self.M = 39.948e-3
        self.Z = 0.9994

        # functions of temperature, pressure and spare parameter 'x'
        self.rho.calc = self._rho
        self.nu.calc = self._nu
        self.mu.calc = self._mu
        self.c_p.calc = self._c_p
        self.lambda_.calc = self._lambda

    def _c_p(self, T, p=1e5, x=0.):
        Tp = C2K([0, 100, 200, 300, 400, 500, 600, 700, 800])
        Up = [0.522, 0.521, 0.521, 0.521, 0.521, 0.520, 0.520, 0.520, 0.520]
        return np.interp(T, Tp, Up)

    def _lambda(self, T, p=1e5, x=0.):
        Tp = C2K([0, 100, 200, 300, 400, 500, 600])
        Up = np.array([16.51, 21.17, 25.59, 29.89, 33.96, 37.91, 39.43]) * 1e-3
        return np.interp(T, Tp, Up)

    def _nu(self, T, p=1e5, x=0.):
        return self._mu(T, p, x) / self._rho(T, p, x)

    def _mu(self, T, p=1e5, x=0.):
        Tp = C2K([0, 100, 200, 300, 400, 500, 600])
        Up = np.array([21.2, 27.1, 32.1, 36.7, 41.0, 45.22, 48.7]) * 1e-6
        return np.interp(T, Tp, Up)

    def _rho(self, T, p=1e5, x=0.):
        Tp = C2K([20, 20])
        Up = [1.6339, 1.6339]
        return np.interp(T, Tp, Up)


class _Generic(Gas):
    """
    Physical and chemical properties of generic gas
    """

    def __init__(self, identifier: str = '_Generic', 
                 latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        """
        Args:
            identifier:
                identifier of matter

            latex:
                Latex-version of identifier. 
                If None, latex is identical with identifier

            comment:
                comment on matter
        """
        super().__init__(identifier=identifier, latex=latex, comment=comment)
        self.version = '151220_dww'

        # reference point and operational range
        self.T._ranges['operational'] = Range(273.16, 600)
        self.T.ref = C2K(20)
        self.T.val = self.T.ref
        self.p._ranges['operational'] = Range(0. + atm(), 100e5 + atm())
        self.p.ref = atm()
        self.p.val = self.p.ref

        # constants
        self.composition[self.identifier] = 100.        
        self.M = cp.CoolProp.PropsSI(self.identifier, 'molemass')

        # functions of temperature, pressure and spare parameter 'x'
        self.c_p.calc = self._c_p
        self.lambda_.calc = self._lambda
        self.mu.calc = self._mu
        self.nu.calc = self._nu
        self.rho.calc = self._rho


    def _c_p(self, T, p=1e5, x=0.):
        T = np.clip(T, 273.16, 600)
        return cp.CoolProp.PropsSI('C', 'T', T, 'P', p, self.identifier)

    def _rho(self, T, p=1e5, x=0.):
        T = np.clip(T, 273.16, 600)
        return cp.CoolProp.PropsSI('Dmass', 'T', T, 'P', p, self.identifier)

    def _lambda(self, T, p=1e5, x=0.):
        T = np.clip(T, 273.16, 600)
        return cp.CoolProp.PropsSI('conductivity', 'T', T, 'P', p, 
                                                   self.identifier)
    def _mu(self, T, p=1e5, x=0.):
        T = np.clip(T, 273.16, 600)
        return cp.CoolProp.PropsSI('viscosity', 'T', T, 'P', p, 
                                                self.identifier)
    def _nu(self, T, p=1e5, x=0.):
        return self._mu(T, p, x) / self._rho(T, p, x)


class Air(_Generic):
    def __init__(self, identifier: str = 'Air', latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        super().__init__(identifier=identifier, latex=latex, comment=comment)

class Ar(_Generic):
    def __init__(self, identifier: str = 'Ar', latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        super().__init__(identifier=identifier, latex=latex, comment=comment)

class CH4(_Generic):
    def __init__(self, identifier: str = 'CH4', latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        super().__init__(identifier=identifier, latex=latex, comment=comment)

class CO2(_Generic):
    def __init__(self, identifier: str = 'CO2', latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        super().__init__(identifier=identifier, latex=latex, comment=comment)

class H2(_Generic):
    def __init__(self, identifier: str = 'H2', latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        super().__init__(identifier=identifier, latex=latex, comment=comment)

class H2O(_Generic):
    def __init__(self, identifier: str = 'H2O', latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        super().__init__(identifier=identifier, latex=latex, comment=comment)

class He(_Generic):
    def __init__(self, identifier: str = 'He', latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        super().__init__(identifier=identifier, latex=latex, comment=comment)

class N2(_Generic):
    def __init__(self, identifier: str = 'N2', latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        super().__init__(identifier=identifier, latex=latex, comment=comment)

class NH3(_Generic):
    def __init__(self, identifier: str = 'NH3', latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        super().__init__(identifier=identifier, latex=latex, comment=comment)

class O2(_Generic):
    def __init__(self, identifier: str = 'O2', latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        super().__init__(identifier=identifier, latex=latex, comment=comment)

class R116(_Generic):
    def __init__(self, identifier: str = 'R116', latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        super().__init__(identifier=identifier, latex=latex, comment=comment)

class R123(_Generic):
    def __init__(self, identifier: str = 'R123', latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        super().__init__(identifier=identifier, latex=latex, comment=comment)

class R125(_Generic):
    def __init__(self, identifier: str = 'R125', latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        super().__init__(identifier=identifier, latex=latex, comment=comment)

class R1234yf(_Generic):
    def __init__(self, identifier: str = 'R1234yf', latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        super().__init__(identifier=identifier, latex=latex, comment=comment)

class R13(_Generic):
    def __init__(self, identifier: str = 'R13', latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        super().__init__(identifier=identifier, latex=latex, comment=comment)

class R14(_Generic):
    def __init__(self, identifier: str = 'R14', latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        super().__init__(identifier=identifier, latex=latex, comment=comment)

class R23(_Generic):
    def __init__(self, identifier: str = 'R23', latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        super().__init__(identifier=identifier, latex=latex, comment=comment)

class R290(_Generic):
    def __init__(self, identifier: str = 'R290', latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        super().__init__(identifier=identifier, latex=latex, comment=comment)

class R32(_Generic):
    def __init__(self, identifier: str = 'R32', latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        super().__init__(identifier=identifier, latex=latex, comment=comment)

class R404A(_Generic):
    def __init__(self, identifier: str = 'R404A', latex: Optional[str] = None, 
                 comment: Optional[str] = None):
        super().__init__(identifier=identifier, latex=latex, comment=comment)
