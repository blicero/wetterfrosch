#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2024-02-06 20:05:38 krylon>
#
# /data/code/python/wetterfrosch/dwd.py
# created on 28. 12. 2023
# (c) 2023 Benjamin Walkenhorst
#
# This file is part of the Wetterfrosch weather app. It is distributed under the
# terms of the GNU General Public License 3. See the file LICENSE for details
# or find a copy online at https://www.gnu.org/licenses/gpl-3.0

"""
wetterfrosch.client

(c) 2023 Benjamin Walkenhorst
"""


import json
import logging
import pprint
import re
import time
from datetime import datetime, timedelta
from threading import Lock
from typing import Any, Final, Optional, Union
from warnings import warn

import requests  # type: ignore

from wetterfrosch import common, data, database
from wetterfrosch.data import Forecast

WARNINGS_URL: Final[str] = \
    "https://www.dwd.de/DWD/warnungen/warnapp/json/warnings.json"

ENVELOPE_PAT: Final[re.Pattern] = \
    re.compile(r"^warnWetter[.]loadWarnings\((.*)\);", re.DOTALL)

PIRATE_URL: Final[str] = \
    "https://api.pirateweather.net/forecast" + \
    "/bqiCjEJd20p0mCOJhCDC6Cs1AoCHOhzg" + \
    "/52.0333,8.5333" + \
    "?units=si"


class LocationList:
    """A (singleton) list of regular expressions describing locations."""

    __slots__ = ["patterns", "lock"]

    clock = Lock()
    _instance = None
    patterns: list[re.Pattern]
    lock: Lock

    def __init__(self):
        raise RuntimeError("Call LocationList.new() instead.")

    @classmethod
    def new(cls, *patterns: Union[str, re.Pattern]) -> Any:
        """Return the singleton instance.
        If it has not been created yet, create it and return it."""
        with cls.clock:
            if cls._instance is None:
                print("Creating singleton instance.")
                try:
                    cls._instance = cls.__new__(cls)
                    cls._instance.patterns = []
                    cls._instance.lock = Lock()
                    for i in patterns:
                        if isinstance(i, str):
                            cls._instance.patterns.append(re.compile(i, re.I))
                        elif isinstance(i, re.Pattern):
                            cls._instance.patterns.append(i)
                        else:
                            raise TypeError(
                                "Patterns must be str or re.Pattern")
                except Exception as e:  # pylint: disable-msg=C0103
                    print("Error creating LocationList singleton instance:", e)
                    raise
            if len(patterns) > 0:
                warn(
                    "Singleton instance already exists, ignoring new patterns")
            return cls._instance

    def cnt(self) -> int:
        """Return the number of patterns in the list"""
        with self.lock:
            return len(self.patterns)

    def clear(self) -> None:
        """Empty the current list of patterns"""
        with self.lock:
            self.patterns = []

    def add(self, item: Union[str, re.Pattern]) -> None:
        """Add a new pattern. If <item> is a string, it is compiled to
        a re.Pattern"""
        with self.lock:
            if isinstance(item, str):
                pat = re.compile(item, re.I)
                self.patterns.append(pat)
            else:
                assert isinstance(item, re.Pattern)
                self.patterns.append(item)

    def replace(self, items: list[str]) -> None:
        """Replace the patterns in the LocationList.
        Assumes that all strings in items are valid regular expressions."""
        with self.lock:
            self.patterns = [re.compile(p, re.I) for p in items]

    def check(self, loc: str) -> bool:
        """Check if the given string is matched by any of the List's
        regular expressions."""
        with self.lock:
            if len(self.patterns) == 0:
                return True
            for p in self.patterns:  # pylint: disable-msg=C0103
                if p.search(loc) is not None:
                    return True
            return False


