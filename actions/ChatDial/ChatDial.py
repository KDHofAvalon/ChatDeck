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


class ChatDial(ChatReadBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def event_callback(self, event: InputEvent, data: dict = None):
        match event:
            case Input.Dial.Events.SHORT_UP:
                self.on_dial_down()
            case Input.Dial.Events.TURN_CW:
                self.on_dial_turn("cw")
            case Input.Dial.Events.TURN_CCW:
                self.on_dial_turn("ccw")

    def on_dial_turn(self, direction: str):
        match direction:
            case "cw":
                self.show_next_message()
            case "ccw":
                self.show_prev_message()

    def on_dial_down(self):
        self.send_to_url()
