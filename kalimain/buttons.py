# -*- coding: utf-8 -*-

""" All button classes used in kalimain

Centralize behavior and appearance here
"""
import tkinter as tk

from kalimain.controltools import combine_commands
from kalimain.observer import Observer, Observable


class KButton(tk.Button):
    pass


class KPanelButton(KButton):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(relief=tk.FLAT)


class ToggleButtonGroup(Observer):
    """ Group of toggle buttons

    """

    def __init__(self, buttons):
        super().__init__()
        self.buttons = buttons
        for button in self.buttons:
            button.add_observer(self)

    def switch_off(self):
        for button in self.buttons:
            if button.state == 1:
                button.toggle()

    def update(self, observable_toggle_button, arg):
        """ Update toggle buttons in toggle button group

        Switch other buttons off when one of the button is
        pressed. Only switch off buttons if they are on. As
        a result, corresponding callback commands are only
        called when a button passes from state=1 to state=0
        :param observable_toggle_button:
        :param arg:
        :return:
        """
        if observable_toggle_button.state == 1:
            buttons_to_switch_off = [button for button in self.buttons if button is not observable_toggle_button]
            for button in buttons_to_switch_off:
                if button.state == 1:
                    button.state = 0
                    button.command()  # Call command corresponding to toggle button


class KToggleButton(KButton, Observable):
    """ Toggle button

    """

    def __init__(self, master=None, command=None, *args, **kwargs):
        """ Build toggle button

        :param master:
        :param command:
        :param args:
        :param kwargs:
        """
        if command is None:
            KButton.__init__(self, master, command=self.toggle, *args, **kwargs)
        else:
            KButton.__init__(self, master, command=combine_commands(self.toggle, command), *args, **kwargs)
        Observable.__init__(self)
        self.state = 0
        self.command = command

    def set_command(self, command):
        self.config(command=combine_commands(self.toggle, command))
        self.command = command

    def toggle(self):
        if self.state == 1:
            self.state = 0
        else:
            self.state = 1
        self.set_changed()
        self.notify_observers()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state
        if new_state == 1:
            self.config(relief=tk.SUNKEN)
        else:
            self.config(relief=tk.RAISED)
