# -*- coding: utf-8 -*-

"""
Modulators
"""

__author__ = 'joscha'
__date__ = '31.03.16'

from model.common import decay

from model.needs import needs, competence, exploration, rest, leading_motive



class Modulator(object):
    """Modulators create a configuration of the cognitive system that amounts to a space of affective states.
    Each modulator has
    a baseline (usually somewhere around 0),
    a minimum and maximum (the interval in which the values vary around the baseline),
    a volatility, which describes how easily it departs from the baseline, and
    a decay, that determines how long it takes to get back to baseline.

    The function calculate dependencies defines how a modulator is influenced by others."""

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


    def approach(self, target):
        """Set the value of the modulator, based on the volatility.
        The target value needs to be between -1 and 1, and gets scaled to the modulator range."""
        if target > 0:
            target = target * (self.max - self.baseline) + self.baseline
        else:
            target = target * (self.baseline - self.min) + self.baseline

        diff = (target - self.value) * self.volatility
        self.value = min(self.max, max(self.min, self.value + diff))


valence = Modulator("valence", baseline=0.2)
arousal = Modulator("arousal")
dominance = Modulator("dominance")  # approach or retraction

resolution_level = Modulator("resolution_level")  # degree of detail in perception and cognition
focus = Modulator("focus")  # selection threshold, and narrowness of perspective
securing_rate = Modulator("securing_rate")  # attention outwards or inwards

modulators = [valence, arousal, dominance, resolution_level, focus, securing_rate]


def update():
    global valence, arousal, dominance, resolution_level, focus, securing_rate


    # valence is average pleasure and pain (~ serotonin)

    average_pleasure = sum([need.pleasure for need in needs]) / len(needs)
    average_pain = sum([need.pain for need in needs]) / len(needs)

    valence.approach(average_pleasure - average_pain)

    # arousal depends on the urges and urgencies of all needs, and the level of exhaustion (~ epinephrine)

    sum_urge_strengths = sum([need.urge_strength for need in needs])
    max_sum_urge_strengths = sum([need.strength for need in needs])

    sum_urgencies = sum([need.urgency for need in needs])
    max_sum_urgencies = sum([need.strength for need in needs])

    arousal.approach(2*(sum_urge_strengths + sum_urgencies) / (max_sum_urge_strengths + max_sum_urgencies)-rest.value)


    # dominance depends on general competence and the estimated probability of getting reward (~ dopamine)

    general_competence = 1 - competence.value
    epistemic_competence = leading_motive.goal.skill.competence
    max_competence = 2

    dominance.approach((general_competence + epistemic_competence) / max_competence)


    # resolution level defines attention to detail

    normalized_arousal = (arousal.value - arousal.baseline) / (arousal.max - arousal.baseline) \
        if arousal.value > arousal.baseline else - (arousal.baseline - arousal.value) / (arousal.baseline - arousal.min)

    leading_urge_strength = leading_motive.need.urge_strength
    max_leading_urge_strength = leading_motive.need.strength

    leading_urge_urgency = leading_motive.need.urge_strength
    max_leading_urge_urgency = leading_motive.need.strength

    resolution_level.approach((- normalized_arousal + (leading_urge_strength - leading_urge_urgency)/
                              (max_leading_urge_strength + max_leading_urge_urgency))/2)

    # focus gives the rate of inhibition of competing urges and stimuli

    perceived_uncertainty = exploration.urge_strength
    max_uncertainty = exploration.strength

    focus.approach((normalized_arousal + (leading_urge_strength + leading_urge_urgency - perceived_uncertainty) /
                   (max_leading_urge_strength + max_leading_urge_urgency + max_uncertainty) + general_competence)/3)

    # securing rate defines how much attention is directed on updating the model of the environment

    securing_rate.approach((perceived_uncertainty-(leading_urge_strength+leading_urge_urgency+epistemic_competence)
                            /(max_leading_urge_strength+max_leading_urge_urgency+1)))
