#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2024-03-06 16:26:08 krylon>
#
# /data/code/python/wetterfrosch/chart.py
# created on 19. 02. 2024
# (c) 2024 Benjamin Walkenhorst
#
# This file is part of the Wetterfrosch weather app. It is distributed
# under the terms of the GNU General Public License 3. See the file
# LICENSE for details or find a copy online at
# https://www.gnu.org/licenses/gpl-3.0

"""
wetterfrosch.chart

Generate charts from the accumulated data.

(c) 2024 Benjamin Walkenhorst
"""

import logging
from datetime import datetime
from threading import Lock, local

import matplotlib.pyplot as plt
import matplotlib as mpl

from wetterfrosch import common, data, database


class Plotter:
    """Plotter generates charts from the data we got from the web."""

    __slots__ = [
        "lock",
        "tls",
        "log",
    ]

    lock: Lock
    log: logging.Logger
    tls: local

    def __init__(self) -> None:
        self.log = common.get_logger("chart")
        self.lock = Lock()
        self.tls = local()

    def _get_db(self) -> database.Database:
        """Get the Database instance for the calling thread."""
        try:
            return self.local.db
        except AttributeError:
            db = database.Database()  # pylint: disable-msg=C0103
            self.local.db = db
            return db

    def render_chart(self, d1: datetime, d2: datetime, path: str) -> None:
        """Render the forecast data for the given period."""
        # db = self.get_db()


# Local Variables: #
# python-indent: 4 #
# End: #
