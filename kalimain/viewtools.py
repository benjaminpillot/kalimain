# -*- coding: utf-8 -*-

""" Everything related to View in kalimain API

More detailed description.
"""
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from PIL import Image, ImageTk, ImageEnhance

from kalimain.exceptions import FloatEntryError


def canvasxy(canvas, container, width, height, x, y):
    """ Convert x/y in container to x/y in canvas

    :param canvas:
    :param container:
    :param width:
    :param height:
    :param x: container x
    :param y: container y
    :return:
    """
    bbox = canvas.bbox(container)
    return bbox[0] + x/width * (bbox[2] - bbox[0]), bbox[1] + y/height * (bbox[3] - bbox[1])


def containerxy(canvas, container, width, height, x, y):
    """ Convert x/y in canvas to x/y in container

    :param canvas:
    :param container:
    :param width: original width of container
    :param height: original height of container
    :param x: canvas x
    :param y: canvas y
    :return:
    """
    bbox = canvas.bbox(container)
    return (x - bbox[0]) * width / (bbox[2] - bbox[0]), (y - bbox[1]) * height / (bbox[3] - bbox[1])


class FloatEntry(tk.Entry):
    """ Geo entry format (latitude/longitude)

    """
    def __init__(self, master=None, **kwargs):
        self.double_var = tk.DoubleVar()
        super().__init__(master, textvariable=self.double_var, **kwargs)

    def get(self):
        try:
            return self.double_var.get()
        except tk.TclError:
            raise FloatEntryError("Invalid float format")


class Tooltip:
    """
    It creates a tooltip for a given widget as the mouse goes on it.

    see:

    https://stackoverflow.com/questions/3221956/
           what-is-the-simplest-way-to-make-tooltips-
           in-tkinter/36221216#36221216

    http://www.daniweb.com/programming/software-development/
           code/484591/a-tooltip-class-for-tkinter

    - Originally written by vegaseat on 2014.09.09.

    - Modified to include a delay time by Victor Zaccardo on 2016.03.25.

    - Modified
        - to correct extreme right and extreme bottom behavior,
        - to stay inside the screen whenever the tooltip might go out on
          the top but still the screen is higher than the tooltip,
        - to use the more flexible mouse positioning,
        - to add customizable background color, padding, waittime and
          wraplength on creation
      by Alberto Vassena on 2016.11.05.

    - Modified
        - Show tooltip text only if widget is activated (state == 'normal')
      by Benjamin Pillot on 2019.04.03

      Tested on Ubuntu 16.04/16.10, running Python 3.5.2

    TODO: themes styles support
    """

    def __init__(self, widget, *, bg='#FFFFEA', pad=(5, 3, 5, 3), text='widget info', waittime=400, wraplength=250):

        self.waittime = waittime  # in miliseconds, originally 500
        self.wraplength = wraplength  # in pixels, originally 180
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<ButtonPress>", self.on_leave)
        self.bg = bg
        self.pad = pad
        self.id = None
        self.tw = None

    def on_enter(self, event=None):
        # Only show tooltip if widget is activated
        if self.widget.cget("state") == tk.NORMAL:
            self.schedule()

    def on_leave(self, event=None):
        self.unschedule()
        self.hide()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.show)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def show(self):
        def tip_pos_calculator(w, lab, *, tip_delta=(10, 5), p=(5, 3, 5, 3)):

            s_width, s_height = w.winfo_screenwidth(), w.winfo_screenheight()

            width, height = (p[0] + lab.winfo_reqwidth() + p[2],
                             p[1] + lab.winfo_reqheight() + p[3])

            mouse_x, mouse_y = w.winfo_pointerxy()

            x1, y1 = mouse_x + tip_delta[0], mouse_y + tip_delta[1]
            x2, y2 = x1 + width, y1 + height

            x_delta = x2 - s_width
            if x_delta < 0:
                x_delta = 0
            y_delta = y2 - s_height
            if y_delta < 0:
                y_delta = 0

            offscreen = (x_delta, y_delta) != (0, 0)

            if offscreen:

                if x_delta:
                    x1 = mouse_x - tip_delta[0] - width

                if y_delta:
                    y1 = mouse_y - tip_delta[1] - height

            offscreen_again = y1 < 0  # out on the top

            if offscreen_again:
                # No further checks will be done.

                # TIP:
                # A further mod might automagically augment the
                # wraplength when the tooltip is too high to be
                # kept inside the screen.
                y1 = 0

            return x1, y1

        bg = self.bg
        pad = self.pad
        widget = self.widget

        # creates a toplevel window
        self.tw = tk.Toplevel(widget)

        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)

        win = tk.Frame(self.tw, background=bg, borderwidth=0)
        label = ttk.Label(win,
                          text=self.text,
                          justify=tk.LEFT,
                          background=bg,
                          relief=tk.SOLID,
                          borderwidth=0,
                          wraplength=self.wraplength)

        label.grid(padx=(pad[0], pad[2]), pady=(pad[1], pad[3]), sticky=tk.NSEW)
        win.grid()

        x, y = tip_pos_calculator(widget, label)

        self.tw.wm_geometry("+%d+%d" % (x, y))

    def hide(self):
        tw = self.tw
        if tw:
            tw.destroy()
        self.tw = None


