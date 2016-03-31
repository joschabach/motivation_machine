# -*- coding: utf-8 -*-

"""
Running the actual simulation experiment
"""

__author__ = 'joscha'
__date__ = '3/15/16'

from random import randint, random
import math

from widgets import Settings
from helper_widgets import Diagram


from model.model import update_all
from model.needs import needs

class Simulation(object):
    def __init__(self):

        self.needs = needs
        self.need_index = needs

        self.current_simstep = 0

        self.log = []

    def step(self):
        """Advances the simulation by a single step. Returns False if we are done"""
        if self.current_simstep < Settings.max_simulation_steps:
            for need in self.needs:
                if random()>0.95:
                    need.frustrate()
                if random()>0.99:
                    need.satisfy()
            update_all()
            self.current_simstep += 1
            self._update_log()
            return True
        return False




    def _update_log(self):
        """adds the current values to the log."""
        self.log.append({"simstep": self.current_simstep,
                         "needs": { need.name: {"value": need.value,
                                                "urge_strength": need.urge_strength,
                                                "urgency": need.urgency,
                                                "pleasure": need.pleasure,
                                                "pain": need.pain} for need in self.needs
                                    }
                         })


class ValuePlot(Diagram):
    key = "value"
    window_title = "Values"


class ValueHistogram(Diagram):
    """A modified PlotWindow to display an updateable histogram"""
    key = "value distribution"
    window_title = "Distribution of Values"

    def plot(self):
        data = self.simulation.log["value"]
        self.subplot.cla()
        if len(data):
            values = [entry for entry in data[-1]]
            self.subplot.hist(values, bins=10, color="blue")



diagrams = [ValuePlot, ValueHistogram]


