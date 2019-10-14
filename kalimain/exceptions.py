# -*- coding: utf-8 -*-

""" Module main description

More detailed description.
"""
from tkinter import messagebox


class KCatcher:
    """ Catch GUI exceptions

    """
    def __init__(self, func, subst, widget):
        self.func = func
        self.subst = subst
        self.widget = widget

    def __call__(self, *args):
        try:
            if self.subst:
                args = self.subst(*args)
            return self.func(*args)
        except Exception as e:
            if isinstance(e, Warning):
                messagebox.showwarning(title=e.__class__.__name__, message=e)
            else:
                messagebox.showerror(title=e.__class__.__name__, message=e)


class KException(Exception):
    pass


class KWarning(Warning):
    pass
# class KException(Observable, Exception):
#
#     def __init__(self, *args):
#         Exception.__init__(self, *args)
#         Observable.__init__(self)
#         self.add_observer(KalimainDisplayError())
#         self.notify_observers(str(self))
#
#     def notify_observers(self, arg=None):
#         self.set_changed()
#         super().notify_observers(arg)


# class KWarning(Observable, Warning):
#
#     def __init__(self, *args):
#         Warning.__init__(self, *args)
#         Observable.__init__(self)
#         self.add_observer(KalimainDisplayWarning())
#         self.notify_observers(str(self))
#
#     def notify_observers(self, arg=None):
#         self.set_changed()
#         super().notify_observers(arg)


# class KalimainDisplayError(Observer):
#
#     def update(self, observable, arg):
#         messagebox.showerror(title=observable.__class__.__name__, message=arg)


# class KalimainDisplayWarning(Observer):
#
#     def update(self, observable, arg):
#         messagebox.showwarning(title=observable.__class__.__name__, message=arg)


class ImageError(KException):
    pass


class EntryError(KException):
    pass


class FloatEntryError(EntryError):
    pass


class DeleteWarning(KWarning):
    pass


class ReadFileWarning(KWarning):
    pass


class ApiConnectionWarning(KWarning):
    pass


class DuplicateElementWarning(KWarning):
    pass


class InvalidNameWarning(KWarning):
    pass
