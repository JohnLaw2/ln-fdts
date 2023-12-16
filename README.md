# ln-fdts
Proposal to change Bitcoin's consensus rules to support Feerate-Dependent Timelocks (FDTs).
In addition, an exact analysis of the risk of a double spend attack that corrects an error in the original Bitcoin whitepaper.
See fdts_v1.1.pdf.

Also, see the following python3 programs:

double_spend.py: exact analysis of the risk of a double spend attack

monte_double_spend.py: Monte Carlo simulation that estimates the risk of a double spend attack and can be used to verify double_spend.py

window.py: exact analysis of the risk of an FDT attack

window_small.py: same as window.py, but for small windows (this program has the advantage of directly implementing the formulas given in the paper fdts_v1.0.pdf)

monte_window: Monte Carlo simulation that estimates the risk of an FDT attack and can be used to verify window.py