# pylint: disable-msg=R0902
class Client:
    """Client fetches weather warnings from the DWD web site."""

    __slots__ = [
        "last_wfetch",
        "winterval",
        "loc_patterns",
        "log",
        "db",
        "cache",
        "known",
        "last_ffetch",
        "finterval",
        "fcache",
    ]

    log: logging.Logger
    last_wfetch: datetime
    loc_patterns: LocationList
    winterval: timedelta
    last_ffetch: datetime
    finterval: timedelta
    db: database.Database
    cache: Optional[list[data.WeatherWarning]]
    known: set[str]
    fcache: Optional[Forecast]

    _loc: list[str] = []

    def __init__(self, interval: int = 30, patterns: Optional[list[str]] = None) -> None:  # noqa: E501 pylint: disable-msg=C0301
        self.log = common.get_logger("client")
        self.winterval = timedelta(seconds=interval)
        self.finterval = timedelta(seconds=600)
        if patterns is not None:
            self.loc_patterns = LocationList.new(*patterns)
        else:
            self.loc_patterns = LocationList.new()
        self.db = database.Database()
        self.last_wfetch = datetime.fromtimestamp(0)
        self.last_ffetch = datetime.fromtimestamp(0)
        self.cache = None
        self.known = self.db.warning_get_keys()
        self.fcache = None

    # pylint: disable-msg=R0911
    def fetch(self, attempt: int = 5) -> Optional[list[data.WeatherWarning]]:
        """Fetch the current list of warnings from DWD."""
        next_fetch = self.last_wfetch + self.winterval
        if next_fetch > datetime.now() and self.fcache is not None:
            self.log.info("Last fetch was %s, next fetch is not due until %s",
                          self.last_wfetch.strftime(common.TIME_FMT),
                          next_fetch.strftime(common.TIME_FMT))
            return self.cache

        try:
            res = requests.get(WARNINGS_URL, verify=True, timeout=5)
            match res.status_code:
                case 200:
                    pass
                case 403:
                    if attempt > 0:
                        time.sleep(1)
                        return self.fetch(attempt - 1)
                    return None
                case _:
                    self.log.error("Failed to fetch warnings: %d",
                                   res.status_code)
                    return None

            body: Final[str] = res.content.decode()
            m: Final[Optional[re.Match[str]]] = \
                ENVELOPE_PAT.match(body)  # pylint: disable-msg=C0103

            if m is None:
                self.log.debug("Cannot parse response:\n%s",
                               body)
                return None

            payload: Final[str] = m[1]
            records: dict = json.loads(payload)
            processed: list[data.WeatherWarning] = []
            self.last_wfetch = datetime.now()
            with self.db:
                for block in records["warnings"].values():
                    for item in block:
                        w = data.WeatherWarning(item)
                        if self.loc_patterns.check(w.region_name):
                            processed.append(w)
                        if not w.cksum() in self.known:
                            if not self.db.warning_has_key(w.cksum()):
                                self.db.warning_add(w)
                            self.known.add(w.cksum())

            self.cache = processed
            return processed
        except Exception as e:  # pylint: disable-msg=W0718
            self.log.error("Failed to fetch weather warnings: %s",
                           pprint.pformat(e.args))
            return None

    def update_locations(self, locations: list[str]) -> None:
        """Replace the list of locations with the given list."""
        # self.loc_patterns.replace(locations)
        self.loc_patterns.clear()
        for pat in locations:
            self.loc_patterns.add(pat)

    def fetch_weather(self) -> Optional[Forecast]:
        """Fetch weather data from Pirate Weather"""
        next_fetch: Final[datetime] = self.last_ffetch + self.finterval
        if next_fetch > datetime.now():
            self.log.info("Last fetch was %s, next fetch is not due until %s",
                          self.last_ffetch.strftime(common.TIME_FMT),
                          next_fetch.strftime(common.TIME_FMT))
            return self.fcache
        try:
            res = requests.get(PIRATE_URL, verify=True, timeout=5)
            match res.status_code:
                case 200:
                    pass
                case code:
                    self.log.error("Failed to fetch forecast: %d", code)
                    return None

            body: Final[str] = res.content.decode()
            records: dict[str, Any] = json.loads(body)
            self.last_ffetch = datetime.now()
            fc: Forecast = Forecast(records)
            self.fcache = fc
            with self.db:
                self.db.forecast_add(fc)
            return fc
        except Exception as e:  # pylint: disable-msg=W0718
            self.log.error("Failed to fetch weather forecast: %s",
                           pprint.pformat(e.args))
            return None

    # def process(self, items: dict) -> Optional[list[data.WeatherWarning]]:
    #     """Process the data we received from the DWD web site."""
    #     warnings: list[data.WeatherWarning] = []
    #     for w in items["warnings"].values():  # pylint: disable-msg=C0103
    #         for event in w:
    #             if self.loc_patterns.check(event["regionName"]):
    #                 warning = data.WeatherWarning(event)
    #                 warnings.append(warning)
    #                 break
    #     return warnings


# Local Variables: #
# python-indent: 4 #
# End: #
