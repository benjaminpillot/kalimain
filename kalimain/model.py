# -*- coding: utf-8 -*-

""" Kalimain model

More detailed description.
"""
import warnings

from kalimain import SESSION, ENGINE
from kalimain.database import HPoint, Hand, Image, Cave, Base, Project
from kalimain.exceptions import DuplicateElementWarning, DeleteWarning
from kalimain.observer import Observable


class Model:

    current_object = None
    db_class = None

    add_object_notifier = None
    delete_object_notifier = None
    set_object_notifier = None

    class Notifier(Observable):

        def __init__(self, outer):
            super().__init__()
            self.outer = outer

        def notify_observers(self, arg=None):
            self.set_changed()
            super().notify_observers(arg)

    class AddNotifier(Notifier):
        pass

    class DeleteNotifier(Notifier):
        pass

    class SetNotifier(Notifier):
        pass

    def __init__(self, session=None):
        self.set_notifiers()
        if session:
            self.session = session

    def add_object(self, obj):
        self.session.add(obj)
        self.session.commit()
        self.add_object_notifier.notify_observers(obj)

    def delete_object(self, obj_id):
        obj = self.session.query(self.db_class).get(obj_id)
        self.session.delete(obj)  # Delete object from SQL session
        self.delete_object_notifier.notify_observers(obj_id)

    def set_object(self, obj_id):
        self.current_object = self.session.query(self.db_class).get(obj_id)
        self.set_object_notifier.notify_observers(self.current_object)

    def set_notifiers(self):
        self.add_object_notifier = self.__class__.AddNotifier(self)
        self.delete_object_notifier = self.__class__.DeleteNotifier(self)
        self.set_object_notifier = self.__class__.SetNotifier(self)


class PointModel(Model):

    current_set_of_points = []

    add_point_notifier = None
    delete_last_point_notifier = None

    class AddPointNotifier(Model.Notifier):
        pass

    class DeleteLastPointNotifier(Model.Notifier):
        pass

    def add_point(self, x, y):
        """ Add point with (x, y) coordinates

        :param x:
        :param y:
        :return:
        """
        self.current_set_of_points.append(HPoint(x=x, y=y))
        self.add_point_notifier.notify_observers(self.current_set_of_points)

    def clear(self):
        self.current_set_of_points = []

    def delete_last_point(self):
        self.current_set_of_points.pop()
        self.delete_last_point_notifier.notify_observers()

    def set_notifiers(self):
        self.add_point_notifier = PointModel.AddPointNotifier(self)
        self.delete_last_point_notifier = PointModel.DeleteLastPointNotifier(self)


class HandModel(Model):

    db_class = Hand

    hand_info_notifier = None

    class HandInfoNotifier(Model.Notifier):

        def notify_observers(self, hand_id=None):
            hand = self.outer.session.query(Hand).get(hand_id)
            super().notify_observers(hand.get_info())

    def __init__(self, session, image_model, point_model):
        super().__init__(session)
        self.image_model = image_model
        self.point_model = point_model

    def add_hand(self):
        hand = Hand(self.point_model.current_set_of_points)
        self.image_model.current_object.hands.append(hand)
        self.add_object(hand)
        self.point_model.clear()

    def delete_object(self, hand_id):
        super().delete_object(hand_id)

    def get_hand_info(self, hand_id):
        self.hand_info_notifier.notify_observers(hand_id)

    def set_notifiers(self):
        self.hand_info_notifier = HandModel.HandInfoNotifier(self)
        super().set_notifiers()


class ImageModel(Model):

    db_class = Image

    @property
    def images(self):
        return self.session.query(Image).all()

    def __init__(self, session, cave_model):
        super().__init__(session)
        self.cave_model = cave_model

    def add_image(self, filename, name=None, description=None):
        """ Add image to collection

        :param filename:
        :param name:
        :param description:
        :return:
        """
        image = Image(filename, name=name, description=description)

        if image not in self.images:
            self.cave_model.current_object.images.append(image)
            self.add_object(image)
        else:
            warnings.warn("Image already in dataset.", DuplicateElementWarning)


class CaveModel(Model):
    """ Cave's corresponding model

    """
    db_class = Cave

    @property
    def caves(self):
        return self.session.query(Cave).all()

    def __init__(self, session, project_model):
        super().__init__(session)
        self.project_model = project_model

    def add_cave(self, latitude, longitude, name=None, description=None):
        cave = Cave(latitude=latitude, longitude=longitude, name=name, description=description)
        if cave not in self.caves:
            self.project_model.current_object.caves.append(cave)
            self.add_object(cave)
        else:
            warnings.warn("Cave already in dataset.", DuplicateElementWarning)

    def delete_object(self, cave_id):
        cave = self.session.query(Cave).get(cave_id)
        if not cave.images:
            self.session.delete(cave)
            self.delete_object_notifier.notify_observers(cave_id)
        else:
            warnings.warn("Cannot delete cave with still related images", DeleteWarning)


class ProjectModel(Model):
    """ Project's corresponding model

    """
    db_class = Project

    @property
    def projects(self):
        return self.session.query(Project).all()

    def add_project(self, name, description=None):
        project = Project(name=name, description=description)
        if project not in self.projects:
            self.add_object(project)
        else:
            warnings.warn("Project with that name already exists", DuplicateElementWarning)


class KModel(Model):
    """ Main API model

    """

    def __init__(self):
        super().__init__()

        # Create all tables if necessary
        Base.metadata.drop_all(ENGINE)  # TODO: Remove this line when deploying (Development version)
        Base.metadata.create_all(ENGINE)

        # Initialize database session
        self.session = SESSION()

        # Initialize sub models
        self.point_model = PointModel(self.session)
        self.project_model = ProjectModel(self.session)
        self.cave_model = CaveModel(self.session, self.project_model)
        self.image_model = ImageModel(self.session, self.cave_model)
        self.hand_model = HandModel(self.session, self.image_model, self.point_model)

    def set_notifiers(self):
        pass
