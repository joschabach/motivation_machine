# -*- coding: utf-8 -*-

"""
Definition of the specific parameters of an agent
"""

__author__ = 'joscha'
__date__ = '08.04.16'


from model.needs import Need, needs
from model.modulators import Modulator, modulators



default_pain_sensitivity = 1.0
default_pleasure_sensitivity = 1.0

# anticipated events will elicit pleasure and displeasure responses
default_pleasure_from_imagination = 0.1
default_pain_from_imagination = 0.2
# anticipated events will even directly influence some demands
default_satisfaction_from_imagination = 0.1
default_frustration_from_imagination = 0.1

# we do hyperbolic discounting, with reward/(1 + k * time_to_event)
anticipation_discount_factor = 0.5 / 3600  # after one hour, the event is only worth 2/3 (=1/1+.5)


Modulator("valence", baseline=0.2, min=-1.0, max=1.0)
Modulator("arousal", baseline=0.3, min=0.0, max=1.0)
Modulator("dominance", baseline=0.0, min=-1.0, max=1.0)  # approach or retraction

Modulator("resolution_level", baseline=0.5, min=0.0, max=1.0)  # detail in perception and cognition
Modulator("focus", baseline=0.5, min=0.0, max=1.0)  # selection threshold, and narrowness of perspective
Modulator("securing_rate", baseline=0.0, min=-1.0, max=1.0)  # attention outwards or inwards
