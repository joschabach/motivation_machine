# -*- coding: utf-8 -*-

"""
More Tkinter UI definition
"""

__author__ = 'joscha'
__date__ = '3/15/16'

from tkinter import *
from tkinter import ttk
from configuration import Settings
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SimFrame(Frame):
    """Definition of the simulator wiget"""
    def __init__(self, parent=None, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)

        self.app = self.master.master

        self.visible = True


        self.icon_reset = PhotoImage(file="icons/media-previous.gif")
        self.icon_run = PhotoImage(file="icons/media-play.gif")
        self.icon_step = PhotoImage(file="icons/media-next.gif")
        self.icon_ffwd = PhotoImage(file="icons/media-fast-forward.gif")
        self.icon_stop = PhotoImage(file="icons/media-pause.gif")
        self.icon_fstep = PhotoImage(file="icons/media-fast-next.gif")

        self.grid(column=0, row=0, sticky=(W, E, N, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0, minsize=40)
        self.rowconfigure(1, weight=1)


        # toolbar
        toolbar = ttk.Frame(self, relief="raised", borderwidth=1, padding=(12, 6, 12, 6))
        toolbar.grid(column=0, row=0, sticky=(W, E, N))
        toolbar.columnconfigure(3, weight=1)

        self.toolbar = toolbar

        ttk.Label(toolbar, text="Simulation:").grid(row=0, column=1, sticky=E)


        spacer = ttk.Frame(toolbar)
        spacer.grid(row=0, column=3, sticky=(W, E))
        spacer.columnconfigure(1, weight = 1, minsize=2)

        toolbar.button_reset = ttk.Button(toolbar, image=self.icon_reset, command=self.app.reset_simulation)
        toolbar.button_reset.grid(row = 0, column = 4)

        toolbar.button_run = ttk.Button(toolbar, image=self.icon_run, command=self.app.run_simulation)
        toolbar.button_run.grid(row=0, column=5)

        toolbar.button_step = ttk.Button(toolbar, image=self.icon_step, command=self.app.step_simulation)
        toolbar.button_step.grid(row=0, column=6)

        # toolbar.button_generation = ttk.Button(toolbar, image=self.icon_ffwd, command=self.app.calculate_all)
        # toolbar.button_generation.grid(row=0, column=7)
        #
        # toolbar.button_generation = ttk.Button(toolbar, image=self.icon_fstep, command=self.app.advance_one_generation)
        # toolbar.button_generation.grid(row=0, column=8)

        toolbar.button_stop = ttk.Button(toolbar, image=self.icon_stop, command=self.app.stop_simulation)
        toolbar.button_stop.grid(row=0, column=9)

        self.simstep = IntVar()
        ttk.Label(toolbar, text="Step:").grid(row=0, column=10, sticky=E)
        self.step_field = ttk.Entry(toolbar, width=10, textvariable= self.simstep, state="readonly")
        self.step_field.grid(row=0, column=11)

        self.generation = IntVar()
        ttk.Label(toolbar, text="Generation:").grid(row=0, column=12, sticky=E)
        self.generation_field = ttk.Entry(toolbar, width=10, textvariable = self.generation, state="readonly")
        self.generation_field.grid(row=0, column=13)


        # body
        self.body = ttk.Frame(self)
        self.body.grid(column=0, row=1, sticky=(W, E, N, S))
        self.body.columnconfigure(0, weight=1)
        self.body.rowconfigure(0, weight=1)
        self.body.columnconfigure(1, weight=0)

        canvasframe = ttk.Frame(self.body)
        canvasframe.grid(column=0, row=0, sticky=(W, E, N, S))
        canvasframe.columnconfigure(0, weight=1)
        canvasframe.rowconfigure(0, weight=1)

        if Settings.fullscreen:
            self.canvas = Canvas(canvasframe)
            self.canvas.config(width=self.winfo_width(), height=self.winfo_height(), bg='black')
            self.grid(row=0, column=0, sticky=(W, E, N, S))
            self.rowconfigure(0, weight=1)
            self.columnconfigure(0, weight=1)
        else:
            self.canvas = ScrollableCanvas(canvasframe)


        pane = ttk.Frame(self.body, padding=(12, 12, 12, 12))
        pane.grid(column=1, row=0, sticky=(W, E, N))
        pane.rowconfigure(0, weight=1)


class ConfigDialog(Toplevel):
    def __init__(self, parent=None, *args, **kwargs):
        Toplevel.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.title("Configure simulation")
        self.resizable(FALSE, FALSE)

        content = ttk.Frame(self, padding = (12, 12, 12, 12))
        content.grid(row =0, column=0, sticky = (W, E, N, S))

        def key_to_labeltext(string):  # 'variable_name_string' -> 'Variable name string'
            return (string[0].upper() + string[1:]).replace("_", " ")

        self.configvalues = {}

        config = [key for key in dir(Settings) if not key.startswith('_')]

        for index, key in enumerate(config):
            value = getattr(Settings, key)
            if isinstance(value, int):
                self.configvalues[key] = IntVar()
            elif isinstance(value, float):
                self.configvalues[key] = DoubleVar()
            else:
                self.configvalues[key] = StringVar()
            self.configvalues[key].set(value)
            ttk.Label(content, text=key_to_labeltext(key)).grid(row=index, column=0, sticky=E)
            ttk.Entry(content, textvariable = self.configvalues[key],
                      width=9).grid(row=index, column=1, sticky=(W, E))

        buttonbox = ttk.Frame(content, padding = (12, 20, 0, 10))
        buttonbox.grid(row = len(config), column=0, columnspan=2, sticky = (E, N, S))

        ttk.Button(buttonbox, text="Cancel", command=self.destroy).grid(row=0, column=0, sticky=E)
        ttk.Button(buttonbox, text="Apply values", default = "active",
                   command=self.apply_values).grid(row=0, column=1, sticky=E)

    def apply_values(self):
        """Close config window, update game settings, and start the simulator"""
        self.destroy()
        for key, value in self.configvalues.items():
            setattr(Settings, key, self.configvalues[key].get())
        self.parent.reset_simulation()


class ScrollableCanvas(Canvas):

    def __init__(self, parent=None, *args, **kwargs):
        Canvas.__init__(self, parent, *args, **kwargs)

        self._width =  1200
        self._height = 980

        self._starting_drag_position = ()

        self.config(width = self._width, height=self._height, bg='white')

        # scrollbars
        self.sbarV = Scrollbar(self.master, orient=VERTICAL)
        self.sbarH = Scrollbar(self.master, orient=HORIZONTAL)

        self.sbarV.config(command=self.yview)
        self.sbarH.config(command=self.xview)

        self.config(yscrollcommand=self.sbarV.set)
        self.config(xscrollcommand=self.sbarH.set)

        self.sbarV.grid(row=0, column=1, sticky=(N, S))
        self.sbarH.grid(row=1, column=0, sticky=(E, W))

        # mouse wheel scroll bindings
        self.bind('<4>', lambda event: self.yview('scroll', -1, 'units'))
        self.bind('<5>', lambda event: self.yview('scroll', 1, 'units'))

        # dragging canvas with mouse middle button
        self.bind("<Button-2>", self.__start_scroll)
        self.bind("<B2-Motion>", self.__update_scroll)
        self.bind("<ButtonRelease-2>", self.__stop_scroll)

        self.grid(row=0, column=0, sticky=(W, E, N, S))
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)


    def __start_scroll(self, event):
        """set the scrolling increment. value of 0 is unlimited and very fast, set it to 1,2,3 to make it slower"""
        self.config(yscrollincrement=3)
        self.config(xscrollincrement=3)

        self._starting_drag_position = (event.x, event.y)

        self.config(cursor="fleur")


    def __update_scroll(self, event):
        deltaX = event.x - self._starting_drag_position[0]
        deltaY = event.y - self._starting_drag_position[1]

        self.xview('scroll', deltaX, 'units')
        self.yview('scroll', deltaY, 'units')

        self._starting_drag_position =  (event.x, event.y)


    def __stop_scroll(self, event):
        """set scrolling speed back to 0, so that mouse scrolling works as expected."""
        self.config(xscrollincrement=0)
        self.config(yscrollincrement=0)

        self.config(cursor="")



