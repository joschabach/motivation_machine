# -*- coding: utf-8 -*-

"""
Explore the main dependencies of the motivation machine
"""

__author__ = 'joscha'
__date__ = '3/14/16'


# initialization

import math
from configuration import Settings

def decay(value, decay = -1):
    """Perform an approximate logistic decay from 1 to 0 within time 'decay':
    we assume the sigmoidal function y = 1-1/(1+e^-12(x-1/2))"""

    if decay<0: return value  # value does not decay

    interval = Settings.update_milliseconds/1000

    x = get_inverted_decay_value(value) + interval/decay  # find out where we have been in the curve
    if x>=1: return 0
    return 1 - 1 / (1 + math.exp(-12 * (x - 0.5)))


def get_inverted_decay_value(y):
    """Solves the logistic decay function y = 1-1/(1+e^-12(x-1/2)) for x,
    so we find out at which point we are in the curve"""

    if y >=1: return 0.0
    if y <= 0: return 1.0
    return min(1, max(0, math.log((1 - y) / y) / 6 + 0.5))


class Need(object):
    """Basic element of motivation; may be either physiological, social or cognitive.
    Each need is normalized between 0 and 1, and but its corresponding urge and reward signals are weighted by a
    strength parameter. Gain and loss determine how easily the need gets satisfied or frustrated"""
    def __init__(self,
                 name,
                 initial_value = 0.5,
                 strength = 1.0,
                 decay = 3600,
                 gain = 1.0,
                 loss = 1.0,
                 pleasure_decay = 10,
                 pain_decay = 10):
        self.name = name
        self.value = initial_value  # current value of the need
        self.strength = strength  # relative strength of urge, compared to competing urges
        self.decay = decay  # time until resource is fully depleted by itself, in seconds
        self.gain = gain  # factor by which events may satisfy the need
        self.loss = loss  # factor by which events may frustrate the need
        self.urge_strength = 0.0  # strength of urge signal
        self.urgency = 0.0  # strength of urgency signal
        self.pleasure = 0.0  # pleasure received from satisfying the need
        self.pain = 0.0  # displeasure received from frustrating the need
        self.pleasure_decay = pleasure_decay  # time until a maximal pleasure signal disappears, in seconds
        self.pain_decay = pain_decay  # time until a maximal pain signal disappears, in seconds

    def update(self):
        """Perform updates of all dynamic values of the drive"""
        self.value = decay(self.value, self.decay)
        self.pleasure = decay(self.pleasure, self.pleasure_decay)
        self.pain = decay(self.pain, self.pain_decay)
        self.compute_urge_strength()
        self.compute_urgency()
        self.compute_pain()

    def compute_urge_strength(self):
        """response function of urge signal depending on lack of the resource"""
        demand = 1 - self.value
        self.urge_strength = self.strength * demand ** 2

    def compute_urgency(self):
        """response function of urgency signal depending on time until depletion of the resource.
        In a real architecture, the urgency depends on the expectation horizon for associated events."""
        time_left = (get_inverted_decay_value(self.value) * self.decay)

        self.urgency = self.strength * max(0, 300-time_left)/300 ** 2

    def compute_pain(self):
        """pain created by depletion of resource"""
        self.pain = min(1, max(self.pain, self.strength*(20*(0.1-self.value)))**2)  # pain starts at 10%

    def satisfy(self, value = 0.2):
        """increase satisfaction of a need by the given value, trigger pleasure signal proportional to strength"""
        delta = min(1, self.value + value*self.gain)-self.value
        self.value = self.value + delta
        self.pleasure = min(1, self.strength * delta)

    def frustrate(self, value = 0.2):
        """decrease satisfaction of a need by the given value, trigger pain signal proportional to strength"""
        delta = self.value - max(0, self.value - value * self.loss)
        self.value = self.value - delta
        self.pain = min(1, self.strength * delta)


# define the needs of our agent; these are going to be used in the simulation

