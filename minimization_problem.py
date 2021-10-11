#!/usr/bin/env python
import pygmo as pg

class MinimizationProblem:
    """
    Modelize the exploration problem to be solved by pygmo optimizers.
    """

    ###### Methods used by Pygmo ######

    def __init__(self, solution_size, lower_bound=None, upper_bound=None):
        """
        Create a pygmo problem object modelizing the exploration problem.
        
        Arguments: 
        - solution_size: size of individuals (number of genes)
        - lower_bound: minimum value for a gene. If None, no minimum value will be applied
        - upper_bound: maximum value for a gene. If None, no maximum value will be applied
        """
        # set problem dimession
        self.dim = solution_size   # indv is a flatten vector of x1,x2,x3...
        if lower_bound is not None:
            self.min_x = lower_bound
        if upper_bound is not None:
            self.max_x = upper_bound

        # instantiate a pygmo problem
        self.problem = pg.problem(self)

    def fitness(self, X):
        """
        Evaluates fitness of X, which is the sum of all elements of the vector X.

        Arguments:
        - X: vector solution (flatten vector of x1,x2,x3.. within lower & upper bounds)
        """
        fitness = sum(X)
        return [fitness]  # or use [-fitness] to transform into a maximization problem


    def get_bounds(self):
        """
        Set bounds for genes.
        In our problem genes are float numbers
        """
        return ([self.min_x] * self.dim, 
                [self.max_x] * self.dim)

    def get_nix(self):
        """
        Set number of integer variables in the solution (individual)
        Used to make the individuals use integers for waypoint coordinates instead of float values
        """
        return 0  # or use self.dim to force integer values

    def get_name(self):
        return "Minimization problem"

    def get_extra_info(self):
        return "Solutions lenght: " + str(self.dim)
