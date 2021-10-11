#!/usr/bin/env python
import random
import math
import numpy as np

class XBOA:
    """
    BOA: Crossover Butterfly Optimization Algorithm.

    Implements the XBOA algorithm as a Pygmo UDA
    """
    def __init__(self, gen=1, c=0.01, a=0.1, p=0.8, mu=2, max_gen=1, variant="xBOA"):
        """
        Creates a Pygmo UDA implementing the Crossover Butterfly Optimization Algorithm

        Arguments:
        - gen: number of generations (iterations) to evolve the population
        - c: Sensory modality
        - a: Power exponent
        - p: Switch probability
        - mu: Used for xABOA variant only (for more information see [Zhang et al. 2020])
        - variant: Select which variant to execute from the following cases:
          1. "xBOA": The xBOA algorithm from [Bendahmane et al. 2021], which is a variant of BOA [Arora et al. 2019] + the crossover operator
          2. "xABOA": xBOA + the non-linear update rule for the sensory modality from [Zhang et al. 2020]
        - max_gen: max number of generations (used for updating the sensory modality)
    
        References:
        - [Bendahmane et al. 2021] "Unknown Area Exploration for Robots with Energy Constraints using a Modified Butterfly Optimization Algorithm" 
        - [Zhang et al. 2020] "A chaotic hybrid butterfly optimization algorithm with particle swarm optimization for high-dimensional optimization problems"
        - [Arora et al. 2019] "Butterfly optimization algorithm: a novel approach for global optimization"
        """
        self.iterations = gen if gen > 1 else 1
        self.c = c
        self.a = a
        self.p = p if p>=0 and p<=1 else 0.8
        self.mu = mu
        self.variant = variant.lower()
        if self.variant not in ["xboa", "xaboa"]:
            self.variant = "xboa"
        self.max_iterations = max_gen
        self.verbosity_level = 0
        self.log = []
        self.current_iteration = 1
        self.mu = mu

    def evolve(self, population):
        """
        Evolve the population for a certain number of iterations (specified 
        during initiatlization)
        """
        # extract population individuals
        bounds = population.problem.get_bounds()
        pop_size = len(population.get_ID())

        for i in range(self.iterations):
            old_best_fit = population.champion_f

            # extract population individuals
            solutions_x = population.get_x()
            solutions_fitness = population.get_f()
            solutions_IDs = population.get_ID()
            pop = dict()
            for id, fit, x in zip(solutions_IDs, solutions_fitness, solutions_x):
                pop[id] = {'fit':fit[0], 'x':x}

            # loop through every butterfly
            for id in solutions_IDs:
                x = pop[id]['x']

                # compute frangrace
                fitness = pop[id]['fit']
                if fitness > 0:
                    f = self.c * (fitness ** self.a)
                else:
                    # multiply by -1 to avoid getting a complex result when calculating exponent
                    f = self.c * ((-fitness) ** self.a)

                # move butterflies
                if random.random() > self.p:
                    # apply crossover operator to create two offsprings
                    j = id
                    while j == id and pop_size > 1: 
                        j = random.choice(list(pop))
                    mate = pop[j]['x'].copy()
                    x_ = x.copy()
                    crossover_point = random.choice(range(len(x)-1))+1
                    x1 = x_[:crossover_point]
                    x2 = x_[crossover_point:]
                    mate1 = mate[:crossover_point]
                    mate2 = mate[crossover_point:]
                    offspring1 = np.concatenate([x1, mate2])
                    offspring2 = np.concatenate([mate1, x2])
                
                    # add offsprings to the population and evaluate the fitness
                    offspring1 = self.force_bounds(offspring1, bounds)
                    offspring2 = self.force_bounds(offspring2, bounds)
                    new_fitness1 = population.problem.fitness(offspring1)[0]
                    new_fitness2 = population.problem.fitness(offspring2)[0]
                    
                    # replace parent by best offspring
                    if new_fitness1 < fitness or new_fitness2 < fitness:
                        if new_fitness1 < new_fitness2:
                            pop[id] = {'fit':new_fitness1, 'x':offspring1}
                        else:
                            pop[id] = {'fit':new_fitness2, 'x':offspring2} 
                else:
                    # find random butterfly in the neighbourhood
                    r1 = random.random()
                    r2 = random.random()
                    j = random.choice(list(pop))
                    k = random.choice(list(pop))
                    x += f * (r1 * r2 * pop[j]['x'] - pop[k]['x'])

                    # add new solution to the population if better
                    x = self.force_bounds(x, bounds)
                    new_fitness = population.problem.fitness(x)[0]
                    if new_fitness < fitness:
                        pop[id] = {'fit':new_fitness, 'x':x} 

            # update sensory modality: 
            if self.variant == "xaboa":
                # update sensor modality using a non-linear update rule according to [Zhang et al. 2020]
                (a0, a1) = (0.1, 0.3)
                it = (self.current_iteration/self.max_iterations)**2
                self.c = a0 - (a0-a1)*math.sin(math.pi/self.mu*it)
            else:
                # update sensor modality according to the classic linear rule according to [Arora et al. 2016]
                self.c += 0.025 / (self.c * self.max_iterations)

            # calculate fitness improvemnt and save log
            improvemnt =  population.champion_f[0] - old_best_fit[0]
            self.save_log(i+1, population.problem.get_fevals(), 
                population.champion_f[0], improvemnt)

        # update the population
        for i in range(len(solutions_IDs)):
            id = solutions_IDs[i]
            population.set_xf(i, pop[id]['x'], [pop[id]['fit']])

        return population
    
    def set_verbosity(self, l):
        """
        Set verbosity level
        """
        if l > 0:
            self.verbosity_level = int(l)
            print("\n{:^7}{:^7}{:>15}{:>15}".format("Gen", "Fevals", "Fbest", "Improv"))
    
    def get_name(self):
        if self.variant == "xboa":
            name = "xBOA: Crossover Butterfly Optimization Algorithm (UDA)"
        else:
            name = "xABOA: Crossover Adaptative Butterfly Optimization Algorithm (UDA)"
        return name
    
    def get_extra_info(self):
        return "\tSensor modality (C): {}\n\t\tPower exponent (a): {}\
                \n\t\tSwitch Probability (p): {}\n\t\tVerbosity level (p): {}".format(
                self.c, self.a, self.p, self.verbosity_level)

    def get_log(self):
        """
        Return the best fitness log according to the verbosity level
        """
        return self.log

    def save_log(self, iteration, fevals, fbest, improvemnt):
        """
        Archive and print logs
        """
        if self.verbosity_level > 0 and iteration % self.verbosity_level == 0:
            self.log.append([iteration, fevals, fbest, improvemnt])
            print("{:^7}{:^7}{:>15}{:>15}".format(iteration, 
                fevals, round(fbest, 7), round(improvemnt, 7)))

    def force_bounds(self, x, bounds):
        """  
        Force solution genes to be within lower & upper bounds
        """
        for k in range(len(x)):
            if x[k] < bounds[0][k]:
                x[k] = bounds[0][k]
            elif x[k] > bounds[1][k]:
                x[k] = bounds[1][k]
        return x

    def set_iter(self, i):
        self.current_iteration = i
