"""haakon8855"""

from matplotlib import pyplot as plt

from configuration import Config
from reinforcement_learning import ReinforcementLearning
from pole_balancing import PoleBalancing
from hanoi import Hanoi
from gambler import Gambler


class GPRLSystem:
    """
    General purpose reinforcement learning system
    """
    def __init__(self, config_file: str):
        self.config = Config.get_config(config_file)
        conf_globals = self.config['GLOBALS']
        self.problem = conf_globals['problem']
        self.episodes = int(conf_globals['episodes'])
        self.max_steps = int(conf_globals['max_steps'])
        self.table_critic = conf_globals['table_critic'] == 'true'
        self.epsilon = float(conf_globals['epsilon'])
        self.lrate = float(conf_globals['lrate'])
        self.trace_decay = float(conf_globals['trace_decay'])
        self.drate = float(conf_globals['drate'])

        if self.problem == 'cartpole':
            self.sim_world = PoleBalancing()
        elif self.problem == 'hanoi':
            num_pegs = int(conf_globals['num_pegs'])
            num_discs = int(conf_globals['num_discs'])
            self.sim_world = Hanoi(num_pegs=num_pegs, num_discs=num_discs)
        elif self.problem == 'gambler':
            win_prob = float(conf_globals['win_prob'])
            self.sim_world = Gambler(win_prob=win_prob)

        self.reinforcement_learner = ReinforcementLearning(
            self.sim_world, self.episodes, self.max_steps, self.table_critic,
            self.epsilon, self.lrate, self.trace_decay, self.drate)

        if self.problem == 'gambler':
            self.before = True
            self.visualize_gambler_policy()

    def run(self):
        """
        Runs the reinforcement learning system on the specified problem/simworld
        """
        self.reinforcement_learner.train()
        if self.problem == 'gambler':
            self.visualize_gambler_policy()

    def visualize_gambler_policy(self):
        """
        Visualizes the policy for the gambler simworld.
        """
        min_state = 1
        max_state = self.sim_world.max_coins
        states = list(range(min_state, max_state))
        wagers = []
        for state in states:
            wagers.append(self.reinforcement_learner.get_action((state, )))
        plt.plot(states, wagers)
        if self.before:
            plt.savefig('plots/before.png')
            self.before = False
        else:
            plt.savefig('plots/after.png')
        plt.clf()


if __name__ == "__main__":
    gprl = GPRLSystem("configs/config_pole.ini")
    # gprl = GPRLSystem("configs/config_hanoi.ini")
    # gprl = GPRLSystem("configs/config_gambler.ini")
    gprl.run()
