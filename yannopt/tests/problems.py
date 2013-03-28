import numpy as np

from yannopt.constraints import base as constraints
from yannopt.problem import minimize, Solution
from yannopt import functions as f


def quadratic_program1():
  A = np.array([[1.0, 0.5, 0.0],
                [0.5, 1.0, 0.5],
                [0.0, 0.5, 1.0]])
  b = np.array([1.0, 2.0, 3.0])
  objective = f.Quadratic(A, b)

  problem   = minimize(objective)
  solution  = objective.solution()
  initial   = np.zeros(len(b))

  return Solution(problem=problem, x=solution, x0=initial)


def quadratic_program2():
  Q = np.array([[1.0, 0.5, 0.0],
                [0.5, 1.0, 0.5],
                [0.0, 0.5, 1.0]])
  c = np.array([1.0, 2.0, 3.0])
  objective = f.Quadratic(Q, c)

  A = np.array([[1.0, 0.0, -1.0],
                [0.0, 1.0,  0.5]])
  b = np.array([0.2, 0.4])
  constraint = constraints.LinearEquality(A, b)

  problem   = minimize(objective).subject_to(constraint)
  solution  = np.array([-2.48,  1.74, -2.68])
  initial   = np.linalg.lstsq(A, b)[0]

  return Solution(problem=problem, x=solution, x0=initial)