# -*- coding: utf-8 -*-

""" Simple emulation of Java's synchronized keyword, from Peter Norvig

See https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Observer.html
"""
import threading


def synchronized(method):
    def f(*args):
        self = args[0]
        self.mutex.acquire()
        try:
            return method(*args)
        finally:
            self.mutex.release()
    return f


def synchronize(aclass, names=None):
    """Synchronize methods in the given class.
    Only synchronize the methods whose names are
    given, or all methods if names=None."""
    if isinstance(names, str):
        names = names.split()
    for (name, val) in aclass.__dict__.items():
        if callable(val) and name != '__init__' and (names is None or name in names):
            setattr(aclass, name, synchronized(val))
            # aclass.__dict__[name] = synchronized(val)


# You can create your own self.mutex, or inherit
# from this class:
class Synchronization:
    def __init__(self):
        self.mutex = threading.RLock()
