# -*- coding: utf-8 -*-

""" Module for window dialogs

Add here any window dialog necessary to Kalimain
"""
import tkinter as tk

from tkinter import font as tkfont
from abc import ABCMeta, abstractmethod

from kalimain.viewtools import FloatEntry
from kalimain.widgets import KListbox


class Dialog(tk.Toplevel, metaclass=ABCMeta):
    """ Base class for window dialogs

    Thanks to http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
    """

    def __init__(self, parent, title=None):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        # self.update_idletasks()
        # self.geometry("+%d+%d" % (self.root_x + (self.root_w - self.winfo_width())//2,
        #                           self.root_y + (self.root_h - self.winfo_height())/2))

        self.initial_focus.focus_set()

        self.wait_window(self)

    #
    # construction hooks

    @abstractmethod
    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = tk.Frame(self)

        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):

        return 1  # override

    @abstractmethod
    def apply(self):

        pass

    @property
    def root_x(self):
        return self.parent.winfo_rootx()

    @property
    def root_y(self):
        return self.parent.winfo_rooty()

    @property
    def root_w(self):
        return self.parent.winfo_width()

    @property
    def root_h(self):
        return self.parent.winfo_height()


class KDialog(Dialog):

    font = None
    font_size = 10

    # Entries
    name_entry = None
    description_entry = None

    # Format values
    label_width = 20
    label_anchor = 'nw'
    text_height = 10
    entry_width = 60

    def __init__(self, parent, title=None, default_name=None, default_description=None):

        self.default_name_entry = default_name
        self.default_description_entry = default_description
        super().__init__(parent, title)

    def body(self, master):
        self.font = tkfont.Font(master, size=self.font_size)

        # Labels
        tk.Label(master, text="Name:", anchor=self.label_anchor, width=self.label_width, font=self.font).grid(row=0)
        tk.Label(master, text="Description:", anchor=self.label_anchor, width=self.label_width, height=self.text_height,
                 font=self.font).grid(row=1)

        # Entries
        self.name_entry = tk.Entry(master, width=self.entry_width, bg="white", font=self.font)
        self.description_entry = tk.Text(master, height=self.text_height, width=self.entry_width, bg="white",
                                         font=self.font)
        self.name_entry.grid(row=0, column=1)
        self.description_entry.grid(row=1, column=1)

        if self.default_name_entry:
            self.name_entry.insert(0, self.default_name_entry)

        if self.default_description_entry:
            self.description_entry.insert(0, self.default_description_entry)

    def apply(self):
        name = self.name_entry.get().strip()
        if name:
            self.result = dict(name=name, description=self.description_entry.get("1.0", "end-1c"))


class ImageDialog(KDialog):
    """ Image's window dialog

    """

    def body(self, master):
        super().body(master)


class CaveDialog(KDialog):
    """ Cave's window dialog for cave's metadata implementation

    """
    latitude_entry = None
    longitude_entry = None

    def body(self, master):
        super().body(master)

        tk.Label(master, text="Latitude:", anchor=self.label_anchor, width=self.label_width, font=self.font).grid(row=2)
        tk.Label(master, text="Longitude:", anchor=self.label_anchor, width=self.label_width, font=self.font).grid(
            row=3)

        self.latitude_entry = FloatEntry(master, width=self.entry_width, bg="white")
        self.longitude_entry = FloatEntry(master, width=self.entry_width, bg="white")

        self.latitude_entry.grid(row=2, column=1)
        self.longitude_entry.grid(row=3, column=1)

        return self.name_entry  # initial focus

    def apply(self):
        super().apply()
        self.result.update(latitude=self.latitude_entry.get(),
                           longitude=self.longitude_entry.get())


class NewProjectDialog(KDialog):
    """ Project's dialog when user creates new project

    """
    pass


class OpenProjectDialog(Dialog):
    """ Project's dialog when user opens existing project

    """
    list_height = 20
    list_width = 20

    klistbox = None
    items = None

    def __init__(self, parent, items):
        self.items = items
        super().__init__(parent, "Open project")

    def body(self, master):
        super().body(master)

        self.klistbox = KListbox(master, width=self.list_width, height=self.list_height)
        self.klistbox.populate([item.name for item in self.items], [item.id for item in self.items])
        self.klistbox.grid(row=0, column=1)

    def apply(self):
        if self.klistbox.curselection():
            self.result = dict(project_id=self.klistbox.get_selected_id())
