# -*- coding: utf-8 -*-

"""

"""

__author__ = 'joscha'
__date__ = '31.03.16'


from model.modulators import valence, dominance, competence, arousal

class Behavior(object):
    """A behavior is a behavioral tendency that results from a configuration of needs and modulators."""

    def __init__(self, name):
        self.name = name
        self.value = 0


fight = Behavior("fight")
flight = Behavior("flight")
foraging = Behavior("foraging")
exploration = Behavior("exploration")
courtship = Behavior("courtship")
approach = Behavior("approach")
reflection = Behavior("reflection")
supplication = Behavior("supplication")

behaviors = (fight, flight, foraging, exploration, courtship, approach, reflection, supplication)

def reset():
    for behavior in behaviors:
        behavior.value = 0

def update():
    fight = -valence.value * (dominance.value + competence.value + arousal.value)
    flight = -valence.value * (-dominance.value - competence.value)

