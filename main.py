# Import StreamController modules
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport

# Import logging
from loguru import logger as log

# Import actions
from .actions.ChatDial.ChatDial import ChatDial
from .actions.ChatKeys.ChatKeys import ChatKeys

# Import system libraries
import os

# Import GTK
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw


# Import our settings
from .settings import (
    PluginSettings,
    KEY_APP_ID,
    DEFAULT_APP_ID,
    KEY_APP_SECRET,
    DEFAULT_APP_SECRET,
    KEY_TARGET_CHANNEL,
    DEFAULT_TARGET_CHANNEL,
    KEY_IGNORED_USERS,
    DEFAULT_IGNORED_USERS,
    KEY_MAX_MESSAGES,
    DEFAULT_MAX_MESSAGES,
)


class ChatDeck(PluginBase):
    def __init__(self):
        super().__init__()
        self.lm = self.locale_manager
        self.lm.set_to_os_default()

        # Initialize settings
        self._settings_manager = PluginSettings(self)
        self.has_plugin_settings = False

        # Start backend, if already authenticated
        if os.path.exists(
            self.settings_path.replace("settings.json", "twitch_auth.json")
        ):
            self._setup_backend()

        # Register actions
        self.chat_dial_holder = ActionHolder(
            plugin_base=self,
            action_base=ChatDial,
            action_id="com_LanaTheRaven_ChatDeck::ChatDial",
            action_name="Chat Dial",
            action_support={
                Input.Key: ActionInputSupport.UNSUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED,
            },
        )
        self.add_action_holder(self.chat_dial_holder)

        self.chat_keys_holder = ActionHolder(
            plugin_base=self,
            action_base=ChatKeys,
            action_id="com_LanaTheRaven_ChatDeck::ChatKeys",
            action_name="Chat Keys",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNSUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED,
            },
        )
        self.add_action_holder(self.chat_keys_holder)

        # Register plugin
        self.register(
            plugin_name="ChatDeck",
            github_repo="https://github.com/KDHofAvalon/ChatDeck",
            plugin_version="0.1.0",
            app_version="1.5.0-beta.14",
        )

    def _setup_backend(self) -> bool:
        # Launch backend_ChatReader
        backend_path = os.path.join(self.PATH, "backend", "backend_ChatReader.py")
        self.launch_backend(
            backend_path=backend_path,
            open_in_terminal=False,
            venv_path=os.path.join(self.PATH, "backend", ".venv"),
        )

    def auth_callback(self):
        if not os.path.exists(
            self.settings_path.replace("settings.json", "twitch_auth.json")
        ):
            # Launch backend only after supplying initial settings
            self._setup_backend()
        else:
            # Tell backend to update settings
            self.backend.auth_updated("frontend")

    def settings_callback(self):
        self.backend.settings_updated()

    def get_settings_area(self):
        return self._settings_manager.get_settings_area()
