# Import our custom code
from plugins.com_LanaTheRaven_ChatDeck.ChatDeckBase import ChatReadBase

# Import StreamController modules
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.DeckManagement.InputIdentifier import Input, InputEvent

# Import log functionality
from loguru import logger as log

# Import gtk modules - used for the config rows
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw


class ChatKeys(ChatReadBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def event_callback(self, event: InputEvent, data: dict = None):
        match event:
            case Input.Key.Events.SHORT_UP:
                self.on_key_down()
            case Input.Key.Events.HOLD_STOP:
                self.on_key_hold()

    def on_key_down(self):
        if self.message_no > -1:
            if self.message_no == min(self.messages.keys()):
                self.message_no = max(self.messages.keys()) + 1
        self.show_prev_message()

    def on_key_hold(self):
        self.send_to_url()
