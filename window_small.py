# Calculates probability of a window of "w" consecutive blocks having fewer than "b" honest blocks, based on the fraction of dishonest miners and values of "w" and "b"
# Only usable for small values of "w" (less than 5)
# Usage: python3 window_small.py -f 0.40 -w 4

import sys
import argparse

class Combinations(object):                                     # calculates n choose m
    def __init__(self,
                 max_n):                                        # maximum number of items selected from
      self.max_n = max_n
      self.value = [[1]]					# (0 choose 0) = 1
      for n in range(1, self.max_n+1):
          prev_values = self.value[n-1]                         # values for "n-1" items
          new_values = []                                       # values for "n" items
          new_values.append(1)                                  # 0 selections case
          for m in range(1, n):
              new_values.append(prev_values[m-1] + prev_values[m])
          new_values.append(1)                                  # "n" selections case
          self.value.append(new_values)                         # add newly-calculated values for "n" items

    def choose(self, n, m):                                     # return n choose m
        assert 0 <= m <= n
        assert n <= self.max_n
        return self.value[n][m]

class Window(object):                                           # calculates probability of a window of a given size having fewer than "b" honest blocks given fraction of dishonest miners
    def __init__(self,
                 w_log,                                         # base-4 logarithm of "w", which is size of window
                 dishonest_prob):                               # fraction of miners that are dishonest
        self.w_log = w_log
        self.w = 4 ** w_log
        self.q = dishonest_prob
        self.p = 1.0 - dishonest_prob
        self.combinations = Combinations(2*self.w)              # calculates (n choose m) for n <= 2*w

    def calc_few_honest_prob(self,                              # calculates probability of given window having fewer than "b" honest blocks
                             b_log):                            # base-4 log of "b", which is excess number of honest blocks within window
        b = 4 ** b_log
        success_prob = 0.0                                      # probability of fewer than "b" honest blocks in window
        # case 1: "w" honest blocks mined before "w - b + 1" dishonest blocks mined (ignoring pre-mine)
        for k in range(self.w - b + 1):                         # number of dishonest blocks mined when w honest blocks are first mined (ignoring pre-mine)
            case_choices = self.combinations.choose(self.w + k - 1, k)
            pq_powers = (self.p ** (k + b - 1)) * (self.q ** (self.w - b + 1))
                                                                # product of powers of p and q within summation
            success_case_prob = pq_powers
            pq_powers = pq_powers * self.q / self.p
            success_case_prob += (self.w - b - k + 1) * pq_powers
            pq_powers = pq_powers * self.q / self.p
            success_case_prob -= (self.w - b - k + 1) * pq_powers
            success_prob += case_choices * success_case_prob
        # case 2: "w - b + 1" dishonest blocks mined before "w" honest blocks mined (ignoring pre-mine)
        for k in range(self.w):                                 # number of honest blocks mined when "w - b + 1" dishonest blocks are first mined (ignoring pre-mine)
            case_choices = self.combinations.choose(self.w - b + k, k)
            pq_powers = (self.p ** k) * (self.q ** (self.w - b + 1))
            success_prob += case_choices * pq_powers
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
