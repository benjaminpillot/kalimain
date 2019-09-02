# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""
import os
import warnings

from geopy import Nominatim
from geopy.exc import GeocoderServiceError
from numpy import sqrt
from PIL import Image as PilImage
from pycountry_convert import country_alpha2_to_continent_code, convert_continent_code_to_continent_name
from shapely.geometry import Polygon
from sqlalchemy import Column, Integer, ForeignKey, Boolean, Float, String
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy.orm import relationship

from kalimain.exceptions import ImageError, ApiConnectionWarning


class Base:
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower() + "s"

    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=Base)


class HPoint(Base):
    """ Point class for storing hand canvas_points

    """
    x = Column(Integer)
    y = Column(Integer)
    hand_id = Column(Integer, ForeignKey('hands.id'))

    hand = relationship("Hand", back_populates="hpoints")


class Hand(Base):
    """ Hand class for storing hands

    """

    left = Column(Boolean)
    right = Column(Boolean)
    D1 = Column(Float)
    D2 = Column(Float)
    D3 = Column(Float)
    D4 = Column(Float)
    D5 = Column(Float)
    manning = Column(Float)
    image_id = Column(Integer, ForeignKey('images.id'))

    image = relationship("Image", back_populates="hands")
    hpoints = relationship("HPoint", order_by=HPoint.id, back_populates="hand", cascade="all, delete-orphan")

    def __init__(self, list_of_points):
        # TODO: add hand with 15 canvas_points
        self.hpoints = list_of_points
        self.left, self.right = self.is_left_handed(), not self.is_left_handed()
        self.D1, self.D2, self.D3, self.D4, self.D5 = self.finger_heights()
        self.manning = self.manning_index()

    def get_info(self):
        """ Return a dict of the hand's main info and features

        :return:
        """
        return dict(d1=self.D1, d2=self.D2, d3=self.D3, d4=self.D4, d5=self.D5, manning=self.manning)

    @staticmethod
    def distance(pt1, pt2):
        # Do not return numpy float to avoid error when inserting into the database
        return float(sqrt((pt2.x - pt1.x) ** 2 + (pt2.y - pt1.y) ** 2))

    @staticmethod
    def height_of_finger(start, mid, end):
        """ Return height of finger based on 3 canvas_points

        :param start:
        :param mid:
        :param end:
        :return:
        """
        return 2 * Polygon([(start.x, start.y), (mid.x, mid.y), (end.x, end.y)]).area / Hand.distance(start, end)

    def finger_heights(self):
        """ Get height of fingers

        :return:
        """
        if self.is_left_handed():
            finger_order = [10, 7, 5, 3, 1]
        else:
            finger_order = [1, 4, 6, 8, 10]
        return [self.height_of_finger(*self.hpoints[i - 1:i + 2]) for i in finger_order]

    def is_left_handed(self):
        """ Is hand left or right ?

        Compute width of first and last finger
        :return:
        """
        if self.distance(self.hpoints[0], self.hpoints[2]) < self.distance(self.hpoints[-1], self.hpoints[-3]):
            return True
        else:
            return False

    def manning_index(self):
        """ Compute Manning index

        Compute Manning index (ratio 2-Digit/4-Digit)
        :return:
        """
        return self.D2 / self.D4


class Image(Base):
    """ Image class instance for storing image of hands

    """
    name = Column(String(50))
    description = Column(String(200))
    path = Column(String(200))
    width = Column(Integer)
    height = Column(Integer)
    cave_id = Column(Integer, ForeignKey("caves.id"))

    cave = relationship("Cave", back_populates="images")
    hands = relationship("Hand", order_by=Hand.id, back_populates="image", cascade="all, delete-orphan")

    def __init__(self, filename, **kwargs):
        super().__init__(**kwargs)

        try:
            self._image = PilImage.open(filename)
        except (FileNotFoundError, OSError):
            raise ImageError("Unable to read file '%s" % filename)
        else:
            self.path = filename
            self.width = self._image.width
            self.height = self._image.height

    def __eq__(self, other):
        if not isinstance(other, Image):
            return False
        if self.size == other.size and os.stat(self.path).st_size == os.stat(other.path).st_size:
            return True
        else:
            return False

    @property
    def size(self):
        return self.width, self.height


class Cave(Base):
    """ Cave class instance for storing caves to which belong images and hands

    """
    # Primary attributes
    name = Column(String(50))
    description = Column(String(200))
    latitude = Column(Float)
    longitude = Column(Float)
    project_id = Column(Integer, ForeignKey("projects.id"))

    # Secondary attributes (retrieved using geopy library)
    city = Column(String(50))
    town = Column(String(50))
    village = Column(String(50))
    suburb = Column(String(50))
    country = Column(String(50))
    country_code = Column(String(2))
    county = Column(String(50))
    state = Column(String(50))
    continent = Column(String(50))
    address = Column(String(200))

    # Relationships
    project = relationship("Project", back_populates="caves")
    images = relationship("Image", order_by=Image.id, back_populates="cave", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.geolocator = Nominatim(user_agent="Kalimain")

        try:
            self.location = self.geolocator.reverse("%f, %f" % (self.latitude, self.longitude))
        except GeocoderServiceError:
            warnings.warn("Unable to reach service: only primary attributes will be set", ApiConnectionWarning)
        else:
            # Set secondary attributes
            self.get_secondary_attributes()

    def __eq__(self, other):
        if not isinstance(other, Cave):
            return False
        if self.latitude == other.latitude and self.longitude == other.longitude:
            return True
        else:
            return False

    def get_continent(self):
        if self.country is not None:
            continent_code = country_alpha2_to_continent_code(self.country_code.upper())
            return convert_continent_code_to_continent_name(continent_code)

    def get_secondary_attributes(self):
        self.address = self.location.raw["display_name"]

        for key, val in self.location.raw["address"].items():
            try:
                self.__setattr__(key, val)
            except AttributeError:
                pass

        self.continent = self.get_continent()


class Project(Base):
    """ Project class instance

    """
    name = Column(String(50))
    description = Column(String(1000))

    caves = relationship("Cave", order_by=Cave.id, back_populates="project", cascade="all, delete-orphan")

    def __eq__(self, other):
        if not isinstance(other, Project):
            return False
        if self.name == other.name:
            return True
        else:
            return False
