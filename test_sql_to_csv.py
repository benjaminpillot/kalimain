# -*- coding: utf-8 -*-

""" Module summary description.

More detailed description.
"""

__author__ = 'Benjamin Pillot'
__copyright__ = 'Copyright 2019, Benjamin Pillot'
__email__ = 'benjaminpillot@riseup.net'


from sqlalchemy import Table

import kalimain
from kalimain.model import KModel
from utils.toolset.sqlcsv import SqlCsv

test = KModel()
test.project_model.add_project(name="projet_1")
test.project_model.add_project(name="projet_2", description="Une autre description histoire de voir")
test.project_model.add_project(name="projet_3", description="Une description pour voir")
test.project_model.set_object(2)
test.cave_model.add_cave(latitude=42, longitude=9, name="grotte_1")
test.cave_model.add_cave(latitude=50, longitude=13, name="grotte_2")
test.cave_model.set_object(2)
test.image_model.add_image("/home/benjamin/Documents/kalimain/sample/Montage main Tewet - copie.tif", name="image_1")
test.cave_model.set_object(1)
test.image_model.add_image("/home/benjamin/Documents/kalimain/sample/IK-bouquetPL_red - copie.tif", name="image_2")


sqlobj = SqlCsv(kalimain.ENGINE, test.session)
sqlobj.to_csv("images", "/home/benjamin/Documents/kalimain/test_images.csv", map_foreign_key_tables=True)

# sqlobj.inspector.get_foreign_keys("caves")
