# -*- coding: utf-8 -*-

"""
Emotions
"""

__author__ = 'joscha'
__date__   = '31.03.16'


class Emotion(object):
    """An emotion is an emergent configuration of the cognitive system of an agent"""

    def __init__(self, name):
        self.name = name
        self.value = 0


emotion_list = [
    Emotion("joy"),
    Emotion("bliss"),
    Emotion("anger"),
    Emotion("disgust"),
    Emotion("sadness"),
    Emotion("fear"),
    Emotion("pride"),
    Emotion("pity"),
    Emotion("guilt"),
    Emotion("shame"),
    Emotion("pain"),
    Emotion("startle"),
    Emotion("anxiety")
]