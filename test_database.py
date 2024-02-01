#!/usr/bin/env python3
# pylint: disable-msg=C0302
# -*- coding: utf-8 -*-
# Time-stamp: <2024-01-31 20:05:34 krylon>
#
# /data/code/python/wetterfrosch/test_database.py
# created on 13. 01. 2024
# (c) 2024 Benjamin Walkenhorst
#
# This file is part of the Wetterfrosch weather app. It is distributed under the
# terms of the GNU General Public License 3. See the file LICENSE for details
# or find a copy online at https://www.gnu.org/licenses/gpl-3.0

"""
wetterfrosch.test_database

(c) 2024 Benjamin Walkenhorst
"""

import json
import os
import unittest
from datetime import datetime
from typing import Final

from krylib import isdir

from wetterfrosch import common, database
from wetterfrosch.data import WeatherWarning

TEST_ROOT: str = "/tmp/"

if isdir("/data/ram"):
    TEST_ROOT = "/data/ram"


class DatabaseTest(unittest.TestCase):
    """Test the Database class. Duh."""

    folder: str
    db: database.Database

    @classmethod
    def setUpClass(cls) -> None:
        stamp = datetime.now()
        folder_name = \
            stamp.strftime("wetterfrosch_test_database_%Y%m%d_%H%M%S")
        cls.folder = os.path.join(TEST_ROOT,
                                  folder_name)
        common.set_basedir(cls.folder)

    @classmethod
    def tearDownClass(cls) -> None:
        os.system(f"/bin/rm -rf {cls.folder}")

    def __get_db(self) -> database.Database:
        """Get the shared database instance."""
        return self.__class__.db

    def test_01_db_open(self) -> None:
        """Test opening the database."""
        try:
            self.__class__.db = database.Database(common.path.db())
        except Exception as e:  # pylint: disable-msg=W0718
            self.fail(f"Failed to open database: {e}")
        finally:
            self.assertIsNotNone(self.__class__.db)

    # This could easily become very tedious unless I figure out a way to semi-
    # randomly generate dummy warnings.
    # And how much effort am I willing to put into it?
    def test_02_db_add(self) -> None:
        """Test adding warnings to the database."""
        db = self.__get_db()
        raw = json.loads(TEST_DATA)
        cnt: int = 0
        try:
            with db:
                for group in raw.values():
                    for item in group:
                        w = WeatherWarning(item)
                        db.warning_add(w)
                        cnt += 1

            with db:
                items = db.warning_get_all()
                self.assertEqual(len(items), cnt)
        except Exception as e:  # pylint: disable-msg=W0718
            self.fail(f"Failed to add items to the database: {e}")

    def test_03_db_get_keys(self) -> None:
        """Test gettings the keys from the database records."""
        db = self.__get_db()
        keys = db.warning_get_keys()
        self.assertIsNotNone(keys)
        self.assertIsInstance(keys, set)
        self.assertGreater(len(keys), 0)
        for k in keys:
            self.assertTrue(db.warning_has_key(k))

    def test_04_db_acknowledge(self) -> None:
        """Test acknowledging database records."""
        db = self.__get_db()
        warnings = db.warning_get_all()
        self.assertGreater(len(warnings), 0)
        try:
            with db:
                for w in warnings:
                    self.assertFalse(w.acknowledged)
                    db.warning_acknowledge(w)
                    self.assertTrue(w.acknowledged)
        except Exception as e:  # pylint: disable-msg=W0718
            self.fail(f"An unexpected exception occured: {e}")

        warnings = db.warning_get_all()
        for w in warnings:
            self.assertTrue(w.acknowledged)

        for w in warnings:
            with self.assertRaises(AssertionError):
                w.wid = 0
                db.warning_acknowledge(w)


