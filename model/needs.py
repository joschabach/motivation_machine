# -*- coding: utf-8 -*-

"""
The needs of our agent
"""
from configuration import Settings

__author__ = 'joscha'
__date__ = '31.03.16'

from model.common import decay, get_inverted_decay_value, clip



class Need(object):
    """Basic element of motivation; may be either physiological, social or cognitive.
    Each need is normalized between 0 and 1, and but its corresponding urge and reward signals are weighted by a
    strength parameter. Gain and loss determine how easily the need gets satisfied or frustrated"""

    def __init__(self,
                 name,
                 type="physiological",
                 initial_value=0.5,
                 weight=1.0,
                 decay=3600,
                 gain=1.0,
                 loss=1.0,
                 pleasure_from_imagination=None,
                 pain_from_imagination=None,
                 satisfaction_from_imagination=None,
                 frustration_from_imagination=None,
                 pain_sensitivity=None,
                 pleasure_sensitivity=None,
                 pleasure_decay=10.0,
                 pain_decay=10.0):

        self.name = name
        self.type = type  # "physiological", "social" or "cognitive"
        self.initial_value = initial_value  # store this for the next reset
        self.value = initial_value  # current value of the need (between 0 and 1)
        self.weight = weight  # relative strength of urge, compared to competing urges
        self.decay = decay  # time until resource is fully depleted by itself, in seconds
        self.gain = gain  # factor by which events may satisfy the need
        self.loss = loss  # factor by which events may frustrate the need
        self.urge = 0.0  # strength of urge signal
        self.urgency = 0.0  # strength of urgency signal
        self.pleasure = 0.0  # pleasure received from satisfying the need
        self.pain = 0.0  # displeasure received from frustrating the need

        from model import agent

        self.pleasure_from_imagination = pleasure_from_imagination if pleasure_from_imagination is not None else \
            agent.default_pleasure_from_imagination  # discount factor for anticipated events
        self.pain_from_imagination = pain_from_imagination if pain_from_imagination is not None else \
            agent.default_pain_from_imagination
        self.satisfaction_from_imagination =satisfaction_from_imagination if satisfaction_from_imagination is not None \
            else agent.default_satisfaction_from_imagination  # factor for anticipated events
        self.frustration_from_imagination = frustration_from_imagination if frustration_from_imagination is not None \
            else agent.default_frustration_from_imagination
        self.pain_sensitivity = pain_sensitivity  # factor by which decrease in value is experienced as pain
        self.pleasure_sensitivity = pleasure_sensitivity  # factor by which increase in value is experienced as pleasure
        self.pleasure_decay = pleasure_decay  # time until a maximal pleasure signal disappears, in seconds
        self.pain_decay = pain_decay  # time until a maximal pain signal disappears, in seconds

    def update(self):
        """Perform updates of all dynamic values of the drive"""
        self.value = decay(self.value, self.decay)
        self.pleasure = decay(self.pleasure/self.weight, self.pleasure_decay) * self.weight
        self.pain = decay(self.pain/self.weight, self.pain_decay) * self.weight
        self._compute_urge_strength()
        self._compute_urgency()
        self._compute_pain_from_depletion()

    def _compute_urge_strength(self):
        """response function of urge signal depending on lack of the resource"""
        demand = 1 - self.value
        self.urge = self.weight * clip(demand) ** 2

    def _compute_urgency(self):
        """response function of urgency signal depending on time until depletion of the resource.
        In a real architecture, the urgency depends on the expectation horizon for associated events."""
        time_left = (get_inverted_decay_value(self.value) * self.decay)

        self.urgency = self.weight * max(0, 300 - time_left) / 300 ** 2

    def _compute_pain_from_depletion(self):
        """pain created by depletion of resource"""
        pain = clip(1-20*self.value)**2 * self.weight * self.pain_sensitivity   # pain starts at 90% depletion
        self.pain = max(self.pain, pain)

    def satisfy(self, delta):
        """increase satisfaction of a need by the given value,
        trigger pleasure signal proportional to weight."""
        delta = min(1 - self.value, abs(delta) * self.gain)
        self.value += delta
        self._increase_pleasure(delta)

    def imagine_satisfy(self, delta):
        """Increase satisfaction of a need according to an imagined value"""
        delta = min(1-self.value, abs(delta) * self.gain)
        self.value += min(1 - self.value, delta * self.satisfaction_from_imagination)
        self._increase_pleasure(min(1 - self.value, delta * self.pleasure_from_imagination))

    def frustrate(self, delta):
        """decrease satisfaction of a need by the given value,
        trigger pain signal proportional to weight."""
        delta = min(self.value, abs(delta) * self.loss)
        self.value -= delta
        if self.name == "exploration": delta *= (1 - competence.value) / 2
        self._increase_pain(delta)

    def imagine_frustrate(self, delta):
        """decrease satisfaction of a need according to an imagined value"""
        delta = min(self.value, abs(delta) * self.loss)
        self.value -= delta * self.frustration_from_imagination
        self._increase_pain(min(self.value, delta * self.pain_from_imagination))

    def _increase_pleasure(self, delta):
        """increase the pleasure level in relation to the given value"""
        self.pleasure += delta * self.pleasure_sensitivity * self.weight
        self.pleasure = min(self.pleasure, self.pleasure_sensitivity * self.weight)

    def _increase_pain(self, delta):
        """increase the pain level in relation to the given value"""
        self.pain += delta * self.pain_sensitivity * self.weight
        self.pain = min(self.pain, self.pain_sensitivity * self.weight)

    def is_leading_motive(self):
        if not goal: return False
        return self is goal.consumption.need

