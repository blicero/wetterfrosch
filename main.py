#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2025-07-06 15:51:21 krylon>
#
# /data/code/python/wetterfrosch/wetterfrosch.py
# created on 14. 02. 2024
# (c) 2024 Benjamin Walkenhorst
#
# This file is part of the Wetterfrosch weather app. It is distributed
# under the terms of the GNU General Public License 3. See the file
# LICENSE for details or find a copy online at
# https://www.gnu.org/licenses/gpl-3.0

"""
wetterfrosch.wetterfrosch

(c) 2024 Benjamin Walkenhorst
"""

import argparse
import os
import time
from typing import Final

import krylib

from wetterfrosch import client, common, gui


def main() -> None:
    """The entry point to the application."""  # noqa: D401
    argp: argparse.ArgumentParser = argparse.ArgumentParser()
    argp.add_argument("-g", "--gui",
                      action="store_true",
                      help="Display a graphical user interface")
    argp.add_argument("-b", "--basedir",
                      default=common.path.base(),
                      help="The directory to store application-specific files in")

    args = argp.parse_args()

    common.set_basedir(args.basedir)

    places: list[str] = []
    loc_path: Final[str] = common.path.locations()

    if krylib.fexist(loc_path):
        with open(loc_path,
                  "r",
                  encoding="utf-8") \
                  as fh:  # pylint: disable-msg=C0103
            for line in fh:
                places.append(line.strip())

    places = sorted(set(places))

    c: client.Client = client.Client()
    c.start()

    if args.gui:
        if not "DISPLAY" in os.environ:
            os.environ["DISPLAY"] = ":0.0"
        g: gui.WetterGUI = gui.WetterGUI(c)
        g.run()
    else:
        # do nothing, let the worker threads run in the background.
        while True:
            time.sleep(10)


if __name__ == '__main__':
    main()

# Local Variables: #
# python-indent: 4 #
# End: #
