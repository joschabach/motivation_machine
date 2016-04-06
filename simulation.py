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


import model.api as api
from model.needs import needs, consumptions
from model.modulators import modulators, aggregates

class Simulation(object):
    def __init__(self):

        api.reset()
        self.needs = needs
        self.consumptions = consumptions
        self.modulators = modulators
        self.aggregates = aggregates
        self.need_index = needs

        self.current_simstep = 0

        self.log = []

    def step(self):
        """Advances the simulation by a single step. Returns False if we are done"""
        if self.current_simstep < Settings.max_simulation_steps:
            for consumption in self.consumptions:
                if random()>0.99:
                    consumption.trigger()
            api.update()
            self.current_simstep += 1
            self._update_log()
            return True
        return False




    def _update_log(self):
        """adds the current values to the log."""
        self.log.append(api.get_data())


class ValuePlot(Diagram):

    key = "value"
    window_title = "Values"

    number_of_data_points = 50

    def plot(self):
        """overwrite this method to produce a different diagram type"""
        self.data = self.simulation.log[-self.number_of_data_points:]
        self.subplot.cla()
        if len(self.data):
            self.draw("needs", "food", "value", "blue")
            self.draw("consumptions", "eat", "value", "green")
            self.draw("consumptions", "success", "value", "red")

    def draw(self, category, element, value, color = None):
        t = [s[category][element][value] for s in self.data]
        if color: self.subplot.plot(t, color = color, linewidth = 1.0)
        else: self.subplot.plot(t, color = color, linewidth = 1.0)


class ValueHistogram(Diagram):
    """A modified PlotWindow to display an updateable histogram"""
    key = "value distribution"
    window_title = "Distribution of Values"

    def plot(self):
        data = self.simulation.log["needs"]["food"]["value"]
        self.subplot.cla()
        if len(data):
            values = [entry for entry in data[-1]]
            self.subplot.hist(values, bins=10, color="blue")



diagrams = [ValuePlot, ValueHistogram]


