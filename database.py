#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2024-02-07 17:49:13 krylon>
#
# /data/code/python/wetterfrosch/database.py
# created on 13. 01. 2024
# (c) 2024 Benjamin Walkenhorst
#
# This file is part of the Wetterfrosch weather app. It is distributed under the
# terms of the GNU General Public License 3. See the file LICENSE for details
# or find a copy online at https://www.gnu.org/licenses/gpl-3.0

"""
wetterfrosch.database

(c) 2024 Benjamin Walkenhorst
"""

import logging
import sqlite3
import threading
import time
from datetime import datetime
from enum import Enum, auto
from math import ceil, floor
from typing import Final, Optional

import krylib

from wetterfrosch import common
from wetterfrosch.data import Forecast, WeatherWarning

OPEN_LOCK: Final[threading.Lock] = threading.Lock()

INIT_QUERIES: Final[list[str]] = [
    """
    CREATE TABLE warning (
        id              INTEGER PRIMARY KEY,
        state           TEXT NOT NULL,
        wtype           INTEGER NOT NULL,
        level           INTEGER NOT NULL,
        start           INTEGER NOT NULL,
        end             INTEGER NOT NULL,
        region_name     TEXT NOT NULL,
        description     TEXT NOT NULL,
        event           TEXT NOT NULL,
        headline        TEXT NOT NULL,
        instruction     TEXT NOT NULL,
        state_short     TEXT NOT NULL,
        altitude_start  INTEGER,
        altitude_end    INTEGER,
        acknowledged    INTEGER NOT NULL DEFAULT 0,
        key             TEXT GENERATED ALWAYS AS (
                                start ||
                                '--' ||
                                end ||
                                '--' ||
                                region_name ||
                                '--' ||
                                event ||
                                '--' ||
                                description ||
                                '--' ||
                                level
                        ) VIRTUAL,
        CHECK           (start <= end),
        CHECK           (altitude_start <= altitude_end)
    ) STRICT
    """,
    "CREATE INDEX wrn_reg_idx ON warning (region_name)",
    "CREATE INDEX wrn_start_idx ON warning (start)",
    "CREATE INDEX wrn_end_idx ON warning (end)",
    "CREATE INDEX wrn_evt_idx ON warning (event)",
    "CREATE INDEX wrn_ack_idx ON warning (acknowledged)",
    """
CREATE TABLE forecast (
    id INTEGER PRIMARY KEY,
    timestamp INTEGER UNIQUE NOT NULL,
    location TEXT NOT NULL,
    summary TEXT NOT NULL,
    icon TEXT NOT NULL,
    prob_rain INTEGER NOT NULL,
    temperature INTEGER NOT NULL,
    temperature_apparent INTEGER NOT NULL,
    humidity INTEGER NOT NULL,
    wind_speed INTEGER NOT NULL,
    visibility REAL NOT NULL,
    CHECK (prob_rain >= 0),
    CHECK (temperature BETWEEN -60 AND 50),
    CHECK (humidity >= 0),
    CHECK (wind_speed >= 0),
    CHECK (visibility >= 0)
) STRICT""",
    "CREATE UNIQUE INDEX fc_time_idx ON forecast (timestamp)",
]


# pylint: disable-msg=C0103
class Query(Enum):
    """Symbolic constants to identify database queries"""
    WarningAdd = auto()
    WarningGetByPeriod = auto()
    WarningGetAll = auto()
    WarningGetKeys = auto()
    WarningHasKey = auto()
    WarningAcknowledge = auto()
    ForecastAdd = auto()
    ForecastGetCurrent = auto()
    ForecastGetRecent = auto()
    ForecastGetByPeriod = auto()


