#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2024-01-09 20:04:06 krylon>
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
import time
from datetime import datetime
from threading import Lock, Thread, local
from typing import Any, Final

import gi  # type: ignore
import notify2
import requests  # type: ignore

from wetterfrosch import client, common

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GLib", "2.0")
gi.require_version("Gio", "2.0")

from gi.repository import \
    Gdk as gdk  # noqa: E402 pylint: disable-msg=C0413,C0411
from gi.repository import \
    GLib as glib  # noqa: E402 pylint: disable-msg=C0413,C0411
from gi.repository import \
    Gtk as gtk  # noqa: E402 pylint: disable-msg=C0413,C0411

# from gi.repository import Gio \
#     as gio  # noqa: E402 pylint: disable-msg=C0413,C0411

APP_ID: Final[str] = f"{common.APP_NAME}/{common.APP_VERSION}"
ICON_NAME_DEFAULT: Final[str] = "weather-storm-symbolic"
ICON_NAME_WARN: Final[str] = "weather-severe-alert-symbolic"
FETCH_INTERVAL: Final[int] = 300


IPINFO_URL: Final[str] = "https://ipinfo.io/json"


def get_location() -> str:
    """Try to determine our location (city) using ipinfo.io"""
    res = requests.get(IPINFO_URL, verify=True, timeout=5)
    if res.status_code != 200:
        return ""
    data = res.json()
    return data["city"]


# pylint: disable-msg=R0902,R0903
class WetterGUI:
    """Graphical frontend to the wetterfrosch app"""

    # pylint: disable-msg=R0915
    def __init__(self) -> None:
        self.log = common.get_logger("GUI")
        self.lock: Final[Lock] = Lock()
        self.local = local()
        self.queue: queue.SimpleQueue = queue.SimpleQueue()
        self.visible: bool = False
        self.active: bool = True

        self.location = get_location()

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
            int,  # Record ID
            int,  # Level
            str,  # Region
            str,  # Start
            str,  # End
            str,  # Event
            str,  # Headline
            str,  # Description
            str,  # Instructions
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

        self.warn_view = gtk.TreeView(model=self.store)

        for c in columns:
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
            c = client.Client(60, [self.location])
            self.local.client = c
            return c

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
        # ...

        menu.show_all()

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

    def display_data(self, data: list[dict]) -> None:
        """Display weather warnings."""
        self.store.clear()
        now: Final[datetime] = datetime.now()
        has_warnings: bool = False
        self.log.debug("Displaying data:\n\t%s",
                       pprint.pformat(data))
        for event in data:
            d1: datetime = datetime.fromtimestamp(event["start"]/1000)
            d2: datetime = datetime.fromtimestamp(event["end"]/1000)

            if d1 <= now <= d2:
                n = notify2.Notification(
                    event["headline"],
                    event["description"],
                    ICON_NAME_WARN)
                n.show()
                has_warnings = True

            liter = self.store.append()
            self.store.set(
                liter,
                (0, 1, 2, 3, 4, 5, 6, 7, 8),
                (
                    0,
                    event["level"],
                    event["regionName"],
                    d1.strftime(common.TIME_FMT),
                    d2.strftime(common.TIME_FMT),
                    event["event"],
                    event["headline"],
                    event["description"],
                    event["instruction"],
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
