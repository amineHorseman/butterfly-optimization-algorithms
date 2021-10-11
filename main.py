#!/usr/bin/env python
import yaml

from minimization_problem import MinimizationProblem
from optimizer import Optimizer

def load_arg_or_none(dict_obj, arg_name):
    return dict_obj[arg_name] if arg_name in dict_obj else None

# parameters
with open('params.yaml', 'r') as f:
   params = yaml.safe_load(f)
   solution_size = load_arg_or_none(params, 'solution_size')
   lower_bound = load_arg_or_none(params, 'lower_bound')
   upper_bound = load_arg_or_none(params, 'upper_bound')
   pop_size = load_arg_or_none(params, 'pop_size')
   max_iterations = load_arg_or_none(params, 'max_iterations')
   method = load_arg_or_none(params, 'method')
   method_params = load_arg_or_none(params, 'method_params')
   verbosity_level = load_arg_or_none(params, 'verbosity_level')
   seed = load_arg_or_none(params, 'seed')
   early_stopping_counter = load_arg_or_none(params, 'early_stopping_counter')

# launch optimization
problem = MinimizationProblem(solution_size, lower_bound, upper_bound)
solver = Optimizer(problem, method=method, pop_size=pop_size, iterations=max_iterations, 
   verbosity_level=verbosity_level, seed=seed, early_stopping_counter=early_stopping_counter,
   **method_params)
best_solution = solver.get_solution()
print("Best solution: {}".format(best_solution))
