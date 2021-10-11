#!/usr/bin/env python
import time
import pygmo as pg

from minimization_problem import MinimizationProblem
from optimizers.boa import BOA
from optimizers.saboa import SABOA
from optimizers.xboa import XBOA

class Optimizer:
    """
    Solve the problem using pygmo algorithms
    """

    def __init__(self, problem, method='random', pop_size=10, iterations=1, 
        verbosity_level=None, seed=None, early_stopping_counter=10, **kwargs):
        """
        Creates an Optimizer object for solving the problem
        
        Arguments: 
        - problem: A pygmo problem object to optimize
        - method: optimization algorithm name
        - pop_size: number of solutions in the population (ignored when method is 'random')
        - iterations: number of generations
        - verbosity_level: set log frequecy for pygmo optimizers
        - seed: set a fixed seed for generating stochastic variables
        - early_stopping_counter: number of iterations with no fitness improvemnt to stop
        - **kwargs: captures additional args for tuning the solver (depend on the method)
        """
        self.interations = iterations
        self.early_stopping_counter = early_stopping_counter

        # create the population
        self.population = pg.population(problem, pop_size, seed=seed)
        
        # create the solver
        if method.lower() in ['boa', 'mboa', 'aboa']:
            self.solver = self.boa_solver(max_gen=iterations, variant=method, **kwargs)
            self.custom_algorithm = True
        elif method.lower() == 'saboa':
            self.solver = self.saboa_solver(max_gen=iterations, **kwargs)
            self.custom_algorithm = True
        elif method.lower() in ['xboa', 'xaboa']:
            self.solver = self.xboa_solver(max_gen=iterations, variant=method, **kwargs)
            self.custom_algorithm = True
        else:
            self.solver = 'random'
            self.solver_name = 'Random'
        
        # set verbosity level
        if verbosity_level is not None and verbosity_level > 0:
            self.verbosity_level = verbosity_level
            if self.solver == 'random':
                print("Solving problem using: Random")
            else:
                print("Solving problem using {}".format(self.solver.get_name()))
        else:
            self.verbosity_level = 0

    def get_solution(self):
        """
        Launch the optimization process and return the best solution found
        """
        if self.solver == 'random':
            best_solution = self.population.get_x()[0]
        else:
            early_stopping_counter = self.early_stopping_counter
            old_best_fitness = self.population.champion_f[0]
            if self.verbosity_level > 0:
                print("{:^7}{:^10}{:>10}{:>10}{:>10}".format(
                    "Gen", "Fevals", "Fbest", "Improv", "Duration"))
            for i in range(1, self.interations+1):
                # evolve the population for 1 iteration at a time
                time_start = time.time()
                alg = self.solver.extract(object)
                if self.custom_algorithm:
                    alg.set_iter(i)
                self.population = self.solver.evolve(self.population)
                duration = round(time.time() - time_start, 2)

                # get best fitness so far and save statistics
                best_fitness = self.population.champion_f[0]
                fitness_evaluations = self.population.problem.get_fevals()

                # check early stopping condition
                improvemnt = best_fitness - old_best_fitness
                if improvemnt == 0:
                    early_stopping_counter -= 1
                else:
                    early_stopping_counter = self.early_stopping_counter
                old_best_fitness = best_fitness
                
                # log statistics on screen
                if self.verbosity_level > 0 and i % self.verbosity_level == 0:
                    print("{:^7}{:^10}{:>10}{:>10}{:>10}".format(i, 
                        fitness_evaluations, 
                        round(best_fitness, 6), 
                        round(improvemnt, 6), 
                        duration))

                # early stopping
                if early_stopping_counter <= 0:
                    break
            
            if self.verbosity_level > 0:
                early_stop_msg = "(early stopping)" if early_stopping_counter <= 0 else ""
                print("Executed: {} generations {}".format(i, early_stop_msg))
            best_solution = self.population.champion_x
        return best_solution

    def boa_solver(self, sensory_modality=0.01, power_exponent=0.1, 
        switch_probability=0.8, mu=2, variant="BOA", max_gen=1, **unused_args):
        """ 
        Solve the problem using Burtterfly Optimization Algorithm.

        Arguments:
        - sensory_modality: regulates the degree of absorption of the fragrance
        - power_exponent: regulates the response's sensitivity to sensory stimulus
        - switch_probability: used to switch between global search and local search
        - mu: used for ABOA variant only (for more information see [Zhang et al. 2020])
        - variant: Select which variant to execute from the following cases:
          1. "BOA": The standard BOA algorithm from [Arora et al. 2019] & [Arora et al. 2016]
          2. "mBOA": BOA with intensive search from [Arora et al. 2018]
          3. "ABOA": BOA with a non-linear update rule for the sensory modality from [Zhang et al. 2020]
        - max_gen: max number of generations (used for updating the sensory modality)
        - **unused_args: capture additional args that may have been added in Optimizer config
        """
        solver = pg.algorithm(BOA(gen=1, c=sensory_modality, a=power_exponent,
            p=switch_probability, mu=mu, variant=variant, max_gen=max_gen))
        return solver

    def saboa_solver(self, switch_probability=0.8, max_gen=1, **unused_args):
        """ 
        Solve the problem using Self-Adaptative Burtterfly Optimization Algorithm.
        [Fan et al. 2020]

        Arguments:
        - switch_probability: used to switch between global search and local search
        - max_gen: max number of generations (used for updating the sensory modality)
        - **unused_args: capture additional args that may have been added in Optimizer config
        """
        solver = pg.algorithm(SABOA(gen=1, p=switch_probability, max_gen=max_gen))
        return solver

    def xboa_solver(self, sensory_modality=0.01, power_exponent=0.1,
        switch_probability=0.8, mu=2, variant="xBOA", max_gen=1, **unused_args):
        """ 
        Solve the problem using Crossover Burtterfly Optimization Algorithm.

        Arguments:
        - sensory_modality: regulates the degree of absorption of the fragrance
        - power_exponent: regulates the response's sensitivity to sensory stimulus
        - switch_probability: used to switch between global search and local search
        - mu: Used for xABOA variant only (for more information see [Zhang et al. 2020])
        - variant: Select which variant to execute from the following cases:
          1. "xBOA": The xBOA algorithm from [Bendahmane et al. 2021]
          2. "xABOA": xBOA + the non-linear update rule for the sensory modality from [Zhang et al. 2020]
        - max_gen: max number of generations (used for updating the sensory modality)
        - **unused_args: capture additional args that may have been added in Optimizer config
        """
        solver = pg.algorithm(XBOA(gen=1, c=sensory_modality, a=power_exponent, 
            p=switch_probability, mu=mu, variant=variant, max_gen=max_gen))
        return solver