db_queries: Final[dict[Query, str]] = {
    Query.WarningAdd: """
INSERT INTO warning (
    state,
    wtype,
    level,
    start,
    end,
    region_name,
    description,
    event,
    headline,
    instruction,
    state_short,
    altitude_start,
    altitude_end)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    RETURNING id
    """,
    Query.WarningGetAll: """
SELECT
    id,
    state,
    wtype,
    level,
    start,
    end,
    region_name,
    description,
    event,
    headline,
    instruction,
    state_short,
    altitude_start,
    altitude_end,
    acknowledged
FROM warning
ORDER BY start, region_name
    """,
    Query.WarningGetByPeriod: """
SELECT
    id,
    state,
    wtype,
    level,
    start,
    end,
    region_name,
    description,
    event,
    headline,
    instruction,
    state_short,
    altitude_start,
    altitude_end,
    acknowledged
FROM warning
WHERE start <= ? AND ? <= end -- XXX Needs thorough testing!
ORDER BY start, region_name
    """,
    Query.WarningGetKeys: """
 SELECT
    key
FROM warning
ORDER BY region_name, event, start, end
    """,
    Query.WarningHasKey: """
SELECT
    COUNT(id) AS cnt
 FROM warning
 WHERE key = ?
    """,
    Query.WarningAcknowledge: """
UPDATE warning
SET acknowledged = ?
WHERE id = ?
    """,
    Query.ForecastAdd: """
INSERT INTO forecast
    (timestamp,
     location,
     summary,
     icon,
     prob_rain,
     temperature,
     temperature_apparent,
     humidity,
     wind_speed,
     visibility)
    VALUES
    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
RETURNING id
    """,
    Query.ForecastGetCurrent: """
SELECT
    id,
    timestamp,
    location,
    summary,
    icon,
    prob_rain,
    temperature,
    temperature_apparent,
    humidity,
    wind_speed,
    visibility
FROM forecast
ORDER BY timestamp DESC
LIMIT 1
    """,
    Query.ForecastGetRecent: """
SELECT
    id,
    timestamp,
    location,
    summary,
    icon,
    prob_rain,
    temperature,
    temperature_apparent,
    humidity,
    wind_speed,
    visibility
FROM forecast
ORDER BY timestamp DESC
LIMIT ?
    """,
    Query.ForecastGetByPeriod: """
SELECT
    id,
    timestamp,
    location,
    summary,
    icon,
    prob_rain,
    temperature,
    temperature_apparent,
    humidity,
    wind_speed,
    visibility
FROM forecast
WHERE timestamp BETWEEN ? AND ?
ORDER BY timestamp
""",
}


