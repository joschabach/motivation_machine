# -*- coding: utf-8 -*-

"""
Helper functions
"""

__author__ = 'joscha'
__date__ = '31.03.16'

import math
from configuration import Settings


def decay(value, decay=-1):
    """Perform an approximate logistic decay from 1 to 0 within time 'decay':
    we assume the sigmoidal function y = 1-1/(1+e^-12(x-1/2))"""

    if decay < 0: return value  # value does not decay

    interval = Settings.update_milliseconds / 1000

    x = get_inverted_decay_value(value) + interval / decay  # find out where we have been in the curve
    if x >= 1: return 0
    return 1 - 1 / (1 + math.exp(-12 * (x - 0.5)))


def get_inverted_decay_value(y):
    """Solves the logistic decay function y = 1-1/(1+e^-12(x-1/2)) for x,
    so we find out at which point we are in the curve"""

    if y >= 1: return 0.0
    if y <= 0: return 1.0
    return min(1, max(0, math.log((1 - y) / y) / 6 + 0.5))