class Framework:

    """
    GUIFramework is a class that provides a higher level of abstraction for
    the development of Tkinter graphic user interfaces (GUIs).
    Every class that uses this GUI framework must inherit from this class
    and should pass the root window as an argument to this class by calling
    the super method as follows:
        super().__init__(root)

    Building Menus:
    To build a menu, call build_menu() method with one argument for
    menu_definition, where menu_definition is a tuple where each item is a string of the
    format:
        'Top Level Menu Name - MenuItemName/Accelrator/Commandcallback/Underlinenumber'.

        MenuSeparator is denoted by a string 'sep'.

    For instance, passing this tuple as an argument to this method

        menu_definition = (
                      'File - &New/Ctrl+N/new_file, &Open/Ctrl+O/openfile, &Save/Ctrl+S/save, Save&As//saveas, sep,
                      Exit/Alt+F4/close', 'Edit - Cut/Ctrl+X/cut, Copy/Ctrl+C/copy, Paste/Ctrl+V/paste, Sep',
                      )

    will generate a File and Edit Menu Buttons with listed menu items for each of the buttons.
    """

    def __init__(self, root, width, height):
        self.root = root
        x_offset = (self.screen_w - width)/2 if width <= self.screen_w else 0
        y_offset = (self.screen_h - height)/2 if height <= self.screen_h else 0
        self.root.geometry("%dx%d+%d+%d" % (width, height, x_offset, y_offset))
        self.width = width
        self.height = height
        self.menu_bar = []

    def build_menu(self, menu_definitions, font_size=12):
        font = tkfont.Font(self.root, size=font_size, weight="normal")
        menu_bar = tk.Menu(self.root, font=font)
        for definition in menu_definitions:
            menu = tk.Menu(menu_bar, tearoff=0)
            top_level_menu, pull_down_menus = definition.split('-')
            menu_items = map(str.strip, pull_down_menus.split(','))
            for item in menu_items:
                self._add_menu_command(menu, item, font)
            menu_bar.add_cascade(label=top_level_menu, menu=menu)
            self.menu_bar.append(menu)
        self.root.config(menu=menu_bar)

    def _add_menu_command(self, menu, item, font):
        if item == 'sep':
            menu.add_separator()
        else:
            menu_label, accelerator_key = item.split('/')
            try:
                underline = menu_label.index('&')
                menu_label = menu_label.replace('&', '', 1)
            except ValueError:
                underline = None
            menu.add_command(label=menu_label, underline=underline, accelerator=accelerator_key, font=font)

    @property
    def screen_w(self):
        return self.root.winfo_screenwidth()

    @property
    def screen_h(self):
        return self.root.winfo_screenheight()


