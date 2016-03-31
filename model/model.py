# -*- coding: utf-8 -*-

"""
Explore the main dependencies of the motivation machine
"""

__author__ = 'joscha'
__date__ = '3/14/16'


# initialization




from model.behaviors import update as update_behaviors
from model.modulators import update as update_modulators
from model.needs import update as update_needs


def update_all():
    update_needs()
    update_modulators()
    update_behaviors()