#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2024-02-19 18:12:43 krylon>
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
import sys
import time
from datetime import datetime, timedelta
from threading import Lock, Thread, local
from typing import Any, Final, Optional, Union
from warnings import warn

import krylib
import requests  # type: ignore

from wetterfrosch import common, data, database
from wetterfrosch.data import Forecast

IPINFO_URL: Final[str] = "https://ipinfo.io/json"

WARNINGS_URL: Final[str] = \
    "https://www.dwd.de/DWD/warnungen/warnapp/json/warnings.json"

ENVELOPE_PAT: Final[re.Pattern] = \
    re.compile(r"^warnWetter[.]loadWarnings\((.*)\);", re.DOTALL)

PIRATE_URL: Final[str] = \
    "https://api.pirateweather.net/forecast" + \
    "/bqiCjEJd20p0mCOJhCDC6Cs1AoCHOhzg" + \
    "/52.001259788359754,8.538241122650915" + \
    "?units=si"


def pirate_url(coords: tuple[float, float]) -> str:
    """Generate the URL for the Pirate Weather API"""
    addr: Final[str] = "https://api.pirateweather.net/forecast" + \
        "/bqiCjEJd20p0mCOJhCDC6Cs1AoCHOhzg" + \
        f"/{coords[0]},{coords[1]}" + \
        "?units=si"
    return addr


