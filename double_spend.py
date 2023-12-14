# Calculates risk of a bitcoin payment being double spent based on its depth in the blockchain and the fraction of dishonest miner hashpower, with premining, assuming payment time is controlled by honest party
# Usage: python3 double_spend.py -f 0.45 -d 589

import sys
import argparse

class Binomial(object):                                         # binomial distribution values
    def __init__(self,
                 prob,                                          # probability of success per trial
                 trials):                                       # number of trials
      self.prob = prob
      self.trials = trials
      self.fail = 1.0 - self.prob                               # probability of failure per trial
      self.value = [[1.0]]                                      # self.value[y][x] gives prob of exactly x successes in y trials
      for trial in range(1, trials+1):
          prev_values = self.value[trial-1]                     # values for "trial-1" trials
          new_values = []                                       # values for "trial" trials
          new_values.append(prev_values[0] * self.fail)         # 0 successes case
          for successes in range(1, trial):
              new_values.append((prev_values[successes-1] * self.prob) + (prev_values[successes] * self.fail))
          new_values.append(prev_values[trial-1] * self.prob)   # "trial" successes case
          self.value.append(new_values)                         # add newly-calculated values for "trial" trials

    def get_value(self, successes, trials):                     # return probability of given number of successes for given number of trials
        assert 0 <= successes <= trials
        assert trials <= self.trials
        return self.value[trials][successes]

class DoubleSpend(object):                                      # calculates probability of a double spend given depth and fraction of dishonest miners
    def __init__(self,
                 max_depth,                                     # maximum depth of spend attempting to be double spent
                 dishonest_frac):                               # fraction of miners that are dishonest
        self.max_depth = max_depth
        self.dishonest_frac = dishonest_frac
        self.honest_frac = 1.0 - dishonest_frac
        self.ratio = self.dishonest_frac / self.honest_frac     # ratio of dishonest to honest hashpower; is q/p value in gambler's ruin problem
        self.binomial = Binomial(self.honest_frac, 2*max_depth) # calculates probability of each number of honest blocks mined within first 2*max_depth blocks

    def calc_double_spend(self,                                 # calculates probability of given spend being double spent given its depth
                         depth):                                # depth of spend attempting to be double spent
        premine_prob = 0.0                                      # probability of successful double spend attack (including pre-mining)
        for k in range(depth):
                                                                # number of dishonest blocks mined when depth honest blocks are first mined (ignoring pre-mine)
            node_prob = self.binomial.get_value(k, depth - 1 + k) * self.dishonest_frac
            deficit = depth - k
            premine_case_prob = 2.0 + deficit * self.ratio - deficit * (self.ratio ** 2)
            premine_prob += node_prob * premine_case_prob
        print(f'frac: {dishonest_frac:.2f} depth: {depth:4d} prob: {premine_prob:13.6e}')

 
# Main program
parser = argparse.ArgumentParser(description='Calculate probability of a successful bitcoin payment double spend attack based on fraction of dishonest miner hashpower and depth of payment, given timing of attack selected by honest party')
parser.add_argument('-f', dest='frac', help='fraction of hashpower that is dishonest')
parser.add_argument('-d', dest='depth', help='maximum depth of spend')
args = parser.parse_args()
dishonest_frac = float(args.frac)
max_depth = int(args.depth)
d = DoubleSpend(max_depth, dishonest_frac)
for depth in range(1, max_depth+1):
    d.calc_double_spend(depth)
