# -*- coding: utf-8 -*-

""" Module main description

More detailed description.
"""
import warnings
import tkinter as tk

from kalimain.controller import KController
from kalimain.exceptions import KCatcher
from kalimain.model import KModel
from kalimain.view import KView


# Try to make warnings as exceptions in order to use it with KCatcher
# (Not sure it's a good pattern though...)
warnings.filterwarnings('error')

# Tkinter exception catcher
tk.CallWrapper = KCatcher

# Main model & view
model = KModel()
view = KView(tk.Tk(), model)

# Main controller
c = KController(view, model)
c.run()
