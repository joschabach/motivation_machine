# -*- coding: utf-8 -*-

"""
Helper functions
"""

__author__ = 'joscha'
__date__ = '31.03.16'

import math
from configuration import Settings


def decay(value, decay_time=-1):
    """Perform an approximate logistic decay from 1 to 0 within time 'decay':
    we assume the sigmoidal function y = 1-1/(1+e^-12(x-1/2))"""

    if decay_time < 0: return value  # value does not decay

    interval = Settings.update_milliseconds / 1000

    x = get_inverted_decay_value(value) + interval/decay_time  # find out where we have been in the curve
    if x >= 1: return 0
    return (1 - 1 / (1 + math.exp(-12 * (x - 0.5))))


def get_inverted_decay_value(y):
    """Solves the logistic decay function y = 1-1/(1+e^-12(x-1/2)) for x,
    so we find out at which point we are in the curve"""

    if y >= 1: return 0.0
    if y <= 0: return 1.0
    return min(1, max(0, math.log((1.0 - y) / y) / 12.0 + 0.5))

def exponential_scaling(x, factor=6):
    """Scales a number between 0 and infinity to a number between 0 and 1."""
    return 1/-math.exp(x*factor)+1