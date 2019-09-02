# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
import tkinter as tk
from tkinter import ttk

from kalimain.observer import Observable


class AutoScrollbar(ttk.Scrollbar):
    """
        A scrollbar that hides itself if it's not needed.
        Works only if you use the grid geometry manager
    """
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.pack_forget()
        else:
            if str(self.cget("orient")) == tk.HORIZONTAL:
                # Not sure why, but ttk scrollbar requires str to get the string from cget...
                self.pack(side="bottom", fill="x")
            else:
                self.pack(side="right", fill="y")

    def grid(self, **kw):
        raise tk.TclError('Cannot use grid with this widget')

    def place(self, **kw):
        raise tk.TclError('Cannot use place with this widget')


class KFrame(tk.Frame):

    pass


class KCFrame(KFrame):

    def __init__(self, master):
        super().__init__(master, bg="white")


class KListbox(tk.Listbox, Observable):

    height = 5
    bg = "white"
    exportselection = 0
    current = None

    item_ids = []

    @property
    def items(self):
        return list(self.get(0, tk.END))

    def __init__(self, master=None, *args, **kwargs):
        Observable.__init__(self)

        # ListBox initialization
        listbox_frame = KFrame(master)
        listbox_frame.pack(fill="both", expand="yes")
        scrollbar_v = AutoScrollbar(listbox_frame, orient=tk.VERTICAL)
        scrollbar_h = AutoScrollbar(listbox_frame, orient=tk.HORIZONTAL)
        super().__init__(listbox_frame, *args, yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set,
                         height=self.height, bg=self.bg, exportselection=self.exportselection)
        self.config(**kwargs)
        scrollbar_v.config(command=self.yview)
        scrollbar_h.config(command=self.xview)

        # Start polling
        self.poll()

    def append(self, item, item_id):
        items = self.items + [item]
        item_ids = self.item_ids + [item_id]
        self.populate(items, item_ids)

    def drop(self, item_id):
        self.delete(self.item_ids.index(item_id))
        self.item_ids.remove(item_id)

    def get_selected_id(self):
        if self.curselection():
            return self.item_ids[self.curselection()[0]]

    def get_selected_item(self):
        if self.curselection():
            return self.items[self.curselection()[0]]

    def poll(self):
        now = self.curselection()
        if now != self.current:
            self.set_changed()
            self.notify_observers()
            self.current = now
        self.after(250, self.poll)

    def populate(self, items, item_ids):
        self.item_ids = [i for _, i in sorted(zip(items, item_ids))]
        self.delete(0, tk.END)
        self.insert(tk.END, *sorted(items))


class KScale(tk.Scale):

    def __init__(self, master, initial_value=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.config(sliderrelief=tk.FLAT)

        if initial_value:
            self.set(initial_value)

    @property
    def length(self):
        return self.cget('to') - self.cget('from')


class KScaleImgFactor(KScale):

    def __init__(self, master, initial_value, *args, **kwargs):
        super().__init__(master, initial_value, *args, **kwargs)

        # Normalized factor (1.0) corresponds to initial value
        self.normalized_factor = initial_value

    @property
    def factor(self):
        return float(self.get()) / self.normalized_factor