#
# # define the needs of our agent; these are going to be used in the simulation
#
# food = Need("food", type="physiological", initial_value=1, weight=0.6, decay=1, gain=0.5, loss=0.01,
#             satisfaction_from_imagination=0.0, frustration_from_imagination=0.0)
# water = Need("water", type="physiological", weight=1, decay=9000, gain=1, loss=0.3,
#              satisfaction_from_imagination=0.0, frustration_from_imagination=0.0)
# rest = Need("rest", type="physiological", weight=0.3, decay=60000, gain=1, loss=0.5,
#             satisfaction_from_imagination=0.0, frustration_from_imagination=0.0)
# health = Need("health", type="physiological", weight=10, decay=31536080, gain=0.05, loss=0.2,
#               satisfaction_from_imagination=0.0, frustration_from_imagination=0.0)
# libido = Need("libido", type="physiological", weight=8, decay=200000, gain=0.8, loss=0.2,
#               satisfaction_from_imagination=0.0, frustration_from_imagination=0.0)
#
# affiliation = Need("affiliation", type="social", weight=2, decay=60000, gain=0.1, loss=0.5)
# legitimacy = Need("legitimacy", type="social", weight=12, decay=1000000, gain=0.1, loss=0.5)
# nurturing = Need("nurturing", type="social", weight=3, decay=6400, gain=0.5, loss=0.7)
# dominance = Need("dominance", type="social", weight=0.5, decay=300000, gain=0.2, loss=0.4)
# affection = Need("affection", type="social", weight=10, decay=10000000, gain=0.8, loss=1)
#
# competence = Need("competence", type="cognitive", weight=0.3, decay=1000)
# exploration = Need("exploration", type="cognitive", weight=0.1, decay=1000)
# aesthetics = Need("aesthetics", type="cognitive", weight=0.2, decay=6400)


needs = []


def get_need(name):
    return [n for n in needs if n.name == name][0]


goal = None


class Consumption(object):
    """Create a consumption to satisfy or frustrate a need.
    You can change the actual reward and duration later when triggering the event"""

    def __init__(self, name, need, reward=1.0, duration=3.0, max_reward=3.0, anticipation_discount_factor=None):

        self.name = name
        self.need = need  # the need that gets frustrated or rewarded
        self.value = 0  # current amount of satisfaction or frustration generated by this consumptor
        self.default_reward = reward  # total reward generated by a typical consumption
        self.default_duration = duration  # duration over which the reward is typically experienced
        self.max_reward = max_reward  # limit of cumulated reward that can be received per timestep

        from model import agent

        self.anticipation_discount_factor = anticipation_discount_factor if anticipation_discount_factor is not None \
            else agent.anticipation_discount_factor# how much do I believe in the future?
        self.events = []  # list of currently active events of this category


    def trigger(self, reward=None, duration=-1):
        """Set a reward value and a duration in s for the consumption.
        We could do this directly, but I want to show it in the visualization.
        Multiple active rewards will stack, and will be triggered in parallel."""
        if reward is None: reward = self.default_reward
        if duration == -1: duration = self.default_duration
        reward_per_timestep = reward / duration * Settings.update_milliseconds / 1000.0
        self.events.append((reward_per_timestep, duration))

    def get_anticipated_reward(self, reward, expiration):
        """Returns a discounted reward value, based on the interval until the consumption expires"""

        if expiration < 0:
            return reward / 2.0
        else:
            return reward / (1.0 + self.anticipation_discount_factor * expiration)  # hyperbolic discounting

    def anticipate(self, reward=None, certainty = 1.0, skill = 1.0, expiration=-1):
        """Generates an imagined satisfaction or frustration of the need, proportional to its discounted
        value, certainty, and skill"""
        if reward is None: reward = self.default_reward

        discounted_reward = self.get_anticipated_reward(reward, expiration)
        if discounted_reward > 0:
            self.need.imagine_satisfy(certainty * skill * discounted_reward)  # appetence
        else:
            self.need.imagine_frustrate(certainty * (1.0-skill) * discounted_reward)  # aversion

    def update(self):
        """Make sure we call this every cycle and turn it off again"""
        value = 0
        for event in self.events:
            reward, duration = event
            if duration > 0:
                if duration < Settings.update_milliseconds / 1000.0:  # fractional reward
                    value += reward * (duration / Settings.update_milliseconds / 1000.0)
                else:
                    value += reward  # we assume that it is all positive, or all negative

        self.value = min(self.max_reward, max(-self.max_reward, value))  # limit cumulated reward

        self.events[:] = [(reward, duration - Settings.update_milliseconds / 1000.0) for reward, duration in self.events
                          if duration > Settings.update_milliseconds / 1000.0]  # delete events when they are over

        if self.value > 0:
            self.need.satisfy(self.value)
        else:
            self.need.frustrate(-self.value)


