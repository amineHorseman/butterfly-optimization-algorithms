#!/usr/bin/env python
import random

class SABOA:
    """
    SABOA: Self Adaptative Butterfly Optimization Algorithm.

    Implements the SABOA algorithm as a Pygmo UDA
    """
    def __init__(self, gen=1, p=0.8, max_gen=1):
        """
        Creates a Pygmo UDA implementing Self-Adaptative Butterfly Optimization Algorithm

        References:
        - [Fan et al. 2020] "A Self-Adaption Butterfly Optimization Algorithm for Numerical Optimization Problems"
        - [Arora et al. 2019] "Butterfly optimization algorithm: a novel approach for global optimization"
        
        Arguments:
        - gen: number of generations (iterations) to evolve the population
        - p: Switch probability
        - max_gen: max number of generations (used for updating the sensory modality)
        """
        self.iterations = gen if gen > 1 else 1
        self.p = p if p>=0 and p<=1 else 0.8
        self.max_iterations = max_gen
        self.verbosity_level = 0
        self.log = []
        self.current_iteration = 1

    def evolve(self, population):
        """
        Evolve the population for a certain number of iterations (specified 
        during initiatlization)
        """
        # extract population individuals
        bounds = population.problem.get_bounds()
        solutions_x = population.get_x()
        solutions_fitness = population.get_f()
        solutions_IDs = population.get_ID()
        best_id = solutions_IDs[population.best_idx()]
        worst_id = solutions_IDs[population.worst_idx()]
        pop = dict()
        for id, fit, x in zip(solutions_IDs, solutions_fitness, solutions_x):
            pop[id] = {'fit':fit, 'x':x}

        for i in range(self.iterations):
            old_best_fit = pop[best_id]['fit']
            for id in solutions_IDs:
                x = pop[id]['x']
                
                # compute frangrace
                u = random.random()
                f = u * (1 - self.current_iteration/self.max_iterations)

                # move butterflies
                if random.random() > self.p:
                    # move toward best butterfly
                    x += pop[best_id]['x'] + (x - pop[best_id]['x']) * f
                else:
                    # find random butterfly in the neighbourhood
                    x = 0.5 * (pop[best_id]['x'] + pop[worst_id]['x']) * f

                # force solution bounds and evaluate the fitness
                x = self.force_bounds(x, bounds)
                new_fitness = population.problem.fitness(x)

                # evaluate new butterfly and update the population if needed
                if new_fitness < pop[id]['fit'][0]:
                    pop[id] = {'fit':new_fitness, 'x':x} 
                if new_fitness < pop[best_id]['fit']:
                    best_id = id
                if new_fitness > pop[worst_id]['fit']:
                    worst_id = id
            
            # calculate fitness improvemnt and save log
            improvemnt =  pop[best_id]['fit'][0] - old_best_fit[0]
            self.save_log(i+1, population.problem.get_fevals(), 
                pop[best_id]['fit'][0], improvemnt)

        # update the population
        for i in range(len(solutions_IDs)):
            id = solutions_IDs[i]
            population.set_xf(i, pop[id]['x'], pop[id]['fit'])

        return population
    
    def set_verbosity(self, l):
        """
        Set verbosity level
        """
        if l > 0:
            self.verbosity_level = int(l)
            print("\n{:^7}{:^7}{:>15}{:>15}".format("Gen", "Fevals", "Fbest", "Improv"))
    
    def get_name(self):
        return "SABOA: Self-Adaptative Butterfly Optimization Algorithm (UDA)"
    
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