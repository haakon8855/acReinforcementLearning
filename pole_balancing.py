"""Haakoas"""

from random import uniform
import numpy as np
from matplotlib import pyplot as plt


class PoleBalancing:
    """
    PoleBalancing class for holding the simulated world for balancing a pole
    on a cart.
    """

    def __init__(self,
                 length=0.5,
                 mass_p=0.1,
                 gravity=-9.8,
                 tau=0.02,
                 max_steps=300):
        # Constants:
        self.length = length  # m
        self.mass_p = mass_p  # kg
        self.gravity = gravity  # m/s^2
        self.tau = tau  # s, timestep length tau
        self.mass_c = 1  # kg
        self.force = 10  # N
        self.max_angle = 0.21  # radians
        self.max_x_pos = 2.4  # m
        self.steps = max_steps  # num of timesteps in episode
        # State parameters:
        self.angle = 0
        self.angle_vel = 0
        self.x_pos = 0
        self.x_vel = 0
        self.current_step = 0
        self.balancing_failed = False
        self.cart_exited = False
        self.historic_angle = []
        self.best_history = []
        self.best_game_length = float('-inf')
        self.historic_game_length = []
        self.produce_initial_state()

    def produce_initial_state(self):
        """
        Initializes the sim world to its initial state where the cart has
        zero velocity, the pole has zero angular velocity, the cart is placed
        in the middle of the world and the angle of the pole is randomized
        between the lower and upper bound for the angle.
        """
        self.angle = uniform(-self.max_angle, self.max_angle)
        self.angle_vel = 0
        self.x_pos = 0
        self.x_vel = 0
        self.current_step = 0
        self.balancing_failed = False
        self.cart_exited = False
        self.historic_angle = [self.angle]
        return self.get_current_state()

    def update(self, action: bool):
        """
        Advances the sim world by one timestep.
        Parameter means to apply F if True and -F if False, i.e. either go right
        or go left.
        """
        self.current_step += 1
        next_state = self.get_child_state(action)
        self.x_pos = next_state[0]
        self.x_vel = next_state[1]
        self.angle = next_state[2]
        self.angle_vel = next_state[3]

        self.historic_angle.append(self.angle)

        # Update state values with the newly updated ones
        if not self.balancing_failed:
            if np.abs(self.angle) >= self.max_angle:
                # If pole is outside allowed range
                self.balancing_failed = True
        if not self.cart_exited:
            if np.abs(self.x_pos) >= self.max_x_pos:
                # If cart is outside allowed range
                self.cart_exited = True
        if self.is_current_state_failed_state():
            # Give negative reward if agent fails
            return -1000
        # Give positive reward if agent does not fail in current step
        return 1

    def get_child_state(self, action: bool, rounded=False):
        """
        Returns the child state if given action is performed.
        """
        # Set the bangbang-force, either positive or negative F
        bb_force = [-self.force, self.force][action]
        # Calculate double derivatives
        angle_acc = self.update_angle_acc(bb_force)
        x_acc = self.update_x_acc(bb_force, angle_acc)
        # Calculate state variables
        x_pos = self.x_pos + self.tau * self.x_vel
        x_vel = self.x_vel + self.tau * x_acc
        angle = self.angle + self.tau * self.angle_vel
        angle_vel = self.angle_vel + self.tau * angle_acc
        if rounded:
            return PoleBalancing.round_state((x_pos, x_vel, angle, angle_vel))
        return x_pos, x_vel, angle, angle_vel

    def update_angle_acc(self, bb_force):
        """
        Updates the acceleration of the angle.
        """
        numerator_fraction = (np.cos(self.angle) *
                              (-bb_force - self.mass_p * self.length *
                               (self.angle_vel**2) * np.sin(self.angle))) / (
                                   self.mass_p + self.mass_c)
        numerator = self.gravity * np.sin(self.angle) + numerator_fraction
        denominator = self.length * (4 / 3 - (self.mass_p *
                                              (np.cos(self.angle)**2)) /
                                     (self.mass_p + self.mass_c))
        return numerator / denominator

    def update_x_acc(self, bb_force, angle_acc):
        """
        Updates the acceleration of the cart.
        """
        numerator = bb_force + self.mass_p * self.length * (
            (self.angle_vel**2) * np.sin(self.angle) -
            angle_acc * np.cos(self.angle))
        denominator = self.mass_p + self.mass_c
        return numerator / denominator

    def get_current_state(self):
        """
        Returns the one-hot-encoded representation of the
        current state of the sim world.
        """
        return PoleBalancing.round_state(
            (self.x_pos, self.x_vel, self.angle, self.angle_vel))

    def is_current_state_final_state(self):
        """
        Returns whether the current state is a final state.
        Returns True if current step is more than the number of steps to success
        so long as the cart never exited the area during the entire episode and
        as long as the pole never went outside the permitted angle range during
        the entire episode.
        """
        return (self.current_step >= self.steps) and (
            not self.cart_exited) and (not self.balancing_failed)

    def is_current_state_failed_state(self):
        """
        Returns whether the current state is a failed state or not.
        Returns True if the cart has previously exited the area or the pole's
        angle has previously went over its permitted maximum angle.
        """
        return self.cart_exited or self.balancing_failed

    def get_legal_actions(self, state=None):
        """
        Returns the legal actions from the current state. The action (boolean)
        represents whether the cart will be pushed to the right or not. If True
        it will be pushed to the right, if False it will be pushed to the left.
        """
        if state is None:
            pass
        return False, True

    def plot_history_best_episode(self):
        """
        Plots the historic angle of the pole.
        """
        plt.plot(self.best_history)
        plt.show()

    def plot_historic_game_length(self):
        """
        Plots the historic number of steps for each game.
        """
        plt.plot(self.historic_game_length)
        plt.show()

    def store_game_length(self):
        """
        Stores the game length in a list to plot later.
        """
        if self.current_step > self.best_game_length:
            self.best_history = self.historic_angle.copy()
            self.best_game_length = self.current_step
        self.historic_game_length.append(self.current_step)

    def get_state_length(self):
        """
        Returns the length of the one-hot encoded state representation vector.
        """
        return len(self.get_current_state())

    def __str__(self):
        outstring = ""
        outstring += f"\nx_pos: {self.x_pos}"
        outstring += f"\nx_vel: {self.x_vel}"
        outstring += f"\nangle: {self.angle}"
        outstring += f"\nangle_vel: {self.angle_vel}"
        return outstring

    @staticmethod
    def round_state(state):
        """
        Rounds the state variables and returns the result
        state = x_pos, x_vel, angle, angle_vel
        """
        # Round values and one-hot-encode them
        state_oh = PoleBalancing.one_hot_state(
            (np.sign(state[0]), round(state[1]), np.sign(state[2]),
             round(state[3])))
        return tuple(state_oh)

    @staticmethod
    def one_hot_state(rounded_state):
        """
        Returns the one-hot encoding of the state representatinon given.
        """
        # Get one-hot-encoded vectors for each state variable.
        # Second parameter is maximum absolute value of that variable.
        x_pos_oh = PoleBalancing.one_hot_variable(rounded_state[0], 1)
        x_vel_oh = PoleBalancing.one_hot_variable(rounded_state[1], 3)
        angle_oh = PoleBalancing.one_hot_variable(rounded_state[2], 1)
        angle_vel_oh = PoleBalancing.one_hot_variable(rounded_state[3], 3)
        return x_pos_oh + x_vel_oh + angle_oh + angle_vel_oh

    @staticmethod
    def one_hot_variable(rounded_var: int, abs_max: int):
        """
        Returns the one-hot encoding of one rounded state variable
        """
        vector = [0] * (abs_max * 2 + 1)
        for i, val in enumerate(range(-abs_max, abs_max + 1)):
            if rounded_var <= val:
                vector[i] = 1
                return vector
        vector[-1] = 1
        return vector
