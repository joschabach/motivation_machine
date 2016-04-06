# -*- coding: utf-8 -*-

"""
Interface of the motivation machine
"""

__author__ = 'joscha'
__date__ = '3/14/16'



import model.needs, model.modulators, model.events

step = 0

def reset():
    """Returns the model to the starting state"""
    global step
    step = 0
    model.needs.reset()
    model.modulators.reset()
    model.events.reset()

def update():
    """Call this in every simulation cycle"""
    global step
    step +=1
    model.needs.update()
    model.modulators.update()
    model.events.update()

def get_needs():
    """Returns a dict of dicts with the agent's needs"""
    return model.needs.get_needs()

def get_consumptions():
    """Returns a dict of dicts with the agent's consumptive effectors"""
    return model.needs.get_consumptions()

def get_modulators():
    """Returns a dict of dicts with modulator values"""
    return model.modulators.get_modulators()

def get_aggregates():
    """Returns a dict of dicts with aggregates of pain, pleasure, urgency etc."""
    return model.modulators.get_aggregates()

def get_events():
    """Returns a sorted list of dicts with the currently anticipated events"""
    return model.events.get_events()

def get_data():
    """Returns a dict of all the above items"""
    return {"step": step,
            "needs": get_needs(),
            "consumptions": get_consumptions(),
            "modulators": get_modulators(),
            "aggregates": get_aggregates(),
            "events": get_events()}

def create_event(id, consumption_name="admiration", expected_reward=0, certainty=1, skill=0.8, expiration=-1):
    """Create a new expected event (can also be aversive).
    These are not actual events, but estimates of the agent.
    The creation of events gives us pleasure and pain signals, too."""
    model.events.create_event(id, consumption_name, expected_reward, certainty, skill, expiration)

def change_event(id, expected_reward = None, certainty = None, skill = None, expiration = None):
    """Change the expectations of an event. The amount of change results in pleasure and pain signals.
    Omitted parameters are left unchanged."""
    model.events.change_event(id, expected_reward, certainty, skill, expiration)

def drop_event(id):
    """This is effectively a change of the event, in which we also delete the event. We are disappointed, and
    hence update the exploration need"""
    model.events.drop_event(id)

def remove_event(id):
    """Delete the event from our expectations, without any other consequences"""
    model.events.remove_event(id)

def execute_event(id, reward=None):
    """Make an event happen, and react to its deviation from or confirmation of expectations.
    If no reward is given, we use the expected value of the event"""
    model.events.execute_event(id, reward)

def consume(consumption_name, reward=None):
    """Just consume an unexpected gain or loss. If no reward is given, we use the default value of the consumption"""
    model.events.consume(consumption_name, reward)

def set_goal(event_id):
    """Elevates an event to the goal; the associated consumption will become the intended action"""
    model.events.set_goal(event_id)
