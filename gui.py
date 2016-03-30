# -*- coding: utf-8 -*-

"""
Tkinter UI definition
"""

__author__ = 'joscha'
__date__ = '3/15/16'

from tkinter import *
from tkinter import ttk, filedialog, messagebox
from configuration import Settings
import math


import simulation as simulation


from helper_widgets import MainMenu, SimFrame, ConfigDialog


app = Tk()

app.minsize(500, 250)

# menus
app.option_add('*tearOff', FALSE)
menubar = MainMenu(app)
for diagram in simulation.diagrams:
    key = diagram.key
    menubar.menu_plot.add_command(label= "Plot " + key, command=lambda key=key : app.open_diagram(key))
app.config(menu=menubar)

# diagram
app.open_diagrams = {}

# frames
content_frame = ttk.Frame(app)

app.columnconfigure(0, weight=1)
app.rowconfigure(0, weight=1)

content_frame.grid(column=0, row=0, sticky=(N, W, E, S))
content_frame.columnconfigure(0, weight=1)
content_frame.rowconfigure(0, weight=1)

simulator = SimFrame(content_frame)
simulator.grid(row=0, column=0, sticky=(W, E))

spacer = ttk.Frame(content_frame)
spacer.grid(row=98, column=0, sticky=(W, E, N, S))
spacer.rowconfigure(0, weight=1)


status = StringVar()
status_bar = ttk.Frame(content_frame, padding = (6, 6, 6, 6), relief="sunken")
status_bar.grid(row=99, column=0, sticky=(W, E, N, S))
status_label = ttk.Label(status_bar, textvariable = status)
status_label.grid(row=0, column=0, sticky=(W, E, N, S))


# simulation thread
running = False
gen_running = True

reset_simulation()

def open_diagram(app, key):
    """open a diagram window for the given type"""
    if not key in app.open_diagrams:
        for Diagram in simulation.diagrams:
            if Diagram.key == key:
                app.open_diagrams[key] = Diagram(app, app.simulation)


def calculate_agent_coordinates(app, agents):
    """Arrange the agents in a circle on the canvas"""
    app.agent_coordinates = []
    origin = (350, 350)
    r = 300
    k = len(agents)
    for n in range(0, k):
        app.agent_coordinates.append(
            (r * math.cos(2 * math.pi * n / k) + origin[0],
             r * math.sin(2 * math.pi * n / k) + origin[1])
        )


def configure_simulation(app):
    """Configure simulation settings and initialize values"""
    ConfigDialog(app)  # will call reset simulation for us

def run_simulation(app):
    """Starts a runner that will trigger simulation steps"""
    app.status.set("running")
    app.running = True
    app.gen_running = False
    while app.running:
        app.simulation.step()
        app.update()

def stop_simulation(app):
    """Pauses the runner that triggers simulation steps"""
    app.running = False
    app.gen_running = False
    app.status.set("paused")

def reset_simulation(app):
    """Initializes all values to original settings and sets up the canvas"""

    app.running = False
    app.gen_running = False

    app.simulation = simulation.Simulation(app)  # the app parameter tells the sim where to find the gui

    diagrams = list(app.open_diagrams.values())
    for plot in diagrams:
        plot.destroy()  # close diagrams because they are bound to old data sets

    app.setup_need_drawings(app.simulation.agents)
    app.display_simstep()
    app.display_generation()
    app.status.set("ready to start")


def step_simulation(app):
    """Advances the simulation by a single step"""
    app.running = False
    app.gen_running = False
    app.status.set("step")
    app.simulation.step()
    app.status.set("paused")

def advance_one_generation(app):
    """Advances the simulation by a full generation"""
    app.running = False
    app.gen_running = False
    app.status.set("calculating...")
    app.update()
    app.simulation.calculate_generation()
    app.status.set("paused")

def calculate_all(app):
    """Perform the complete calculation"""
    app.running = False
    app.gen_running = True
    app.status.set("calculating...")
    while app.simulation.current_generation < Settings.number_of_generations and app.gen_running:
        app.simulation.calculate_generation()
        app.update()
    app.status.set("paused")

def export_simulation_data(app):
    filename = filedialog.asksaveasfilename()
    print("export simulation "+filename)

def export_plot(app):
    print("export diagram")

def show_contact(app):
    messagebox.showinfo(title="Contact", message="Joscha Bach, 2014\njoscha@mit.edu")

def setup_agent_drawings(app, agents):
    """Draw agents and their reputation values"""
    c = app.simulator.canvas
    app.calculate_need_coordinates(agents)
    app.simulator.canvas.delete(ALL)
    radius = 10
    offset = 18
    app.agent_drawings = []
    app.agent_deception_labels = []
    app.agent_reputation_labels = []
    app.agent_value_labels = []

    for i, (x, y) in enumerate(app.agent_coordinates):
        app.agent_drawings.append(c.create_oval(x-radius, y-radius, x+radius, y+radius,
                                                                     outline="black", fill="lightblue", width=2))
        app.agent_deception_labels.append(c.create_text(x, y - offset,
                                                         text=agents[i]["deception probability"], fill="brown"))
        app.agent_value_labels.append(c.create_text(x, y+offset, text=agents[i]["value"], fill="orange"))
        app.agent_reputation_labels.append(c.create_text(x, y+2*offset,
                                                          text=agents[i]["reputation"], fill="blue"))

    app.current_relation = None  # no line is drawn between agent images

def update_agent_value_labels(app, agent_index, agent):
    """paints the updated values on the canvas"""
    app.simulator.canvas.itemconfig(app.agent_deception_labels[agent_index],
                                     text= "%.3f" % agent["deception probability"])
    app.simulator.canvas.itemconfig(app.agent_value_labels[agent_index], text=agent["value"])
    app.simulator.canvas.itemconfig(app.agent_reputation_labels[agent_index], text=agent["reputation"])


def draw_relation(app, agent_index1, agent_index2, relation=None):
    """draws a visible link between two agents, of type "defect" or "cooperate".
    the line index is then stored in app.current_relation, so that it can be deleted later"""
    if agent_index1 is None or agent_index2 is None:
        app.delete_current_relation()
        return
    if relation is "defect":
        color = "red"
    elif relation is "cooperate":
        color = "green"
    else:
        color = "black"

    if app.current_relation:
        app.simulator.canvas.coords(app.current_relation,
                                     app.agent_coordinates[agent_index1][0],
                                     app.agent_coordinates[agent_index1][1],
                                     app.agent_coordinates[agent_index2][0],
                                     app.agent_coordinates[agent_index2][1])
        app.simulator.canvas.itemconfig(app.current_relation, fill=color, width=2)
    else:
        app.current_relation = app.simulator.canvas.create_line(app.agent_coordinates[agent_index1],
                                             app.agent_coordinates[agent_index2],
                                             arrow = "last", fill = color, width=2)

def delete_current_relation(app):
    """removes the currently drawn line on the canvas, if there is one"""
    if app.current_relation:
        app.simulator.canvas.delete(app.current_line)
        app.current_relation = None

def display_simstep(app):
    """updates the simstep display in the gui"""
    app.simulator.simstep.set(app.simulation.current_simstep)
    app.update_plots()

def display_generation(app):
    """updates the generation display in the gui"""
    app.simulator.generation.set(app.simulation.current_generation)


def update_plots(app):
    try:
        for plot in app.open_diagrams.values():
            plot.update_diagram()
    except RuntimeError:  # thread hates it when we add new diagrams while running
        pass

