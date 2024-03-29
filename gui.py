#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: <2024-02-19 19:23:44 krylon>
#
# /data/code/python/wetterfrosch/gui.py
# created on 02. 01. 2024
# (c) 2024 Benjamin Walkenhorst
#
# This file is part of the Wetterfrosch weather app. It is distributed
# under the terms of the GNU General Public License 3. See the file
# LICENSE for details or find a copy online at
# https://www.gnu.org/licenses/gpl-3.0

"""
wetterfrosch.gui

(c) 2024 Benjamin Walkenhorst
"""

import json
import re
import sys
import traceback
from datetime import datetime, timedelta
from threading import Lock, local
from typing import Any, Final, Optional

import gi  # type: ignore
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

ICON_NAMES: Final[dict[str, str]] = {
    "cloudy": "clouds",
    "clear-night": "clear-night",
    "partly-cloudy-night": "few-clouds-night",
    "partly-cloudy-day": "few-clouds",
    "rain": "showers",
}


# pylint: disable-msg=R0902,R0903
class WetterGUI:
    """Graphical frontend to the wetterfrosch app"""

    # pylint: disable-msg=R0915
    def __init__(self, clnt: Optional[client.Client] = None) -> None:
        self.log = common.get_logger("GUI")
        self.lock: Final[Lock] = Lock()
        self.local = local()
        self.alert_cache: set[str] = set()
        self.visible: bool = False
        self.active: bool = True
        self.coords: list[float] = [0, 0]
        self.here: str = ""
        self.here_stamp: datetime = datetime.fromtimestamp(0)
        self.fc_stamp: datetime = datetime.fromtimestamp(0)
        self.location: list[str] = []

        # loc: str = self.get_location()
        # if loc != "":
        #     self.location.append(loc)

        # loc_path: Final[str] = common.path.locations()

        # if krylib.fexist(loc_path):
        #     with open(loc_path,
        #               "r",
        #               encoding="utf-8") \
        #             as fh:  # pylint: disable-msg=C0103
        #         for line in fh:
        #             self.location.append(line.strip())

        # self.location = sorted(set(self.location))

        if clnt is None:
            self.client = client.Client(30, self.location)
        else:
            self.client = clnt
        self.client.start()

        db = self.get_database()
        self.alert_cache = db.warning_get_keys()

        ################################################################
        # Create window and widgets ####################################
        ################################################################

        warn_columns: Final[list[tuple[int, str]]] = [
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

        self.warning_store = gtk.ListStore(
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

        fc_columns: Final[list[tuple[int, str]]] = [
            (0, "ID"),
            (1, "Zeitpunkt"),
            (2, "% Regen"),
            (3, "Regenmenge"),
            (4, "Temperatur"),
            (5, "Luftfeuchtigkeit"),
            (6, "Luftdruck"),
            (7, "Wind (m/s)"),
            (8, "% Bedeckt"),
            (9, "Sichtweite"),
        ]

        self.fc_store = gtk.ListStore(
            int,        # 0, ID
            str,        # 1, Zeitpunkt
            int,        # 2, % Regen
            float,      # 3, Regenmenge
            int,        # 4, Temperatur
            int,        # 5, Luftfeuchtigkeit
            float,      # 6, Luftdruck
            int,        # 7, Wingeschwindigkeit
            int,        # 8, % Bedeckt
            float,      # 9, Sichtweite
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

        self.mb_edit_item: gtk.MenuItem = \
            gtk.MenuItem.new_with_mnemonic("_Bearbeiten")
        self.edit_menu: gtk.Menu = gtk.Menu()
        self.em_loc_item: gtk.MenuItem = \
            gtk.MenuItem.new_with_mnemonic("_Orte verwalten")

        self.mb_debug_item: gtk.MenuItem = \
            gtk.MenuItem.new_with_mnemonic("Debu_g")
        self.debug_menu: gtk.Menu = gtk.Menu()
        self.db_load_item: gtk.MenuItem = \
            gtk.MenuItem.new_with_mnemonic("_Lade aus Datei...")
        self.db_msg_item: gtk.MenuItem = \
            gtk.MenuItem.new_with_mnemonic("_Nachricht anzeigen")

        self.fc_grid: gtk.Grid = gtk.Grid.new()
        self.fc_grid.set_column_homogeneous(True)
        self.fc_grid.set_row_homogeneous(True)
        self.fc_grid.set_column_spacing(4)
        self.fc_grid.set_row_spacing(2)
        self.fc_lbl_time: gtk.Label = gtk.Label.new("Zeit")
        self.fc_lbl_loc: gtk.Label = gtk.Label.new("Ort")
        self.fc_lbl_summary: gtk.Label = gtk.Label.new("Wetterlage")
        self.fc_lbl_prob_rain: gtk.Label = gtk.Label.new("Regen")
        self.fc_lbl_temp: gtk.Label = gtk.Label.new("Temperatur")
        self.fc_lbl_humid: gtk.Label = gtk.Label.new("Luftfeuchtigkeit")
        self.fc_lbl_wind: gtk.Label = gtk.Label.new("Windgeschwindigkeit")
        self.fc_view_time: gtk.TextView = gtk.TextView.new()
        self.fc_view_loc: gtk.TextView = gtk.TextView.new()
        self.fc_view_summary: gtk.TextView = gtk.TextView.new()
        self.fc_view_prob_rain: gtk.TextView = gtk.TextView.new()
        self.fc_view_temp: gtk.TextView = gtk.TextView.new()
        self.fc_view_humid: gtk.TextView = gtk.TextView.new()
        self.fc_view_wind: gtk.TextView = gtk.TextView.new()

        fc_labels: tuple[gtk.Label, ...] = (
            self.fc_lbl_time,
            self.fc_lbl_loc,
            self.fc_lbl_summary,
            self.fc_lbl_prob_rain,
            self.fc_lbl_temp,
            self.fc_lbl_humid,
            self.fc_lbl_wind,
        )

        for lbl in fc_labels:
            lbl.set_xalign(1.0)

        fc_views: tuple[gtk.Widget, ...] = (
            self.fc_view_time,
            self.fc_view_loc,
            self.fc_view_summary,
            self.fc_view_prob_rain,
            self.fc_view_temp,
            self.fc_view_humid,
            self.fc_view_wind,
        )

        for v in fc_views:
            v.editable = False

        self.notebook = gtk.Notebook.new()

        self.warn_view = gtk.TreeView(model=self.warning_store)

        for c in warn_columns:  # pylint: disable-msg=C0103
            col = gtk.TreeViewColumn(
                c[1],
                gtk.CellRendererText(),
                text=c[0],
                size=12,
            )
            self.warn_view.append_column(col)

        self.sw_warning: gtk.ScrolledWindow = gtk.ScrolledWindow()

        self.forecast_view = gtk.TreeView(model=self.fc_store)

        for c in fc_columns:
            col = gtk.TreeViewColumn(
                c[1],
                gtk.CellRendererText(),
                text=c[0],
                size=12,
            )
            self.forecast_view.append_column(col)

        self.sw_forecast: gtk.ScrolledWindow = gtk.ScrolledWindow()

        ################################################################
        # Assemble window and widgets ##################################
        ################################################################

        self.fc_grid.attach(self.fc_lbl_time, 0, 0, 1, 1)
        self.fc_grid.attach(self.fc_view_time, 1, 0, 1, 1)
        self.fc_grid.attach(self.fc_lbl_loc, 2, 0, 1, 1)
        self.fc_grid.attach(self.fc_view_loc, 3, 0, 1, 1)
        self.fc_grid.attach(self.fc_lbl_summary, 4, 0, 1, 1)
        self.fc_grid.attach(self.fc_view_summary, 5, 0, 1, 1)
        self.fc_grid.attach(self.fc_lbl_temp, 0, 1, 1, 1)
        self.fc_grid.attach(self.fc_view_temp, 1, 1, 1, 1)
        self.fc_grid.attach(self.fc_lbl_humid, 2, 1, 1, 1)
        self.fc_grid.attach(self.fc_view_humid, 3, 1, 1, 1)
        self.fc_grid.attach(self.fc_lbl_wind, 4, 1, 1, 1)
        self.fc_grid.attach(self.fc_view_wind, 5, 1, 1, 1)
        self.fc_grid.attach(self.fc_lbl_prob_rain, 6, 1, 1, 1)
        self.fc_grid.attach(self.fc_view_prob_rain, 7, 1, 1, 1)

        # For some reason, pylint has thinks a couple of methods we call here
        # on gtk Widgets do not exist when in fact they do. So I disable them
        # on a case-by-case basis.

        self.sw_warning.set_vexpand(True)
        self.sw_warning.set_hexpand(True)
        self.sw_warning.add(self.warn_view)  # pylint: disable-msg=E1101

        self.sw_forecast.set_vexpand(True)
        self.sw_forecast.set_hexpand(True)
        self.sw_forecast.add(self.forecast_view)  # pylint: disable-msg=E1101

        self.nb_lbl_warn = gtk.Label.new("Warnungen")
        self.nb_lbl_forecast = gtk.Label.new("Vorhersage")

        self.notebook.append_page(self.sw_warning, self.nb_lbl_warn)
        self.notebook.append_page(self.sw_forecast, self.nb_lbl_forecast)

        self.win.add(self.mbox)  # pylint: disable-msg=E1101
        self.mbox.pack_start(self.menubar,  # pylint: disable-msg=E1101
                             False,
                             True,
                             0)
        self.mbox.pack_start(self.fc_grid,  # pylint: disable-msg=E1101
                             False,
                             True,
                             0)
        # self.mbox.pack_start(self.scrolled_view,  # pylint: disable-msg=E1101
        #                      False,
        #                      True,
        #                      0)
        self.mbox.pack_start(self.notebook,
                             False,
                             True,
                             0)

        ################################################################
        # Create menu ##################################################
        ################################################################

        self.menubar.add(self.mb_file_item)
        self.menubar.add(self.mb_edit_item)
        self.menubar.add(self.mb_debug_item)

        self.mb_file_item.set_submenu(self.file_menu)
        self.file_menu.add(self.fm_refresh_item)
        self.file_menu.add(self.fm_quit_item)

        self.mb_edit_item.set_submenu(self.edit_menu)
        self.edit_menu.add(self.em_loc_item)

        self.mb_debug_item.set_submenu(self.debug_menu)
        self.debug_menu.add(self.db_load_item)
        self.debug_menu.add(self.db_msg_item)

        ################################################################
        # Set up signal handlers #######################################
        ################################################################

        self.win.connect("destroy", self.__quit)
        self.tray.connect("activate", self.__toggle_visible)
        self.tray.connect("button-press-event", self.tray_menu)
        self.fm_quit_item.connect("activate", self.__quit)
        self.fm_refresh_item.connect("activate", self.load)
        self.em_loc_item.connect("activate", self.edit_locations)
        self.db_load_item.connect("activate", self.load_from_file)
        self.db_msg_item.connect("activate", self.dbg_display_msg)

        self.win.show_all()  # pylint: disable-msg=E1101
        self.visible = True
        glib.timeout_add(5_000, self.__get_warnings)
        glib.timeout_add(5_000, self.update_forecast)
        glib.timeout_add(500, self._fetch_init_data)

    def run(self) -> None:
        """Run the Gtk mainloop"""
        gtk.main()

    def _fetch_init_data(self) -> bool:
        self.__get_warnings()
        self.update_forecast()
        return False

    def get_database(self) -> database.Database:
        """Get the Database instance for the calling thread."""
        try:
            return self.local.db
        except AttributeError:
            db = database.Database()  # pylint: disable-msg=C0103
            self.local.db = db
            return db

    def get_location(self) -> str:
        """Try to determine our location (city) using ipinfo.io"""
        try:
            res = requests.get(IPINFO_URL, verify=True, timeout=5)
            if res.status_code != 200:
                return ""
            data = res.json()
            self.coords = [float(x) for x in data["loc"].split(",")]
            self.here = data["city"]
            return data["city"]
        except Exception as e:  # pylint: disable-msg=W0718,C0103
            self.log.error("Failed to get location: %s", e)
            return ""

    def icon_from_forecast(self) -> str:
        """Try to generate an icon name from the forecast"""
        name: str = self.cur_forecast.icon
        if name in ICON_NAMES:  # pylint: disable-msg=R1715
            name = ICON_NAMES[name]
        icon: Final[str] = f"weather-{name}-symbolic"
        self.log.debug("Forecast says %s, icon is %s",
                       self.cur_forecast.icon,
                       icon)
        return icon

    def update_forecast(self) -> bool:
        """Refresh the weather forecast"""
        try:
            db = self.get_database()
            fc = db.forecast_get_current()
            if fc is not None:
                self.cur_forecast = fc  # pylint: disable-msg=W0201
                try:
                    icon = self.icon_from_forecast()
                    self.win.set_icon_name(icon)
                    self.tray.set_from_icon_name(icon)
                except:  # noqa: B001,E722 pylint: disable-msg=W0702
                    self.log.error("Cannot set window icon to %s: %s",
                                   self.cur_forecast.icon,
                                   sys.exception())
                if fc.timestamp == self.fc_stamp:
                    # self.log.debug("Weather forecast is already current.")
                    return True
                self.fc_stamp = fc.timestamp
                self.fc_view_time.get_buffer().set_text(
                    fc.timestamp.strftime(common.TIME_FMT))
                self.fc_view_loc.get_buffer().set_text(
                    f"{fc.location[0]:.02f}/{fc.location[1]:.02f}")
                self.fc_view_summary.get_buffer().set_text(fc.summary)
                self.fc_view_temp.get_buffer().set_text(f"{fc.temperature} °C")
                self.fc_view_humid.get_buffer().set_text(f"{fc.humidity} %")
                self.fc_view_wind.get_buffer().set_text(
                    f"{fc.wind_speed} km/h")
                self.fc_view_prob_rain.get_buffer().set_text(
                    f"{fc.probability_rain} %")
                self.fc_store.clear()
                for p in fc.hourly:
                    fiter = self.fc_store.append()
                    self.fc_store.set(
                        fiter,
                        (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
                        (
                            p.pid,
                            p.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                            p.probability_rain,
                            p.rain_amt,
                            p.temperature,
                            p.humidity,
                            p.pressure,
                            p.wind_speed,
                            p.cloud_cover,
                            p.visibility,
                        ))
            else:
                self.log.error("Client did not return forecast data")
        except Exception as e:  # pylint: disable-msg=W0718
            self.log.error("Error refreshing forecast: %s", e)
        return True

    def __toggle_visible(self, *_ignore: Any) -> None:
        if self.visible:
            self.win.hide()
        else:
            self.win.show_all()  # pylint: disable-msg=E1101
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
            _ = dlg.run()  # pylint: disable-msg=E1101
        finally:
            dlg.destroy()
            self.log.debug("We are still alive!")

    def display_data(self, data: list[WeatherWarning]) -> None:
        """Display weather warnings."""
        self.warning_store.clear()
        now: Final[datetime] = datetime.now()
        has_warnings: bool = False
        delta: Final[timedelta] = timedelta(hours=12)
        delta_d: Final[datetime] = now + delta
        for event in data:
            d1: datetime = event.start  # pylint: disable-msg=C0103
            d2: datetime = event.end  # pylint: disable-msg=C0103

            if d1 <= now <= d2 or now <= d1 <= delta_d:
                if not self.__known_alert(event):
                    try:
                        n = notify2.Notification(  # pylint: disable-msg=C0103
                            event.headline,
                            event.description,
                            ICON_NAME_WARN)
                        n.show()
                    except Exception as e:  # pylint: disable-msg=W0718
                        self.log.error("Failed to display notification: %s - %s",  # noqa: E501
                                       type(e),
                                       e)
                    has_warnings = True
                    with self.lock:
                        self.alert_cache.add(event.cksum())

                liter = self.warning_store.append()
                self.warning_store.set(
                    liter,
                    (0, 1, 2, 3, 4, 5, 6, 7, 8),
                    (
                        event.wid,
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

    def __get_warnings(self) -> bool:
        try:
            d1 = datetime.now() - timedelta(hours=2)
            d2 = datetime.now() + timedelta(hours=12)
            locations = client.LocationList.new()
            db = self.get_database()
            warnings = db.warning_get_by_period(d1, d2)
            dwarnings: list[WeatherWarning] = []
            for w in warnings:
                if not locations.check(w.region_name):
                    continue
                dwarnings.append(w)
            self.display_data(dwarnings)
        except Exception as e:  # pylint: disable-msg=W0718
            self.log.error("Error processing warnings: %s", e)
        return True

    def __known_alert(self, alert: WeatherWarning) -> bool:
        with self.lock:
            return alert.cksum() in self.alert_cache

    def load(self, *_ignore: Any) -> bool:
        """Fetch data, process, display"""
        try:
            now: Final[datetime] = datetime.now()
            d1: Final[datetime] = now - timedelta(hours=2)
            d2: Final[datetime] = now + timedelta(hours=12)
            db = self.get_database()
            warnings = db.warning_get_by_period(d1, d2)
            self.display_data(warnings)
        except Exception as e:  # pylint: disable-msg=W0718
            self.log.error("Something went wrong refreshing our data: %s", e)
            traceback.print_exception(e)
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
            res = dlg.run()  # pylint: disable-msg=E1101
            if res != gtk.ResponseType.OK:
                self.log.debug("Response from FileChooserDialog was {res}")
                return

            path: Final[str] = dlg.get_filename()  # pylint: disable-msg=E1101
            self.log.debug("Read warnings from {path}")

            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                warnings = data
                assert warnings is not None
                self.display_data(warnings)
        finally:
            dlg.destroy()

    # pylint: disable-msg=R0914
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
        content: Final[str] = NEWLINE.join(self.location)
        txt.get_buffer().set_text(content)
        mbox.add(txt)
        dlg.show_all()  # pylint: disable-msg=E1101

        try:
            response = dlg.run()  # pylint: disable-msg=E1101
            if response != gtk.ResponseType.OK:
                self.log.debug("Cancel editing of location list")
                return

            buf = txt.get_buffer()
            start: gtk.TextIter = buf.get_start_iter()
            end: gtk.TextIter = buf.get_end_iter()
            newlist: Final[str] = buf.get_text(start, end, True)
            if newlist != content:
                self.log.debug("Location list was modified, checking new list")
                patterns: Final[list[str]] = sorted(set(newlist.split(NEWLINE)))
                valid: bool = True
                for p in patterns:
                    try:
                        r: re.Pattern = re.compile(p, re.I)
                        assert r is not None
                    except re.error as e:
                        self.log.error("Invalid pattern '%s': %s", p, e)
                        valid = False
                        break
                    except AssertionError:
                        self.log.error(
                            "Failed to compile location to regex: %s",
                            p)
                        valid = False
                        break
                if valid:
                    with open(common.path.locations(),
                              "w",
                              encoding="utf-8") as fh:
                        fh.write(newlist)
                    loc_list = client.LocationList.new()
                    loc_list.replace(patterns)
        finally:
            dlg.destroy()

    def dbg_display_msg(self, _ignore: Any) -> None:
        """Display a random message for debugging purposes"""
        try:
            self.display_msg("Bla bla bla")
        finally:
            self.log.debug("We displayed a message")


# Local Variables: #
# python-indent: 4 #
# End: #
