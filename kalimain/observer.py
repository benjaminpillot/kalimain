# -*- coding: utf-8 -*-

""" Observer pattern

Observer pattern implemented thanks to:
https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Observer.html
"""
from kalimain.synchronization import Synchronization, synchronize


class Observer:
    def update(self, observable, arg):
        """Called when the observed object is
        modified. You call an Observable object's
        notifyObservers method to notify all the
        object's observers of the change."""
        pass


class Observable(Synchronization):
    def __init__(self):
        self.obs = []
        self.changed = 0
        Synchronization.__init__(self)

    def add_observer(self, observer):
        if observer not in self.obs:
            self.obs.append(observer)

    def delete_observer(self, observer):
        self.obs.remove(observer)

    def notify_observers(self, arg=None):
        """If 'changed' indicates that this object
        has changed, notify all its observers, then
        call clearChanged(). Each observer has its
        update() called with two arguments: this
        observable object and the generic 'arg'."""

        self.mutex.acquire()
        try:
            if not self.changed:
                return
            # Make a local copy in case of synchronous
            # additions of observers:
            local_array = self.obs[:]
            self.clear_changed()
        finally:
            self.mutex.release()
        # Updating is not required to be synchronized:
        for observer in local_array:
            observer.update(self, arg)

    def delete_observers(self):
        self.obs = []

    def set_changed(self):
        self.changed = 1

    def clear_changed(self):
        self.changed = 0

    def has_changed(self):
        return self.changed

    def count_observers(self):
        return len(self.obs)


synchronize(Observable, "add_observer delete_observer delete_observers " + "set_changed clear_changed has_changed " +
            "count_observers")
