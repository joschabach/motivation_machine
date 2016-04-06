# -*- coding: utf-8 -*-

"""
Modulators
"""

__author__ = 'joscha'
__date__ = '31.03.16'

from model.common import decay, exponential_scaling
from model.needs import needs, competence, exploration, consumptions
from model.events import events, goal


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


valence = Modulator("valence", baseline=0.2, min=-1.0, max=1.0)
arousal = Modulator("arousal", baseline=0.3, min=0.0, max=1.0)
dominance = Modulator("dominance", baseline=0.0, min=-1.0, max=1.0)  # approach or retraction

resolution_level = Modulator("resolution_level", baseline=0.5, min=0.0, max=1.0)  # detail in perception and cognition
focus = Modulator("focus", baseline=0.5, min=0.0, max=1.0)  # selection threshold, and narrowness of perspective
securing_rate = Modulator("securing_rate", baseline=0.0, min=-1.0, max=1.0)  # attention outwards or inwards

modulators = [valence, arousal, dominance, resolution_level, focus, securing_rate]

def get_modulator(name):
    return [m for m in modulators if m.name == name][0]

# intermediate parameters, normalized between 0 and 1, so we can use them for display
class Aggregate(object):
    def __init__(self, name, value=0):
        self.name = name
        self.value = value


combined_urge = Aggregate("combined_urge_strength")
combined_urgency = Aggregate("combined_urgency")  # global stress level
combined_pain = Aggregate("combined_pain")
combined_pleasure = Aggregate("combined_pleasure")
general_competence = Aggregate("general_competence")
epistemic_competence = Aggregate("epistemic_competence")

aggregates = [combined_pleasure, combined_pain, combined_urge, combined_urgency,
              general_competence, epistemic_competence]

def get_aggregate(name):
    return [a for a in aggregates if a.name == name][0]


def compute_global_pain():
    """Update the global pain perception (nociception) of the agent. It roughly aligns with 'substance p', and
    also depends on the attention of the agent.
    We scale from 0..1."""

    amplify = 2  # increase signal for leading motive; this is on top of the normal weight
    # todo: we might also want to amplify depending on securing rate

    sum_pain = sum([need.pain for need in needs]) + goal.consumption.need.pain * amplify * focus.value
    max_pain = sum([need.weight for need in needs]) + goal.consumption.need.weight * amplify * focus.max
    combined_pain.value = exponential_scaling(sum_pain / max_pain)


def compute_global_pleasure():
    """Update the global pleasure perception of the agent. It roughly aligns with endorphine, and
    also depends on the attention of the agent.
    We scale from 0..1."""
    amplify = 2  # increase signal for leading motive; this is on top of the normal weight
    # todo: we might also want to amplify depending on securing rate

    sum_pleasure = sum([need.pleasure for need in needs]) + goal.consumption.need.pleasure * amplify * focus.value
    max_pleasure = sum([need.weight for need in needs]) + goal.consumption.need.weight * amplify * focus.max
    combined_pleasure.value = exponential_scaling(sum_pleasure / max_pleasure)


def compute_global_urge():
    """Combines the strength of all current urges into a value between 0 and 1.
    Also takes attention into account."""
    amplify = 2  # increase signal for leading motive; this is on top of the normal weight

    sum_urge_strength = sum([need.urge for need in needs]) + goal.consumption.need.urge * amplify * focus.value
    max_urge_strength = sum([need.weight for need in needs]) + goal.consumption.need.weight * amplify * focus.value
    combined_urge.value = exponential_scaling(sum_urge_strength / max_urge_strength)


def compute_global_urgency():
    """Combines the strength of all current urgencies into a value between 0 and 1. It amounts to a global stress
    level (~ cortisol).
    Also takes attention into account."""

    amplify = 2  # increase signal for leading motive; this is on top of the normal weight

    sum_urgency = sum([need.urgency for need in needs]) + goal.consumption.need.urgency * amplify * focus.value
    max_urgency = sum([need.weight for need in needs]) + goal.consumption.need.weight * amplify * focus.max
    combined_urgency.value = exponential_scaling(sum_urgency / max_urgency)


def compute_global_competence():
    """Tells us how well we are able to cope with the world right now"""
    general_competence.value = 1 - competence.value
    epistemic_competence.value = goal.skill


def update():
    """Call this function in every timestep to update the modulator influences."""

    for modulator in modulators:
        modulator.update()

    compute_global_pain()
    compute_global_pleasure()

    # valence combines pleasure and pain (~ serotonin)
    valence.approach(combined_pleasure.value - combined_pain.value)

    # arousal depends on the urges and urgencies of all needs (~ noradrenaline)
    compute_global_urge()
    compute_global_urgency()

    arousal.approach((combined_urge.value + combined_urgency.value)/2)

    # dominance depends on general competence and the estimated probability of getting reward (~ dopamine)
    compute_global_competence()
    dominance.approach((general_competence.value + epistemic_competence.value) / 2)

    # resolution level defines attention to detail
    amplify = 1  # factor by which we increase arousal based on strength of leading motive
    target = amplify * (goal.consumption.need.urge- goal.consumption.need.urgency) - arousal.get_normalized_value()
    max_target = amplify * (goal.consumption.need.weight - 0) + 1.0
    min_target = amplify * (0 - goal.consumption.need.weight) - 1.0
    normalized_target = ((target - min_target) * 2) / (max_target - min_target) - 1

    resolution_level.approach(normalized_target)

    # focus gives the rate of inhibition of competing urges and stimuli
    target = (arousal.get_normalized_value() + goal.consumption.need.urge + goal.consumption.need.urgency
              - exploration.urge  # = perceived uncertainty
              + general_competence.value)
    max_target = (1.0 + goal.consumption.need.weight + goal.consumption.need.weight - 0 + 1.0)
    min_target = (-1.0 + goal.consumption.need.weight + goal.consumption.need.weight - exploration.weight - 0)
    normalized_target = ((target - min_target) * 2) / (max_target - min_target) - 1

    focus.approach(normalized_target)

    # securing rate defines how much attention is directed on updating the model of the environment
    target = (exploration.urge-(goal.consumption.need.urge + goal.consumption.need.urgency)
              + epistemic_competence.value)
    max_target = (exploration.weight - (0 + 0) + 1.0)
    min_target = (exploration.weight - (goal.consumption.need.weight + goal.consumption.need.weight) + 0)
    normalized_target = ((target - min_target) * 2) / (max_target - min_target) - 1

    securing_rate.approach(normalized_target)


def reset():
    """set all values to their initial condition"""
    for modulator in modulators:
        modulator.value = modulator.baseline
    for aggregate in aggregates:
        aggregate.value = 0


def get_aggregates():
    """returns a list of aggregated values"""
    return {a.name: {"name": a.name,
                     "value": a.value}
            for a in aggregates}


def get_modulators():
    """returns a list of modulators with values"""
    return {m.name: {"name": m.name,
                     "value": m.value,
                     "baseline": m.baseline,
                     "min": m.min,
                     "max": m.max}
            for m in modulators}
