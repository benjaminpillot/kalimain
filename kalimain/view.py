# -*- coding: utf-8 -*-

""" Kalimain GUI view

More detailed description.
"""
import tkinter as tk
from abc import abstractmethod
from tkinter import messagebox, ttk
from tkinter.ttk import Separator

from shapely.geometry import Point, Polygon

from kalimain.buttons import KToggleButton, KPanelButton, KButton
from kalimain.controltools import ToggleCursor
from kalimain.observer import Observable
from kalimain.viewtools import Framework, ZoomAdvanced, containerxy, canvasxy, Tooltip
from kalimain.widgets import KListbox, KFrame, KCFrame, KScale, KScaleImgFactor


class SubView(Observable):

    def __init__(self, root, model, screen_w, screen_h):
        super().__init__()
        self.root = root
        self.model = model
        self.screen_w = screen_w
        self.screen_h = screen_h

        # Initialize GUI
        self.create_gui()

    @abstractmethod
    def create_gui(self):
        pass

    def notify_observers(self, arg=None):
        self.set_changed()
        super().notify_observers(arg)


class MainView(SubView):
    """ Main API tab view

    """
    canvas_frame = None
    control_panel = None
    cave_control_panel = None
    image_control_panel = None
    cave_listbox = None
    image_listbox = None
    left_bar = None
    left_bar_buttons = []
    left_bar_toggle_buttons = []

    # Control panel buttons
    add_cave_button = None
    delete_cave_button = None
    add_image_button = None
    delete_image_button = None
    image_enhance_scale = []

    # Geometry
    image = None
    canvas_lines = []
    canvas_points = []
    hands = dict()

    # Design
    listbox_select_bg = "sky blue"
    listbox_select_fg = "white"
    point_color = "red"
    line_color = "black"
    hand_color = "green"
    line_width = 2
    icon_size = 128

    # Left bar control parameters
    button_icon = ['icons/save_hand.png', 'icons/undo.png']
    button_tooltip = ["Store hand", "Undo"]
    toggle_icon = ['icons/crosshair2.png', 'icons/hand3.png', 'icons/rubber.png', 'icons/info2.png']
    toggle_tooltip = ["Add point", "Pan image", "Delete hand", "Info"]
    toggle_cursor = ["crosshair", "fleur", "X_cursor", "question_arrow"]

    ###################
    # Protected GUI creation methods
    def _create_drawing_canvas(self):
        self.canvas_frame = KCFrame(self.root)
        self.canvas_frame.pack(side="left", expand="yes", fill="both")
        Separator(self.root, orient=tk.VERTICAL).pack(side="left", fill="y")

    def _create_control_panel(self):
        self.control_panel = tk.Frame(self.root)
        self.control_panel.pack(side="left", expand="no", fill="both")
        self.cave_control_panel = KFrame(self.control_panel)
        self.image_control_panel = KFrame(self.control_panel)
        self.image_enhance_panel = KFrame(self.control_panel)
        self.cave_control_panel.pack(side="top", expand="no", fill="both")
        Separator(self.control_panel, orient=tk.HORIZONTAL).pack(side="top", fill="x", pady=1)
        self.image_control_panel.pack(side="top", expand="no", fill="both")
        Separator(self.control_panel, orient=tk.HORIZONTAL).pack(side="top", fill="x", pady=1)
        self.image_enhance_panel.pack(side="bottom", expand="no", fill="both")

    def _create_cave_control_panel_buttons(self):
        self.add_cave_button = KPanelButton(self.cave_control_panel, text="New cave")
        self.delete_cave_button = KPanelButton(self.cave_control_panel, text="Delete")
        self.add_cave_button.pack(side="top", expand="no", fill="x", padx=2, pady=1)
        self.delete_cave_button.pack(side="top", expand="no", fill="x", padx=2, pady=1)

    def _create_image_control_panel_buttons(self):
        self.add_image_button = KPanelButton(self.image_control_panel, text="Add image")
        self.delete_image_button = KPanelButton(self.image_control_panel, text="Delete")
        self.add_image_button.pack(side="top", expand="no", fill="x", padx=2, pady=1)
        self.delete_image_button.pack(side="top", expand="no", fill="x", padx=2, pady=1)

    def _create_image_enhance_controls(self):
        for i, enhance in enumerate(["Color", "Brightness", "Contrast", "Sharpness"]):
            self.image_enhance_scale.append(KScaleImgFactor(self.image_enhance_panel, 1.0, from_=-2.0, to=10.0,
                                            resolution=0.01, orient=tk.HORIZONTAL))
            tk.Label(self.image_enhance_panel, text=enhance).pack(side="bottom", expand="no", fill="both")
            self.image_enhance_scale[i].pack(side="bottom", expand="no", fill="both")

    def _create_control_panel_listbox(self):
        self.cave_listbox = KListbox(self.cave_control_panel, selectbackground=self.listbox_select_bg,
                                     selectforeground=self.listbox_select_fg)
        self.image_listbox = KListbox(self.image_control_panel, selectbackground=self.listbox_select_bg,
                                      selectforeground=self.listbox_select_fg)
        self.cave_listbox.pack(side="top", fill="both", expand="yes")
        self.image_listbox.pack(side="top", fill="both", expand="yes")

    def _create_left_bar(self):
        self.left_bar = KFrame(self.root, relief=tk.RAISED)
        self.left_bar.pack(fill="y", side="left", padx=2)  # pady = external padding (rembourrage...)
        Separator(self.root, orient=tk.VERTICAL).pack(side="left", fill="y")

    def _create_left_bar_buttons(self):
        icon = [tk.PhotoImage(file=file).subsample(self.icon_x, self.icon_y) for file in self.button_icon]
        for i, (ic, tooltip) in enumerate(zip(icon, self.button_tooltip)):
            self.left_bar_buttons.append(KButton(self.left_bar, image=ic))
            self.left_bar_buttons[i].pack(side="top", expand="no")
            self.left_bar_buttons[i].image = ic
            self.left_bar_buttons[i].tooltip = Tooltip(self.left_bar_buttons[i], text=tooltip)
        Separator(self.left_bar, orient=tk.HORIZONTAL).pack(side="top", fill="x", pady=5, padx=1)

    def _create_left_bar_toggle_buttons(self):
        icon = [tk.PhotoImage(file=file).subsample(self.icon_x, self.icon_y) for file in self.toggle_icon]
        for i, (ic, tooltip, cursor) in enumerate(zip(icon, self.toggle_tooltip, self.toggle_cursor)):
            self.left_bar_toggle_buttons.append(KToggleButton(self.left_bar, image=ic))
            self.left_bar_toggle_buttons[i].pack(side="top", expand="no")
            self.left_bar_toggle_buttons[i].image = ic
            self.left_bar_toggle_buttons[i].tooltip = Tooltip(self.left_bar_toggle_buttons[i], text=tooltip)
            self.left_bar_toggle_buttons[i].cursor = ToggleCursor(self.left_bar_toggle_buttons[i], self.canvas_frame,
                                                                  cursor)

    def create_gui(self):
        self._create_left_bar()
        self._create_drawing_canvas()
        self._create_left_bar_buttons()
        self._create_left_bar_toggle_buttons()
        self._create_control_panel()
        self._create_control_panel_listbox()
        self._create_cave_control_panel_buttons()
        self._create_image_control_panel_buttons()
        self._create_image_enhance_controls()

    #########
    # Methods
    def add_hand(self, hand):
        self.hands[hand.id] = \
            dict(canvas_points=self.canvas_points, canvas_lines=self.canvas_lines,
                 polygon=Polygon([(pt.x, pt.y) for pt in hand.hpoints]))

    def clear_canvas(self):
        self.hands.clear()
        self.delete_image()
        self.reset_canvas_objects()

    def containerxy(self, event):
        """ Return container x and y coordinates when within container

        :param event:
        :return:
        """
        x, y = self.image.canvas.canvasx(event.x), self.image.canvas.canvasy(event.y)
        bbox = self.image.canvas.bbox(self.image.container)
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
            return containerxy(self.image.canvas, self.image.container, self.image.width, self.image.height, x, y)

    def delete_hand(self, hand_id):
        """ Delete hand representation

        :param hand_id:
        :return:
        """
        hand = self.hands.pop(hand_id)
        for obj in hand["canvas_lines"] + hand["canvas_points"]:
            self.image.canvas.delete(obj)

    def delete_image(self):
        if self.image is not None:
            self.image.delete()
            self.image = None

    def delete_last_point(self):
        if len(self.canvas_points) > 1:
            self.image.canvas.delete(self.canvas_lines.pop())
        self.image.canvas.delete(self.canvas_points.pop())

    def disp_hand_info(self, info):
        """ Display hand features in message box

        :param info:
        :return:
        """
        text = "D1 = %.2f px\nD2 = %.2f px\nD3 = %.2f px\nD4 = %.2f px\nD5 = %.2f px\n\nMANNING = %.2f" % \
               tuple([info[key] for key in ["d1", "d2", "d3", "d4", "d5", "manning"]])
        messagebox.showinfo("Hand info", message=text)

    def draw_line(self, line, color=None):
        if color is None:
            color = self.line_color
        start_x, start_y = canvasxy(self.image.canvas, self.image.container, self.image.width, self.image.height,
                                    line[0].x, line[0].y)
        end_x, end_y = canvasxy(self.image.canvas, self.image.container, self.image.width, self.image.height,
                                line[-1].x, line[-1].y)

        return self.image.canvas.create_line(start_x, start_y, end_x, end_y, fill=color, width=self.line_width)

    def draw_point(self, point, color=None):
        if color is None:
            color = self.point_color
        x, y = canvasxy(self.image.canvas, self.image.container, self.image.width, self.image.height, point.x, point.y)

        return self.image.canvas.create_rectangle(x - 2 * self.image.imscale, y - 2 * self.image.imscale,
                                                  x + 2 * self.image.imscale, y + 2 * self.image.imscale,
                                                  outline=color)

    def freeze_hand(self):
        for point in self.canvas_points:
            self.image.canvas.itemconfig(point, outline=self.hand_color)
        for line in self.canvas_lines:
            self.image.canvas.itemconfig(line, fill=self.hand_color)

    def get_cursor_hand_id(self, event):
        """ Get id of hand under cursor

        :return:
        """
        if self.hands:  # If there are hands
            x, y = containerxy(self.image.canvas, self.image.container, self.image.width, self.image.height,
                               self.image.canvas.canvasx(event.x), self.image.canvas.canvasy(event.y))
            for hand_id, dct in self.hands.items():
                if Point([x, y]).within(dct["polygon"]):
                    return hand_id

    def get_scale_factor(self):
        return dict(color=self.image_enhance_scale[0].factor, brightness=self.image_enhance_scale[1].factor,
                    contrast=self.image_enhance_scale[2].factor, sharpness=self.image_enhance_scale[3].factor)

    def load_canvas(self, image):
        self.load_image(image)
        for hand in image.hands:
            self.hands[hand.id] = dict(canvas_points=[self.draw_point(pt, self.hand_color) for pt in hand.hpoints],
                                       canvas_lines=[self.draw_line([pt0, pt1], self.hand_color) for pt0, pt1
                                                     in zip(hand.hpoints[:-1], hand.hpoints[1::])],
                                       polygon=Polygon([(pt.x, pt.y) for pt in hand.hpoints]))

    def load_image(self, image):
        self.image = ZoomAdvanced(self.canvas_frame, path=image.path)

    def reset_canvas_objects(self):
        self.canvas_lines = []
        self.canvas_points = []

    @property
    def icon_x(self):
        return self.icon_y

    @property
    def icon_y(self):
        return self.screen_h // (self.icon_size * 2)


class DataDisplayView(SubView):
    """ Display data tab

    """

    def create_gui(self):
        pass


class KView(Framework):

    tabs = []
    views = []

    tab_views = (MainView, DataDisplayView)
    tab_titles = ("Insert", "Display")

    def __init__(self, root, model, width=1200, height=900):
        super().__init__(root, width, height)
        self.model = model
        self.notebook = ttk.Notebook(self.root)
        self.create_gui()

    def _create_menu(self):
        menu_definitions = (
            'File- &New project/Ctrl+N, &Open project/Ctrl+O, sep, '
            'Exit/Alt+F4',
            'Help- About/F1'
        )
        self.build_menu(menu_definitions)

    def _create_tabs(self):
        """ Create tkinter tabs

        :return:
        """
        for i, (title, view) in enumerate(zip(self.tab_titles, self.tab_views)):
            self.tabs.append(tk.Frame(self.notebook))
            self.notebook.add(self.tabs[i], text=title)
            self.views.append(view(self.tabs[i], self.model, self.screen_w, self.screen_h))
        self.notebook.pack(expand="yes", fill="both")

    def create_gui(self):
        self._create_menu()
        self._create_tabs()
