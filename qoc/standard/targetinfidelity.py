"""
targetinfidelity.py - a module for defining the target fidelity cost function
"""

import autograd.numpy as anp
import numpy as np

from qoc.models import Cost
from qoc.util import conjugate_transpose

class TargetInfidelity(Cost):
    """a class to encapsulate the target infidelity cost function
    Fields:
    alpha :: float - the wieght factor for this cost
    dcost_dparams :: (params :: numpy.ndarray, states :: numpy.ndarray, step :: int)
                      -> dcost_dparams :: numpy.ndarray
        - the gradient of the cost function with respect to the parameters
    dcost_dstates :: (params :: numpy.ndarray, states :: numpy.ndarray, step :: int)
                      -> dcost_dstates :: numpy.ndarray
        - the gradient of the cost function with respect to the states
    name :: str - a unique identifier for this cost
    requires_step_evaluation :: bool - True if the cost needs
        to be computed at each optimization time step, False
        if it should be computed only at the final optimization
        time step
    state_normalization_constant :: float - value used to compute
        the cost averaged over the states
    target_states_dagger :: numpy.ndarray - the hermitian conjugate of
        the target states
    """
    name = "target_infidelity"
    requires_step_evaluation = False


    def __init__(self, target_states, alpha=1.):
        """
        See class definition for parameter specification.
        target_states :: numpy.ndarray - an array of states
            that correspond to the target state for each of the initial states
            used in optimization
        """
        super().__init__(alpha)
        self.target_states_dagger = conjugate_transpose(anp.stack(target_states))
        self.state_normalization_constant = len(target_states)
        # This cost function does not make use of parameter penalties.
        self.dcost_dparams = (lambda params, states, step:
                              np.zeros_like(params))


    def cost(self, params, states, step):
        """
        Args:
        params :: numpy.ndarray - the control parameters for all time steps
        states :: numpy.ndarray - an array of the states evolved to
            the current time step
        step :: int - the pulse time step
        Returns:
        cost :: float - the penalty
        """
        fidelity = anp.sum(anp.square(anp.abs(anp.matmul(self.target_states_dagger,
                                                         states)[:,0,0])), axis=0)
        infidelity = 1 - (fidelity / self.state_normalization_constant)
        print("infidelity:{}"
              "".format(infidelity))
        return self.alpha * infidelity

