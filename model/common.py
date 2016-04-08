# -*- coding: utf-8 -*-

"""
Helper functions
"""

__author__ = 'joscha'
__date__ = '31.03.16'

import math
from configuration import Settings


def clip(value, min_value=0.0, max_value=1.0):
    """Make some formulas more readable; clip limits a value to a range, typically between 0 and 1"""
    return min(max_value, max(value, min_value))


def decay(previous_value, decay_time=-1):
    """Perform an approximate logistic decay from 1 to 0 within time 'decay':
    we assume the sigmoidal function y = 1-1/(1+e^-12(x-1/2))"""

    if decay_time < 0: return previous_value  # value does not decay

    interval = Settings.update_milliseconds / 1000

    x = get_inverted_decay_value(previous_value) + interval/decay_time  # find out where we have been in the curve
    if x >= 1: return 0
    return 1 - 1 / (1 + math.exp(-12 * (x - 0.5)))


def get_inverted_decay_value(y):
    """Solves the logistic decay function y = 1-1/(1+e^-12(x-1/2)) for x,
    so we find out at which point we are in the curve"""
    if y >= 1: return 0.0
    if y <= 0: return 1.0
    return min(1, max(0, math.log((1.0 - y) / y) / 12.0 + 0.5))


def exponential_scaling(x, factor=6):
    """Scales a number between 0 and infinity to a number between 0 and 1."""
    return 1-math.exp(-max(0, x)*factor)


def calculate_signal_strength(step, total_amount = 1.0, duration = 3.5):
    """This function computes the amount of a signaling component released in a single timestep.
    We assume that a chemical signal, such as a neurotransmitter, is delivered with a right-skewed distribution,
    i.e. can be described with a curve that rapidly rises and slowly decays.
    The total amount of the signaling component is the area below the curve,
    the duration is the time until the signal is almost zero.
    We approximate the curve as a chi distribution with degree 2: f(x) = x * exp(-x*x/2)
    It peaks after 1s at 0.6, and has delivered 99.78% of the signal after 3.5s. Half of the signal
    has been delivered at 1.41s"""
    step_length = Settings.update_milliseconds / 1000 * duration / 3.5
    t1 = step * step_length
    t2 = (step+1) * step_length
    # amount is the integral from t1 to t2, i.e. beginning and end of the current timestep of the simulation
    amount = math.exp(-t1*t1/2) - math.exp(-t2*t2/2)
    return amount * total_amount
