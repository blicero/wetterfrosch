#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2024-01-19 22:10:27 krylon>
#
# /data/code/python/wetterfrosch/gui.py
# created on 02. 01. 2024
# (c) 2024 Benjamin Walkenhorst
#
# This file is part of the Vox audiobook reader. It is distributed under the
# terms of the GNU General Public License 3. See the file LICENSE for details
# or find a copy online at https://www.gnu.org/licenses/gpl-3.0

"""
wetterfrosch.gui

(c) 2024 Benjamin Walkenhorst
"""

import json
import pprint
import queue
import re
import time
from datetime import datetime, timedelta
from threading import Lock, Thread, local
from typing import Any, Final

import gi  # type: ignore
import krylib
import notify2  # type: ignore
import requests  # type: ignore

from wetterfrosch import client, common, database
from wetterfrosch.data import WeatherWarning

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GLib", "2.0")
gi.require_version("Gio", "2.0")

from gi.repository import \
    Gdk as gdk  # noqa: E402 pylint: disable-msg=C0413,C0411 # type: ignore
from gi.repository import \
    GLib as glib  # noqa: E402 pylint: disable-msg=C0413,C0411 # type: ignore
from gi.repository import \
    Gtk as gtk  # noqa: E402 pylint: disable-msg=C0413,C0411 # type: ignore

# from gi.repository import Gio \
#     as gio  # noqa: E402 pylint: disable-msg=C0413,C0411

APP_ID: Final[str] = f"{common.APP_NAME}/{common.APP_VERSION}"
ICON_NAME_DEFAULT: Final[str] = "weather-storm-symbolic"
ICON_NAME_WARN: Final[str] = "weather-severe-alert-symbolic"
FETCH_INTERVAL: Final[int] = 300
NEWLINE: Final[str] = "\n"

IPINFO_URL: Final[str] = "https://ipinfo.io/json"


