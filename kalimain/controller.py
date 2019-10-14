# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
import os
import tkinter as tk
from _tkinter import TclError
from abc import abstractmethod
from tkinter import messagebox, filedialog
from tkinter.ttk import Style

from kalimain import __version__ as __kversion__
from kalimain import __copyright__ as __kcopyright__
from kalimain.buttons import ToggleButtonGroup
from kalimain.controltools import Command, KState
from kalimain.dialog import CaveDialog, ImageDialog, NewProjectDialog
from kalimain.observer import Observer


class Controller:

    # Observer classes
    class AddObserver(Observer):
        def __init__(self, view):
            self.view = view

    def __init__(self, view, model):
        self.model = model
        self.view = view
        # self.set_observers()
        self.add_observers_to_notifiers()
        self.add_controls()

    @abstractmethod
    def add_observers_to_notifiers(self):
        pass

    @abstractmethod
    def add_controls(self):
        pass


class MainController(Controller):

    # Controls
    toggle_button_group = None
    mouse_button1 = None

    ##################
    # Observer classes

    class AddPointObserver(Controller.AddObserver):

        def update(self, observable, points):
            self.view.canvas_points.append(self.view.draw_point(points[-1]))
            if len(points) > 1:
                self.view.canvas_lines.append(self.view.draw_line(points[-2:]))
            self.view.notify_observers()

    class AddHandObserver(Controller.AddObserver):

        def update(self, observable, hand):
            self.view.freeze_hand()
            self.view.add_hand(hand)
            self.view.reset_canvas_objects()
            self.view.notify_observers()

    class DeleteHandObserver(Controller.AddObserver):

        def update(self, observable, hand_id):
            self.view.delete_hand(hand_id)
            self.view.notify_observers()

    class DeleteLastPointObserver(Controller.AddObserver):

        def update(self, observable, arg):
            self.view.delete_last_point()
            self.view.notify_observers()

    class HandInfoObserver(Controller.AddObserver):

        def update(self, observable, info):
            self.view.disp_hand_info(info)

    class AddImageObserver(Controller.AddObserver):

        def update(self, observable, image):
            self.view.image_listbox.append(image.name, image.id)

    class DeleteImageObserver(Controller.AddObserver):

        def update(self, observable, image_id):
            self.view.clear_canvas()
            self.view.image_listbox.drop(image_id)
            self.view.notify_observers()

    class SetImageObserver(Controller.AddObserver):

        def update(self, observable, image):
            self.view.clear_canvas()
            self.view.load_canvas(image)
            self.view.notify_observers()

    class AddCaveObserver(Controller.AddObserver):

        def update(self, observable, cave):
            self.view.cave_listbox.append(cave.name, cave.id)

    class DeleteCaveObserver(Controller.AddObserver):

        def update(self, observable, cave_id):
            self.view.cave_listbox.drop(cave_id)

    class SetCaveObserver(Controller.AddObserver):

        def update(self, observable, cave):
            self.view.image_listbox.populate([img.name for img in cave.images], [img.id for img in cave.images])

    class SetProjectObserver(Controller.AddObserver):

        def update(self, observable, project):
            self.view.cave_listbox.populate([cave.name for cave in project.caves], [cave.id for cave in project.caves])

    ####################
    # Controller methods
    def _add_commands(self):
        """ Add commands to view buttons

        :return:
        """
        # Left bar buttons
        for i, button in enumerate(self.view.left_bar_buttons):
            button.config(command=self.__getattribute__("on_left_bar_button%d" % i))

        for i, button in enumerate(self.view.left_bar_toggle_buttons):
            button.set_command(self.__getattribute__("on_toggle_button%d" % i))

        # Control panel
        self.view.add_cave_button.config(command=self.on_new_cave)
        self.view.delete_cave_button.config(command=self.on_delete_cave)
        self.view.add_image_button.config(command=self.on_add_image)
        self.view.delete_image_button.config(command=self.on_delete_image)

    def _add_update_controls(self):
        """ Add update function rules to buttons

        :return:
        """
        def cliststate():
            return True if self.view.cave_listbox.curselection() else False

        def imgliststate():
            return True if self.view.image_listbox.curselection() else False

        def imgstate():
            return True if self.view.image else False

        def handstate():
            return True if self.view.hands else False

        def undostate():
            return True if self.view.canvas_points else False

        def ptstate():
            return True if len(self.view.canvas_points) == 12 else False

        self.view.left_bar_buttons[0].kstate = KState(self.view.left_bar_buttons[0], self.view, ptstate)
        self.view.left_bar_buttons[1].kstate = KState(self.view.left_bar_buttons[1], self.view, undostate)
        self.view.left_bar_toggle_buttons[0].kstate = KState(self.view.left_bar_toggle_buttons[0], self.view, imgstate)
        self.view.left_bar_toggle_buttons[1].kstate = KState(self.view.left_bar_toggle_buttons[1], self.view, imgstate)
        self.view.left_bar_toggle_buttons[2].kstate = KState(self.view.left_bar_toggle_buttons[2], self.view, handstate)
        self.view.left_bar_toggle_buttons[3].kstate = KState(self.view.left_bar_toggle_buttons[3], self.view, handstate)
        self.view.delete_cave_button.kstate = KState(self.view.delete_cave_button, self.view.cave_listbox, cliststate)
        self.view.add_image_button.kstate = KState(self.view.add_image_button, self.view.cave_listbox, cliststate)
        self.view.delete_image_button.kstate = KState(self.view.delete_image_button, self.view.image_listbox,
                                                      imgliststate)
        for scale in self.view.image_enhance_scale:
            scale.kstate = KState(scale, self.view, imgstate)

    def add_controls(self):
        """ Add controls to widgets

        :return:
        """
        # Toggle controls
        self.toggle_button_group = ToggleButtonGroup(self.view.left_bar_toggle_buttons)
        self.toggle_button_group.cmd = Command(self.view.image_listbox, self.toggle_button_group.switch_off)

        # Listbox controls
        self.view.cave_listbox.cmd = Command(self.view.cave_listbox, self.on_select_cave)
        self.view.image_listbox.cmd = Command(self.view.image_listbox, self.on_select_image)

        # Image enhance controls
        for i, scale in enumerate(self.view.image_enhance_scale):
            scale.config(command=self.__getattribute__("on_scale%d" % i))

        # Add commands to buttons
        self._add_commands()

        # Add update controls
        self._add_update_controls()

    # def set_observers(self):
    #     """ Set view observers
    #
    #     :return:
    #     """
    #     self.add_image_observer = MainController.AddImageObserver(self.view)
    #     self.delete_image_observer = MainController.DeleteImageObserver(self.view)
    #     self.set_image_observer = MainController.SetImageObserver(self.view)
    #     self.add_cave_observer = MainController.AddCaveObserver(self.view)
    #     self.delete_cave_observer = MainController.DeleteCaveObserver(self.view)
    #     self.set_cave_observer = MainController.SetCaveObserver(self.view)
    #     self.add_point_observer = MainController.AddPointObserver(self.view)
    #     self.add_hand_observer = MainController.AddHandObserver(self.view)
    #     self.delete_hand_observer = MainController.DeleteHandObserver(self.view)
    #     self.delete_last_point_observer = MainController.DeleteLastPointObserver(self.view)
    #     self.hand_info_observer = MainController.HandInfoObserver(self.view)
    #     self.set_project_observer = MainController.SetProjectObserver(self.view)

    def add_observers_to_notifiers(self):
        """ Add observers to notifiers

        :return:
        """
        self.model.image_model.add_object_notifier.add_observer(MainController.AddImageObserver(self.view))
        self.model.image_model.delete_object_notifier.add_observer(MainController.DeleteImageObserver(self.view))
        self.model.image_model.set_object_notifier.add_observer(MainController.SetImageObserver(self.view))
        self.model.cave_model.add_object_notifier.add_observer(MainController.AddCaveObserver(self.view))
        self.model.cave_model.delete_object_notifier.add_observer(MainController.DeleteCaveObserver(self.view))
        self.model.cave_model.set_object_notifier.add_observer(MainController.SetCaveObserver(self.view))
        self.model.point_model.add_point_notifier.add_observer(MainController.AddPointObserver(self.view))
        self.model.hand_model.add_object_notifier.add_observer(MainController.AddHandObserver(self.view))
        self.model.hand_model.delete_object_notifier.add_observer(MainController.DeleteHandObserver(self.view))
        self.model.point_model.delete_last_point_notifier.add_observer(MainController.DeleteLastPointObserver(
            self.view))
        self.model.hand_model.hand_info_notifier.add_observer(MainController.HandInfoObserver(self.view))
        self.model.project_model.set_object_notifier.add_observer(MainController.SetProjectObserver(self.view))

    ##################
    # Callback methods
    def on_left_bar_button0(self):
        self.model.hand_model.add_hand()

    def on_left_bar_button1(self):
        self.model.point_model.delete_last_point()

    def on_toggle_button0(self):
        if self.view.left_bar_toggle_buttons[0].state == 1:
            self.mouse_button1 = self.view.image.canvas.bind("<Button-1>", self.on_mouse_button_draw)
        else:
            self.view.image.canvas.unbind("<Button-1>", self.mouse_button1)

    def on_toggle_button1(self):
        if self.view.left_bar_toggle_buttons[1].state == 1:
            self.view.image.bind_mouse_moves()
        else:
            self.view.image.unbind_mouse_moves()

    def on_toggle_button2(self):
        if self.view.left_bar_toggle_buttons[2].state == 1:
            self.mouse_button1 = self.view.image.canvas.bind("<Button-1>", self.on_mouse_button_erase)
        else:
            self.view.image.canvas.unbind("<Button-1>", self.mouse_button1)

    def on_toggle_button3(self):
        if self.view.left_bar_toggle_buttons[3].state == 1:
            self.mouse_button1 = self.view.image.canvas.bind("<Button-1>", self.on_mouse_button_info)
        else:
            self.view.image.canvas.unbind("<Button-1>", self.mouse_button1)

    def on_new_cave(self):
        """ Add cave button callback

        :return:
        """
        meta = CaveDialog(self.view.root, title="New cave", default_name="Cave %d" % (len(
            self.view.cave_listbox.items) + 1))
        if meta.result:
            self.model.cave_model.add_cave(**meta.result)

    def on_delete_cave(self):
        answer = messagebox.askokcancel("Delete cave", "Are you sure you want to delete '%s'?" %
                                        self.view.cave_listbox.get_selected_item())
        if answer:
            self.model.cave_model.delete_object(self.view.cave_listbox.get_selected_id())

    def on_add_image(self):
        """ Add image button callback

        :return:
        """
        # TODO: change initial dir for file dialog
        file = filedialog.askopenfile(initialdir="/home/benjamin/Documents/kalimain/sample", title='Import image')
        if file:
            meta = ImageDialog(self.view.root, title="Add image", default_name=os.path.splitext(
                os.path.basename(file.name))[0])
            if meta.result:
                self.model.image_model.add_image(file.name, **meta.result)

    def on_delete_image(self):
        answer = messagebox.askokcancel("Delete image", "Are you sure you want to delete '%s'?" %
                                        self.view.image_listbox.get_selected_item())
        if answer:
            self.model.image_model.delete_object(self.view.image_listbox.get_selected_id())

    ##################
    # Listbox controls
    def on_select_cave(self):
        if self.view.cave_listbox.curselection():
            cave_id = self.view.cave_listbox.item_ids[self.view.cave_listbox.index(tk.ANCHOR)]
            self.model.cave_model.set_object(cave_id)

    def on_select_image(self):
        if self.view.image_listbox.curselection():
            image_id = self.view.image_listbox.item_ids[self.view.image_listbox.index(tk.ANCHOR)]
            self.model.image_model.set_object(image_id)
        else:
            self.view.clear_canvas()

    ########################
    # Image enhance controls
    def on_scale0(self, _):
        """ Color scale

        :return:
        """
        self.view.image.enhance(self.view.get_scale_factor())

    def on_scale1(self, _):
        """ Brightness scale

        :return:
        """
        self.view.image.enhance(self.view.get_scale_factor())

    def on_scale2(self, _):
        """ Contrast scale

        :return:
        """
        self.view.image.enhance(self.view.get_scale_factor())

    def on_scale3(self, _):
        """ Sharpness scale

        :return:
        """
        self.view.image.enhance(self.view.get_scale_factor())

    #############
    # Mouse binds
    def on_mouse_button_draw(self, event):
        """ Draw clicked button callback

        Add point when mouse button is clicked and cursor located within image
        :param event:
        :return:
        """
        xy = self.view.containerxy(event)
        if xy:
            self.model.point_model.add_point(x=xy[0], y=xy[1])

    def on_mouse_button_erase(self, event):
        """ Erase clicked button callback

        Erase hand when mouse button is clicked within
        :param event:
        :return:
        """
        hand_id = self.view.get_cursor_hand_id(event)
        if hand_id:
            answer = messagebox.askokcancel("Delete hand", "Are you sure you want to delete this hand?")
            if answer:
                self.model.hand_model.delete_object(hand_id)

    def on_mouse_button_info(self, event):
        """ Get info about hands when moving over with the cursor

        :return:
        """
        hand_id = self.view.get_cursor_hand_id(event)
        if hand_id:
            self.model.hand_model.get_hand_info(hand_id)


