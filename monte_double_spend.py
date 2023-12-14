# Monte Carlo simulation which calculates risk of a bitcoin payment being double spent based on its depth in the blockchain and the fraction of dishonest miner hashpower, with premining, assuming payment time is controlled by honest party
# Usage: python3 monte_double_spend.py -f 0.35 -d 62 -t 1000000

import sys
import math
import numpy as np
import random
import argparse

PREMINE_FACTOR = 30                                             # number of multiples of "depth" honest blocks mined during pre-mine period and post-payment period

# Main program
parser = argparse.ArgumentParser(description='Calculate probability of a successful bitcoin payment double spend attack based on fraction of dishonest miner hashpower and depth of payment, given timing of attack selected by honest party')
parser.add_argument('-f', dest='frac', help='fraction of hashpower that is dishonest')
parser.add_argument('-d', dest='depth', help='depth of payment in blockchain (in blocks)')
parser.add_argument('-t', dest='trials', help='number of Monte Carlo trials')
args = parser.parse_args()
dishonest_prob = float(args.frac)
depth = int(args.depth)
trials = int(args.trials)
honest_prob = 1.0 - dishonest_prob
random_generator = random.Random()
random_generator.seed(1000+trials)
successes = 0.0                                                 # number of double-spend attack successes
blocks = PREMINE_FACTOR * depth
for trial in range(trials):                                     # perform "trials" Monte Carlo trials
    honest_block = 0                                            # block number of last block mined by honest miners
    dishonest_block = 0                                         # block number of last block mined by dishonest miners
    while (honest_block < blocks):                              # simulate pre-mine period
        if (random_generator.random() < dishonest_prob):
            dishonest_block += 1
        else:
            honest_block += 1
            if (dishonest_block < honest_block):
                dishonest_block = honest_block
    while (honest_block < blocks + depth):                      # simulate payment period
        if (random_generator.random() < dishonest_prob):
            dishonest_block += 1
        else:
            honest_block += 1
    if (dishonest_block >= honest_block):
        successful_attack = True
    else:
        successful_attack = False
    while ((not successful_attack) and (honest_block < 2 * blocks + depth)):         # simulate post-payment period
        if (random_generator.random() < dishonest_prob):
            dishonest_block += 1
            if (dishonest_block >= honest_block):
                successful_attack = True
        else:
            honest_block += 1
    if (successful_attack):
        successes += 1
success_prob = successes / trials
print('frac:', dishonest_prob, 'depth:', depth, 'trials:', trials, 'success_prob:', success_prob)
