#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2024-02-07 15:50:37 krylon>
#
# /data/code/python/wetterfrosch/data.py
# created on 12. 01. 2024
# (c) 2024 Benjamin Walkenhorst
#
# This file is part of the Wetterfrosch weather app. It is distributed under the
# terms of the GNU General Public License 3. See the file LICENSE for details
# or find a copy online at https://www.gnu.org/licenses/gpl-3.0

"""
wetterfrosch.data

(c) 2024 Benjamin Walkenhorst
"""

# import hashlib
from datetime import datetime, timedelta
from typing import Any, Final, Optional


# pylint: disable-msg=R0902,R0903
class WeatherWarning:
    """Represents a warning issued by the DWD about severe
    weather conditions."""

    __slots__ = [
        "wid",
        "state",
        "wtype",
        "level",
        "start",
        "end",
        "region_name",
        "description",
        "event",
        "headline",
        "instruction",
        "state_short",
        "altitude_start",
        "altitude_end",
        "acknowledged",
    ]

    wid: int
    state: str
    wtype: int
    level: int
    start: datetime
    end: datetime
    region_name: str
    description: str
    event: str
    headline: str
    instruction: str
    state_short: str
    altitude_start: Optional[int]
    altitude_end: Optional[int]
    acknowledged: bool

    def __init__(self, record: dict, wid: int = 0) -> None:
        self.wid = wid
        self.state = record["state"]
        self.wtype = record["type"]
        self.level = record["level"]
        self.start = datetime.fromtimestamp(record["start"]/1000)
        if ("end" in record) and record["end"] is not None:
            self.end = datetime.fromtimestamp(record["end"]/1000)
        else:
            self.end = self.start
        if self.start == self.end:
            self.end += timedelta(hours=12)
        self.region_name = record["regionName"]
        self.description = record["description"]
        self.event = record["event"]
        self.headline = record["headline"]
        self.instruction = record["instruction"]
        self.state_short = record["stateShort"]
        self.altitude_end = record["altitudeEnd"]
        self.altitude_start = record["altitudeStart"]
        if "acknowledged" in record:
            self.acknowledged = record["acknowledged"]
        else:
            self.acknowledged = False

    def cksum(self) -> str:
        """Produce a checksum to see if two Warnings are identical."""
        summary: Final[str] = \
            f"{self.start}--{self.end}--{self.region_name}--{self.event}--" + \
            f"{self.description}--{self.level}"

        # cksum: Final[str] = hashlib.sha512(summary.encode()).hexdigest()
        # return cksum
        return summary


humid_table: Final[dict[int, int]] = {
    16: 99,
    17: 93,
    18: 88,
    19: 83,
    20: 78,
    21: 74,
    22: 70,
    23: 66,
    24: 62,
    25: 59,
    26: 56,
    27: 53,
    28: 50,
    29: 47,
    30: 43,
    31: 43,
    32: 40,
    33: 38,
    34: 36,
    35: 35,
    36: 33,
    37: 31,
}


class Forecast:
    """Current weather data / forecast as obtained by Pirate Weather"""

    __slots__ = [
        "fid",
        "timestamp",
        "location",
        "summary",
        "icon",
        "probability_rain",
        "temperature",
        "temperature_apparent",
        "humidity",
        "wind_speed",
        "visibility",
    ]

    fid: int
    timestamp: datetime
    location: tuple[float, float]
    summary: str
    icon: str
    probability_rain: int
    temperature: int
    temperature_apparent: float
    humidity: int
    wind_speed: int
    visibility: float

    def __init__(self, forecast: dict, fid: int = 0) -> None:
        assert fid >= 0
        self.fid = fid
        self.timestamp = datetime.fromtimestamp(forecast["currently"]["time"])
        self.location = (forecast["latitude"], forecast["longitude"])
        self.summary = forecast["currently"]["summary"]
        self.icon = forecast["currently"]["icon"]
        self.probability_rain = \
            int(forecast["currently"]["precipProbability"] * 100)
        self.temperature = int(forecast["currently"]["temperature"])
        self.temperature_apparent = \
            int(forecast["currently"]["apparentTemperature"])
        self.humidity = int(forecast["currently"]["humidity"] * 100)
        self.wind_speed = \
            int(forecast["currently"]["windSpeed"])
        self.visibility = forecast["currently"]["visibility"]

    @classmethod
    def from_db(cls, row: tuple) -> Any:
        """Construct a Forecast instance from the database row."""
        loc = [float(x) for x in row[2].split("/")]
        fc = cls.__new__(cls)
        fc.fid = row[0]
        fc.timestamp = datetime.fromtimestamp(row[1])
        fc.location = (loc[0], loc[1])
        fc.summary = row[3]
        fc.icon = row[4]
        fc.probability_rain = row[5]
        fc.temperature = row[6]
        fc.temperature_apparent = row[7]
        fc.humidity = row[8]
        fc.wind_speed = row[9]
        fc.visibility = row[10]
        return fc

    def is_humid(self) -> bool:
        """Return True if it's humid by central European standards."""
        humid: bool = False
        match self.temperature:
            case x if x < 16:
                humid = False
            case x if x in humid_table:
                humid = self.humidity >= humid_table[x]
            case _:
                humid = False
        return humid

    def icon_name(self) -> str:
        """Attempt to guess the name of the appropriate icon to display for
        the weather forecast."""
        return f"weather-{self.icon}-symbolic"

# local Variables: #
# python-indent: 4 #
# End: #