# pylint: disable-msg=R0902,R0903
class WetterGUI:
    """Graphical frontend to the wetterfrosch app"""

    # pylint: disable-msg=R0915
    def __init__(self) -> None:
        self.log = common.get_logger("GUI")
        self.lock: Final[Lock] = Lock()
        self.local = local()
        self.alert_cache: set[str] = set()
        self.queue: queue.SimpleQueue = queue.SimpleQueue()
        self.visible: bool = False
        self.active: bool = True

        self.location: list[str] = []
        loc: str = self.get_location()
        if loc != "":
            self.location.append(loc)

        loc_path: Final[str] = common.path.locations()

        if krylib.fexist(loc_path):
            with open(loc_path,
                      "r",
                      encoding="utf-8") \
                    as fh:  # pylint: disable-msg=C0103
                for line in fh:
                    self.location.append(line.strip())

        db = self.get_database()
        self.alert_cache = db.warning_get_keys()

        self.refresh_worker = Thread(target=self.__refresh_worker, daemon=True)
        self.refresh_worker.start()

        ################################################################
        # Create window and widgets ####################################
        ################################################################

        columns: Final[list[tuple[int, str]]] = [
            (0, "ID"),
            (1, "Level"),
            (2, "Region"),
            (3, "Start"),
            (4, "Ende"),
            (5, "Ereignis"),
            (6, "Überschrift"),
            (7, "Beschreibung"),
            (8, "Hinweise"),
        ]

        self.store = gtk.ListStore(
            int,  # 0, Record ID
            int,  # 1, Level
            str,  # 2, Region
            str,  # 3, Start
            str,  # 4, End
            str,  # 5, Event
            str,  # 6, Headline
            str,  # 7, Description
            str,  # 8, Instructions
        )

        self.win = gtk.Window()
        self.win.set_title(f"{common.APP_NAME} {common.APP_VERSION}")
        self.win.set_icon_name(ICON_NAME_DEFAULT)
        self.tray = gtk.StatusIcon.new_from_icon_name(ICON_NAME_DEFAULT)
        self.tray.set_has_tooltip(True)
        self.tray.set_title(f"{common.APP_NAME} {common.APP_VERSION}")
        self.tray.set_tooltip_text(f"{common.APP_NAME} {common.APP_VERSION}")

        notify2.init(APP_ID, "glib")

        self.mbox: gtk.Box = gtk.Box(orientation=gtk.Orientation.VERTICAL)
        self.menubar: gtk.MenuBar = gtk.MenuBar()

        self.mb_file_item: gtk.MenuItem = \
            gtk.MenuItem.new_with_mnemonic("_Datei")
        self.file_menu: gtk.Menu = gtk.Menu()
        self.fm_refresh_item: gtk.MenuItem = \
            gtk.MenuItem.new_with_mnemonic("_Aktualisieren")
        self.fm_quit_item: gtk.MenuItem = \
            gtk.MenuItem.new_with_mnemonic("_Beenden")
        self.fm_load_item: gtk.MenuItem = \
            gtk.MenuItem.new_with_mnemonic("_Lade aus Datei...")

        self.mb_edit_item: gtk.MenuItem = \
            gtk.MenuItem.new_with_mnemonic("_Bearbeiten")
        self.edit_menu: gtk.Menu = gtk.Menu()
        self.em_loc_item: gtk.MenuItem = \
            gtk.MenuItem.new_with_mnemonic("_Orte verwalten")

        self.warn_view = gtk.TreeView(model=self.store)

        for c in columns:  # pylint: disable-msg=C0103
            col: gtk.TreeViewColumn = gtk.TreeViewColumn(
                c[1],
                gtk.CellRendererText(),
                text=c[0],
                size=12,
            )
            self.warn_view.append_column(col)

        self.scrolled_view: gtk.ScrolledWindow = gtk.ScrolledWindow()

        ################################################################
        # Assemble window and widgets ##################################
        ################################################################

        self.win.add(self.mbox)
        self.mbox.pack_start(self.menubar, False, True, 0)
        self.mbox.pack_start(self.scrolled_view, False, True, 0)
        self.scrolled_view.set_vexpand(True)
        self.scrolled_view.set_hexpand(True)
        self.scrolled_view.add(self.warn_view)

        ################################################################
        # Create menu ##################################################
        ################################################################

        self.menubar.add(self.mb_file_item)
        self.mb_file_item.set_submenu(self.file_menu)
        self.file_menu.add(self.fm_refresh_item)
        if common.DEBUG:
            self.file_menu.add(self.fm_load_item)
        self.file_menu.add(self.fm_quit_item)

        self.mb_edit_item.set_submenu(self.edit_menu)
        self.edit_menu.add(self.em_loc_item)

        ################################################################
        # Set up signal handlers #######################################
        ################################################################

        self.win.connect("destroy", self.__quit)
        self.tray.connect("activate", self.__toggle_visible)
        self.tray.connect("button-press-event", self.tray_menu)
        self.fm_quit_item.connect("activate", self.__quit)
        self.fm_refresh_item.connect("activate", self.load)
        if common.DEBUG:
            self.fm_load_item.connect("activate", self.load_from_file)

        self.win.show_all()
        self.visible = True
        glib.timeout_add(2000, self.__check_queue)

    def get_client(self) -> client.Client:
        """Get the Client instance for the calling thread."""
        try:
            return self.local.client
        except AttributeError:
            c = client.Client(60, self.location)  # # pylint: disable-msg=C0103
            self.local.client = c
            return c

    def get_database(self) -> database.Database:
        """Get the Database instance for the calling thread."""
        try:
            return self.local.db
        except AttributeError:
            db = database.Database()  # pylint: disable-msg=C0103
            self.local.db = db
            return db

    def __toggle_visible(self, *_ignore: Any) -> None:
        if self.visible:
            self.win.hide()
        else:
            self.win.show_all()
        self.visible = not self.visible

    def __quit(self, *_ignore: Any) -> None:
        with self.lock:
            self.active = False
        self.tray.set_visible(False)
        self.win.destroy()
        gtk.main_quit()

    def is_active(self) -> bool:
        """Return the GUI's active flag."""
        with self.lock:
            return self.active

    def tray_menu(self, _icon: gtk.StatusIcon, event: gdk.EventButton) -> None:
        """Display the popup menu for the tray icon."""
        if event.button != 3:
            return

        menu = gtk.Menu()
        ref_item = gtk.MenuItem.new_with_mnemonic("_Aktualisieren")
        quit_item = gtk.MenuItem.new_with_mnemonic("_Beenden")

        ref_item.connect("activate", self.load)
        quit_item.connect("activate", self.__quit)

        menu.append(ref_item)
        menu.append(quit_item)
        menu.show_all()
        menu.popup_at_pointer(event)

    def get_location(self) -> str:
        """Try to determine our location (city) using ipinfo.io"""
        try:
            res = requests.get(IPINFO_URL, verify=True, timeout=5)
            if res.status_code != 200:
                return ""
            data = res.json()
            return data["city"]
        except Exception as e:  # pylint: disable-msg=W0718,C0103
            self.log.error("Failed to get location: %s", e)
            return ""

    def display_msg(self, msg: str) -> None:
        """Display a message in a dialog."""
        self.log.info(msg)

        dlg = gtk.Dialog(
            parent=self.win,
            title="Attention",
            modal=True,
        )

        dlg.add_buttons(
            gtk.STOCK_OK,
            gtk.ResponseType.OK,
        )

        area = dlg.get_content_area()
        lbl = gtk.Label(label=msg)
        area.add(lbl)
        dlg.show_all()  # pylint: disable-msg=E1101

        try:
            dlg.run()  # pylint: disable-msg=E1101
        finally:
            dlg.destroy()

    def display_data(self, data: list[WeatherWarning]) -> None:
        """Display weather warnings."""
        self.store.clear()
        now: Final[datetime] = datetime.now()
        has_warnings: bool = False
        db = self.get_database()
        delta: Final[timedelta] = timedelta(hours=12)
        delta_d: Final[datetime] = now + delta
        self.log.debug("Displaying data:\n\t%s",
                       pprint.pformat(data))
        with db:
            for event in data:
                d1: datetime = event.start  # pylint: disable-msg=C0103
                d2: datetime = event.end  # pylint: disable-msg=C0103

                if d1 <= now <= d2 or now <= d1 <= delta_d:
                    if not self.__known_alert(event):
                        n = notify2.Notification(  # pylint: disable-msg=C0103
                            event.headline,
                            event.description,
                            ICON_NAME_WARN)
                        n.show()
                        has_warnings = True
                        with self.lock:
                            self.alert_cache.add(event.cksum())
                        db.warning_add(event)

                    liter = self.store.append()
                    self.store.set(
                        liter,
                        (1, 2, 3, 4, 5, 6, 7, 8),
                        (
                            event.level,
                            event.region_name,
                            d1.strftime(common.TIME_FMT),
                            d2.strftime(common.TIME_FMT),
                            event.event,
                            event.headline,
                            event.description,
                            event.instruction,
                        ),
                    )

        if has_warnings:
            self.tray.set_from_icon_name(ICON_NAME_WARN)
        else:
            self.tray.set_from_icon_name(ICON_NAME_DEFAULT)

    def __refresh_worker(self) -> None:
        """Periodically fetch data from the DWD and process it."""
        while self.is_active():
            try:
                dwd: client.Client = self.get_client()
                raw = dwd.fetch()
                if raw is None:
                    self.display_msg("Client did not return any data.")
                else:
                    proc = dwd.process(raw)
                    if proc is None or len(proc) == 0:
                        self.display_msg(
                            "No warnings were left after processing.")
                    else:
                        self.queue.put(proc)
            except Exception as e:  # pylint: disable-msg=W0718
                self.log.error(
                    "Something went wrong refreshing our data: %s",
                    e)
            finally:
                time.sleep(FETCH_INTERVAL)

    def __check_queue(self) -> bool:
        if not self.queue.empty():
            if self.queue.qsize() > 0:
                item = self.queue.get()
                self.display_data(item)
        return True

    def __known_alert(self, alert: WeatherWarning) -> bool:
        with self.lock:
            return alert.cksum() in self.alert_cache

    def load(self, *_ignore: Any) -> bool:
        """Fetch data, process, display"""
        c = self.get_client()
        try:
            raw = c.fetch()
            if raw is None:
                self.display_msg("Client did not return any data.")
                return True
            proc = c.process(raw)
            if proc is None or len(proc) == 0:
                self.display_msg("No warnings were left after processing.")
                return True
            self.display_data(proc)
            return True
        except Exception as e:  # pylint: disable-msg=W0718
            self.log.error("Something went wrong refreshing our data: %s", e)
            return True

    def load_from_file(self, _ignore: Any) -> None:
        """Load warnings from a file, mainly for testing purposes."""
        dlg: gtk.FileChooserDialog = gtk.FileChooserDialog(
            title="Datei auswählen...",
            parent=self.win,
            action=gtk.FileChooserAction.OPEN)
        dlg.add_buttons(
            gtk.STOCK_CANCEL,
            gtk.ResponseType.CANCEL,
            gtk.STOCK_OPEN,
            gtk.ResponseType.OK,
        )

        try:
            res = dlg.run()
            if res != gtk.ResponseType.OK:
                self.log.debug("Response from FileChooserDialog was {res}")
                return

            path: Final[str] = dlg.get_filename()
            self.log.debug("Read warnings from {path}")

            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                warnings = self.get_client().process(data)
                assert warnings is not None
                self.display_data(warnings)
        finally:
            dlg.destroy()

    def edit_locations(self, _ignore: Any) -> None:
        """Edit the list of location we are interested in."""
        dlg: gtk.Dialog = gtk.Dialog(
            title="Bearbeite Orte",
            parent=self.win,
        )
        dlg.add_buttons(
            gtk.STOCK_CANCEL,
            gtk.ResponseType.CANCEL,
            gtk.STOCK_OK,
            gtk.ResponseType.OK,
        )

        mbox = dlg.get_content_area()
        txt: gtk.TextView = gtk.TextView.new()
        txt.editable = True
        content: Final[str] = NEWLINE.join(self.locations)
        txt.get_buffer().set_text(content)
        mbox.add(txt)

        try:
            response = dlg.run()
            if response != gtk.ResponseType.OK:
                return

            buf = txt.get_buffer()
            start: gtk.TextIter = buf.get_start_iter()
            end: gtk.TextIter = buf.get_end_iter()
            newlist: Final[str] = buf.get_text(start, end, True)
            if newlist != content:
                patterns: Final[list[str]] = newlist.split(NEWLINE)
                valid: bool = True
                for p in patterns:
                    try:
                        r: re.Pattern = re.compile(p, re.I)
                        assert r is not None
                    except re.error as e:
                        self.log.error("Invalid pattern '%s': %s", p, e)
                        valid = False
                        break
                if valid:
                    with open(common.path.location(), "w", "utf-8") as fh:
                        fh.write(newlist)
        finally:
            dlg.destroy()


def main() -> None:
    """Create a WetterGUI instance and start the Gtk main loop."""
    ui = WetterGUI()
    ui.log.debug("Let's go")
    gtk.main()


if __name__ == '__main__':
    main()

# Local Variables: #
# python-indent: 4 #
# End: #