needs = [
    Need("food", strength=0.6, decay=84000, gain=0.5, loss=0.01),
    Need("water", strength=1, decay=9000, gain=1, loss=0.3),
    Need("rest", strength=0.3, decay=60000, gain=1, loss=0.5),
    Need("health", strength=10, decay=31536080, gain=0.05, loss=0.2),
    Need("libido", strength=8, decay=200000, gain=0.8, loss=0.2),

    Need("affiliation", strength=2, decay=60000, gain=0.1, loss=0.5),
    Need("legitimacy", strength=12, decay=1000000, gain=0.1, loss=0.5),
    Need("nurturing", strength=3, decay=6400, gain=0.5, loss=0.7),
    Need("dominance", strength=0.5, decay=300000, gain=0.2, loss=0.4),
    Need("affection", strength=10, decay=10000000, gain=0.8, loss=1),

    Need("competence", strength=0.3, decay=1000),
    Need("exploration", strength=0.1, decay=1000),
    Need("aesthetics", strength=0.2, decay=6400)
]

need_index = dict((need.name, need) for need in needs)


class Skill(object):
    """Skills are abilities to handle types of events. They relate to epistemic competence."""

    def __init__(self, type, competence=1, certainty=1, cost=0):
        self.type = type  # class of the skill
        self.competence = competence  # probability of success
        self.certainty = certainty  # probability that estimate of successprobability is correct
        self.cost = cost  # effort necessary to execute the skill


skills = [
    Skill("default")
]

skill_index = dict((skill.type, skill) for skill in skills)


class Event(object):
    """Events are occurrences in the inner or perceptual world of the agent. They become
    relevant if they are associated with the expectation of satisfying or frustrating a need."""

    def __init__(self, id, situation = None, expected_reward = 0, certainty = 1,
                 skill = skill_index["default"], expiration = -1):
        self.id = id  # identifier for the event
        self.situation = situation  # reference to some element in the world (situations can have multiple associated events)
        self.expected_reward = expected_reward  # if positive, satisfaction; if negative, frustration of the need
        self.certainty = certainty  # confidence that the event will yield the reward
        self.skill = skill  # category of competence necessary to get the reward / avoid frustration
        self.expiration = expiration  # time left until event no longer available (-1: event does not time out)

    def update(self):
        if self.expiration > 0: self.expiration -= Settings.update_milliseconds/1000




class Leading_motive(object):
    """Technically, a leading motive is made up of an urge, a goal situation and a plan to realize it"""
    def __init__(self, need, event):
        self.need = need
        self.event = event

leading_motive =

def select_leading_motive(need, event):
    """Commit to pursuing a behavior that satisfies a need, by attempting to reach a goal event.
    In a live cognitive architecture, this is done by decisionmaking procedures and may involve planning."""
    global leading_motive
    leading_motive = (need, event)

class Modulator(object):
    """Modulators create a configuration of the cognitive system that amounts to a space of affective states.
    Each modulator has
    a baseline (usually somewhere around 0),
    a minimum and maximum (the interval in which the values vary around the baseline),
    a volatility, which describes how easily it departs from the baseline, and
    a decay, that determines how long it takes to get back to baseline."""

    def __init__(self, name, baseline = 0.0, min = -1.0, max = 1.0, volatility = 1.0, decay = 20):
        self.name = name
        self.value = baseline
        self.baseline = baseline
        self.min = min
        self.max = max
        self.volatility = volatility
        self.decay = decay

    def update(self):
        """Perform updates of the value of the modulator, based on the time."""

        # map interval to (1..0)
        if self.value >= self.baseline:
            value = (self.value - self.baseline) / (self.max - self.baseline)
            self.value = decay(value, self.decay) * (self.max - self.baseline) + self.baseline
        else:
            value = (self.baseline - self.value) / (self.baseline - self.min)
            self.value = self.baseline - decay(value, self.decay) * (self.baseline - self.min)

        self.compute_influences()

    def compute_influences(self):
        pass

modulators = [
    Modulator("valence", baseline = 0.2),
    Modulator("arousal"),
    Modulator("dominance"),  # approach or retraction
    Modulator("resolution_level"),  # degree of detail in perception and cognition
    Modulator("focus"),  # selection threshold, and narrowness of perspective
    Modulator("securing_rate")  # attention outwards or inwards
]

modulator_index = dict((modulator.name, modulator) for modulator in modulators)