# define the consumptive actions of the agent. These are triggered to activate the corresponding event
# the values should not correspond to the sensitivity of your particular agent, but to the default amount in
# which an event of this type will affect the needs of the agent in your particular environment.

eat = Consumption("eat", food, reward=1, duration=20.0)
drink = Consumption("drink", water, reward=0.5, duration=5.0)
sweat = Consumption("sweat", water, reward=-0.1, duration=30.0)
recover = Consumption("recover", rest, reward=0.3, duration=10.0)
sprint = Consumption("sprint", rest, reward=-0.5, duration=10.0)
bruise = Consumption("bruise", health, reward=-.3, duration=3.0)
heal = Consumption("heal", health, reward=0.1, duration=20.0)
mate = Consumption("mate", libido, reward=1.0, duration=120.0)

acceptance = Consumption("acceptance", affiliation, reward=0.5, duration=3.0)
rejection = Consumption("rejection", affiliation, reward=-0.5, duration=3.0)
pride = Consumption("pride", legitimacy, reward=1, duration=10.0)
shame = Consumption("shame", legitimacy, reward=-1, duration=10.0)
support = Consumption("support", nurturing, reward=1.0, duration=3.0)
supplication = Consumption("supplication", nurturing, reward=-0.5, duration=3.0)
win = Consumption("win", dominance, reward=1, duration=3.0)
loss = Consumption("loss", dominance, reward=-1, duration=3.0)
connection = Consumption("connection", affection, reward=1, duration=30.0)
abandonment = Consumption("abandonment", affection, reward=-1, duration=30.0)

success = Consumption("success", competence, reward=1.0, duration=1.0)
failure = Consumption("failure", competence, reward=-1.0, duration=1.0)
confirmation = Consumption("confirmation", exploration, reward=1.0, duration=1.0)
disconfirmation = Consumption("disconfirmation", exploration, reward=-1.0, duration=1.0)
admiration = Consumption("admiration", aesthetics, reward=1.0, duration=3.0)
disgust = Consumption("disgust", aesthetics, reward=-0.2, duration=3.0)


consumptions = [eat, drink, sweat, recover, sprint, bruise, heal, mate,
                acceptance, rejection, pride, shame, support, supplication, win, loss, connection, abandonment,
                success, failure, confirmation, disconfirmation, admiration, disgust]


def get_consumption(name):
    return [c for c in consumptions if c.name == name][0]


def update():
    for need in needs:
        need.update()

    for consumption in consumptions:
        consumption.update()


def reset():
    for need in needs:
        need.value = need.initial_value
        need.pleasure = 0.0
        need.pain = 0.0

    for consumption in consumptions:
        consumption.events = []


def get_needs():
    """Returns a list with current need states"""
    return {n.name: {"name": n.name,
                     "type": n.type,
                     "weight": n.weight,
                     "value": n.value,
                     "urge": n.urge,
                     "urgency": n.urgency,
                     "pain": n.pain,
                     "pleasure": n.pleasure,
                     "is_leading_motive": n.is_leading_motive()}
            for n in needs}


def get_consumptions():
    """Returns a list with current consumption states"""
    return {c.name: {"name": c.name,
                     "need": c.need.name,
                     "type": "aversive" if c.default_reward < 0 else "appetitive",
                     "value": c.value}
            for c in consumptions}
