#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2024-01-17 10:28:24 krylon>
#
# /data/code/python/wetterfrosch/data.py
# created on 12. 01. 2024
# (c) 2024 Benjamin Walkenhorst
#
# This file is part of the Vox audiobook reader. It is distributed under the
# terms of the GNU General Public License 3. See the file LICENSE for details
# or find a copy online at https://www.gnu.org/licenses/gpl-3.0

"""
wetterfrosch.data

(c) 2024 Benjamin Walkenhorst
"""

# import hashlib
from datetime import datetime
from typing import Final, Optional


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

    def __init__(self, record: dict, wid: int = 0) -> None:
        self.wid = wid
        self.state = record["state"]
        self.wtype = record["type"]
        self.level = record["level"]
        self.start = datetime.fromtimestamp(record["start"]/1000)
        if ("end" in record) and record["end"] is not None:
            self.end = datetime.fromtimestamp(record["end"]/1000 + 14400)
        else:
            self.end = self.start
        self.region_name = record["regionName"]
        self.description = record["description"]
        self.event = record["event"]
        self.headline = record["headline"]
        self.instruction = record["instruction"]
        self.state_short = record["stateShort"]
        self.altitude_end = record["altitudeEnd"]
        self.altitude_start = record["altitudeStart"]

    def cksum(self) -> str:
        """Produce a checksum to see if two Warnings are identical."""
        summary: Final[str] = \
            f"{self.start}--{self.end}--{self.region_name}--{self.event}--" + \
            f"{self.headline}--{self.level}"

        # cksum: Final[str] = hashlib.sha512(summary.encode()).hexdigest()
        # return cksum
        return summary

# local Variables: #
# python-indent: 4 #
# End: #
