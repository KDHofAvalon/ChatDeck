import gi
import sys
import os

from loguru import logger as log

from src.backend.PluginManager import PluginBase

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw


KEY_APP_ID = "app_id"
DEFAULT_APP_ID = ""

KEY_APP_SECRET = "app_secret"
DEFAULT_APP_SECRET = ""

KEY_TARGET_CHANNEL = "target_channel"
DEFAULT_TARGET_CHANNEL = ""

KEY_IGNORED_USERS = "ignored_users"
DEFAULT_IGNORED_USERS = []

KEY_MAX_MESSAGES = "max_messages"
DEFAULT_MAX_MESSAGES = 10  # count


class PluginSettings:
    def __init__(self, plugin_base: PluginBase.PluginBase):
        self._plugin_base = plugin_base
        self._settings_cache = None

    def get_settings_area(self) -> Adw.PreferencesGroup:
        self._app_id_entry = Adw.EntryRow(
            title=self._plugin_base.lm.get("settings.app-id.label"),
        )

        self._app_secret_entry = Adw.PasswordEntryRow(
            title=self._plugin_base.lm.get("settings.app-secret.label"),
        )

        self._target_channel_entry = Adw.EntryRow(
            title=self._plugin_base.lm.get("settings.target-channel.label"),
        )

        self._auth_to_twitch = Gtk.Button(
            label=self._plugin_base.lm.get("settings.twitch-auth.label")
        )
        self._auth_to_twitch.set_margin_top(12)
        self._auth_to_twitch.set_margin_bottom(12)

        self._ignored_users_entry = Adw.EntryRow(
            title=self._plugin_base.lm.get("settings.ignored-users.label"),
        )

        self._max_messages_adjustment = Gtk.Adjustment(
            value=DEFAULT_MAX_MESSAGES,
            lower=5,
            upper=250,
            step_increment=1,
            page_increment=10,
        )
        self._max_messages_spin = Adw.SpinRow(
            adjustment=self._max_messages_adjustment,
            title=self._plugin_base.lm.get("settings.max-messages.label"),
            subtitle=self._plugin_base.lm.get("settings.max-messages.subtitle"),
        )

        self._app_id_entry.connect("notify::text", self._on_change_app_id)
        self._app_secret_entry.connect("notify::text", self._on_change_app_secret)
        self._target_channel_entry.connect(
            "notify::text", self._on_change_target_channel
        )
        self._auth_to_twitch.connect("clicked", self._on_auth_clicked)
        self._ignored_users_entry.connect("notify::text", self._on_change_ignored_users)
        self._max_messages_spin.connect("notify::value", self._on_change_max_messages)

        self._load_settings()
        self._enable_auth()

        pref_group = Adw.PreferencesGroup()
        pref_group.set_title(self._plugin_base.lm.get("settings.title"))
        pref_group.add(self._app_id_entry)
        pref_group.add(self._app_secret_entry)
        pref_group.add(self._target_channel_entry)
        pref_group.add(self._auth_to_twitch)
        pref_group.add(self._ignored_users_entry)
        pref_group.add(self._max_messages_spin)
        return pref_group

    def _get_cached_settings(self):
        if self._settings_cache is None:
            self._settings_cache = self._plugin_base.get_settings()
        return self._settings_cache

    def _invalidate_cache(self):
        self._settings_cache = None

    def _load_settings(self):
        settings = self._get_cached_settings()
        app_id = str(settings.get(KEY_APP_ID, DEFAULT_APP_ID))
        app_secret = str(settings.get(KEY_APP_SECRET, DEFAULT_APP_SECRET))
        target_channel = str(settings.get(KEY_TARGET_CHANNEL, DEFAULT_TARGET_CHANNEL))
        ignored_users = list(settings.get(KEY_IGNORED_USERS, DEFAULT_IGNORED_USERS))
        max_messages = int(settings.get(KEY_MAX_MESSAGES, DEFAULT_MAX_MESSAGES))

        self._app_id_entry.set_text(app_id)
        self._app_secret_entry.set_text(app_secret)
        self._target_channel_entry.set_text(target_channel)
        self._ignored_users_entry.set_text(str(", ".join(ignored_users)))
        self._max_messages_spin.set_value(max_messages)

    def _update_settings(self, key: str, value):
        settings = self._get_cached_settings()
        settings[key] = value
        self._plugin_base.set_settings(settings)
        self._invalidate_cache()

    def _on_change_app_id(self, entry, _):
        ident = str(entry.get_text())
        self._update_settings(KEY_APP_ID, ident)
        self._enable_auth()

    def _on_change_app_secret(self, entry, _):
        secret = str(entry.get_text())
        self._update_settings(KEY_APP_SECRET, secret)
        self._enable_auth()

    def _on_change_target_channel(self, entry, _):
        channel = str(entry.get_text())
        self._update_settings(KEY_TARGET_CHANNEL, channel)
        self._enable_auth()

    def _on_auth_clicked(self, _):
        self._plugin_base.auth_callback()

    def _on_change_ignored_users(self, entry, _):
        rawusers = str(entry.get_text())
        users = []
        for item in rawusers.split(","):
            users.append(item.strip())
        self._update_settings(KEY_IGNORED_USERS, users)
        self._plugin_base.settings_callback()

    def _on_change_max_messages(self, spin, _):
        maximum = int(spin.get_value())
        self._update_settings(KEY_MAX_MESSAGES, maximum)
        self._plugin_base.settings_callback()

    def _enable_auth(self):
        settings = self._plugin_base.get_settings()
        app_id = settings.get(KEY_APP_ID, DEFAULT_APP_ID)
        app_secret = settings.get(KEY_APP_SECRET, DEFAULT_APP_SECRET)
        target_channel = settings.get(KEY_TARGET_CHANNEL, DEFAULT_TARGET_CHANNEL)
        self._auth_to_twitch.set_sensitive(
            len(app_id) > 0 and len(app_secret) > 0 and len(target_channel) > 0
        )

    def get_app_id(self) -> str:
        self._get_cached_settings()
        return str(settings.get(KEY_APP_ID, DEFAULT_APP_ID))

    def get_app_secret(self) -> str:
        self._get_cached_settings()
        return str(settings.get(KEY_APP_SECRET, DEFAULT_APP_SECRET))

    def get_target_channel(self) -> str:
        self._get_cached_settings()
        return str(settings.get(KEY_TARGET_CHANNEL, DEFAULT_TARGET_CHANNEL))

    def get_ignored_users(self) -> list:
        self._get_cached_settings()
        return list(settings.get(KEY_IGNORED_USERS, DEFAULT_IGNORED_USERS))

    def get_max_messages(self) -> int:
        self._get_cached_settings()
        return int(settings.get(KEY_MAX_MESSAGES, DEFAULT_MAX_MESSAGES))