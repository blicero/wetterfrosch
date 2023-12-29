#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2023-12-29 18:50:30 krylon>
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


import logging
import re
import urllib.request
from datetime import datetime, timedelta
from typing import Final

from wetterfrosch import common

WARNINGS_URL: Final[str] = \
    "https://www.dwd.de/DWD/warnungen/warnapp/json/warnings.json"

envelope_pat: Final[re.Pattern] = \
    re.compile(r"^[^{]+(.*)\);'$", re.DOTALL)


class Client:
    """Client fetches weather warnings from the DWD web site."""

    __slots__ = [
        "last_fetch",
        "interval",
        "log",
    ]

    log: logging.Logger
    last_fetch: datetime
    interval: timedelta

    def __init__(self, interval: int = 30) -> None:
        self.log = common.get_logger("client")
        self.interval = timedelta(seconds=interval)
        self.last_fetch = datetime.fromtimestamp(0)

    def fetch(self) -> str:
        """Fetch the current list of warnings from DWD."""
        body: Final[str] = urllib.request.urlopen(WARNINGS_URL).read().decode()
        return body

# Local Variables: #
# python-indent: 4 #
# End: #