class MainMenu(Menu):
    def __init__(self, *args, **kwargs):
        Menu.__init__(self, *args, **kwargs)

        menu_simulation = Menu(self)
        self.add_cascade(menu = menu_simulation, label='Simulation')
        self.menu_plot = Menu(self)
        self.add_cascade(menu=self.menu_plot, label='Diagrams')
        menu_help = Menu(self)
        self.add_cascade(menu = menu_help, label='Help')

        app = self.master

        menu_simulation.add_command(label='Configure...', command = app.configure_simulation)
        menu_simulation.add_separator()
        menu_simulation.add_command(label='Run', command = app.run_simulation)
        menu_simulation.add_command(label='Reset', command=app.reset_simulation)
        menu_simulation.add_command(label='Save data...', command=app.export_simulation_data)

        menu_help.add_command(label='Contact', command=app.show_contact)


class Diagram(Toplevel):
    """A matplotlib window that displays an updateable diagram.
    parent: root window
    data: where we get our values from
    key: the key of the plot window, must be unique
    title: optional window title
    """

    window_title = "Diagram"
    key = "diagram"

    def __init__(self, parent, simulation, *args, **kwargs):
        Toplevel.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.title(self.window_title)
        self.bind("<Destroy>", self.destroy)

        self.simulation = simulation

        figure = plt.Figure(figsize=(5, 4), dpi=100)
        self.subplot = figure.add_subplot(111)

        plt.ion()

        self.canvas = FigureCanvasTkAgg(figure, master=self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        self.update_diagram()


    def update_diagram(self):
        """re-reads the datasource and redraws the diagram accordingly"""
        self.plot()
        self.canvas.draw()

    def plot(self):
        """overwrite this method to produce a different diagram type"""
        data = self.simulation.log
        if len(data):
            values = [step["needs"]["food"]["value"] for step in data]
            self.subplot.plot(values, color="orange", linewidth=1.0)

    def destroy(self):
        self.parent.open_diagrams.pop(self.key, None)  # remove from index of open plot windows
        Toplevel.destroy(self)

