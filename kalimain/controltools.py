# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
import tkinter as tk

from kalimain.observer import Observer


def combine_commands(*commands):
    def combined_command(*args, **kwargs):
        for cmd in commands:
            cmd(*args, **kwargs)
    return combined_command


class Command(Observer):

    def __init__(self, observable, *commands):

        self.observable = observable
        self.observable.add_observer(self)
        self.commands = commands

    def update(self, observable, arg):
        for cmd in self.commands:
            cmd()


class KState(Observer):
    def __init__(self, widget, observable, state_function):
        self.poll_state = state_function
        self.widget = widget
        self.observable = observable
        self.observable.add_observer(self)
        self.update(self.observable, None)

    def update(self, observable, arg):
        if self.poll_state():
            self.widget.config(state=tk.NORMAL)
        else:
            self.widget.config(state=tk.DISABLED)


class ToggleCursor(Observer):
    """ Cursor observing toggle button

    """

    def __init__(self, button, frame, cursor):
        self.button = button
        self.frame = frame
        self.cursor = cursor
        self.button.add_observer(self)

    def update(self, toggle_button, arg):
        if toggle_button.state == 1:
            self.frame.config(cursor=self.cursor)
        else:
            self.frame.config(cursor="")
