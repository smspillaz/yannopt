"""
Common loss functions
"""
import numpy as np

from .base import Function
from .utils import drop_dimensions


################################## Interfaces ##################################
class Prox(object):
  """A function that implements the prox operator

    prox_{eta}(x) = argmin_{y} eta f(y) + (1/2) ||y-x||_2^2
  """

  def prox(self, x, eta):
    raise NotImplementedError("Prox function not implemented")


################################## Classes #####################################
class LogisticLoss(Function):
  """Logistic Regression loss function

    \sum_{i} log(1 + exp(-y_i x_i' w))

  Parameters
  ----------
  X : [n_samples, n_features] array-like
      feature matrix
  y : [n_samples] array-like
      labels for each sample. Must be in {0, 1}
  """

  def __init__(self, X, y):
    self.X = np.atleast_2d(X)
    self.y = np.atleast_1d(y)

  def eval(self, x):
    X, y = self.X, self.y
    denominators = np.log(1 + np.exp(X.dot(x)))
    numerators = y * X.dot(x)
    return -1 * np.sum(numerators - denominators)

  def gradient(self, x):
    # gradient[f](w) = \sum_{i} (y_i - P(y=1|x;w)) x_i
    X, y = self.X, self.y
    y_hat = 1.0 / (1 + np.exp(-1 * X.dot(x)))
    return -1 * np.sum((y - y_hat)[:, np.newaxis] * X, axis=0)

  def hessian(self, x):
    # hessian[f](w) = \sum_{i} P(y=1|x;w) P(y=0|x;w) x_i x_i'
    n = len(x)
    X, y = self.X, self.y

    result = np.zeros((n, n))
    y_hat = 1.0 / (1 + np.exp(-1 * X.dot(x)))
    for (i, y_pred) in enumerate(y_hat):
      result += y_pred * (1.0 - y_pred) * np.outer(X[i], X[i])
    return result


class HingeLoss(Function):
  """SVM's Hinge loss function

    \sum_{i} max(0, 1 - y_i x_i' w)

  Parameters
  ----------
  X : [n_samples, n_features] array-like
      feature matrix
  y : [n_samples] array-like
      labels for each sample. Must be in {0, 1}
  """
  def __init__(self, X, y):
    self.X = np.atleast_2d(X)
    self.y = np.atleast_1d(y)

  def eval(self, x):
    X, y = self.X, self.y
    y = 2 * y - 1
    losses = np.maximum(0, 1 - y * X.dot(x))
    return np.sum(losses)

  def gradient(self, x):
    # gradient[f](w) = \sum_{i} 1[1 - y_i x_i'w > 0] -1 * y_i x_i
    X, y = self.X, self.y
    y = 2 * y - 1
    losses = np.maximum(0, 1 - y * X.dot(x))
    return np.sum(((losses > 0) * y)[:, np.newaxis] * X, axis=0)


class Quadratic(Prox, Function):
  """Quadratic function

  0.5 x'Ax + b'x + c

  Parameters
  ----------
  A : [n, n] array-like
      Symmetric, positive semidefinite matrix
  b : [n] array-like
  c : [1] array-like
  """

  def __init__(self, A, b, c=0.0):
    self.A = np.atleast_2d(A)
    self.b = np.atleast_1d(b)
    self.c = np.asarray(c)

  def eval(self, x):
    A, b, c = self.A, self.b, self.c
    return 0.5 * x.dot(A).dot(x) + b.dot(x) + c

  def gradient(self, x):
    A, b = self.A, self.b
    return A.dot(x) + b

  def hessian(self, x):
    return self.A

  def solution(self):
    A, b = self.A, self.b
    return np.linalg.solve(A, -b)

  def prox(self, x, eta):
    A, b = self.A, self.b
    n = len(x)
    return np.linalg.lstsq(np.eye(n) + eta * A, x - eta * b)[0]


class Affine(Function):
  """Affine function

    Ax + b

  Parameters
  ----------
  A : [m, n] array-like
  b : [m] array-like
  """

  def __init__(self, A, b):
    self.A = A
    self.b = b

  def eval(self, x):
    A, b = self.A, self.b
    return A.dot(x) + b

  def gradient(self, x):
    A, b = self.A, self.b
    return self.A.T

  def hessian(self, x):
    n = len(x)
    return np.zeros((n,n))


class Constant(Prox, Function):

  def __init__(self, c):
    self.c = c

  def eval(self, x):
    return self.c

  def gradient(self, x):
    n = x.shape[0]
    return np.zeros(n)

  def hessian(self, x):
    n = x.shape[0]
    return np.zeros((n,n))

  def prox(self, x, eta):
    return x


class Separable(Function):
  """A separable function

  Function of the form,

      f(x) = \sum_{i} f_{i}(x)
  """

  def __init__(self, functions):
    self.functions = functions

  def eval(self, x):
    evals = [f(x) for f in self.functions]
    return np.sum(evals)

  def gradient(self, x):
    gradients = [f.gradient(x) for f in self.functions]
    return sum(gradients)

  def hessian(self, x):
    hessians = [f.hessian(x) for f in self.functions]
    return sum(hessians)


class Composition(Function):
  """f(g(x))

  Parameters
  ----------
  outer_functions : Function or [Function]
      components of f, stacked
  inner_functions : Function or [Function]
      components of g, stacked
  """

  def __init__(self, outer_functions, inner_functions):

    if isinstance(outer_functions, Function):
      outer_functions = [outer_functions]

    if isinstance(inner_functions, Function):
      inner_functions = [inner_functions]

    self.outer_functions = outer_functions
    self.inner_functions = inner_functions

  def eval(self, x):
    y = np.hstack(g(x) for g in self.inner_functions)
    z = np.hstack(f(y) for f in self.outer_functions)
    return z

  def gradient(self, x):
    y = np.hstack(g(x) for g in self.inner_functions)
    G = np.vstack(np.atleast_2d(f.gradient(y).T) for f in self.outer_functions)
    H = np.vstack(np.atleast_2d(g.gradient(x).T) for g in self.inner_functions)
    return drop_dimensions( ( G.dot(H) ).T )

  def hessian(self, x):
    raise NotImplementedError("TODO")


class SquaredL2Norm(Quadratic):
  """(1/2)||Ax - b||_2^2"""

  def __init__(self, A=None, b=None, n=None):
    if n is None:
      n = A.shape[1]

    if A is None:
      A = np.eye(n)

    if b is None:
      b = np.zeros(n)

    # use (1/2)||Ax-b||_2^2
    #     = (1/2) (Ax-b)'(Ax-b)
    #     = (1/2) (x'A'Ax -2b'Ax + b'b)
    #     = (1/2) x'Qx - r'x + (1/2) s
    Q = A.T.dot(A)
    r = -b.dot(A)
    s = 0.5 * b.dot(b)

    Quadratic.__init__(self, A=Q, b=r, c=s)


class L1Norm(Prox, Function):
  """||x||_1"""

  def eval(self, x):
    return np.sum(np.abs(x))

  def gradient(self, x):
    return np.sign(x)

  def hessian(self, x):
    raise NotImplementedError("Hessian not defined")

  def prox(self, x, eta):
    return np.maximum(x - eta, 0) - np.maximum(-x - eta, 0)


################################## Functions ###################################
def quadratic_approx(f, x):
  """Compute quadratic approximation to a smooth function

    f(y) ~~ f(x) + g'(y-x) + (1/2 lmbda)(y-x)'H(y-x)

  where g = gradient[f](x)
        H =  hessian[f](x)
  """
  c = f(x)
  g = f.gradient(x)
  H = f.hessian(x)

  return Quadratic(H, g, c)