class DataDisplayController(Controller):

    def add_controls(self):
        pass

    def add_observers_to_notifiers(self):
        pass


class KController(Controller):

    tab_controllers = (MainController, DataDisplayController)

    # Observer classes
    class AddProjectObserver(Controller.AddObserver):

        def update(self, observable, project):
            pass

    def __init__(self, view, model):
        """ Build KController class instance

        """
        super().__init__(view, model)

        # Sub controllers
        self.controllers = [control(view, self.model) for control, view in zip(self.tab_controllers, self.view.views)]

    def run(self):
        self.view.root.style = Style()
        self.view.root.style.theme_use("clam")
        self.view.root.title("Kalimain")
        self.view.root.deiconify()
        self.view.root.mainloop()

    def add_controls(self):
        """ Add controls to Menu bar

        :return:
        """

        for menu in self.view.menu_bar:
            for item in range(menu.index("end") + 1):
                try:
                    entry = menu.entrycget(item, "label").lower()
                    if entry == "new project":
                        menu.entryconfig(item, command=self.on_new_project)
                    elif entry == "open project":
                        menu.entryconfig(item, command=self.on_open_project)
                    elif entry == "exit":
                        menu.entryconfig(item, command=self.on_close)
                    elif entry == "about":
                        menu.entryconfig(item, command=self.on_about_menu)
                except TclError:  # To avoid separators in Menu entrycget
                    pass

    # def set_observers(self):
    #
    #     self.add_project_observer = KController.AddProjectObserver(self.view)

    def add_observers_to_notifiers(self):

        self.model.project_model.add_object_notifier.add_observer(KController.AddProjectObserver(self.view))

    @staticmethod
    def on_about_menu():
        messagebox.showinfo("About", message="Kalimain %s\n%s" % (__kversion__, __kcopyright__))

    def on_close(self):
        self.view.root.destroy()

    def on_new_project(self):
        meta = NewProjectDialog(self.view.root, title="New project", default_name="Project %d" % (len(
            self.model.project_model.projects) + 1))
        if meta.result:
            self.model.project_model.add_project(**meta.result)

    def on_open_project(self):
        pass
