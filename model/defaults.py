# -*- coding: utf-8 -*-

"""
Additional default properties for the agent
"""

__author__ = 'joscha'
__date__ = '08.04.16'

pain_sensitivity = 1.0
pleasure_sensitivity = 1.0

# anticipated events will elicit pleasure and displeasure responses
pleasure_from_imagination = 0.1
pain_from_imagination = 0.2
# anticipated events will even directly influence some demands
satisfaction_from_imagination = 0.1
frustration_from_imagination = 0.1

# we do hyperbolic discounting, with reward/(1 + k * time_to_event)
anticipation_discount_factor = 0.5 / 3600  # after one hour, the event is only worth 2/3 (=1/1+.5)