class Database:
    """Database provides a wrapper around the, uh, database connection
    and exposes the operations to be performed on it."""

    __slots__ = [
        "db",
        "log",
        "path",
    ]

    db: sqlite3.Connection
    log: logging.Logger
    path: Final[str]

    def __init__(self, path: str = "") -> None:
        if path == "":
            path = common.path.db()
        self.path = path
        self.log = common.get_logger("database")
        self.log.debug("Open database at %s", path)
        with OPEN_LOCK:
            exist: Final[bool] = krylib.fexist(path)
            self.db = sqlite3.connect(path)
            self.db.isolation_level = None

            cur: Final[sqlite3.Cursor] = self.db.cursor()
            cur.execute("PRAGMA foreign_keys = true")
            cur.execute("PRAGMA journal_mode = WAL")

            if not exist:
                self.__create_db()

    def __create_db(self) -> None:
        """Initialize a freshly created database"""
        self.log.debug("Initialize fresh database at %s", self.path)
        with self.db:
            for query in INIT_QUERIES:
                cur: sqlite3.Cursor = self.db.cursor()
                cur.execute(query)
        self.log.debug("Database initialized successfully.")

    def __enter__(self) -> None:
        self.db.__enter__()

    def __exit__(self, ex_type, ex_val, traceback):
        return self.db.__exit__(ex_type, ex_val, traceback)

    def warning_add(self, w: WeatherWarning) -> None:
        """Add one warning to the database."""
        self.log.debug("Add warning to database: %s in %s from %s to %s",
                       w.event,
                       w.region_name,
                       w.start.strftime(common.TIME_FMT),
                       w.end.strftime(common.TIME_FMT))
        cur: Final[sqlite3.Cursor] = self.db.cursor()
        cur.execute(db_queries[Query.WarningAdd],
                    (
                        w.state,
                        w.wtype,
                        w.level,
                        int(w.start.timestamp()),
                        int(w.end.timestamp()),
                        w.region_name,
                        w.description,
                        w.event,
                        w.headline,
                        w.instruction,
                        w.state_short,
                        w.altitude_start,
                        w.altitude_end,
                    ))
        row = cur.fetchone()
        w.wid = row[0]

    def warning_get_all(self) -> list[WeatherWarning]:
        """Fetch all warnings from the database.
        Caveat programmor."""
        cur: Final[sqlite3.Cursor] = self.db.cursor()
        cur.execute(db_queries[Query.WarningGetAll])
        results: list[WeatherWarning] = []
        for row in cur:
            raw: dict = {
                "state": row[1],
                "type": row[2],
                "level": row[3],
                "start": row[4] * 1000,
                "end": row[5] * 1000,
                "regionName": row[6],
                "description": row[7],
                "event": row[8],
                "headline": row[9],
                "instruction": row[10],
                "stateShort": row[11],
                "altitudeStart": row[12],
                "altitudeEnd": row[13],
                "acknowledged": row[14],
            }
            record = WeatherWarning(raw, row[0])
            results.append(record)
        return results

    def warning_get_by_period(self, t1: datetime, t2: datetime) -> \
            list[WeatherWarning]:
        """Fetch all warnings for the given period."""
        cur: Final[sqlite3.Cursor] = self.db.cursor()
        cur.execute(db_queries[Query.WarningGetByPeriod],
                    (ceil(t2.timestamp()),
                     floor(t1.timestamp())))
        results: list[WeatherWarning] = []
        for row in cur:
            raw: dict = {
                "state": row[1],
                "type": row[2],
                "level": row[3],
                "start": row[4] * 1000,
                "end": row[5] * 1000,
                "regionName": row[6],
                "description": row[7],
                "event": row[8],
                "headline": row[9],
                "instruction": row[10],
                "stateShort": row[11],
                "altitudeStart": row[12],
                "altitudeEnd": row[13],
                "acknowledged": row[14],
            }
            record = WeatherWarning(raw, row[0])
            results.append(record)
        return results

    def warning_get_keys(self) -> set[str]:
        """Return the keys of all warnings stored in the database."""
        cnt: int = 0
        cur: Final[sqlite3.Cursor] = self.db.cursor()
        cur.execute(db_queries[Query.WarningGetKeys])
        results: set[str] = set()
        for row in cur:
            cnt += 1
            results.add(row[0])
        self.log.debug("Found %d warnings in database", cnt)
        l: int = len(results)
        if l != cnt:
            diff: int = cnt - l
            self.log.warning("Found %d duplicate warnings in database.", diff)
        return results

    def warning_has_key(self, key: str) -> bool:
        """Check if the given key is present in the database."""
        cur: Final[sqlite3.Cursor] = self.db.cursor()
        cur.execute(db_queries[Query.WarningHasKey], (key, ))
        row = cur.fetchone()
        return row[0] > 0

    def warning_acknowledge(self, w: WeatherWarning) -> None:
        """Mark a WeatherWarning as acknowledged."""
        assert w.wid > 0
        stamp: int = int(time.time())
        cur: Final[sqlite3.Cursor] = self.db.cursor()
        cur.execute(db_queries[Query.WarningAcknowledge],
                    (stamp, w.wid))
        w.acknowledged = True

    def forecast_add(self, fc: Forecast) -> None:
        """Add a Forecast to the database."""
        self.log.debug(
            "Add Forecast to database: %s @ %s %d °C, %d %% humidity.",
            fc.timestamp.strftime(common.TIME_FMT),
            fc.location,
            fc.temperature,
            fc.humidity)
        cur: Final[sqlite3.Cursor] = self.db.cursor()
        cur.execute(db_queries[Query.ForecastAdd],
                    (
                        int(fc.timestamp.timestamp()),
                        f"{fc.location[0]}/{fc.location[1]}",
                        fc.summary,
                        fc.icon,
                        fc.probability_rain,
                        fc.temperature,
                        fc.temperature_apparent,
                        fc.humidity,
                        fc.wind_speed,
                        fc.visibility,
                    ))
        row = cur.fetchone()
        fc.fid = row[0]

    def forecast_get_current(self) -> Optional[Forecast]:
        """Return the most recent Forecast from the database."""
        cur: Final[sqlite3.Cursor] = self.db.cursor()
        cur.execute(db_queries[Query.ForecastGetCurrent])
        row = cur.fetchone()
        if row is None:
            return None
        return Forecast.from_db(row)

    def forecast_get_recent(self, n: int = 5) -> list[Forecast]:
        """Get the <n> most recent Forecast items."""
        cur: Final[sqlite3.Cursor] = self.db.cursor()
        cur.execute(db_queries[Query.ForecastGetRecent], (n, ))
        records: list[Forecast] = []
        for row in cur:
            fc = Forecast.from_db(row)
            records.append(fc)
        return records

# Local Variables: #
# python-indent: 4 #
# End: #