# Test data
TEST_DATA: Final[str] = """
{
    "106535000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Vogelsbergkreis",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "107132000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Altenkirchen (Westerwald)",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703901600000,
        "regionName": "Kreis Altenkirchen (Westerwald)",
        "end": 1703912400000,
        "description": "Es treten oberhalb 600 m Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": 600,
        "altitudeEnd": null
      }
    ],
    "116065000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kyffhäuserkreis",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "108326000": [
      {
        "state": "Baden-Württemberg",
        "type": 1,
        "level": 3,
        "start": 1703869200000,
        "regionName": "Schwarzwald-Baar-Kreis",
        "end": 1703923200000,
        "description": "Es treten oberhalb 1000 m Sturmböen mit Geschwindigkeiten um 80km/h (22 m/s, 44 kn, Bft 9) aus südwestlicher Richtung auf. In exponierten Lagen muss mit schweren Sturmböen um 90 km/h (25 m/s, 48 kn, Bft 10) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BW",
        "altitudeStart": 1000,
        "altitudeEnd": null
      }
    ],
    "103252000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Hameln-Pyrmont",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "909671999": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Aschaffenburg",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105512000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Bottrop",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "901059001": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Schleswig-Flensburg - Binnenland",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109477000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Kulmbach",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "901059002": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Schleswig-Flensburg - Küste",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105170000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Wesel",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103102000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Salzgitter",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105362000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Rhein-Erft-Kreis",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103358000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Heidekreis",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "107131000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Ahrweiler",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703901600000,
        "regionName": "Kreis Ahrweiler",
        "end": 1703912400000,
        "description": "Es treten oberhalb 600 m Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": 600,
        "altitudeEnd": null
      }
    ],
    "105554000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Borken",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "201068000": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Ostholsteinische Seen",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103251000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Diepholz",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105958000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 3,
        "start": 1703840580000,
        "regionName": "Hochsauerlandkreis",
        "end": 1703923200000,
        "description": "Es treten oberhalb 600 m Sturmböen mit Geschwindigkeiten zwischen 65 km/h (18 m/s, 35 kn, Bft 8) und 80 km/h (22 m/s, 44 kn, Bft 9) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "NRW",
        "altitudeStart": 600,
        "altitudeEnd": null
      },
      {
        "state": "Nordrhein-Westfalen",
        "type": 2,
        "level": 3,
        "start": 1703833200000,
        "regionName": "Hochsauerlandkreis",
        "end": 1703916000000,
        "description": "Es tritt Dauerregen auf. Dabei werden Niederschlagsmengen bis 30 l/m² erwartet.",
        "event": "DAUERREGEN",
        "headline": "Amtliche WARNUNG vor DAUERREGEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Hochsauerlandkreis",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "115083000": [
      {
        "state": "Sachsen-Anhalt",
        "type": 1,
        "level": 3,
        "start": 1703856660000,
        "regionName": "Kreis Börde",
        "end": 1703872800000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 60 km/h (17 m/s, 33 kn, Bft 7) und 70 km/h (20 m/s, 38 kn, Bft 8) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "SA",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Sachsen-Anhalt",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Börde",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SA",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109476000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Kronach",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105915000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Hamm",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "106534000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Marburg-Biedenkopf",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "107133000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Bad Kreuznach",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703901600000,
        "regionName": "Kreis Bad Kreuznach",
        "end": 1703912400000,
        "description": "Es treten oberhalb 600 m Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": 600,
        "altitudeEnd": null
      }
    ],
    "105916000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Herne",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103359000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Stade",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105382000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Rhein-Sieg-Kreis",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103402000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Emden",
        "end": 1703934000000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "116066000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 3,
        "start": 1703759520000,
        "regionName": "Kreis Schmalkalden-Meiningen",
        "end": 1703934000000,
        "description": "Es treten oberhalb 800 m Sturmböen mit Geschwindigkeiten zwischen 65 km/h (18 m/s, 35 kn, Bft 8) und 80 km/h (22 m/s, 44 kn, Bft 9) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "TH",
        "altitudeStart": 800,
        "altitudeEnd": null
      },
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Schmalkalden-Meiningen",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "115084000": [
      {
        "state": "Sachsen-Anhalt",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Burgenlandkreis",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SA",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103103000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Wolfsburg",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105766000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Lippe",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109475000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Hof",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105962000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 2,
        "level": 3,
        "start": 1703833200000,
        "regionName": "Märkischer Kreis",
        "end": 1703916000000,
        "description": "Es tritt Dauerregen auf. Dabei werden Niederschlagsmengen bis 30 l/m² erwartet.",
        "event": "DAUERREGEN",
        "headline": "Amtliche WARNUNG vor DAUERREGEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Märkischer Kreis",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "106431000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Bergstraße",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "915085002": [
      {
        "state": "Sachsen-Anhalt",
        "type": 1,
        "level": 4,
        "start": 1703782800000,
        "regionName": "Kreis Harz - Bergland (Oberharz)",
        "end": 1703890800000,
        "description": "Es treten oberhalb 1000 m Orkanböen mit Geschwindigkeiten zwischen 100 km/h (28 m/s, 55 kn, Bft 10) und 120 km/h (33 m/s, 64 kn, Bft 12) aus südwestlicher Richtung auf.",
        "event": "ORKANBÖEN",
        "headline": "Amtliche UNWETTERWARNUNG vor ORKANBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es sind unter anderem verbreitet schwere Schäden an Gebäuden möglich. Bäume können zum Beispiel entwurzelt werden und Dachziegel, Äste oder Gegenstände herabstürzen. Schließen Sie alle Fenster und Türen! Sichern Sie Gegenstände im Freien! Halten Sie insbesondere Abstand von Gebäuden, Bäumen, Gerüsten und Hochspannungsleitungen. Vermeiden Sie möglichst den Aufenthalt im Freien!",
        "stateShort": "SA",
        "altitudeStart": 1000,
        "altitudeEnd": null
      },
      {
        "state": "Sachsen-Anhalt",
        "type": 1,
        "level": 3,
        "start": 1703856660000,
        "regionName": "Kreis Harz - Bergland (Oberharz)",
        "end": 1703872800000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 60 km/h (17 m/s, 33 kn, Bft 7) und 70 km/h (20 m/s, 38 kn, Bft 8) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "SA",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Sachsen-Anhalt",
        "type": 2,
        "level": 3,
        "start": 1703844000000,
        "regionName": "Kreis Harz - Bergland (Oberharz)",
        "end": 1703923200000,
        "description": "Es tritt Dauerregen auf. Dabei werden Niederschlagsmengen bis 30 l/m² erwartet.",
        "event": "DAUERREGEN",
        "headline": "Amtliche WARNUNG vor DAUERREGEN",
        "instruction": "",
        "stateShort": "SA",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Sachsen-Anhalt",
        "type": 1,
        "level": 3,
        "start": 1703890800000,
        "regionName": "Kreis Harz - Bergland (Oberharz)",
        "end": 1703934000000,
        "description": "Es treten oberhalb 1000 m schwere Sturmböen mit Geschwindigkeiten um 100 km/h (28 m/s, 55 kn, Bft 10) aus südwestlicher Richtung auf.",
        "event": "SCHWERE STURMBÖEN",
        "headline": "Amtliche WARNUNG vor SCHWEREN STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Vereinzelt können zum Beispiel Bäume entwurzelt und Dächer beschädigt werden. Achten Sie besonders auf herabstürzende Äste, Dachziegel oder Gegenstände.",
        "stateShort": "SA",
        "altitudeStart": 1000,
        "altitudeEnd": null
      },
      {
        "state": "Sachsen-Anhalt",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Harz - Bergland (Oberharz)",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SA",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "915085001": [
      {
        "state": "Sachsen-Anhalt",
        "type": 1,
        "level": 3,
        "start": 1703856660000,
        "regionName": "Kreis Harz - Tiefland",
        "end": 1703872800000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 60 km/h (17 m/s, 33 kn, Bft 7) und 70 km/h (20 m/s, 38 kn, Bft 8) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "SA",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Sachsen-Anhalt",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Harz - Tiefland",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SA",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "115087000": [
      {
        "state": "Sachsen-Anhalt",
        "type": 2,
        "level": 3,
        "start": 1703844000000,
        "regionName": "Kreis Mansfeld-Südharz",
        "end": 1703923200000,
        "description": "Es tritt Dauerregen auf. Dabei werden Niederschlagsmengen bis 30 l/m² erwartet.",
        "event": "DAUERREGEN",
        "headline": "Amtliche WARNUNG vor DAUERREGEN",
        "instruction": "",
        "stateShort": "SA",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Sachsen-Anhalt",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Mansfeld-Südharz",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SA",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "115002000": [
      {
        "state": "Sachsen-Anhalt",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Halle (Saale)",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SA",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "116068000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Sömmerda",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "114511000": [
      {
        "state": "Sachsen",
        "type": 1,
        "level": 3,
        "start": 1703856660000,
        "regionName": "Stadt Chemnitz",
        "end": 1703872800000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 60 km/h (17 m/s, 33 kn, Bft 7) und 70 km/h (20 m/s, 38 kn, Bft 8) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Sachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Chemnitz",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "101053000": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Herzogtum Lauenburg",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "107134000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Birkenfeld",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703901600000,
        "regionName": "Kreis Birkenfeld",
        "end": 1703912400000,
        "description": "Es treten oberhalb 600 m Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": 600,
        "altitudeEnd": null
      }
    ],
    "116067000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 3,
        "start": 1703759520000,
        "regionName": "Kreis Gotha",
        "end": 1703934000000,
        "description": "Es treten oberhalb 800 m Sturmböen mit Geschwindigkeiten zwischen 65 km/h (18 m/s, 35 kn, Bft 8) und 80 km/h (22 m/s, 44 kn, Bft 9) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "TH",
        "altitudeStart": 800,
        "altitudeEnd": null
      },
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Gotha",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "106432000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Darmstadt-Dieburg und Stadt Darmstadt",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "115088000": [
      {
        "state": "Sachsen-Anhalt",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Saalekreis",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SA",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "901057001": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Plön - Binnenland",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105770000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Minden-Lübbecke",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "901057002": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Plön - Küste",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105513000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Gelsenkirchen",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "116069000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 3,
        "start": 1703759520000,
        "regionName": "Kreis Hildburghausen",
        "end": 1703934000000,
        "description": "Es treten oberhalb 800 m Sturmböen mit Geschwindigkeiten zwischen 65 km/h (18 m/s, 35 kn, Bft 8) und 80 km/h (22 m/s, 44 kn, Bft 9) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "TH",
        "altitudeStart": 800,
        "altitudeEnd": null
      },
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Hildburghausen",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "901058001": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Rendsburg-Eckernförde - Binnenland",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "203259000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Steinhuder Meer",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "901058002": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Rendsburg-Eckernförde - Küste",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "115086000": [
      {
        "state": "Sachsen-Anhalt",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Jerichower Land",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SA",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103101000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Braunschweig",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109473000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Coburg",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "115001000": [
      {
        "state": "Sachsen-Anhalt",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Dessau-Roßlau",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SA",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "107135000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Cochem-Zell",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105954000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 2,
        "level": 3,
        "start": 1703833200000,
        "regionName": "Ennepe-Ruhr-Kreis",
        "end": 1703916000000,
        "description": "Es tritt Dauerregen auf. Dabei werden Niederschlagsmengen bis 30 l/m² erwartet.",
        "event": "DAUERREGEN",
        "headline": "Amtliche WARNUNG vor DAUERREGEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Ennepe-Ruhr-Kreis",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "107340000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Südwestpfalz und Stadt Pirmasens",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105911000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Bochum",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103460000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Vechta",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "107233000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Vulkaneifel",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703901600000,
        "regionName": "Kreis Vulkaneifel",
        "end": 1703912400000,
        "description": "Es treten oberhalb 600 m Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": 600,
        "altitudeEnd": null
      }
    ],
    "907235999": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Trier-Saarburg und Stadt Trier",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703901600000,
        "regionName": "Kreis Trier-Saarburg und Stadt Trier",
        "end": 1703912400000,
        "description": "Es treten oberhalb 600 m Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": 600,
        "altitudeEnd": null
      }
    ],
    "115090000": [
      {
        "state": "Sachsen-Anhalt",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Stendal",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SA",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "203258000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Dümmer See",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103459000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Osnabrück",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "501000008": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703840160000,
        "regionName": "Östlich Rügen",
        "end": null,
        "description": "Südwest 6 bis 7, dabei Böen von 9 Beaufort, strichweise Gewitter.",
        "event": "STARKWIND",
        "headline": "Amtliche Warnung des Seewetterdienstes Hamburg vor STARKWIND",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105122000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Solingen",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "914730001": [
      {
        "state": "Sachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Nordsachsen - Nord",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105314000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Bonn",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105378000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 2,
        "level": 3,
        "start": 1703833200000,
        "regionName": "Rheinisch-Bergischer Kreis",
        "end": 1703916000000,
        "description": "Es tritt Dauerregen auf. Dabei werden Niederschlagsmengen bis 30 l/m² erwartet.",
        "event": "DAUERREGEN",
        "headline": "Amtliche WARNUNG vor DAUERREGEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Rheinisch-Bergischer Kreis",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "914730002": [
      {
        "state": "Sachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Nordsachsen - Süd",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "501000004": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703866320000,
        "regionName": "Elbe von Hamburg bis Cuxhaven",
        "end": null,
        "description": "Westteil Südwest bis West 5 bis 6, dabei Böen von 8 Beaufort, strichweise Gewitter.",
        "event": "STARKWIND",
        "headline": "Amtliche Warnung des Seewetterdienstes Hamburg vor STARKWIND",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "501000005": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703866320000,
        "regionName": "Nordfriesische Küste",
        "end": null,
        "description": "Südwest bis West 6 bis 7, dabei Böen von 9 Beaufort, strichweise Gewitter.",
        "event": "STARKWIND",
        "headline": "Amtliche Warnung des Seewetterdienstes Hamburg vor STARKWIND",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109674000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Haßberge",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "501000006": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703840160000,
        "regionName": "Flensburg bis Fehmarn",
        "end": null,
        "description": "Südwest 6 bis 7, dabei Böen von 9 Beaufort, strichweise Gewitter.",
        "event": "STARKWIND",
        "headline": "Amtliche Warnung des Seewetterdienstes Hamburg vor STARKWIND",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105570000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Warendorf",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "501000007": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703840160000,
        "regionName": "Östlich Fehmarn bis Rügen",
        "end": null,
        "description": "Südwest 6 bis 7, dabei Böen von 9 Beaufort, strichweise Gewitter.",
        "event": "STARKWIND",
        "headline": "Amtliche Warnung des Seewetterdienstes Hamburg vor STARKWIND",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "116070000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 3,
        "start": 1703759520000,
        "regionName": "Ilm-Kreis",
        "end": 1703934000000,
        "description": "Es treten oberhalb 800 m Sturmböen mit Geschwindigkeiten zwischen 65 km/h (18 m/s, 35 kn, Bft 8) und 80 km/h (22 m/s, 44 kn, Bft 9) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "TH",
        "altitudeStart": 800,
        "altitudeEnd": null
      },
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Ilm-Kreis",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "501000001": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703866320000,
        "regionName": "Ostfriesische Küste",
        "end": null,
        "description": "Südwest bis West 6 bis 7, dabei Böen von 9 Beaufort, strichweise Gewitter.",
        "event": "STARKWIND",
        "headline": "Amtliche Warnung des Seewetterdienstes Hamburg vor STARKWIND",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "107339000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Mainz-Bingen und Stadt Mainz",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "112062000": [
      {
        "state": "Brandenburg",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Elbe-Elster",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BB",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105762000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Höxter",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "501000002": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703866320000,
        "regionName": "Helgoland",
        "end": null,
        "description": "Südwest bis West 6 bis 7, dabei Böen von 9 Beaufort, strichweise Gewitter.",
        "event": "STARKWIND",
        "headline": "Amtliche Warnung des Seewetterdienstes Hamburg vor STARKWIND",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "501000003": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703866320000,
        "regionName": "Elbe-/Wesermündung",
        "end": null,
        "description": "Südwest bis West 6 bis 7, dabei Böen von 9 Beaufort, strichweise Gewitter.",
        "event": "STARKWIND",
        "headline": "Amtliche Warnung des Seewetterdienstes Hamburg vor STARKWIND",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109673000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 3,
        "start": 1703763480000,
        "regionName": "Kreis Rhön-Grabfeld",
        "end": 1703923200000,
        "description": "Es treten oberhalb 800 m Sturmböen mit Geschwindigkeiten um 70 km/h (20 m/s, 38 kn, Bft 8) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BY",
        "altitudeStart": 800,
        "altitudeEnd": null
      },
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Rhön-Grabfeld",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105974000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Soest",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "115003000": [
      {
        "state": "Sachsen-Anhalt",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Magdeburg",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SA",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "106635000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 3,
        "start": 1703840580000,
        "regionName": "Kreis Waldeck-Frankenberg",
        "end": 1703923200000,
        "description": "Es treten oberhalb 600 m Sturmböen mit Geschwindigkeiten zwischen 65 km/h (18 m/s, 35 kn, Bft 8) und 80 km/h (22 m/s, 44 kn, Bft 9) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "HE",
        "altitudeStart": 600,
        "altitudeEnd": null
      },
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Waldeck-Frankenberg",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "107320000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Zweibrücken",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "909475999": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Hof",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109780000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 3,
        "start": 1703836800000,
        "regionName": "Kreis Oberallgäu",
        "end": 1703926800000,
        "description": "Es treten oberhalb 1500 m Sturmböen mit Geschwindigkeiten um 75 km/h (21 m/s, 41 kn, Bft 9) anfangs aus südwestlicher, später aus westlicher Richtung auf. In exponierten Lagen muss mit Sturmböen bis 85 km/h (24 m/s, 47 kn, Bft 9) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BY",
        "altitudeStart": 1500,
        "altitudeEnd": null
      }
    ],
    "116072000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 3,
        "start": 1703759520000,
        "regionName": "Kreis Sonneberg",
        "end": 1703934000000,
        "description": "Es treten oberhalb 800 m Sturmböen mit Geschwindigkeiten zwischen 65 km/h (18 m/s, 35 kn, Bft 8) und 80 km/h (22 m/s, 44 kn, Bft 9) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "TH",
        "altitudeStart": 800,
        "altitudeEnd": null
      },
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Sonneberg",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109182000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 3,
        "start": 1703836800000,
        "regionName": "Kreis Miesbach",
        "end": 1703926800000,
        "description": "Es treten oberhalb 1500 m Sturmböen mit Geschwindigkeiten um 75 km/h (21 m/s, 41 kn, Bft 9) anfangs aus südwestlicher, später aus westlicher Richtung auf. In exponierten Lagen muss mit Sturmböen bis 85 km/h (24 m/s, 47 kn, Bft 9) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BY",
        "altitudeStart": 1500,
        "altitudeEnd": null
      }
    ],
    "116071000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Weimarer Land",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "115089000": [
      {
        "state": "Sachsen-Anhalt",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Salzlandkreis",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SA",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105334000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "StädteRegion Aachen",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703901600000,
        "regionName": "StädteRegion Aachen",
        "end": 1703912400000,
        "description": "Es treten oberhalb 600 m Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": 600,
        "altitudeEnd": null
      }
    ],
    "903452001": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Aurich - Binnenland",
        "end": 1703934000000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "108237000": [
      {
        "state": "Baden-Württemberg",
        "type": 1,
        "level": 3,
        "start": 1703869200000,
        "regionName": "Kreis Freudenstadt",
        "end": 1703923200000,
        "description": "Es treten oberhalb 1000 m Sturmböen mit Geschwindigkeiten um 80km/h (22 m/s, 44 kn, Bft 9) aus südwestlicher Richtung auf. In exponierten Lagen muss mit schweren Sturmböen um 90 km/h (25 m/s, 48 kn, Bft 10) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BW",
        "altitudeStart": 1000,
        "altitudeEnd": null
      }
    ],
    "903452002": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 3,
        "start": 1703869200000,
        "regionName": "Kreis Aurich - Küste",
        "end": 1703934000000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 55 km/h (15 m/s, 30 kn, Bft 7) und 75 km/h (21 m/s, 41 kn, Bft 9) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "106636000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Werra-Meißner-Kreis",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105914000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 2,
        "level": 3,
        "start": 1703833200000,
        "regionName": "Stadt Hagen",
        "end": 1703916000000,
        "description": "Es tritt Dauerregen auf. Dabei werden Niederschlagsmengen bis 30 l/m² erwartet.",
        "event": "DAUERREGEN",
        "headline": "Amtliche WARNUNG vor DAUERREGEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Hagen",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "903455001": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Friesland - Binnenland",
        "end": 1703934000000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105978000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Unna",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "116073000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 3,
        "start": 1703759520000,
        "regionName": "Kreis Saalfeld-Rudolstadt",
        "end": 1703934000000,
        "description": "Es treten oberhalb 800 m Sturmböen mit Geschwindigkeiten zwischen 65 km/h (18 m/s, 35 kn, Bft 8) und 80 km/h (22 m/s, 44 kn, Bft 9) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "TH",
        "altitudeStart": 800,
        "altitudeEnd": null
      },
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Saalfeld-Rudolstadt",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "903455002": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 3,
        "start": 1703869200000,
        "regionName": "Kreis Friesland - Küste",
        "end": 1703934000000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 55 km/h (15 m/s, 30 kn, Bft 7) und 75 km/h (21 m/s, 41 kn, Bft 9) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109672000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 3,
        "start": 1703763480000,
        "regionName": "Kreis Bad Kissingen",
        "end": 1703923200000,
        "description": "Es treten oberhalb 800 m Sturmböen mit Geschwindigkeiten um 70 km/h (20 m/s, 38 kn, Bft 8) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BY",
        "altitudeStart": 800,
        "altitudeEnd": null
      },
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Bad Kissingen",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "116052000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Gera",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "909471999": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Bamberg",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "907339999": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Mainz-Bingen und Stadt Mainz",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "106533000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Limburg-Weilburg",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109671000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Aschaffenburg",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "909472999": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 3,
        "start": 1703763480000,
        "regionName": "Kreis und Stadt Bayreuth",
        "end": 1703934000000,
        "description": "Es treten oberhalb 1000 m Sturmböen mit Geschwindigkeiten um 70 km/h (20 m/s, 38 kn, Bft 8) aus südwestlicher Richtung auf. In exponierten Lagen muss mit Sturmböen bis 85 km/h (24 m/s, 47 kn, Bft 9) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BY",
        "altitudeStart": 1000,
        "altitudeEnd": null
      }
    ],
    "116051000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Erfurt",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "907340999": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Südwestpfalz und Stadt Pirmasens",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "104012000": [
      {
        "state": "Bremen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Bremerhaven",
        "end": 1703934000000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HB",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103158000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Wolfenbüttel",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "107235000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Trier-Saarburg und Stadt Trier",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703901600000,
        "regionName": "Kreis Trier-Saarburg und Stadt Trier",
        "end": 1703912400000,
        "description": "Es treten oberhalb 600 m Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": 600,
        "altitudeEnd": null
      }
    ],
    "109479000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 3,
        "start": 1703763480000,
        "regionName": "Kreis Wunsiedel i. Fichtelgebirge",
        "end": 1703934000000,
        "description": "Es treten oberhalb 1000 m Sturmböen mit Geschwindigkeiten um 70 km/h (20 m/s, 38 kn, Bft 8) aus südwestlicher Richtung auf. In exponierten Lagen muss mit Sturmböen bis 85 km/h (24 m/s, 47 kn, Bft 9) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BY",
        "altitudeStart": 1000,
        "altitudeEnd": null
      },
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Wunsiedel i. Fichtelgebirge",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "106531000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Gießen",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109180000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 3,
        "start": 1703836800000,
        "regionName": "Kreis Garmisch-Partenkirchen",
        "end": 1703926800000,
        "description": "Es treten oberhalb 1500 m Sturmböen mit Geschwindigkeiten um 75 km/h (21 m/s, 41 kn, Bft 9) anfangs aus südwestlicher, später aus westlicher Richtung auf. In exponierten Lagen muss mit Sturmböen bis 85 km/h (24 m/s, 47 kn, Bft 9) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BY",
        "altitudeStart": 1500,
        "altitudeEnd": null
      }
    ],
    "116053000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Jena",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "907338999": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Rhein-Pfalz-Kreis und Stadt Ludwigshafen",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109777000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 3,
        "start": 1703836800000,
        "regionName": "Kreis Ostallgäu",
        "end": 1703926800000,
        "description": "Es treten oberhalb 1500 m Sturmböen mit Geschwindigkeiten um 75 km/h (21 m/s, 41 kn, Bft 9) anfangs aus südwestlicher, später aus westlicher Richtung auf. In exponierten Lagen muss mit Sturmböen bis 85 km/h (24 m/s, 47 kn, Bft 9) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BY",
        "altitudeStart": 1500,
        "altitudeEnd": null
      }
    ],
    "105124000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 2,
        "level": 3,
        "start": 1703833200000,
        "regionName": "Stadt Wuppertal",
        "end": 1703916000000,
        "description": "Es tritt Dauerregen auf. Dabei werden Niederschlagsmengen bis 30 l/m² erwartet.",
        "event": "DAUERREGEN",
        "headline": "Amtliche WARNUNG vor DAUERREGEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Wuppertal",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109372000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 3,
        "start": 1703763480000,
        "regionName": "Kreis Cham",
        "end": 1703934000000,
        "description": "Es treten oberhalb 1000 m Sturmböen mit Geschwindigkeiten um 70 km/h (20 m/s, 38 kn, Bft 8) aus südwestlicher Richtung auf. In exponierten Lagen muss mit Sturmböen bis 85 km/h (24 m/s, 47 kn, Bft 9) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BY",
        "altitudeStart": 1000,
        "altitudeEnd": null
      }
    ],
    "115091000": [
      {
        "state": "Sachsen-Anhalt",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Wittenberg",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SA",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "112061000": [
      {
        "state": "Brandenburg",
        "type": 1,
        "level": 2,
        "start": 1703890800000,
        "regionName": "Kreis Dahme-Spreewald",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BB",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "101004000": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Neumünster",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105316000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Leverkusen",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103351000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Celle",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105166000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Viersen",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105358000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Düren",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105913000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Dortmund",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "106532000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Lahn-Dill-Kreis",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703901600000,
        "regionName": "Lahn-Dill-Kreis",
        "end": 1703912400000,
        "description": "Es treten oberhalb 600 m Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": 600,
        "altitudeEnd": null
      }
    ],
    "909473999": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Coburg",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "116074000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Saale-Holzland-Kreis",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "101003000": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Hansestadt Lübeck",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103159000": [
      {
        "state": "Niedersachsen",
        "type": 2,
        "level": 3,
        "start": 1703848020000,
        "regionName": "Kreis Göttingen",
        "end": 1703923200000,
        "description": "Es tritt Dauerregen auf. Dabei werden Niederschlagsmengen bis 30 l/m² erwartet.",
        "event": "DAUERREGEN",
        "headline": "Amtliche WARNUNG vor DAUERREGEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Göttingen",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105315000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Köln",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "114729000": [
      {
        "state": "Sachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Leipzig",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105970000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 3,
        "start": 1703840580000,
        "regionName": "Kreis Siegen-Wittgenstein",
        "end": 1703923200000,
        "description": "Es treten oberhalb 600 m Sturmböen mit Geschwindigkeiten zwischen 65 km/h (18 m/s, 35 kn, Bft 8) und 80 km/h (22 m/s, 44 kn, Bft 9) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "NRW",
        "altitudeStart": 600,
        "altitudeEnd": null
      },
      {
        "state": "Nordrhein-Westfalen",
        "type": 2,
        "level": 3,
        "start": 1703833200000,
        "regionName": "Kreis Siegen-Wittgenstein",
        "end": 1703916000000,
        "description": "Es tritt Dauerregen auf. Dabei werden Niederschlagsmengen bis 30 l/m² erwartet.",
        "event": "DAUERREGEN",
        "headline": "Amtliche WARNUNG vor DAUERREGEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Siegen-Wittgenstein",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "106439000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Rheingau-Taunus-Kreis",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703901600000,
        "regionName": "Rheingau-Taunus-Kreis",
        "end": 1703912400000,
        "description": "Es treten oberhalb 600 m Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": 600,
        "altitudeEnd": null
      }
    ],
    "106631000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 3,
        "start": 1703759760000,
        "regionName": "Kreis Fulda",
        "end": 1703923200000,
        "description": "Es treten oberhalb 800 m Sturmböen mit Geschwindigkeiten zwischen 65 km/h (18 m/s, 35 kn, Bft 8) und 80 km/h (22 m/s, 44 kn, Bft 9) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "HE",
        "altitudeStart": 800,
        "altitudeEnd": null
      },
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Fulda",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "913073001": [
      {
        "state": "Mecklenburg-Vorpommern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Vorpommern-Rügen - Binnenland",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "MV",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "906633999": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Kassel",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103156000": [
      {
        "state": "Niedersachsen",
        "type": 2,
        "level": 3,
        "start": 1703848020000,
        "regionName": "Kreis Göttingen",
        "end": 1703923200000,
        "description": "Es tritt Dauerregen auf. Dabei werden Niederschlagsmengen bis 30 l/m² erwartet.",
        "event": "DAUERREGEN",
        "headline": "Amtliche WARNUNG vor DAUERREGEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Göttingen",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "913073002": [
      {
        "state": "Mecklenburg-Vorpommern",
        "type": 1,
        "level": 3,
        "start": 1703869200000,
        "regionName": "Kreis Vorpommern-Rügen - Küste",
        "end": 1703890800000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 55 km/h (15 m/s, 30 kn, Bft 7) und 65 km/h (18 m/s, 35 kn, Bft 8) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "MV",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Mecklenburg-Vorpommern",
        "type": 1,
        "level": 2,
        "start": 1703890800000,
        "regionName": "Kreis Vorpommern-Rügen - Küste",
        "end": 1703934000000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "MV",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "913073003": [
      {
        "state": "Mecklenburg-Vorpommern",
        "type": 1,
        "level": 3,
        "start": 1703869200000,
        "regionName": "Kreis Vorpommern-Rügen - Insel Rügen",
        "end": 1703890800000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 55 km/h (15 m/s, 30 kn, Bft 7) und 65 km/h (18 m/s, 35 kn, Bft 8) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "MV",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Mecklenburg-Vorpommern",
        "type": 1,
        "level": 2,
        "start": 1703890800000,
        "regionName": "Kreis Vorpommern-Rügen - Insel Rügen",
        "end": 1703934000000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "MV",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109189000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 3,
        "start": 1703836800000,
        "regionName": "Kreis Traunstein",
        "end": 1703926800000,
        "description": "Es treten oberhalb 1500 m Sturmböen mit Geschwindigkeiten um 75 km/h (21 m/s, 41 kn, Bft 9) anfangs aus südwestlicher, später aus westlicher Richtung auf. In exponierten Lagen muss mit Sturmböen bis 85 km/h (24 m/s, 47 kn, Bft 9) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BY",
        "altitudeStart": 1500,
        "altitudeEnd": null
      }
    ],
    "105117000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Mülheim an der Ruhr",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "116076000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Greiz",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "108315000": [
      {
        "state": "Baden-Württemberg",
        "type": 1,
        "level": 3,
        "start": 1703869200000,
        "regionName": "Kreis Breisgau-Hochschwarzwald und Stadt Freiburg",
        "end": 1703923200000,
        "description": "Es treten oberhalb 1000 m Sturmböen mit Geschwindigkeiten um 80km/h (22 m/s, 44 kn, Bft 9) aus südwestlicher Richtung auf. In exponierten Lagen muss mit schweren Sturmböen um 90 km/h (25 m/s, 48 kn, Bft 10) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BW",
        "altitudeStart": 1000,
        "altitudeEnd": null
      }
    ],
    "107313000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Landau in der Pfalz",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103241000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Region Hannover",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "914522002": [
      {
        "state": "Sachsen",
        "type": 1,
        "level": 3,
        "start": 1703856660000,
        "regionName": "Kreis Mittelsachsen - Bergland",
        "end": 1703872800000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 60 km/h (17 m/s, 33 kn, Bft 7) und 70 km/h (20 m/s, 38 kn, Bft 8) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Sachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Mittelsachsen - Bergland",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109679000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Würzburg",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "914522001": [
      {
        "state": "Sachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Mittelsachsen - Tiefland",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "116075000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Saale-Orla-Kreis",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "108316000": [
      {
        "state": "Baden-Württemberg",
        "type": 1,
        "level": 3,
        "start": 1703869200000,
        "regionName": "Kreis Emmendingen",
        "end": 1703923200000,
        "description": "Es treten oberhalb 1000 m Sturmböen mit Geschwindigkeiten um 80km/h (22 m/s, 44 kn, Bft 9) aus südwestlicher Richtung auf. In exponierten Lagen muss mit schweren Sturmböen um 90 km/h (25 m/s, 48 kn, Bft 10) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BW",
        "altitudeStart": 1000,
        "altitudeEnd": null
      }
    ],
    "101002000": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Kiel",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "112067000": [
      {
        "state": "Brandenburg",
        "type": 1,
        "level": 2,
        "start": 1703890800000,
        "regionName": "Kreis Oder-Spree",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BB",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "106440000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Wetteraukreis",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "903352001": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Cuxhaven - Binnenland",
        "end": 1703934000000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "903352002": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Cuxhaven - Küste",
        "end": 1703934000000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "116054000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 3,
        "start": 1703759520000,
        "regionName": "Stadt Suhl",
        "end": 1703934000000,
        "description": "Es treten oberhalb 800 m Sturmböen mit Geschwindigkeiten zwischen 65 km/h (18 m/s, 35 kn, Bft 8) und 80 km/h (22 m/s, 44 kn, Bft 9) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "TH",
        "altitudeStart": 800,
        "altitudeEnd": null
      },
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Suhl",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103454000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Emsland",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "106632000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Hersfeld-Rotenburg",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "108337000": [
      {
        "state": "Baden-Württemberg",
        "type": 1,
        "level": 3,
        "start": 1703869200000,
        "regionName": "Kreis Waldshut",
        "end": 1703923200000,
        "description": "Es treten oberhalb 1000 m Sturmböen mit Geschwindigkeiten um 80km/h (22 m/s, 44 kn, Bft 9) aus südwestlicher Richtung auf. In exponierten Lagen muss mit schweren Sturmböen um 90 km/h (25 m/s, 48 kn, Bft 10) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BW",
        "altitudeStart": 1000,
        "altitudeEnd": null
      }
    ],
    "103155000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Northeim",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "110042000": [
      {
        "state": "Saarland",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Merzig-Wadern",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SL",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Saarland",
        "type": 1,
        "level": 2,
        "start": 1703901600000,
        "regionName": "Kreis Merzig-Wadern",
        "end": 1703912400000,
        "description": "Es treten oberhalb 600 m Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SL",
        "altitudeStart": 600,
        "altitudeEnd": null
      }
    ],
    "105116000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Mönchengladbach",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "116077000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Altenburger Land",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "909278999": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 3,
        "start": 1703763480000,
        "regionName": "Kreis Straubing-Bogen und Stadt Straubing",
        "end": 1703934000000,
        "description": "Es treten oberhalb 1000 m Sturmböen mit Geschwindigkeiten um 70 km/h (20 m/s, 38 kn, Bft 8) aus südwestlicher Richtung auf. In exponierten Lagen muss mit Sturmböen bis 85 km/h (24 m/s, 47 kn, Bft 9) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BY",
        "altitudeStart": 1000,
        "altitudeEnd": null
      }
    ],
    "107336000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Kusel",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "914628001": [
      {
        "state": "Sachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Sächsische Schweiz-Osterzgebirge - Tiefland",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "112069000": [
      {
        "state": "Brandenburg",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Potsdam-Mittelmark",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BB",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "914628002": [
      {
        "state": "Sachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Sächsische Schweiz-Osterzgebirge - westelbisches Bergland",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "110041000": [
      {
        "state": "Saarland",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Regionalverband Saarbrücken",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SL",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "914628003": [
      {
        "state": "Sachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Sächsische Schweiz-Osterzgebirge - ostelbisches Bergland",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "106438000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Offenbach",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103456000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Grafschaft Bentheim",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "116056000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Eisenach",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "907335999": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Kaiserslautern",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "101001000": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Flensburg",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103157000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Peine",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "116055000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Weimar",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "903457002": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 3,
        "start": 1703869200000,
        "regionName": "Insel Borkum",
        "end": 1703934000000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 55 km/h (15 m/s, 30 kn, Bft 7) und 75 km/h (21 m/s, 41 kn, Bft 9) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105158000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Mettmann",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109678000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Schweinfurt",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "107143000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Westerwaldkreis",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703901600000,
        "regionName": "Westerwaldkreis",
        "end": 1703912400000,
        "description": "Es treten oberhalb 600 m Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": 600,
        "altitudeEnd": null
      }
    ],
    "109187000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 3,
        "start": 1703836800000,
        "regionName": "Kreis und Stadt Rosenheim",
        "end": 1703926800000,
        "description": "Es treten oberhalb 1500 m Sturmböen mit Geschwindigkeiten um 75 km/h (21 m/s, 41 kn, Bft 9) anfangs aus südwestlicher, später aus westlicher Richtung auf. In exponierten Lagen muss mit Sturmböen bis 85 km/h (24 m/s, 47 kn, Bft 9) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BY",
        "altitudeStart": 1500,
        "altitudeEnd": null
      }
    ],
    "108317000": [
      {
        "state": "Baden-Württemberg",
        "type": 1,
        "level": 3,
        "start": 1703869200000,
        "regionName": "Ortenaukreis",
        "end": 1703923200000,
        "description": "Es treten oberhalb 1000 m Sturmböen mit Geschwindigkeiten um 80km/h (22 m/s, 44 kn, Bft 9) aus südwestlicher Richtung auf. In exponierten Lagen muss mit schweren Sturmböen um 90 km/h (25 m/s, 48 kn, Bft 10) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BW",
        "altitudeStart": 1000,
        "altitudeEnd": null
      }
    ],
    "107335000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Kaiserslautern",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "913074001": [
      {
        "state": "Mecklenburg-Vorpommern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Nordwestmecklenburg - Binnenland",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "MV",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "913074002": [
      {
        "state": "Mecklenburg-Vorpommern",
        "type": 1,
        "level": 3,
        "start": 1703869200000,
        "regionName": "Kreis Nordwestmecklenburg - Küste",
        "end": 1703890800000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 55 km/h (15 m/s, 30 kn, Bft 7) und 65 km/h (18 m/s, 35 kn, Bft 8) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "MV",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Mecklenburg-Vorpommern",
        "type": 1,
        "level": 2,
        "start": 1703890800000,
        "regionName": "Kreis Nordwestmecklenburg - Küste",
        "end": 1703934000000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "MV",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109571000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Ansbach",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109677000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Main-Spessart",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "108126000": [
      {
        "state": "Baden-Württemberg",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Hohenlohekreis",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109272000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 3,
        "start": 1703763480000,
        "regionName": "Kreis Freyung-Grafenau",
        "end": 1703934000000,
        "description": "Es treten oberhalb 1000 m Sturmböen mit Geschwindigkeiten um 70 km/h (20 m/s, 38 kn, Bft 8) aus südwestlicher Richtung auf. In exponierten Lagen muss mit Sturmböen bis 85 km/h (24 m/s, 47 kn, Bft 9) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BY",
        "altitudeStart": 1000,
        "altitudeEnd": null
      }
    ],
    "105120000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 2,
        "level": 3,
        "start": 1703833200000,
        "regionName": "Stadt Remscheid",
        "end": 1703916000000,
        "description": "Es tritt Dauerregen auf. Dabei werden Niederschlagsmengen bis 30 l/m² erwartet.",
        "event": "DAUERREGEN",
        "headline": "Amtliche WARNUNG vor DAUERREGEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Remscheid",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "113003000": [
      {
        "state": "Mecklenburg-Vorpommern",
        "type": 1,
        "level": 3,
        "start": 1703869200000,
        "regionName": "Hansestadt Rostock",
        "end": 1703890800000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 55 km/h (15 m/s, 30 kn, Bft 7) und 65 km/h (18 m/s, 35 kn, Bft 8) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "MV",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Mecklenburg-Vorpommern",
        "type": 1,
        "level": 2,
        "start": 1703890800000,
        "regionName": "Hansestadt Rostock",
        "end": 1703934000000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "MV",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "107316000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Neustadt an der Weinstraße",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "903459999": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Osnabrück",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "909679999": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Würzburg",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "106634000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Schwalm-Eder-Kreis",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103153000": [
      {
        "state": "Niedersachsen",
        "type": 2,
        "level": 3,
        "start": 1703848020000,
        "regionName": "Kreis Goslar",
        "end": 1703923200000,
        "description": "Es tritt Dauerregen auf. Dabei werden Niederschlagsmengen bis 30 l/m² erwartet.",
        "event": "DAUERREGEN",
        "headline": "Amtliche WARNUNG vor DAUERREGEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Goslar",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "107337000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Südliche Weinstraße",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "913075004": [
      {
        "state": "Mecklenburg-Vorpommern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Vorpommern-Greifswald - Küste Süd",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "MV",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "906438999": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Offenbach",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "903461002": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Wesermarsch - Küste",
        "end": 1703934000000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105162000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Rhein-Kreis Neuss",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "913075001": [
      {
        "state": "Mecklenburg-Vorpommern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Vorpommern-Greifswald - Binnenland Nord",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "MV",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "914626001": [
      {
        "state": "Sachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Görlitz - Tiefland",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "913075002": [
      {
        "state": "Mecklenburg-Vorpommern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Vorpommern-Greifswald - Küste Nord",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "MV",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "914626002": [
      {
        "state": "Sachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Görlitz - Bergland",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105354000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "StädteRegion Aachen",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703901600000,
        "regionName": "StädteRegion Aachen",
        "end": 1703912400000,
        "description": "Es treten oberhalb 600 m Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": 600,
        "altitudeEnd": null
      }
    ],
    "109271000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 3,
        "start": 1703763480000,
        "regionName": "Kreis Deggendorf",
        "end": 1703934000000,
        "description": "Es treten oberhalb 1000 m Sturmböen mit Geschwindigkeiten um 70 km/h (20 m/s, 38 kn, Bft 8) aus südwestlicher Richtung auf. In exponierten Lagen muss mit Sturmböen bis 85 km/h (24 m/s, 47 kn, Bft 9) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BY",
        "altitudeStart": 1000,
        "altitudeEnd": null
      }
    ],
    "105119000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Oberhausen",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "107232000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Eifelkreis Bitburg-Prüm",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703901600000,
        "regionName": "Eifelkreis Bitburg-Prüm",
        "end": 1703912400000,
        "description": "Es treten oberhalb 600 m Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": 600,
        "altitudeEnd": null
      }
    ],
    "109676000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Miltenberg",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "108127000": [
      {
        "state": "Baden-Württemberg",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Schwäbisch Hall",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "914625001": [
      {
        "state": "Sachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Bautzen - Tiefland",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "114627000": [
      {
        "state": "Sachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Meißen",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "914625002": [
      {
        "state": "Sachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Bautzen - Bergland",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109675000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Kitzingen",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "108128000": [
      {
        "state": "Baden-Württemberg",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Main-Tauber-Kreis",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "106633000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Kassel",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "107338000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Rhein-Pfalz-Kreis und Stadt Ludwigshafen",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103154000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Helmstedt",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "101062000": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Stormarn",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105374000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 2,
        "level": 3,
        "start": 1703833200000,
        "regionName": "Oberbergischer Kreis",
        "end": 1703916000000,
        "description": "Es tritt Dauerregen auf. Dabei werden Niederschlagsmengen bis 30 l/m² erwartet.",
        "event": "DAUERREGEN",
        "headline": "Amtliche WARNUNG vor DAUERREGEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Oberbergischer Kreis",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105566000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Steinfurt",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "114521000": [
      {
        "state": "Sachsen",
        "type": 1,
        "level": 3,
        "start": 1703759220000,
        "regionName": "Erzgebirgskreis",
        "end": 1703934000000,
        "description": "Es treten oberhalb 1000 m schwere Sturmböen mit Geschwindigkeiten zwischen 85 km/h (24 m/s, 47 kn, Bft 9) und 100 km/h (28 m/s, 55 kn, Bft 10) aus südwestlicher Richtung auf.",
        "event": "SCHWERE STURMBÖEN",
        "headline": "Amtliche WARNUNG vor SCHWEREN STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Vereinzelt können zum Beispiel Bäume entwurzelt und Dächer beschädigt werden. Achten Sie besonders auf herabstürzende Äste, Dachziegel oder Gegenstände.",
        "stateShort": "SN",
        "altitudeStart": 1000,
        "altitudeEnd": null
      },
      {
        "state": "Sachsen",
        "type": 1,
        "level": 3,
        "start": 1703856660000,
        "regionName": "Erzgebirgskreis",
        "end": 1703872800000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 60 km/h (17 m/s, 33 kn, Bft 7) und 70 km/h (20 m/s, 38 kn, Bft 8) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Sachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Erzgebirgskreis",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "107231000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Bernkastel-Wittlich",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703901600000,
        "regionName": "Kreis Bernkastel-Wittlich",
        "end": 1703912400000,
        "description": "Es treten oberhalb 600 m Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": 600,
        "altitudeEnd": null
      }
    ],
    "908315999": [
      {
        "state": "Baden-Württemberg",
        "type": 1,
        "level": 3,
        "start": 1703869200000,
        "regionName": "Kreis Breisgau-Hochschwarzwald und Stadt Freiburg",
        "end": 1703923200000,
        "description": "Es treten oberhalb 1000 m Sturmböen mit Geschwindigkeiten um 80km/h (22 m/s, 44 kn, Bft 9) aus südwestlicher Richtung auf. In exponierten Lagen muss mit schweren Sturmböen um 90 km/h (25 m/s, 48 kn, Bft 10) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BW",
        "altitudeStart": 1000,
        "altitudeEnd": null
      }
    ],
    "105758000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Herford",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "112066000": [
      {
        "state": "Brandenburg",
        "type": 1,
        "level": 2,
        "start": 1703890800000,
        "regionName": "Kreis Oberspreewald-Lausitz",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BB",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "114713000": [
      {
        "state": "Sachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Leipzig",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105112000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Duisburg",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "901054001": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 3,
        "start": 1703869200000,
        "regionName": "Kreis Nordfriesland - Binnenland",
        "end": 1703934000000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 55 km/h (15 m/s, 30 kn, Bft 7) und 75 km/h (21 m/s, 41 kn, Bft 9) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109472000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 3,
        "start": 1703763480000,
        "regionName": "Kreis und Stadt Bayreuth",
        "end": 1703934000000,
        "description": "Es treten oberhalb 1000 m Sturmböen mit Geschwindigkeiten um 70 km/h (20 m/s, 38 kn, Bft 8) aus südwestlicher Richtung auf. In exponierten Lagen muss mit Sturmböen bis 85 km/h (24 m/s, 47 kn, Bft 9) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BY",
        "altitudeStart": 1000,
        "altitudeEnd": null
      }
    ],
    "901054002": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 3,
        "start": 1703869200000,
        "regionName": "Kreis Nordfriesland - Küste",
        "end": 1703934000000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 55 km/h (15 m/s, 30 kn, Bft 7) und 75 km/h (21 m/s, 41 kn, Bft 9) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "106434000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Hochtaunuskreis",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703901600000,
        "regionName": "Hochtaunuskreis",
        "end": 1703912400000,
        "description": "Es treten oberhalb 600 m Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": 600,
        "altitudeEnd": null
      }
    ],
    "109173000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 3,
        "start": 1703836800000,
        "regionName": "Kreis Bad Tölz-Wolfratshausen",
        "end": 1703926800000,
        "description": "Es treten oberhalb 1500 m Sturmböen mit Geschwindigkeiten um 75 km/h (21 m/s, 41 kn, Bft 9) anfangs aus südwestlicher, später aus westlicher Richtung auf. In exponierten Lagen muss mit Sturmböen bis 85 km/h (24 m/s, 47 kn, Bft 9) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BY",
        "altitudeStart": 1500,
        "altitudeEnd": null
      }
    ],
    "107137000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Mayen-Koblenz",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703901600000,
        "regionName": "Kreis Mayen-Koblenz",
        "end": 1703912400000,
        "description": "Es treten oberhalb 600 m Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": 600,
        "altitudeEnd": null
      }
    ],
    "112052000": [
      {
        "state": "Brandenburg",
        "type": 1,
        "level": 2,
        "start": 1703890800000,
        "regionName": "Stadt Cottbus",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BB",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "101061000": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Steinburg",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103257000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Schaumburg",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105154000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Kleve",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "112051000": [
      {
        "state": "Brandenburg",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Brandenburg",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BB",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "908226999": [
      {
        "state": "Baden-Württemberg",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Rhein-Neckar-Kreis und Stadt Heidelberg",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105111000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Düsseldorf",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "108225000": [
      {
        "state": "Baden-Württemberg",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Neckar-Odenwald-Kreis",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109471000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Bamberg",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109172000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 3,
        "start": 1703836800000,
        "regionName": "Kreis Berchtesgadener Land",
        "end": 1703926800000,
        "description": "Es treten oberhalb 1500 m Sturmböen mit Geschwindigkeiten um 75 km/h (21 m/s, 41 kn, Bft 9) anfangs aus südwestlicher, später aus westlicher Richtung auf. In exponierten Lagen muss mit Sturmböen bis 85 km/h (24 m/s, 47 kn, Bft 9) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BY",
        "altitudeStart": 1500,
        "altitudeEnd": null
      }
    ],
    "116061000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Eichsfeld",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "108226000": [
      {
        "state": "Baden-Württemberg",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Rhein-Neckar-Kreis und Stadt Heidelberg",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103152000": [
      {
        "state": "Niedersachsen",
        "type": 2,
        "level": 3,
        "start": 1703848020000,
        "regionName": "Kreis Göttingen",
        "end": 1703923200000,
        "description": "Es tritt Dauerregen auf. Dabei werden Niederschlagsmengen bis 30 l/m² erwartet.",
        "event": "DAUERREGEN",
        "headline": "Amtliche WARNUNG vor DAUERREGEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Göttingen",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "101060000": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Segeberg",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "903462001": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Wittmund - Binnenland",
        "end": 1703934000000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "909571999": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Ansbach",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "903462002": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 3,
        "start": 1703869200000,
        "regionName": "Kreis Wittmund - Küste",
        "end": 1703934000000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 55 km/h (15 m/s, 30 kn, Bft 7) und 75 km/h (21 m/s, 41 kn, Bft 9) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "901055001": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Ostholstein - Binnenland",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "909187999": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 3,
        "start": 1703836800000,
        "regionName": "Kreis und Stadt Rosenheim",
        "end": 1703926800000,
        "description": "Es treten oberhalb 1500 m Sturmböen mit Geschwindigkeiten um 75 km/h (21 m/s, 41 kn, Bft 9) anfangs aus südwestlicher, später aus westlicher Richtung auf. In exponierten Lagen muss mit Sturmböen bis 85 km/h (24 m/s, 47 kn, Bft 9) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BY",
        "altitudeStart": 1500,
        "altitudeEnd": null
      }
    ],
    "901055002": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Ostholstein - Küste",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703890800000,
        "regionName": "Kreis Ostholstein - Küste",
        "end": 1703934000000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "909678999": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis und Stadt Schweinfurt",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "106433000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Groß-Gerau",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105515000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Münster",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109278000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 3,
        "start": 1703763480000,
        "regionName": "Kreis Straubing-Bogen und Stadt Straubing",
        "end": 1703934000000,
        "description": "Es treten oberhalb 1000 m Sturmböen mit Geschwindigkeiten um 70 km/h (20 m/s, 38 kn, Bft 8) aus südwestlicher Richtung auf. In exponierten Lagen muss mit Sturmböen bis 85 km/h (24 m/s, 47 kn, Bft 9) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BY",
        "altitudeStart": 1000,
        "altitudeEnd": null
      }
    ],
    "901056001": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Pinneberg (ohne Helgoland)",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105366000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Euskirchen",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703901600000,
        "regionName": "Kreis Euskirchen",
        "end": 1703912400000,
        "description": "Es treten oberhalb 600 m Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": 600,
        "altitudeEnd": null
      }
    ],
    "106412000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Frankfurt am Main",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "901056002": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 3,
        "start": 1703869200000,
        "regionName": "Insel Helgoland",
        "end": 1703934000000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 55 km/h (15 m/s, 30 kn, Bft 7) und 75 km/h (21 m/s, 41 kn, Bft 9) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105558000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Coesfeld",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103151000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Gifhorn",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "110046000": [
      {
        "state": "Saarland",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis St. Wendel",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SL",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Saarland",
        "type": 1,
        "level": 2,
        "start": 1703901600000,
        "regionName": "Kreis St. Wendel",
        "end": 1703912400000,
        "description": "Es treten oberhalb 600 m Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SL",
        "altitudeStart": 600,
        "altitudeEnd": null
      }
    ],
    "107140000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Rhein-Hunsrück-Kreis",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703901600000,
        "regionName": "Rhein-Hunsrück-Kreis",
        "end": 1703912400000,
        "description": "Es treten oberhalb 600 m Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": 600,
        "altitudeEnd": null
      }
    ],
    "203159000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Northeimer Seenplatte",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "107332000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Bad Dürkheim",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "110045000": [
      {
        "state": "Saarland",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Saarpfalz-Kreis",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SL",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "115082000": [
      {
        "state": "Sachsen-Anhalt",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Anhalt-Bitterfeld",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SA",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "901051001": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Dithmarschen - Binnenland",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "901051002": [
      {
        "state": "Schleswig-Holstein",
        "type": 1,
        "level": 3,
        "start": 1703869200000,
        "regionName": "Kreis Dithmarschen - Küste",
        "end": 1703934000000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 55 km/h (15 m/s, 30 kn, Bft 7) und 75 km/h (21 m/s, 41 kn, Bft 9) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "SH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "106437000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Odenwaldkreis",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105114000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Krefeld",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105711000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Bielefeld",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105370000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Heinsberg",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103254000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Hildesheim",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "116062000": [
      {
        "state": "Thüringen",
        "type": 2,
        "level": 3,
        "start": 1703844000000,
        "regionName": "Kreis Nordhausen",
        "end": 1703923200000,
        "description": "Es tritt Dauerregen auf. Dabei werden Niederschlagsmengen bis 30 l/m² erwartet.",
        "event": "DAUERREGEN",
        "headline": "Amtliche WARNUNG vor DAUERREGEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Nordhausen",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105562000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Recklinghausen",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "107331000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Alzey-Worms",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105754000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Gütersloh",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109575000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Neustadt a.d. Aisch-Bad Windsheim",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BY",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105966000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 2,
        "level": 3,
        "start": 1703833200000,
        "regionName": "Kreis Olpe",
        "end": 1703916000000,
        "description": "Es tritt Dauerregen auf. Dabei werden Niederschlagsmengen bis 30 l/m² erwartet.",
        "event": "DAUERREGEN",
        "headline": "Amtliche WARNUNG vor DAUERREGEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Olpe",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "914524002": [
      {
        "state": "Sachsen",
        "type": 1,
        "level": 3,
        "start": 1703856660000,
        "regionName": "Kreis Zwickau - Bergland",
        "end": 1703872800000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 60 km/h (17 m/s, 33 kn, Bft 7) und 70 km/h (20 m/s, 38 kn, Bft 8) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Sachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Zwickau - Bergland",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "106435000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Main-Kinzig-Kreis",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "906432999": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Darmstadt-Dieburg und Stadt Darmstadt",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103405000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Wilhelmshaven",
        "end": 1703934000000,
        "description": "Es treten Windböen mit Geschwindigkeiten um 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe sowie in exponierten Lagen muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "109276000": [
      {
        "state": "Bayern",
        "type": 1,
        "level": 3,
        "start": 1703763480000,
        "regionName": "Kreis Regen",
        "end": 1703934000000,
        "description": "Es treten oberhalb 1000 m Sturmböen mit Geschwindigkeiten um 70 km/h (20 m/s, 38 kn, Bft 8) aus südwestlicher Richtung auf. In exponierten Lagen muss mit Sturmböen bis 85 km/h (24 m/s, 47 kn, Bft 9) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BY",
        "altitudeStart": 1000,
        "altitudeEnd": null
      }
    ],
    "914524001": [
      {
        "state": "Sachsen",
        "type": 1,
        "level": 3,
        "start": 1703856660000,
        "regionName": "Kreis Zwickau - Tiefland",
        "end": 1703872800000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 60 km/h (17 m/s, 33 kn, Bft 7) und 70 km/h (20 m/s, 38 kn, Bft 8) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Sachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Zwickau - Tiefland",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103256000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Nienburg (Weser)",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "116064000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Unstrut-Hainich-Kreis",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105113000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Essen",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "107333000": [
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Donnersbergkreis",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Rheinland-Pfalz",
        "type": 1,
        "level": 2,
        "start": 1703901600000,
        "regionName": "Donnersbergkreis",
        "end": 1703912400000,
        "description": "Es treten oberhalb 600 m Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "RP",
        "altitudeStart": 600,
        "altitudeEnd": null
      }
    ],
    "913072001": [
      {
        "state": "Mecklenburg-Vorpommern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Rostock - Binnenland Nord",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "MV",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "913072002": [
      {
        "state": "Mecklenburg-Vorpommern",
        "type": 1,
        "level": 3,
        "start": 1703869200000,
        "regionName": "Kreis Rostock - Küste",
        "end": 1703890800000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 55 km/h (15 m/s, 30 kn, Bft 7) und 65 km/h (18 m/s, 35 kn, Bft 8) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "MV",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Mecklenburg-Vorpommern",
        "type": 1,
        "level": 2,
        "start": 1703890800000,
        "regionName": "Kreis Rostock - Küste",
        "end": 1703934000000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "MV",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "112072000": [
      {
        "state": "Brandenburg",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Teltow-Fläming",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BB",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "110044000": [
      {
        "state": "Saarland",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Saarlouis",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SL",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "913072003": [
      {
        "state": "Mecklenburg-Vorpommern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Rostock - Binnenland Süd",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "MV",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "116063000": [
      {
        "state": "Thüringen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Wartburgkreis",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "TH",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "115081000": [
      {
        "state": "Sachsen-Anhalt",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Altmarkkreis Salzwedel",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SA",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "114612000": [
      {
        "state": "Sachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Stadt Dresden",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "913071001": [
      {
        "state": "Mecklenburg-Vorpommern",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Mecklenburgische Seenplatte - Nord",
        "end": 1703890800000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "MV",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "108336000": [
      {
        "state": "Baden-Württemberg",
        "type": 1,
        "level": 3,
        "start": 1703869200000,
        "regionName": "Kreis Lörrach",
        "end": 1703923200000,
        "description": "Es treten oberhalb 1000 m Sturmböen mit Geschwindigkeiten um 80km/h (22 m/s, 44 kn, Bft 9) aus südwestlicher Richtung auf. In exponierten Lagen muss mit schweren Sturmböen um 90 km/h (25 m/s, 48 kn, Bft 10) gerechnet werden.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "BW",
        "altitudeStart": 1000,
        "altitudeEnd": null
      }
    ],
    "112071000": [
      {
        "state": "Brandenburg",
        "type": 1,
        "level": 2,
        "start": 1703890800000,
        "regionName": "Kreis Spree-Neiße",
        "end": 1703923200000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "BB",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "110043000": [
      {
        "state": "Saarland",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Neunkirchen",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SL",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "106436000": [
      {
        "state": "Hessen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Main-Taunus-Kreis",
        "end": 1703901600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) aus südwestlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "HE",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "914523002": [
      {
        "state": "Sachsen",
        "type": 1,
        "level": 3,
        "start": 1703856660000,
        "regionName": "Vogtlandkreis - Bergland",
        "end": 1703872800000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 60 km/h (17 m/s, 33 kn, Bft 7) und 70 km/h (20 m/s, 38 kn, Bft 8) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Sachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Vogtlandkreis - Bergland",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "914523001": [
      {
        "state": "Sachsen",
        "type": 1,
        "level": 3,
        "start": 1703856660000,
        "regionName": "Vogtlandkreis - Tiefland",
        "end": 1703872800000,
        "description": "Es treten Sturmböen mit Geschwindigkeiten zwischen 60 km/h (17 m/s, 33 kn, Bft 7) und 70 km/h (20 m/s, 38 kn, Bft 8) aus südwestlicher Richtung auf.",
        "event": "STURMBÖEN",
        "headline": "Amtliche WARNUNG vor STURMBÖEN",
        "instruction": "ACHTUNG! Hinweis auf mögliche Gefahren: Es können zum Beispiel einzelne Äste herabstürzen. Achten Sie besonders auf herabfallende Gegenstände.",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      },
      {
        "state": "Sachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Vogtlandkreis - Tiefland",
        "end": 1703937600000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "SN",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "105774000": [
      {
        "state": "Nordrhein-Westfalen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Paderborn",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NRW",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ],
    "103255000": [
      {
        "state": "Niedersachsen",
        "type": 1,
        "level": 2,
        "start": 1703869200000,
        "regionName": "Kreis Holzminden",
        "end": 1703912400000,
        "description": "Es treten Windböen mit Geschwindigkeiten bis 60 km/h (17 m/s, 33 kn, Bft 7) anfangs aus südwestlicher, später aus westlicher Richtung auf. In Schauernähe muss mit Sturmböen um 70 km/h (20 m/s, 38 kn, Bft 8) gerechnet werden.",
        "event": "WINDBÖEN",
        "headline": "Amtliche WARNUNG vor WINDBÖEN",
        "instruction": "",
        "stateShort": "NS",
        "altitudeStart": null,
        "altitudeEnd": null
      }
    ]
  }
"""

# Local Variables: #
# python-indent: 4 #
# End: #
