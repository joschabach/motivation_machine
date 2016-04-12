# -*- coding: utf-8 -*-

"""
Modulators
"""

__author__ = 'joscha'
__date__ = '31.03.16'

from model.common import decay, marginal_sum
from model.needs import needs  # import needs, competence, exploration, consumptions
from model.events import goal


modulators = {}

class Modulator(object):
    """Modulators create a configuration of the cognitive system that amounts to a space of affective states.
    Each modulator has
    a baseline (usually somewhere around 0),
    a minimum and maximum (the interval in which the values vary around the baseline),
    a volatility, which describes how easily it departs from the baseline, and
    a decay, that determines how long it takes to get back to baseline."""

    def __init__(self, name, baseline=0.0, min=-1.0, max=1.0, volatility=1.0, decay=20):
        self.name = name
        self.value = baseline
        self.baseline = baseline
        self.min = min
        self.max = max
        self.volatility = volatility
        self.decay = decay

        modulators[name] = self

    def update(self):
        """Perform updates of the value of the modulator, based on the time."""

        # map interval to (1..0)
        if self.value >= self.baseline:
            value = (self.value - self.baseline) / (self.max - self.baseline)
            self.value = decay(value, self.decay) * (self.max - self.baseline) + self.baseline
        else:
            value = (self.baseline - self.value) / (self.baseline - self.min)
            self.value = self.baseline - decay(value, self.decay) * (self.baseline - self.min)

    def get_normalized_value(self):
        """Scales the modulator from -1 = min over 0 = baseline to +1 = max"""
        if self.value > self.baseline:
            return (self.value - self.baseline)/(self.max - self.baseline)
        else:
            return (self.value - self.baseline)/(self.min - self.baseline)

    def approach(self, target):
        """Set the value of the modulator, based on the volatility.
        The target value needs to be between -1 and 1, and gets scaled to the modulator range."""
        if target > 0:
            target = target * (self.max - self.baseline) + self.baseline
        else:
            target = target * (self.baseline - self.min) + self.baseline

        diff = (target - self.value) * self.volatility
        self.value = min(self.max, max(self.min, self.value + diff))


aggregates = {}

# intermediate parameters, normalized between 0 and 1, so we can use them for display
class Aggregate(object):
    def __init__(self, name, value=0):
        self.name = name
        self.value = value

        aggregates[name] = self


Aggregate("combined_urge")
Aggregate("combined_urgency")  # global stress level
Aggregate("combined_pain")
Aggregate("combined_pleasure")
Aggregate("general_competence")
Aggregate("epistemic_competence")


def adjusted_sum_of_need_properties(property, normalized = False):
    """Uses a marginal sum to add properties of all needs to approach their maximum value.
    Gives a bonus to the currently leading motive, according to the focus modulator.
    If normalized, the result is scaled against a maximum of 1."""
    values = [getattr(need, property) * ((1 + modulators["focus"].value) if need.is_leading_motive() else 1)
              for need in needs.values()]
    maximum = max([need.weight * ((1 + modulators["focus"].value) if need.is_leading_motive() else 1)
                   for need in needs.values()])
    return marginal_sum(values, maximum) if not normalized else marginal_sum(values, maximum)/maximum


