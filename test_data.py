#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2024-02-06 15:05:19 krylon>
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
import sys
import unittest
from typing import Final

import krylib

from wetterfrosch.data import Forecast, WeatherWarning

# One little thing I miss from go is that a test is always run with the cwd
# being the package directory. It even has the convention that a folder named
# "testdata" is ignored for other purposes if it exists. So you can write tests
# relying on "./testdata/foo" being consistently available during testing.

example_warning: Final[str] = "example.json"
example_forecast: Final[str] = "weather2.json"


class WarningTest(unittest.TestCase):
    """Test the parsing of weather data."""

    def test_read_file(self) -> None:
        """Try to read a JSON chunk as returned by the DWD server
        from a file."""
        if not krylib.fexist(example_warning):
            self.skipTest("Sample JSON file not found")
        with open(example_warning, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            for block in data["warnings"].values():
                for item in block:
                    try:
                        _ = WeatherWarning(item)
                    except Exception as e:  # pylint: disable-msg=W0718
                        self.fail(f"Error processing weather data: {e}")


class ForecastTest(unittest.TestCase):
    """Test the parsing and handling of forecast data."""

    def test_01_read_file(self) -> None:
        """Test parsing and processing a sample forecast"""
        if not krylib.fexist(example_forecast):
            self.skipTest("Sample file not found")
        with open(example_forecast, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            try:
                fc: Final[Forecast] = Forecast(data)
                self.assertIsNotNone(fc)
                self.assertIsInstance(fc, Forecast)
                self.assertGreaterEqual(fc.probability_rain, 0)
                self.assertGreaterEqual(fc.temperature, -60)
                self.assertLessEqual(fc.temperature, 50)
                self.assertGreaterEqual(fc.humidity, 0)
                self.assertLessEqual(fc.humidity, 100)
            except Exception as e:  # pylint: disable-msg=W0718
                self.fail(f"Something went wrong: {e}")

    def test_02_from_db_row(self) -> None:
        """Test creating a Forecast from a database row (i.e. tuple)"""
        test_tuples: Final[list[tuple]] = [
            (1, 1707083280, "52.0333/8.5333", "Rain", "rain", 75, 7, 7, 95, 5, 10),
            (2, 1707083280+300, "52.0333/8.5333", "Rain", "rain", 67, 6, 3, 70, 15, 10),
        ]

        for t in test_tuples:
            try:
                fc: Forecast = Forecast.from_db(t)
                self.assertIsInstance(fc, Forecast)
            except:  # noqa: E722,B001  pylint: disable-msg=W0702
                self.fail(f"Failed to construct Forecast: {sys.exception()}")

# Local Variables: #
# python-indent: 4 #
# End: #
