"""haakon8855"""

import random
from collections import defaultdict


class Actor:
    """
    Actor class for making actions in a simulated world.
    """

    def __init__(self, lrate, drate, trace_decay):
        self.policy = defaultdict(lambda: 0)
        self.state_action_eligibility = defaultdict(lambda: 0)
        self.lrate = lrate
        self.drate = drate
        self.trace_decay = trace_decay

    def initiate_eligibility(self):
        """
        Initiates the state-action eligibility.
        """
        self.state_action_eligibility = defaultdict(lambda: 0)

    def get_state_action_eligibility(self, state_action_pair):
        """
        Updates the eligibility for the given state_action_pair.
        """
        return self.state_action_eligibility[state_action_pair]

    def set_state_action_eligibility(self, state_action_pair, value):
        """
        Updates the eligibility for the given state_action_pair.
        """
        self.state_action_eligibility[state_action_pair] = value

    def get_state_action_value(self, state_action_pair):
        """
        Returns the value of the state and action pair.
        """
        return self.policy[state_action_pair]

    def set_state_action_value(self, state_action_pair, value):
        """
        Returns the value of the state and action pair.
        """
        self.policy[state_action_pair] = value

    def update_state_action_value(self, state_action_pair, td_error):
        """
        Updates the state action evaluation given a state action pair
        and td_error.
        """
        # Calculate the new policy value
        new_state_action_value = self.get_state_action_value(
            state_action_pair
        ) + self.lrate * td_error * self.get_state_action_eligibility(
            state_action_pair)
        # Store it in the policy table
        self.set_state_action_value(state_action_pair, new_state_action_value)

    def update_state_action_eligibility(self, state_action_pair):
        """
        Updates the state action eligibility given a state action pair.
        """
        # Calculate the new eligibility value
        new_state_action_eligibility = (
            self.drate * self.trace_decay *
            self.get_state_action_eligibility(state_action_pair))
        # Store it in the eligibility table
        self.set_state_action_eligibility(state_action_pair,
                                          new_state_action_eligibility)

    def get_proposed_action(self, do_argmax, state, possible_actions):
        """
        Returns the proposed action given a state and its possible actions.
        A parameter 'do_argmax' is also specified denoting whether the actor
        should return the action with greatest value or a random action.
        """
        if not do_argmax:
            # Return random action
            return random.choice(possible_actions)
        # Else, return the action with the best policy value
        best_action = []
        best_state_action_value = float('-inf')
        for action in possible_actions:
            state_action_pair = (*state, action)
            state_action_value = self.get_state_action_value(state_action_pair)
            if state_action_value > best_state_action_value:
                best_action = [action]
                best_state_action_value = state_action_value
            elif best_state_action_value == state_action_value:
                best_action.append(action)
        return random.choice(best_action)