def update():
    """Call this function in every timestep to update the modulator influences."""

    for modulator in modulators.values():
        modulator.update()

    # global pain perception (nociception) roughly aligns with 'substance p'
    aggregates["combined_pain"].value = adjusted_sum_of_need_properties("pain")

    # global pleasure perception (~endorphin, but it is more complicated)
    aggregates["combined_pleasure"].value = adjusted_sum_of_need_properties("pleasure")

    # valence combines pleasure and pain
    modulators["valence"].approach(adjusted_sum_of_need_properties("pleasure", True) -
                                   adjusted_sum_of_need_properties("pain", True))

    # combined urge tells us how much we should do stuff (~ dopamine)
    aggregates["combined_urge"].value = adjusted_sum_of_need_properties("urge", normalized = True)

    # combined urgency is the stress level (~ cortisol)
    aggregates["combined_urgency"].value = adjusted_sum_of_need_properties("urgency", normalized = True)

    # arousal depends on the urges and urgencies of all needs (~ noradrenaline)

    modulators["arousal"].approach((aggregates["combined_urge"].value + aggregates["combined_urgency"].value) -1)

    # competence tell us our coping potential
    aggregates["general_competence"].value = needs["competence"].value
    if goal:
        aggregates["epistemic_competence"].value = goal.skill
        aggregates["general_competence"].value = (aggregates["general_competence"].value * goal.skill) ** 0.5
    else:
        aggregates["epistemic_competence"].value = aggregates["general_competence"].value

    # dominance depends on general competence and the estimated probability of getting reward (~ dopamine)
    modulators["dominance"].approach((aggregates["general_competence"].value +
                                      aggregates["epistemic_competence"].value) -1)

    # resolution level defines attention to detail (~ serotonin)
    if goal:
        amplify = 1  # factor by which we increase arousal based on strength of leading motive
        target = amplify * (goal.consumption.need.urge - goal.consumption.need.urgency) -\
                 modulators["arousal"].get_normalized_value()
        max_target = amplify * (goal.consumption.need.weight - 0) + 1.0
        min_target = amplify * (0 - goal.consumption.need.weight) - 1.0
        normalized_target = ((target - min_target) * 2) / (max_target - min_target) - 1
    else:
        normalized_target = 1 - modulators["arousal"].get_normalized_value()

    modulators["resolution_level"].approach(normalized_target)

    # focus gives the rate of inhibition of competing urges and stimuli
    if goal:
        target = (modulators["arousal"].get_normalized_value()
                  + goal.consumption.need.urge
                  + goal.consumption.need.urgency
                  - needs["exploration"].urge  # = perceived uncertainty
                  + aggregates["general_competence"].value)
        max_target = (1.0 + goal.consumption.need.weight + goal.consumption.need.weight - 0 + 1.0)
        min_target = (-1.0 + goal.consumption.need.weight + goal.consumption.need.weight
                      - needs["exploration"].weight - 0)
        normalized_target = ((target - min_target) * 2) / (max_target - min_target) - 1
    else:
        target = modulators["arousal"].get_normalized_value() - needs["exploration"].urge + \
                 aggregates["general_competence"].value
        max_target = 1 - 0 + 1
        min_target = -1 - needs["exploration"].weight
        normalized_target = ((target - min_target) * 2) / (max_target - min_target) - 1

    modulators["focus"].approach(normalized_target)

    # securing rate defines how much attention is directed on updating the model of the environment
    if goal:
        target = (needs["exploration"].urge-(goal.consumption.need.urge + goal.consumption.need.urgency)
                  + aggregates["epistemic_competence"].value)
        max_target = (needs["exploration"].weight - (0 + 0) + 1.0)
        min_target = (needs["exploration"].weight - (goal.consumption.need.weight + goal.consumption.need.weight) + 0)
        normalized_target = ((target - min_target) * 2) / (max_target - min_target) - 1
    else:
        target = needs["exploration"].urge + aggregates["epistemic_competence"].value
        max_target = needs["exploration"].weight + 1.0
        min_target = needs["exploration"].weight
        normalized_target = ((target - min_target) * 2) / (max_target - min_target) - 1

    modulators["securing_rate"].approach(normalized_target)


def reset():
    """set all values to their initial condition"""
    for modulator in modulators.values():
        modulator.value = modulator.baseline
    for aggregate in aggregates.values():
        aggregate.value = 0


def get_aggregates():
    """returns a list of aggregated values"""
    return {a.name: {"name": a.name,
                     "value": a.value}
            for a in aggregates.values()}


def get_modulators():
    """returns a list of modulators with values"""
    return {m.name: {"name": m.name,
                     "value": m.value,
                     "baseline": m.baseline,
                     "min": m.min,
                     "max": m.max}
            for m in modulators.values()}
