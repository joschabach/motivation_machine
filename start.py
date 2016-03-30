# -*- coding: utf-8 -*-

"""
run and test a simulation of the motivation model
"""

__author__ = 'joscha'
__date__ = '3/15/16'

from configuration import APPTITLE, VERSION

import argparse
from widgets import GuiApp

def main():
    app = GuiApp()
    app.title("%s v%s" % (APPTITLE, VERSION))

    # put tkinter windows on top on macos
    app.lift()
    app.call('wm', 'attributes', '.', '-topmost', True)
    app.after_idle(app.call, 'wm', 'attributes', '.', '-topmost', False)

    app.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the %s desktop app." % APPTITLE)
    args = parser.parse_args()
    main()
