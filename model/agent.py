# -*- coding: utf-8 -*-

"""
Definition of the specific parameters of an agent
"""

__author__ = 'joscha'
__date__ = '08.04.16'


from model.needs import Need, Consumption
from model.modulators import Modulator



# Needs

Need("food", type="physiological", initial_value=1, weight=0.6, decay=1, gain=0.5, loss=0.01,
     satisfaction_from_imagination=0.0, frustration_from_imagination=0.0)
Need("water", type="physiological", weight=1, decay=9000, gain=1, loss=0.3,
     satisfaction_from_imagination=0.0, frustration_from_imagination=0.0)
Need("rest", type="physiological", weight=0.3, decay=60000, gain=1, loss=0.5,
     satisfaction_from_imagination=0.0, frustration_from_imagination=0.0)
Need("health", type="physiological", weight=10, decay=31536080, gain=0.05, loss=0.2,
     satisfaction_from_imagination=0.0, frustration_from_imagination=0.0)
Need("libido", type="physiological", weight=8, decay=200000, gain=0.8, loss=0.2,
     satisfaction_from_imagination=0.0, frustration_from_imagination=0.0)

Need("affiliation", type="social", weight=2, decay=60000, gain=0.1, loss=0.5)
Need("legitimacy", type="social", weight=12, decay=1000000, gain=0.1, loss=0.5)
Need("nurturing", type="social", weight=3, decay=6400, gain=0.5, loss=0.7)
Need("dominance", type="social", weight=0.5, decay=300000, gain=0.2, loss=0.4)
Need("affection", type="social", weight=10, decay=10000000, gain=0.8, loss=1)

Need("competence", type="cognitive", weight=0.2, decay=1000, gain = 0.2, loss=0.2)
Need("exploration", type="cognitive", weight=0.1, decay=1000)
Need("aesthetics", type="cognitive", weight=0.2, decay=6400)


# Modulators

Modulator("valence", baseline=0.2, min=-1.0, max=1.0)
Modulator("arousal", baseline=0.3, min=0.0, max=1.0)
Modulator("dominance", baseline=0.0, min=-1.0, max=1.0)  # approach or retraction

Modulator("resolution_level", baseline=0.5, min=0.0, max=1.0)  # detail in perception and cognition
Modulator("focus", baseline=0.5, min=0.0, max=1.0)  # selection threshold, and narrowness of perspective
Modulator("securing_rate", baseline=0.0, min=-1.0, max=1.0)  # attention outwards or inwards

# define the consumptive actions of the agent. These are triggered to activate the corresponding event
# the values should not correspond to the sensitivity of your particular agent, but to the default amount in
# which an event of this type will affect the needs of the agent in your particular environment.

Consumption("eat", "food", reward=1, duration=20.0)
Consumption("drink", "water", reward=0.5, duration=5.0)
Consumption("sweat", "water", reward=-0.1, duration=30.0)
Consumption("recover", "rest", reward=0.3, duration=10.0)
Consumption("sprint", "rest", reward=-0.5, duration=10.0)
Consumption("bruise", "health", reward=-.3, duration=3.0)
Consumption("mate", "libido", reward=1.0, duration=120.0)

Consumption("acceptance", "affiliation", reward=0.5, duration=3.0)
Consumption("rejection", "affiliation", reward=-0.5, duration=3.0)
Consumption("pride", "legitimacy", reward=1, duration=10.0)
Consumption("shame", "legitimacy", reward=-1, duration=10.0)
Consumption("support", "nurturing", reward=1.0, duration=3.0)
Consumption("supplication", "nurturing", reward=-0.5, duration=3.0)
Consumption("win", "dominance", reward=1, duration=3.0)
Consumption("loss", "dominance", reward=-1, duration=3.0)
Consumption("connection", "affection", reward=1, duration=30.0)
Consumption("abandonment", "affection", reward=-1, duration=30.0)

Consumption("success", "competence", reward=1.0, duration=1.0)
Consumption("failure", "competence", reward=-1.0, duration=1.0)
Consumption("confirmation", "exploration", reward=1.0, duration=1.0)
Consumption("disconfirmation", "exploration", reward=-1.0, duration=1.0)
Consumption("admiration", "aesthetics", reward=1.0, duration=3.0)
Consumption("disgust", "aesthetics", reward=-0.2, duration=3.0)
