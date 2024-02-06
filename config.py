#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2024-02-06 14:50:54 krylon>
#
# /data/code/python/wetterfrosch/config.py
# created on 21. 01. 2024
# (c) 2024 Benjamin Walkenhorst
#
# This file is part of the Wetterfrosch weather app. It is distributed under the
# terms of the GNU General Public License 3. See the file LICENSE for details
# or find a copy online at https://www.gnu.org/licenses/gpl-3.0

"""
wetterfrosch.config

(c) 2024 Benjamin Walkenhorst
"""

import logging
from typing import Any, Final

import krylib
import tomlkit

from wetterfrosch import common

defaults: Final[str] = """
# Time-stamp: <2024-01-21 17:33:44 krylon>
[common]

[client]
# List of locations to display warnings for.
# These are regular expressions.
locations = [ "Bielefeld" ]

[gui]
# Icon to display when there are no current warnings
icon_default = "weather-storm-symbolic"
# Icon to display when there are warnings
icon_warn = "weather-severe-alert-symbolic"
# Interval (in seconds) between fetching warnings
fetch_interval = 300

[database]
"""


class Config:
    """Config deals with reading and writing the configuration file."""

    log: logging.Logger
    cfg: dict
    path: str

    def __init__(self, path: str = ""):
        if path == "":
            self.path = common.path.config()
        else:
            self.path = path
        self.log = common.get_logger("config")

        if not krylib.fexist(self.path):
            self.log.info(
                "Configuration file %s does not exist, creating new file with default settings.",
                self.path)
            with open(self.path, "w", encoding="utf-8") as fh:
                fh.write(defaults)

        with open(self.path, "r", encoding="utf-8") as fh:
            config_raw: Final[str] = fh.read()
            self.cfg = tomlkit.parse(config_raw)

    def get_option(self, section: str, key: str) -> Any:
        """Get an item from the configuration."""
        return self.cfg[section][key]

    def set_option(self, section: str, key: str, value: Any) -> None:
        """Change a setting and save it."""
        self.cfg[section][key] = value

        with open(self.path, "w", encoding="utf-8") as fh:
            output = tomlkit.dumps(self.cfg)
            fh.write(output)

# Local Variables: #
# python-indent: 4 #
# End: #
