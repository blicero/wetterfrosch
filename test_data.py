#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2024-02-01 22:18:21 krylon>
#
# /data/code/python/wetterfrosch/test_data.py
# created on 01. 02. 2024
# (c) 2024 Benjamin Walkenhorst
#
# This file is part of the Wetterfrosch weather app. It is distributed
# under the terms of the GNU General Public License 3. See the file
# LICENSE for details or find a copy online at
# https://www.gnu.org/licenses/gpl-3.0

"""
wetterfrosch.test_data

(c) 2024 Benjamin Walkenhorst
"""

import json
import unittest
from typing import Final

import krylib

from wetterfrosch.data import WeatherWarning

# One little thing I miss from go is that a test is always run with the cwd
# being the package directory. It even has the convention that a folder named
# "testdata" is ignored for other purposes if it exists. So you can write tests
# relying on "./testdata/foo" being consistently available during testing.

example: Final[str] = "example.json"


class DataTest(unittest.TestCase):
    """Test the parsing of weather data."""

    def test_read_file(self) -> None:
        """Try to read a JSON chunk as returned by the DWD server
        from a file."""
        if not krylib.fexist(example):
            self.skipTest("Sample JSON file not found")
        with open(example, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            for block in data["warnings"].values():
                for item in block:
                    try:
                        _ = WeatherWarning(item)
                    except Exception as e:
                        self.fail(f"Error processing weather data: {e}")

# Local Variables: #
# python-indent: 4 #
# End: #
