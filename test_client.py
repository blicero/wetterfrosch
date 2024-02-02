#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2024-02-01 21:00:00 krylon>
#
# /data/code/python/wetterfrosch/test_client.py
# created on 02. 01. 2024
# (c) 2024 Benjamin Walkenhorst
#
# This file is part of the Wetterfrosch weather app. It is distributed under the
# terms of the GNU General Public License 3. See the file LICENSE for details
# or find a copy online at https://www.gnu.org/licenses/gpl-3.0

"""
wetterfrosch.test_client

(c) 2024 Benjamin Walkenhorst
"""

import json
import os
import unittest
from datetime import datetime
from typing import Optional

from wetterfrosch import common
from wetterfrosch.client import Client
from wetterfrosch.data import WeatherWarning

TEST_DIR: str = os.path.join(
    datetime.now().strftime("wetterfrosch_test_client_%Y%m%d_%H%M%S"))


class ClientTest(unittest.TestCase):
    """Test the client!"""

    _client: Optional[Client] = None

    @classmethod
    def setUpClass(cls) -> None:
        """Prepare the environment for tests to run in"""
        root = "/tmp"
        if os.path.isdir("/data/ram"):
            root = "/data/ram"
        global TEST_DIR  # pylint: disable-msg=W0603
        TEST_DIR = os.path.join(
            root,
            datetime.now().strftime("wetterfrosch_test_client_%Y%m%d_%H%M%S"))
        common.set_basedir(TEST_DIR)

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up afterwards"""
        os.system(f'rm -rf "{TEST_DIR}"')

    @classmethod
    def client(cls, c: Optional[Client] = None) -> Optional[Client]:
        """Get or set the shared Client instance."""
        if c is not None:
            cls._client = c
        return cls._client

    def test_01_client_create(self) -> None:
        """Create a Client instance."""
        c: Optional[Client] = Client()
        assert c is not None
        self.assertIsNotNone(c)
        self.__class__.client(c)

    def test_02_fetch_data(self) -> None:
        """Try to fetch data."""
        c: Optional[Client] = self.__class__.client()
        self.assertIsNotNone(c)
        try:
            assert c is not None
            data: Optional[list[WeatherWarning]] = c.fetch()
            if data is not None:
                self.assertIsNotNone(data)
                assert data is not None
        except Exception as e:  # pylint: disable-msg=W0718
            self.fail(f"Failed to fetch/parse data from DWD: {e}")

    # def test_03_process_sample_data(self) -> None:
    #     """Test prcessing the sample data.
    #     This works even without a working Internet connection."""
    #     test_files: list[str] = ["example.json", "warnings.json"]
    #     c: Optional[Client] = self.__class__.client()
    #     assert c is not None
    #     self.assertIsNotNone(c)
    #     cwd = os.getcwd()
    #     print(f">>> Working directory is {cwd}")
    #     for f in test_files:
    #         path: str = f
    #         if not cwd.endswith("wetterfrosch"):
    #             path = os.path.join("wetterfrosch", f)
    #         with open(path, 'r', encoding="utf-8") as fh:
    #             try:
    #                 data = json.load(fh)
    #                 res = c.process(data)
    #                 self.assertIsNotNone(res)
    #             except Exception as e:  # pylint: disable-msg=W0718
    #                 self.fail(f"Failed to process {f}: {e}")

# Local Variables: #
# python-indent: 4 #
# End: #
