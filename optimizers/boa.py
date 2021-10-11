#!/usr/bin/env python
import random
import math

class BOA:
    """
    BOA: Butterfly Optimization Algorithm.

    Implements the BOA algorithm as a Pygmo UDA
    """
    def __init__(self, gen=1, c=0.01, a=0.1, p=0.8, mu=2, max_gen=1, variant="BOA"):
        """
        Creates a Pygmo UDA implementing Butterfly Optimization Algorithm

        Arguments:
        - gen: number of generations (iterations) to evolve the population
        - c: Sensory modality
        - a: Power exponent
        - p: Switch probability
        - mu: Used for ABOA variant only (for more information see [Zhang et al. 2020])
        - max_gen: Max number of generations (used for updating the sensory modality)
        - variant: Select which variant to execute from the following cases:
          1. "BOA": The standard BOA algorithm from [Arora et al. 2019] & [Arora et al. 2016]
          2. "mBOA": BOA with intensive search from [Arora et al. 2018]
          3. "ABOA": BOA with a non-linear update rule for the sensory modality from [Zhang et al. 2020]
        
        Implementation notes:
        1. Updating c-parameter:
            In [Arora et al. 2019] pseudo-code, authors change the value of "a" parameter (power 
            exponent), but in their matlab code they update the value of "c" parameter (sensory 
            modality), such as explained in [Arora et al. 2016].
        2. BOA update rules:
            In the paper, the updating rule is supposed to be (r² * best_sol - x), but in authors
            code they generate two separate random numbers (r1*r2 * best_sol -x). 
        3. Switch probability:
            In the paper, the switch condition is supposed to execute when a random number r < p,
            but in authors code they use r > p.
        In our code, we use the same rules as in the authors code, assuming that the pseudo-code
        in the papers might be outdated.
        
        References:
        - [Arora et al. 2016] "An Improved Butterfly Optimization Algorithm for Global Optimization"
        - [Arora et al. 2018] "A modified butterfly optimization algorithm for mechanical design optimization problems"
        - [Arora et al. 2019] "Butterfly optimization algorithm: a novel approach for global optimization"
        - [Zhang et al. 2020] "A chaotic hybrid butterfly optimization algorithm with particle swarm optimization for high-dimensional optimization problems"
        """
        self.iterations = gen if gen > 1 else 1
        self.c = c
        self.a = a
        self.p = p if p>=0 and p<=1 else 0.8
        self.mu = mu
        self.variant = variant.lower()
        if self.variant not in ["boa", "mboa", "aboa"]:
            self.variant = "boa"
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
        pop = dict()
        for id, fit, x in zip(solutions_IDs, solutions_fitness, solutions_x):
            pop[id] = {'fit':fit, 'x':x}

        for i in range(self.iterations):
            old_best_fit = pop[best_id]['fit']
            for id in solutions_IDs:
                x = pop[id]['x']
                
                # compute frangrace
                fitness = pop[id]['fit'][0]
                if fitness > 0:
                    f = self.c * (fitness ** self.a)
                else:
                    # multiply by -1 to avoid getting a complex result when calculating exponent
                    f = self.c * ((-fitness) ** self.a)

                # move butterflies
                r1 = random.random()
                r2 = random.random()
                if random.random() > self.p:
                    # move toward best butterfly
                    x += f * (r1 * r2 * pop[best_id]['x'] - x)
                else:
                    # find random butterfly in the neighbourhood
                    j = random.choice(list(pop))
                    k = random.choice(list(pop))
                    x += f * (r1 * r2 * pop[j]['x'] - pop[k]['x'])

                # force solution bounds and evaluate the fitness
                x = self.force_bounds(x, bounds)
                new_fitness = population.problem.fitness(x)

                # intensive exploitation search [Arora et al. 2018]
                if self.variant == "mboa":
                    if random.random() < self.p:
                        r1 = random.random()
                        r2 = random.random()
                        x2 = pop[best_id]['x'] + (r1-r2)* pop[best_id]['x']
                        x2 = self.force_bounds(x2, bounds)
                        new_fitness_x2 = population.problem.fitness(x2)
                        if new_fitness_x2 < new_fitness:
                            x = x2
                            new_fitness = new_fitness_x2

                # evaluate new butterfly and update the population if needed
                if new_fitness < fitness:
                    pop[id] = {'fit':new_fitness, 'x':x} 
                if new_fitness < pop[best_id]['fit']:
                    best_id = id

            # update sensory modality: 
            if self.variant == "aboa":
                # update sensor modality using a non-linear update rule according to [Zhang et al. 2020]
                (a0, a1) = (0.1, 0.3)
                it = (self.current_iteration/self.max_iterations)**2
                self.c = a0 - (a0-a1)*math.sin(math.pi/self.mu*it)
            else:
                # update sensor modality according to the classic linear rule according to [Arora et al. 2016]
                self.c += 0.025 / (self.c * self.max_iterations)
            
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
        if self.variant == "boa":
            name = "BOA: Butterfly Optimization Algorithm (UDA)"
        elif self.variant == "aboa":
            name = "ABOA: Adaptative Butterfly Optimization Algorithm (UDA)"
        else:
            name = "mBOA: Modified Butterfly Optimization Algorithm (UDA)"
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