class LocationList:
    """A (singleton) list of regular expressions describing locations."""

    __slots__ = ["patterns", "lock", "dupes"]

    clock = Lock()
    _instance = None
    patterns: list[re.Pattern]
    lock: Lock
    dupes: set[str]

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
                    cls._instance.dupes = set()
                    for i in patterns:
                        if isinstance(i, str):
                            if i not in cls._instance.dupes:
                                cls._instance.patterns.append(
                                    re.compile(i, re.I))
                                cls._instance.dupes.add(i)
                        elif isinstance(i, re.Pattern):
                            if i.pattern not in cls._instance.dupes:
                                cls._instance.dupes.add(i.pattern)
                                cls._instance.patterns.append(i)
                        else:
                            raise TypeError(
                                f"Patterns must be str or re.Pattern, not {type(i)}")  # noqa: E501
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
            self.dupes.clear()
            self.patterns = []

    def add(self, item: Union[str, re.Pattern]) -> None:
        """Add a new pattern. If <item> is a string, it is compiled to
        a re.Pattern"""
        with self.lock:
            if isinstance(item, str):
                if item not in self.dupes:
                    pat = re.compile(item, re.I)
                    self.patterns.append(pat)
                    self.dupes.add(item)
            else:
                assert isinstance(item, re.Pattern)
                if item.pattern not in self.dupes:
                    self.patterns.append(item)
                    self.dupes.add(item.pattern)

    def replace(self, items: list[str]) -> None:
        """Replace the patterns in the LocationList.
        Assumes that all strings in items are valid regular expressions."""
        with self.lock:
            self.patterns = [re.compile(p, re.I) for p in items]
            self.dupes = set(items)

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
        "local",
        "last_wfetch",
        "winterval",
        "loc_patterns",
        "here",
        "coords",
        "log",
        "lock",
        "active",
        "wcache",
        "known",
        "last_ffetch",
        "finterval",
        "fcache",
        "pirate_url",
    ]

    local: local
    log: logging.Logger
    last_wfetch: datetime
    loc_patterns: LocationList
    here: str
    coords: tuple[float, float]
    lock: Lock
    active: bool
    winterval: timedelta
    last_ffetch: datetime
    finterval: timedelta
    wcache: Optional[list[data.WeatherWarning]]
    known: set[str]
    fcache: Optional[Forecast]
    pirate_url: str

    _loc: list[str] = []

    def __init__(self, interval: int = 30, patterns: Optional[list[str]] = None) -> None:  # noqa: E501 pylint: disable-msg=C0301
        self.local = local()
        self.log = common.get_logger("client")
        self.lock = Lock()
        self.active = False
        self.winterval = timedelta(seconds=interval)
        self.finterval = timedelta(seconds=600)
        if patterns is not None:
            self.loc_patterns = LocationList.new(*patterns)
        else:
            loc = self.get_location()
            here: Final[str] = loc[0]
            locations: list[str] = [here]
            if krylib.fexist(common.path.locations()):
                with open(common.path.locations(), "r", encoding="utf-8") as fh:  # noqa: E501
                    patterns = [x.strip() for x in fh.readlines()]
                    locations += patterns
            self.loc_patterns = LocationList.new(*locations)
        self.pirate_url = pirate_url(self.coords)
        self.last_wfetch = datetime.fromtimestamp(0)
        self.last_ffetch = datetime.fromtimestamp(0)
        self.wcache = None
        self.known = self.get_database().warning_get_keys()
        self.fcache = None

    def get_database(self) -> database.Database:
        """Get the Database instance for the calling thread."""
        try:
            return self.local.db
        except AttributeError:
            db = database.Database()  # pylint: disable-msg=C0103
            self.local.db = db
            return db

    def get_location(self) -> tuple[str, tuple[float, float]]:
        """Try to determine our location (city) using ipinfo.io"""
        try:
            res = requests.get(IPINFO_URL, verify=True, timeout=5)
            if res.status_code != 200:
                return ("", (0.0, 0.0))
            body = res.json()
            coords = [float(x) for x in body["loc"].split(",")]
            self.coords = (coords[0], coords[1])
            self.here = body["city"]
            return (body["city"], self.coords)
        except Exception as e:  # pylint: disable-msg=W0718,C0103
            self.log.error("Failed to get location: %s", e)
            return ("", (0.0, 0.0))

    def is_active(self) -> bool:
        """Return the Client's active flag, i.e. if the workers are running."""
        with self.lock:
            return self.active

    def stop(self) -> None:
        """Clear the Client's active flag, causing its associated
        workers to exit."""
        with self.lock:
            self.active = False

    def start(self) -> None:
        """Start the worker threads to fetch weather forecasts and warnings."""
        with self.lock:
            if self.active:
                self.log.info("Client is already running, we're good.")
                return
            self.active = True
            warn_worker = Thread(
                target=self._warning_refresh_worker,
                daemon=True,
            )
            forecast_worker = Thread(
                target=self._forecast_refresh_worker,
                daemon=True,
            )

            warn_worker.start()
            forecast_worker.start()

    def _warning_refresh_worker(self) -> None:
        """Regularly fetch warnings from the DWD"""
        while self.is_active():
            try:
                self.fetch_warnings()
            except:  # noqa: E722,B001  pylint: disable-msg=W0702
                self.log.error(
                    "Failed to load warnings: %s",
                    sys.exception())
            finally:
                time.sleep(self.winterval.seconds)

    def _forecast_refresh_worker(self) -> None:
        while self.is_active():
            try:
                self.fetch_forecast()
            except:  # noqa: E722,B001  pylint: disable-msg=W0702
                self.log.error("Failed to load forecast data: %s",
                               sys.exception())
            finally:
                time.sleep(self.finterval.seconds)

    # pylint: disable-msg=R0911
    def fetch_warnings(self, attempt: int = 5) -> Optional[list[data.WeatherWarning]]:  # noqa: E501
        """Fetch the current list of warnings from DWD."""
        next_fetch = self.last_wfetch + self.winterval
        if next_fetch > datetime.now() and self.fcache is not None:
            self.log.info("Last fetch was %s, next fetch is not due until %s",
                          self.last_wfetch.strftime(common.TIME_FMT),
                          next_fetch.strftime(common.TIME_FMT))
            return self.wcache

        try:
            res = requests.get(WARNINGS_URL, verify=True, timeout=5)
            match res.status_code:
                case 200:
                    pass
                case 403:
                    if attempt > 0:
                        time.sleep(1)
                        return self.fetch_warnings(attempt - 1)
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
            with open(common.path.warning(), 'w', encoding='utf-8') as fh:
                fh.write(payload)
            records: dict = json.loads(payload)
            processed: list[data.WeatherWarning] = []
            self.last_wfetch = datetime.now()
            db = self.get_database()
            with db:
                for block in records["warnings"].values():
                    for item in block:
                        w = data.WeatherWarning(item)
                        if self.loc_patterns.check(w.region_name):
                            processed.append(w)
                        if not w.cksum() in self.known:
                            if not db.warning_exist(w):
                                db.warning_add(w)
                            self.known.add(w.cksum())

            with self.lock:
                self.wcache = processed
            return processed
        except Exception as e:  # pylint: disable-msg=W0718
            self.log.error("Failed to fetch weather warnings: %s",
                           pprint.pformat(e.args))
            return None

    def fetch_forecast(self) -> Optional[Forecast]:
        """Fetch weather data from Pirate Weather"""
        next_fetch: Final[datetime] = self.last_ffetch + self.finterval
        if next_fetch > datetime.now():
            self.log.info("Last fetch was %s, next fetch is not due until %s",
                          self.last_ffetch.strftime(common.TIME_FMT),
                          next_fetch.strftime(common.TIME_FMT))
            return self.fcache
        try:
            res = requests.get(self.pirate_url, verify=True, timeout=5)
            match res.status_code:
                case 200:
                    pass
                case code:
                    self.log.error("Failed to fetch forecast: %d", code)
                    return None

            body: Final[str] = res.content.decode()
            with open(common.path.forecast(), 'w', encoding='utf-8') as fh:
                fh.write(body)
            records: dict[str, Any] = json.loads(body)
            self.last_ffetch = datetime.now()
            fc: Forecast = Forecast(records)
            with self.lock:
                self.fcache = fc
            db = self.get_database()
            with db:
                db.forecast_add(fc)
                db.hourly_add(fc)
            return fc
        except Exception as e:  # pylint: disable-msg=W0718
            self.log.error("Failed to fetch weather forecast: %s",
                           pprint.pformat(e.args))
            return None

    def get_warnings_cached(self) -> Optional[list[data.WeatherWarning]]:
        """Return the cached warnings, if there are any."""
        with self.lock:
            return self.wcache

    def get_forecast_cached(self) -> Optional[Forecast]:
        """Return the cached Forecast, if there is one."""
        with self.lock:
            return self.fcache


# Local Variables: #
# python-indent: 4 #
# End: #
