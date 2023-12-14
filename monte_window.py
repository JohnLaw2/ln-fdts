# Monte Carlo simulation which calculates probability of a target window of "w" consecutive blocks having fewer than "b" honest blocks, based on the fraction of dishonest miners and values of "w" and "b"
# Usage: python3 monte_window.py -f 0.25 -w 2 -b 1 -t 1000000

import sys
import math
import numpy as np
import random
import argparse

PREMINE_FACTOR = 30                                             # number of multiples of "w" honest blocks mined during pre-mine period and post-window period

# Main program
parser = argparse.ArgumentParser(description='Calculate probability of a target window of w consecutive blocks having fewer than b honest blocks based on fraction of dishonest miners and values of w and b')
parser.add_argument('-f', dest='frac', help='fraction of hashpower that is dishonest')
parser.add_argument('-w', dest='window_log', help='base-4 logarithm of number of blocks in window')
parser.add_argument('-b', dest='b_log', help='base-4 logarithm of b, which is excess number of honest blocks in window')
parser.add_argument('-t', dest='trials', help='number of Monte Carlo trials')
args = parser.parse_args()
dishonest_prob = float(args.frac)
honest_prob = 1.0 - dishonest_prob
w_log = int(args.window_log)
w = 4 ** w_log
b_log = int(args.b_log)
b = 4 ** b_log
trials = int(args.trials)
random_generator = random.Random()
random_generator.seed(1000+trials)
premine_blocks = PREMINE_FACTOR * w
dishonest_windows = 0                                           # number of trials that resulted in a window without excess honest blocks
for trial in range(trials):                                     # perform "trials" Monte Carlo trials
    honest_block = 0                                            # block number of last block mined by honest miners
    dishonest_block = 0                                         # block number of last block mined by dishonest miners
    while (honest_block < premine_blocks):                      # simulate pre_mine period
        if (random_generator.random() < dishonest_prob):
            dishonest_block += 1
        else:
            honest_block += 1
            if (dishonest_block < honest_block):
                dishonest_block = honest_block
    honest_blocks_permanently_on_chain_in_window = 0            # number of honest blocks within given window that are permanently on-chain
    while (honest_block < premine_blocks + w):                  # simulate window period
        if (random_generator.random() < dishonest_prob):
            dishonest_block += 1
        else:
            honest_block += 1
            if (dishonest_block < honest_block):
                if (honest_blocks_permanently_on_chain_in_window < b - 1):
                    honest_blocks_permanently_on_chain_in_window += 1
                    dishonest_block = honest_block
    if (dishonest_block >= honest_block):
        dishonest_window = True
    else:
        dishonest_window = False
    while ((not dishonest_window) and (honest_block < 2 * premine_blocks + w)):         # simulate post-window period
        if (random_generator.random() < dishonest_prob):
            dishonest_block += 1
            if (dishonest_block >= honest_block):
                dishonest_window = True
        else:
            honest_block += 1
    if (dishonest_window):
        dishonest_windows += 1
print('frac:', dishonest_prob, 'w_log_base_4:', w_log, 'b_log_base_4:', b_log, 'trials:', trials, 'success_prob:', float(dishonest_windows) / float(trials))
