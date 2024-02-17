#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2024-02-17 16:37:08 krylon>
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


# Freitag, 16. 02. 2024, 20:15
# According to Wikipedia, the typical person from central Europe (where I was
# born and live to this day) perceives the weather as humid when the water vapor
# in the air is at least 13.5 gram of water per cubic meter of air.
# The amount of water vapor that air can hold is a function of temperature.
# The humidity is often given as relative humidity, i.e. at 50% humidity, the
# air contains half the water vapor it can hold. But 50% humidity at 20 °C is a
# different amount of water than 50% at 35 °C.
# Wikipedia kindly provides a table that lists the relative humidity for a
# given temperature at which people in central Europe will feel the humidity.
# The minimum temperature required for this is 16 °C, where it's 99%, and
# as the temperature rises, the relative humidity goes down.
# At 37 °C, it's only 31%.
# The table on Wikipedia only goes to 37 °C, but it very rarely gets that
# warm anyway. (At least for now, climate change might affect that in the future.)
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


class Datapoint:
    """A Datapoint is part of a weather forecast and includes conditions
    predicted for some point in the future."""

    # rain_amt is millimeters of rain per square meter per hour

    __slots__ = [
        'pid',
        'timestamp',
        'icon',
        'probability_rain',
        'rain_amt',
        'temperature',
        'humidity',
        'pressure',
        'wind_speed',
        'cloud_cover',
        'visibility',
    ]

    pid: int
    timestamp: datetime
    icon: str
    probability_rain: int
    rain_amt: float
    temperature: int
    humidity: int
    pressure: float
    wind_speed: int
    cloud_cover: int
    visibility: float

    def __init__(self, wdata: dict, pid: int = 0) -> None:
        self.pid = pid
        self.timestamp = datetime.fromtimestamp(wdata['time'])
        self.icon = wdata['icon']
        self.probability_rain = int(wdata['precipProbability'] * 100)
        self.rain_amt = wdata['precipIntensity']
        self.temperature = int(wdata['temperature'])
        self.humidity = int(wdata['humidity'] * 100)
        self.pressure = wdata['pressure']
        self.wind_speed = int(wdata['windSpeed'])
        self.cloud_cover = int(wdata['cloudCover'] * 100)
        self.visibility = wdata['visibility']

    @classmethod
    def from_db(cls, row: tuple) -> Any:
        """Create a Datapoint from a database record."""
        dp = cls.__new__(cls)
        dp.pid = row[0]
        dp.timestamp = datetime.fromtimestamp(row[1])
        dp.icon = row[2]
        dp.probability_rain = row[3]
        dp.rain_amt = row[4]
        dp.temperature = row[5]
        dp.humidity = row[6]
        dp.pressure = row[7]
        dp.wind_speed = row[8]
        dp.cloud_cover = row[9]
        dp.visibility = row[10]

        return dp

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
        "hourly",
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
    hourly: list[Datapoint]

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
        self.hourly = []
        for r in forecast['hourly']['data']:
            p = Datapoint(r)
            self.hourly.append(p)

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

    def hourly_db(self) -> list[tuple]:
        """Return a list of tuples, one for each Datapoint of forecast,
        suitable for feeding to the database."""
        res = []
        for h in self.hourly:
            t = (self.fid,
                 int(h.timestamp.timestamp()),
                 h.icon,
                 h.probability_rain,
                 h.rain_amt,
                 h.temperature,
                 h.humidity,
                 h.pressure,
                 h.wind_speed,
                 h.cloud_cover,
                 h.visibility)
            res.append(t)
        return res

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
