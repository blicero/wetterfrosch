#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2024-01-02 19:51:09 krylon>
#
# /data/code/python/wetterfrosch/gui.py
# created on 02. 01. 2024
# (c) 2024 Benjamin Walkenhorst
#
# This file is part of the Vox audiobook reader. It is distributed under the
# terms of the GNU General Public License 3. See the file LICENSE for details
# or find a copy online at https://www.gnu.org/licenses/gpl-3.0

"""
wetterfrosch.gui

(c) 2024 Benjamin Walkenhorst
"""

from threading import Lock
from typing import Final

import gi  # type: ignore

from wetterfrosch import common

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

from gi.repository import Gtk as gtk  # noqa: E402


class WetterGUI:
    """Graphical frontend to the wetterfrosch app"""

    def __init__(self) -> None:
        self.log = common.get_logger("GUI")
        self.lock = Final[Lock]

# Local Variables: #
# python-indent: 4 #
# End: #
