# -*- coding: utf-8 -*-

"""
The needs of our agent
"""
from configuration import Settings

__author__ = 'joscha'
__date__ = '31.03.16'

from model.common import decay, get_inverted_decay_value

class Need(object):
    """Basic element of motivation; may be either physiological, social or cognitive.
    Each need is normalized between 0 and 1, and but its corresponding urge and reward signals are weighted by a
    strength parameter. Gain and loss determine how easily the need gets satisfied or frustrated"""

    def __init__(self,
                 name,
                 initial_value=0.5,
                 strength=1.0,
                 decay=3600,
                 gain=1.0,
                 loss=1.0,
                 pleasure_decay=10,
                 pain_decay=10):
        self.name = name
        self.value = initial_value  # current value of the need (between 0 and 1)
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
        self._compute_urge_strength()
        self._compute_urgency()
        self._compute_pain()

    def _compute_urge_strength(self):
        """response function of urge signal depending on lack of the resource"""
        demand = 1 - self.value
        self.urge_strength = self.strength * demand ** 2

    def _compute_urgency(self):
        """response function of urgency signal depending on time until depletion of the resource.
        In a real architecture, the urgency depends on the expectation horizon for associated events."""
        time_left = (get_inverted_decay_value(self.value) * self.decay)

        self.urgency = self.strength * max(0, 300 - time_left) / 300 ** 2

    def _compute_pain(self):
        """pain created by depletion of resource"""
        self.pain = min(1, max(self.pain, self.strength * (20 * (0.1 - self.value))) ** 2)  # pain starts at 10%

    def satisfy(self, value=0.2):
        """increase satisfaction of a need by the given value, trigger pleasure signal proportional to strength"""
        delta = min(1, self.value + value * self.gain) - self.value
        self.value = self.value + delta
        self.pleasure = min(1, self.strength * delta)

    def frustrate(self, value=0.2):
        """decrease satisfaction of a need by the given value, trigger pain signal proportional to strength"""
        delta = self.value - max(0, self.value - value * self.loss)
        self.value = self.value - delta
        self.pain = min(1, self.strength * delta)


# define the needs of our agent; these are going to be used in the simulation

food = Need("food", strength=0.6, decay=84000, gain=0.5, loss=0.01)
water = Need("water", strength=1, decay=9000, gain=1, loss=0.3)
rest = Need("rest", strength=0.3, decay=60000, gain=1, loss=0.5)
health = Need("health", strength=10, decay=31536080, gain=0.05, loss=0.2)
libido = Need("libido", strength=8, decay=200000, gain=0.8, loss=0.2)

affiliation = Need("affiliation", strength=2, decay=60000, gain=0.1, loss=0.5)
legitimacy = Need("legitimacy", strength=12, decay=1000000, gain=0.1, loss=0.5)
nurturing = Need("nurturing", strength=3, decay=6400, gain=0.5, loss=0.7)
dominance = Need("dominance", strength=0.5, decay=300000, gain=0.2, loss=0.4)
affection = Need("affection", strength=10, decay=10000000, gain=0.8, loss=1)

competence = Need("competence", strength=0.3, decay=1000)
exploration = Need("exploration", strength=0.1, decay=1000)
aesthetics = Need("aesthetics", strength=0.2, decay=6400)


needs = [food, water, rest, health, libido, affiliation, affection, competence, exploration, aesthetics]


def update():
    for need in needs:
        need.update()


class Skill(object):
    """Skills are abilities to handle types of events. They relate to epistemic competence."""

    def __init__(self, type, competence=1, certainty=1, cost=0):
        self.type = type  # class of the skill
        self.competence = competence  # probability of success
        self.certainty = certainty  # probability that estimate of success probability is correct
        self.cost = cost  # effort necessary to execute the skill


default_skill = Skill("default")
skills = [ default_skill ]


class Goal(object):
    """Goals are events in the inner or perceptual world of the agent. They become
    relevant if they are associated with the expectation of satisfying or frustrating a need."""

    def __init__(self, id, situation = None, expected_reward = 0, certainty = 1,
                 skill = default_skill, expiration = -1):
        self.id = id  # identifier for the event
        self.situation = situation  # reference to an element in the world (situations can have multiple events)
        self.expected_reward = expected_reward  # if positive, satisfaction; if negative, frustration of the need
        self.certainty = certainty  # confidence that the event will yield the reward
        self.skill = skill  # category of competence necessary to get the reward / avoid frustration
        self.expiration = expiration  # time left until event no longer available (-1: event does not time out)

    def update(self):
        if self.expiration > 0:
            self.expiration -= Settings.update_milliseconds/1000


default_goal = Goal("default")
goals = [ default_goal]


class LeadingMotive(object):
    """Here, the leading motive combines a need with a goal"""
    need = rest
    goal = default_goal


leading_motive = LeadingMotive()


def select_leading_motive(need, goal = None):
    """Commit to pursuing a behavior that satisfies a need, by attempting to reach a goal event.
    In a live cognitive architecture, this is done by decisionmaking procedures and may involve planning."""
    global leading_motive
    if not goal:
        goal = default_goal
    leading_motive.need = need
    leading_motive.goal = goal