"""
  Copyright (c) 2018- by Dietmar W Weiss

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
      2018-05-17 DWW
"""

import numpy as np
from lmfit import Minimizer, Parameters, report_fit


def f(x, **kwargs):
    """
    Theoretical submodel f(x) for SINGLE data point

    Args:
        x (1D array_like of float):
            input, shape: (nInp)

        kwargs (dict, optional):
            keyword arguments:

            define (bool, optional):
                if True then return definition of fit parameters
                default: False

            c0, c1, ... (float, optional):
                coefficients

    Returns:
        (lmfit.Parameter object):
            if 'define' then key, initial value and bounds of fit pars
        or
        (1D array_like of float or float):
            if 'define' is False then output, shape: (nOut)
    """
    # return the list of defined lmfit.Parameters entries for lmfit.minimize()
    if kwargs.get('define', False):
        C = Parameters()
        C.add_many(('c0', 5), ('c1', 0.2), ('c2', 3), ('c3', .007))
        return C

    c0, c1, c2, c3 = kwargs.get('c0', 1), kwargs.get('c1', 1), \
        kwargs.get('c2', 1), kwargs.get('c3', 1)

    y0 = c0 * np.sin(x[0] * c2 + c1) * np.exp(-x[0]**2 * c3)
    y1 = x[1]
    return y0, y1


class LmfitExample(object):
    """
    Demonstrates the use of the Lmfit package for curve fitting
    """

    def __init__(self):
        self.x = None
        self.y = None
        self.X = None
        self.Y = None
        self.ready = True
        self._weights = None
        self.best = None

        self.f = f  # assign externally defined function

    def train(self, X, Y, **kwargs):
        """
        Trains model. X and Y are stored as self.X and self.Y if both are not
        None

        Args:
            X (2D or 1D array_like of float):
                training input, shape: (nPoint, nInp) or shape: (nPoint)

            Y (2D or 1D array_like of float):
                training target, shape: (nPoint, nOut) or shape: (nPoint)

            kwargs (dict, optional):
                keyword arguments

                trainers (string or list of string):
                    type of trainers

                epochs (int):
                    maximum number of epochs

                goal (float):
                    residuum to be met

                trials (int):
                    number of repetitions of training with same trainer
                ...

        Returns:
            (dict {str: float or str or int}):
                result of best training trial:
                    'trainer' (str): best trainer
                    'L2'    (float): sqrt{sum{(net(x)-Y)^2}/N} of best training
                    'abs'   (float): max{|net(x) - Y|} of best training
                    'iAbs'    (int): index of Y where absolute error is maximum
                    'epochs'  (int): number of epochs of best training

        Note:
            If X or Y is None, or training fails then self.best['trainer']=None
        """

        def objective(params, X, Y):
            """
            Objective function to be minimized (passed to lmfit.minimize())

            Args:
                params (ordered dict or lmfit.Parameter):
                    dictionary of coefficients with boundaries etc

                X (2D or 1D array_like of float):
                    training input, shape: (nPoint, nInp) or shape: (nPoint)

                Y (2D or 1D array_like of float):
                    training target, shape: (nPoint, nOut) or shape: (nPoint)

            Returns:
                (2D array of float):
                    difference between prediction f(X) and target Y(X)
            """
            opt = {k: params[k] for k in params.keys()}
            return np.subtract(self.predict(X, **opt), Y)

        ###
        silent = kwargs.get('silent', True)

        if X is not None and Y is not None:
            self.X, self.Y = X, Y

        self.ready = True
        self.best = {}

        self._weights = None  # needed in self.predict()
        params = self.f(None, define=True)

        minimizer = Minimizer(objective, params, fcn_args=(X, Y))
        result = minimizer.minimize()
        if not silent:
            report_fit(result)

        # TODO decide on success of training
        self.ready = True
        if self.ready:
            self._weights = result.params.valuesdict()  # fitted params as dict
            self.best = {'trainer': '', 'L2': np.inf, 'abs': np.inf,
                         'iAbs': -1, 'epochs': -1}

    def predict(self, x, **kwargs):
        """
        Prediction for MULTIPLE data points. With MPI (requires paralle.py) the
        execution is distributed. x and y=f(x) is stored as self.x and self.y

        Args:
            x (2D or 1D array_like of float):
                prediction input, shape: (nPoint, nInp) or shape: (nInp)

            kwargs (dict, optional):
                keyword arguments

                c0, c1, ... (multiple float):
                    coefficients
                    default: 1.0

                ... further options to be passed to self.f

        Returns:
            (2D array of float):
                if x is not None and self.ready: prediction output
            or
            (None):
                otherwise
        """
        kw = kwargs.copy()
        if 'x' in kw:
            del kw['x']
        if self._weights is not None:
            for key, val in self._weights.items():
                kw[key] = val

        self.x = x
        self.y = np.array([np.atleast_1d(self.f(x=_x, **kw))
                           for _x in self.x])
        return self.y


# Examples ####################################################################

if __name__ == '__main__':
    import matplotlib.pyplot as plt

    ALL = 1

    if 1 or ALL:
        model = LmfitExample()

        X0 = np.linspace(0, 15, 301)
        X1 = np.linspace(-10, 10, 301)
        X = np.c_[X0, X1]
        C = f(None, define=True)
        Y_exa = model.predict(X, **C)
        Y = Y_exa + np.random.normal(size=Y_exa.shape, scale=0.2)

        y0 = model.predict(X, silent=False)

        best = model.train(X, Y, silent=False)
        print('weights:', model._weights)

        y = model.predict(X, silent=False)

        plt.title('Lmfit Y(X) vs f(X)')
        plt.plot(X[:, 0], Y[:, 0], 'k+', label='Y')
        plt.plot(X[:, 0], y0[:, 0], 'g', label='yStart')
        plt.plot(X[:, 0], y[:, 0], 'b', label='y')
        plt.legend()
        plt.show()