class ZoomAdvanced:
    """ Advanced zoom of an image (with filter possibilities)

    """
    button1_press = None
    button1_motion = None

    img_filter = dict(color=ImageEnhance.Color, contrast=ImageEnhance.Contrast,
                      brightness=ImageEnhance.Brightness, sharpness=ImageEnhance.Sharpness)
    img_factor = dict(color=1.0, contrast=1.0, brightness=1.0, sharpness=1.0)
    has_been_enhanced = False

    # Image within container
    cimage = None
    imagetk = None

    def __init__(self, mainframe, path):
        """ Initialize main frame

        :param mainframe:
        :param path: path to image file
        """
        # ttk.Frame.__init__(self, master=mainframe)
        self.master = mainframe

        # Create canvas and put image on it
        self.canvas = tk.Canvas(self.master, highlightthickness=0, background="white", width=self.master.winfo_width(
            ), height=self.master.winfo_height())
        self.canvas.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        self.canvas.update()  # wait till canvas is created
        # Bind events to the Canvas
        self.canvas.bind('<Configure>', self.show_image)  # canvas is resized
        self.canvas.bind('<MouseWheel>', self.wheel)  # with Windows and MacOS, but not Linux
        self.canvas.bind('<Button-5>', self.wheel)  # only with Linux, wheel scroll down
        self.canvas.bind('<Button-4>', self.wheel)  # only with Linux, wheel scroll up
        self.image = Image.open(path)  # open image
        self.original_image = self.image
        self.width, self.height = self.image.size
        self.imscale = 0.2  # scale for the canvas image
        self.delta = 1.3  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas.create_rectangle(0, 0, self.width, self.height, width=0)

        self.canvas.scale('all', 100, 100, self.imscale, self.imscale)
        self.show_image()

    def _enhance(self):
        """ Apply filter to whole image if necessary

        Applying filter to whole image can be cpu consuming,
        so we only do it when necessary
        :return:
        """
        if self.has_been_enhanced:
            self.image = self.original_image
            self.has_been_enhanced = False
            for key in self.img_filter.keys():
                if self.img_factor[key] != 1:
                    self.image = self.img_filter[key](self.image).enhance(self.img_factor[key])

    def delete(self):
        self.unbind_mouse_moves()
        self.canvas.pack_forget()
        self.canvas.destroy()

    def enhance(self, factor):
        """ Apply filter to original image in container

        Only apply filter to image in container for performance purposes
        :param factor: enhance factor
        :return:
        """
        image = self.cimage
        for key in self.img_filter.keys():
            if factor[key] != 1:
                image = self.img_filter[key](image).enhance(factor[key])
                self.img_factor[key] = factor[key]
        self.has_been_enhanced = True
        self.imagetk.paste(image)

    def bind_mouse_moves(self):
        self.button1_press = self.canvas.bind('<ButtonPress-1>', self.move_from)
        self.button1_motion = self.canvas.bind('<B1-Motion>', self.move_to)

    def unbind_mouse_moves(self):
        self.canvas.unbind('<ButtonPress-1>', self.button1_press)
        self.canvas.unbind('<B1-Motion', self.button1_motion)

    def move_from(self, event):
        """ Remember previous coordinates for scrolling with the mouse

        :param event:
        :return:
        """
        self.canvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        """ Drag (move) canvas to the new position

        :param event:
        :return:
        """
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()  # redraw the image

    def wheel(self, event):
        """ Zoom with mouse wheel

        :param event:
        :return:
        """
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        bbox = self.canvas.bbox(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
            pass  # Ok! Inside the image
        else:
            return  # zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width, self.height)
            if int(i * self.imscale) < 30:
                return  # image is less than 30 pixels
            self.imscale /= self.delta
            scale /= self.delta
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
            if i < self.imscale:
                return  # 1 pixel is bigger than the visible area
            self.imscale *= self.delta
            scale *= self.delta
        self.canvas.scale('all', x, y, scale, scale)  # rescale all canvas objects
        self.show_image()

    def show_image(self, event=None):
        """ Show image on the canvas

        :return:
        """
        bbox1 = self.canvas.bbox(self.container)  # get image area
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (self.canvas.canvasx(0),  # get visible area of the canvas
                 self.canvas.canvasy(0),
                 self.canvas.canvasx(self.canvas.winfo_width()),
                 self.canvas.canvasy(self.canvas.winfo_height()))
        bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]
        self.canvas.configure(scrollregion=bbox)  # set scroll region
        x1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(bbox2[1] - bbox1[1], 0)
        x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y2 = min(bbox2[3], bbox1[3]) - bbox1[1]
        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            x = min(int(x2 / self.imscale), self.width)   # sometimes it is larger on 1 pixel...
            y = min(int(y2 / self.imscale), self.height)  # ...and sometimes not

            # Apply potential filters
            self._enhance()

            # Fit to container (current image as well as original)
            image = self.image.crop((int(x1 / self.imscale), int(y1 / self.imscale), x, y)).resize((
                int(x2 - x1), int(y2 - y1)))
            self.cimage = self.original_image.crop((int(x1 / self.imscale), int(y1 / self.imscale), x, y)).resize((
                int(x2 - x1), int(y2 - y1)))

            # Display
            self.imagetk = ImageTk.PhotoImage(image)
            self.canvas.imageid = self.canvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
                                                           anchor='nw', image=self.imagetk)
            self.canvas.lower(self.canvas.imageid)  # set image into background
