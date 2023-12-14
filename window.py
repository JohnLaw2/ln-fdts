# Calculates probability of a window of "w" consecutive blocks having fewer than "b" honest blocks, based on the fraction of dishonest miners and values of "w" and "b"
# Usage: python3 window.py -f 0.40 -w 6

import sys
import argparse

class Binomial(object):                                         # calculates binomial distribution probabilities
    def __init__(self,
                 prob,                                          # probability of success per trial
                 max_trials):                                   # maximum number of trials
      self.prob = prob
      self.max_trials = max_trials
      self.fail = 1.0 - self.prob                               # probability of failure per trial
      self.value = [[1.0]]                                      # self.value[y][x] gives prob of exactly x successes in y trials
      for trial in range(1, max_trials+1):
          prev_values = self.value[trial-1]                     # values for "trial-1" trials
          new_values = []                                       # values for "trial" trials
          new_values.append(prev_values[0] * self.fail)         # 0 successes case
          for successes in range(1, trial):
              new_values.append((prev_values[successes-1] * self.prob) + (prev_values[successes] * self.fail))
          new_values.append(prev_values[trial-1] * self.prob)   # "trial" successes case
          self.value.append(new_values)                         # add newly-calculated values for "trial" trials

    def get_value(self, successes, trials):                     # return probability of given number of successes for given number of trials
        assert 0 <= successes <= trials
        assert trials <= self.max_trials
        return self.value[trials][successes]

class Window(object):                                           # calculates probability of a window of a given size having fewer than "b" honest blocks given fraction of dishonest miners
    def __init__(self,
                 w_log,                                         # base-4 logarithm of "w", which is size of window
                 dishonest_prob):                               # fraction of miners that are dishonest
        self.w_log = w_log
        self.w = 4 ** w_log
        self.q = dishonest_prob
        self.p = 1.0 - dishonest_prob
        self.binomial = Binomial(self.p, 2*self.w)              # calculates binomial distribution probabilities for <= 2*w trials

    def calc_few_honest_prob(self,                              # calculates probability of given window having fewer than "b" honest blocks
                             b_log):                            # base-4 log of "b", which is excess number of honest blocks within window
        b = 4 ** b_log
        success_prob = 0.0                                      # probability of fewer than "b" honest blocks in window
        # case 1: "w" honest blocks mined before "w - b + 1" dishonest blocks mined (ignoring pre-mine)
        for k in range(self.w - b + 1):                         # number of dishonest blocks mined when w honest blocks are first mined (ignoring pre-mine)
            binomial_prob = self.binomial.get_value(self.w - 1, self.w + k - 1)
            pq_powers = self.q * ((self.q / self.p) ** (self.w - k - b))
                                                                # product of powers of p and q within summation
            success_case_prob = pq_powers
            pq_powers = pq_powers * self.q / self.p
            success_case_prob += (self.w - b - k + 1) * pq_powers
            pq_powers = pq_powers * self.q / self.p
            success_case_prob -= (self.w - b - k + 1) * pq_powers
            success_prob += binomial_prob * success_case_prob
        # case 2: "w - b + 1" dishonest blocks mined before "w" honest blocks mined (ignoring pre-mine)
        for k in range(self.w):                                 # number of honest blocks mined when "w - b + 1" dishonest blocks are first mined (ignoring pre-mine)
            binomial_prob = self.binomial.get_value(k, self.w - b + k)
            pq_powers = self.q
            success_prob += binomial_prob * pq_powers
        print(f'q: {dishonest_prob:.2f} w_log_base_4: {self.w_log:2d} b_log_base_4: {b_log:2d} success_prob: {success_prob:13.6e}')

 
# Main program
parser = argparse.ArgumentParser(description='Calculate probability of a target window of w consecutive blocks having fewer than b honest blocks based on fraction of dishonest miners and values of w and b')
parser.add_argument('-f', dest='frac', help='fraction of hashpower that is dishonest')
parser.add_argument('-w', dest='window_log', help='base-4 logarithm of number of blocks in window')
args = parser.parse_args()
dishonest_prob = float(args.frac)
w_log = int(args.window_log)
window = Window(w_log, dishonest_prob)
for b_log in range(w_log+1):
    window.calc_few_honest_prob(b_log)
