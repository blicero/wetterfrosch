#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2024-01-17 11:35:27 krylon>
#
# /data/code/python/wetterfrosch/dwd.py
# created on 28. 12. 2023
# (c) 2023 Benjamin Walkenhorst
#
# This file is part of the Vox audiobook reader. It is distributed under the
# terms of the GNU General Public License 3. See the file LICENSE for details
# or find a copy online at https://www.gnu.org/licenses/gpl-3.0

"""
wetterfrosch.client

(c) 2023 Benjamin Walkenhorst
"""


import json
import logging
import re
import urllib.request
from datetime import datetime, timedelta
from threading import Lock
from typing import Any, Final, Optional, Union
from warnings import warn

from wetterfrosch import common, data

WARNINGS_URL: Final[str] = \
    "https://www.dwd.de/DWD/warnungen/warnapp/json/warnings.json"

ENVELOPE_PAT: Final[re.Pattern] = \
    re.compile(r"^warnWetter[.]loadWarnings\((.*)\);", re.DOTALL)


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
                self.patterns.append(item)

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


class Client:
    """Client fetches weather warnings from the DWD web site."""

    __slots__ = [
        "last_fetch",
        "interval",
        "loc_patterns",
        "log",
    ]

    log: logging.Logger
    last_fetch: datetime
    loc_patterns: LocationList
    interval: timedelta

    _loc: list[str] = []

    def __init__(self, interval: int = 30, patterns: Optional[list[str]] = None) -> None:  # noqa: E501 pylint: disable-msg=C0301
        self.log = common.get_logger("client")
        self.interval = timedelta(seconds=interval)
        if patterns is not None:
            self.loc_patterns = LocationList.new(*patterns)
        else:
            self.loc_patterns = LocationList.new()
        self.last_fetch = datetime.fromtimestamp(0)

    def fetch(self) -> Optional[dict]:
        """Fetch the current list of warnings from DWD."""
        next_fetch = self.last_fetch + self.interval
        if next_fetch > datetime.now():
            self.log.info("Last fetch was %s, next fetch is not due until %s",
                          self.last_fetch.strftime(common.TIME_FMT),
                          next_fetch.strftime(common.TIME_FMT))
            return None
        with urllib.request.urlopen(WARNINGS_URL) as res:
            if res.status != 200:
                self.log.error("Failed to fetch data from DWD: %d", res.status)
                return None
            self.last_fetch = datetime.now()
            body: Final[str] = res.read().decode()
            m: Final[Optional[re.Match[str]]] = \
                ENVELOPE_PAT.match(body)  # pylint: disable-msg=C0103
            assert m is not None  # SRSLY?
            payload: Final[str] = m[1]
            records: dict = json.loads(payload)
            return records

    def process(self, items: dict) -> Optional[list[data.WeatherWarning]]:
        """Process the data we received from the DWD web site."""
        warnings: list[data.WeatherWarning] = []
        for w in items["warnings"].values():  # pylint: disable-msg=C0103
            for event in w:
                if self.loc_patterns.check(event["regionName"]):
                    warning = data.WeatherWarning(event)
                    warnings.append(warning)
                    break
        return warnings


# Local Variables: #
# python-indent: 4 #
# End: #
