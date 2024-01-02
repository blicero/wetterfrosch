#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2024-01-02 18:53:21 krylon>
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
from typing import Final, Optional

from wetterfrosch import common

WARNINGS_URL: Final[str] = \
    "https://www.dwd.de/DWD/warnungen/warnapp/json/warnings.json"

ENVELOPE_PAT: Final[re.Pattern] = \
    re.compile(r"^warnWetter[.]loadWarnings\((.*)\);", re.DOTALL)


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
    loc_patterns: list[re.Pattern]
    interval: timedelta

    def __init__(self, interval: int = 30, patterns: Optional[list[str]] = None) -> None:  # noqa: E501 pylint: disable-msg=C0301
        self.log = common.get_logger("client")
        self.interval = timedelta(seconds=interval)
        self.loc_patterns = []
        self.last_fetch = datetime.fromtimestamp(0)
        if patterns is not None:
            for p in patterns:
                r = re.compile(p, re.I)
                self.loc_patterns.append(r)

    def fetch(self) -> Optional[dict]:
        """Fetch the current list of warnings from DWD."""
        with urllib.request.urlopen(WARNINGS_URL) as res:
            if res.status != 200:
                self.log.error("Failed to fetch data from DWD: %d", res.status)
                return None
            body: Final[str] = res.read().decode()
            m: Final[Optional[re.Match[str]]] = ENVELOPE_PAT.match(body)
            assert m is not None  # SRSLY?
            payload: Final[str] = m[1]
            data: dict = json.loads(payload)
            return data

    def process(self, data: dict) -> Optional[list[dict]]:
        """Process the data we received from the DWD web site."""
        warnings: list[dict] = []
        for w in data["warnings"].values():
            for event in w:
                if len(self.loc_patterns) == 0:
                    warnings.append(event)
                else:
                    for p in self.loc_patterns:
                        if p.search(event["regionName"]) is not None:
                            warnings.append(event)
                            break
        return warnings


# Local Variables: #
# python-indent: 4 #
# End: #
