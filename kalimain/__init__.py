# -*- coding: utf-8 -*-

""" Module main description

More detailed description.
"""
import base64
import os
import pathlib
import sqlite3

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

__author__ = 'Benjamin Pillot'
__copyright__ = 'Copyright © 2019, Benjamin Pillot - Jean Michel Chazine'
__email__ = 'benjaminpillot@riseup.net'
__version__ = '2.0'


def create_database(db_file):
    """ Create sqlite database

    :param db_file:
    :return:
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Exception as e:
        print(e)
    finally:
        if conn:
            conn.close()


# _kdf = PBKDF2HMAC(
#     algorithm=hashes.SHA256(),
#     length=32,
#     salt=open(os.path.join(str(pathlib.Path.home()), ".kalimain", "keyring"), 'rb').read(16),
#     iterations=100000,
#     backend=default_backend()
# )

# _fernet = Fernet(base64.urlsafe_b64encode(_kdf.derive(b"kalimain")))

# with open(os.path.join(str(pathlib.Path.home()), ".kalimain", "kali_credentials"), 'rb') as file:
#     ENGINE = create_engine("mysql://%s:%s@localhost/kalimaindb" % (_fernet.decrypt(file.read(100)).decode("ascii"),
#                                                                    _fernet.decrypt(file.read()).decode("ascii")),
#                            echo=True)

kalimain_home_directory = os.path.join(str(pathlib.Path.home()), '.kalimain')
path_to_sqlite_db = os.path.join(kalimain_home_directory, 'kalimaindb.db')

try:
    # Create target Directory
    os.mkdir(kalimain_home_directory)
except FileExistsError:
    pass

create_database(path_to_sqlite_db)
ENGINE = create_engine("sqlite:///%s" % path_to_sqlite_db, echo=True)

SESSION = sessionmaker(ENGINE)
