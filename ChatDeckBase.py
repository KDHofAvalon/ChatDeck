# Import StreamController modules
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase

# Import URL handling libraries
import urllib3

# Import log functionality
from loguru import logger as log

# Import gtk modules - used for the config rows
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw


# Set constants
KEY_URL_METHOD = "url_method"
DEFAULT_URL_METHOD = "GET"
AVAILABLE_URL_METHODS = ["GET", "POST"]

KEY_URL_DESTINATION = "url_destination"
DEFAULT_URL_DESTINATION = ""

KEY_URL_USERNAME_VAR = "url_user_var"
DEFAULT_URL_USERNAME_VAR = "username"

KEY_URL_MESSAGE_VAR = "url_mes_var"
DEFAULT_URL_MESSAGE_VAR = "message"


class ChatReadBase(ActionBase):
    def __init__(
        self,
        messages: dict = {},
        message_count: int = 0,
        message_no: int = -1,
        tick_count: int = 0,
        idle_message: str = "",
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.lm = self.plugin_base.locale_manager
        self.lm.set_to_os_default()

        self.messages = messages
        self.message_count = message_count
        self.message_no = message_no
        self.tick_count = tick_count
        self.idle_message = idle_message

    def on_ready(self) -> None:
        self.get_messages()

        self.show_latest_message()

    def on_tick(self):
        self.get_messages()

        self.tick_count = self.tick_count + 1

        if self.message_count > 0:
            if self.tick_count == 10:
                self.idle_message = self.message_no
            elif self.tick_count >= 30:
                self.tick_count = 0
                if self.message_no == self.idle_message:
                    self.show_latest_message()
            elif self.message_no == -1:
                self.tick_count = 0
                self.show_latest_message()

    def show_message(self):
        self.set_label(text=self.messages[self.message_no].username, position="top")
        self.set_label(text=self.messages[self.message_no].message, position="center")

    def get_messages(self):
        try:
            self.messages = self.plugin_base.backend.get_messages()
        except Exception as e:
            log.error(e)
            self.show_error()
            self.messages = {}
        self.message_count = len(self.messages)

    def message_check(self) -> bool:
        if self.message_count > 0:
            return True
        else:
            return False

    def range_check(self):
        if self.message_check:
            first = min(self.messages.keys())
            last = max(self.messages.keys())
            if self.message_no < first:
                self.message_no = first
            elif self.message_no > last:
                self.message_no = last

    def show_next_message(self):
        if self.message_check():
            if self.message_no < max(self.messages.keys()):
                self.message_no = self.message_no + 1
            self.range_check()
            self.show_message()

    def show_prev_message(self, loop: bool = False):
        if self.message_check():
            if self.message_no > min(self.messages.keys()):
                self.message_no = self.message_no - 1
            self.range_check()
            self.show_message()

    def show_latest_message(self):
        if self.message_count > 0:
            self.message_no = max(self.messages.keys())
            self.show_message()
        else:
            self.set_label(text=self.lm.get("ui.ready.message"), position="center")

    def get_config_rows(self) -> "list[Adw.PreferencesRow]":
        self.url_method_model = Gtk.StringList()
        for method in AVAILABLE_URL_METHODS:
            self.url_method_model.append(method)

        self.url_method_combo = Adw.ComboRow(
            model=self.url_method_model,
            title=self.lm.get("action.settings.url-method.label"),
            subtitle=self.lm.get("action.settings.url-method.subtitle"),
        )

        self.url_destination_entry = Adw.EntryRow(
            title=self.lm.get("action.settings.dest-url.label")
        )

        self.url_username_var_entry = Adw.EntryRow(
            title=self.lm.get("action.settings.username-var.label")
        )

        self.url_message_var_entry = Adw.EntryRow(
            title=self.lm.get("action.settings.message-var.label")
        )

        self.load_config_values()

        self.url_method_combo.connect("notify::selected", self.on_url_method_changed)
        self.url_destination_entry.connect(
            "notify::text", self.on_url_destination_changed
        )
        self.url_username_var_entry.connect(
            "notify::text", self.on_url_username_var_changed
        )
        self.url_message_var_entry.connect(
            "notify::text", self.on_url_message_var_changed
        )

        return [
            self.url_method_combo,
            self.url_destination_entry,
            self.url_username_var_entry,
            self.url_message_var_entry,
        ]

    def load_config_values(self):
        settings = self.get_settings()
        url_method = str(settings.get(KEY_URL_METHOD, DEFAULT_URL_METHOD))
        url_destination = str(
            settings.get(KEY_URL_DESTINATION, DEFAULT_URL_DESTINATION)
        )
        url_username_var = str(
            settings.get(KEY_URL_USERNAME_VAR, DEFAULT_URL_USERNAME_VAR)
        )
        url_message_var = str(
            settings.get(KEY_URL_MESSAGE_VAR, DEFAULT_URL_MESSAGE_VAR)
        )

        try:
            selected_index = AVAILABLE_URL_METHODS.index(url_method)
        except ValueError:
            selected_index = AVAILABLE_URL_METHODS.index(DEFAULT_URL_METHOD)

        self.url_method_combo.set_selected(selected_index)
        self.url_destination_entry.set_text(url_destination)
        self.url_username_var_entry.set_text(url_username_var)
        self.url_message_var_entry.set_text(url_message_var)

    def update_settings(self, key: str, value):
        settings = self.get_settings()
        settings[key] = value
        self.set_settings(settings)

    def on_url_method_changed(self, combo, _):
        selected_index = combo.get_selected()
        if 0 <= selected_index < len(AVAILABLE_URL_METHODS):
            url_method = AVAILABLE_URL_METHODS[selected_index]
            self.update_settings(KEY_URL_METHOD, url_method)

    def on_url_destination_changed(self, entry, _):
        url_destination = entry.get_text()
        self.update_settings(KEY_URL_DESTINATION, url_destination)

    def on_url_username_var_changed(self, entry, _):
        url_username_var = entry.get_text()
        self.update_settings(KEY_URL_USERNAME_VAR, url_username_var)

    def on_url_message_var_changed(self, entry, _):
        url_message_var = entry.get_text()
        self.update_settings(KEY_URL_MESSAGE_VAR, url_message_var)

    def send_to_url(self):
        http = urllib3.PoolManager()

        settings = self.get_settings()

        url_method = settings.get(KEY_URL_METHOD, DEFAULT_URL_METHOD)
        url_destination = settings.get(KEY_URL_DESTINATION, DEFAULT_URL_DESTINATION)
        url_username_var = settings.get(KEY_URL_USERNAME_VAR, DEFAULT_URL_USERNAME_VAR)
        url_message_var = settings.get(KEY_URL_MESSAGE_VAR, DEFAULT_URL_MESSAGE_VAR)

        null = http.request(
            url_method,
            url_destination,
            fields={
                url_username_var: self.messages[self.message_no].username,
                url_message_var: self.messages[self.message_no].message,
            },
        )
