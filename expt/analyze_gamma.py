import pickle as pkl
import os.path as op

with open(op.abspath('gamma_caliblo.pkl'), 'rb') as f:
    d_lo = pkl.load(f)

with open(op.abspath('gamma_calibhi.pkl'), 'rb') as f:
    d_hi = pkl.load(f)


last_low = d_lo.intensities[-20:]
last_high = d_hi.intensities[-20:]

print(last_low, last_high)
