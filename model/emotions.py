# -*- coding: utf-8 -*-

"""
Emotions
"""

__author__ = 'joscha'
__date__   = '31.03.16'


from model.modulators import modulators, aggregates
from model.needs import needs
from model.events import events, estimate_future_appetence, estimate_future_aversion

emotions = {}

class Emotion(object):
    """An emotion is an emergent configuration of the cognitive system of an agent"""

    def __init__(self, name, fn):
        self.name = name
        self.value = 0
        self.calculate = fn
        emotions[name] = self

    def update(self):
        self.value = self.calculate()



Emotion("joy", lambda: max(0, modulators["valence"].value) * modulators["arousal"].value)
Emotion("bliss", lambda: max(0, modulators["valence"].value) * modulators["resolution_level"].value)
Emotion("sadness", lambda: max(0, -modulators["valence"].value * (1-modulators["arousal"].value)))
Emotion("anger", lambda: max(0, -modulators["valence"].value) * modulators["arousal"].value)
Emotion("fear", lambda: min(1, -estimate_future_aversion()))
Emotion("hope", lambda: min(1, estimate_future_appetence()))

Emotion("anxiety", lambda: (1-aggregates["general_competence"].value) * (1-needs["exploration"].value))
Emotion("surprise", lambda: min(1, 10 * needs["exploration"].pain) * modulators["arousal"].value)
Emotion("curiosity", lambda: (1 - needs["exploration"].value) * aggregates["general_competence"].value)

Emotion("pride", lambda: max(0, 1-(2*needs["legitimacy"].value)))
Emotion("shame", lambda: max(0, 1 - (2 * needs["legitimacy"].value)))
Emotion("disgust", lambda: min(1, 10 * needs["aesthetics"].pain))

Emotion("shyness", lambda: (1-needs["dominance"].value)*(1-needs["affiliation"].value)*(1-needs["competence"].value))

def testing():
    return max(0, modulators["valence"].value) * modulators["resolution_level"].value

emotions["joy"].update= testing


def reset():
    pass


def update():
    for emotion in emotions.values():
        emotion.update()


def get_emotions():
    return {e.name: {"name": e.name,
                     "value": e.value}
            for e in emotions.values()}
