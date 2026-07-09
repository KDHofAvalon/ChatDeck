# Import Twitch APIs
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand

# Import StreamController Backend functionality
from streamcontroller_plugin_tools import BackendBase

# Import asyncio functionality
import asyncio

# Import os functions
import os

# Import logger
from loguru import logger as log

# Import constants
from backend_ChatReader_CONSTANTS import (
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

app_id: str = ""
app_secret: str = ""
user_scope = [AuthScope.CHAT_READ]
target_channel: str = ""
ignored_users: list = []
messages: dict = {}
max_messages: int = 10


class BackendChatReader(BackendBase):
    def __init__(self):
        super().__init__()

        self.is_ready: bool = False
        self.auth_changed: bool = False

        self.auth_path = self.frontend.settings_path.replace(
            "settings.json", "twitch_auth.json"
        )

    def get_messages(self) -> dict:
        payload = messages
        return payload

    def set_app_id(self, ident: str):
        global app_id
        app_id = ident

    def set_app_secret(self, secret: str):
        global app_secret
        app_secret = secret

    def set_target_channel(self, channel: str):
        global target_channel
        target_channel = channel

    def set_ignored_users(self, users: list):
        global ignored_users
        ignored_users = users

    def set_max_messages(self, maximum: int):
        global max_messages
        current_messages = len(messages)
        while current_messages > maximum:
            del messages[min(messages.keys())]
            current_messages = len(messages)
        max_messages = maximum

    def auth_updated(self, caller: str):
        if caller == "backend":
            self.auth_changed = False
        elif caller == "frontend":
            self.auth_changed = True

    def settings_updated(self):
        settings = self.frontend.get_settings()
        iu = settings.get(KEY_IGNORED_USERS, DEFAULT_IGNORED_USERS)
        mm = settings.get(KEY_MAX_MESSAGES, DEFAULT_MAX_MESSAGES)

        if iu != ignored_users:
            self.set_ignored_users(iu)

        if mm != max_messages:
            self.set_max_messages(mm)

    def pull_settings(self, setup: bool = False):
        settings = self.frontend.get_settings()
        if setup:
            self.set_app_id(settings.get(KEY_APP_ID, DEFAULT_APP_ID))
            self.set_app_secret(settings.get(KEY_APP_SECRET, DEFAULT_APP_SECRET))
            self.set_target_channel(
                settings.get(KEY_TARGET_CHANNEL, DEFAULT_TARGET_CHANNEL)
            )
            self.set_ignored_users(
                settings.get(KEY_IGNORED_USERS, DEFAULT_IGNORED_USERS)
            )
            self.set_max_messages(settings.get(KEY_MAX_MESSAGES, DEFAULT_MAX_MESSAGES))
            if app_id != "" and app_secret != "" and target_channel != "":
                self.ready_state(True)
        else:
            return settings

    def ready_state(self, ready: bool):
        self.is_ready = ready

    def stop_reader(self):
        print("Unimplemented")


class ChatMessageData:
    def __init__(self, username="", message=""):
        self.username = username
        self.message = message

    def set_data(self, username: str, message: str):
        self.username = username
        self.message = message

    def set_user(self, username: str):
        self.username = username

    def set_message(self, message: str):
        self.message = message


# Triggers when the reader starts, causes channel join
async def on_ready(ready_event: EventData):
    await ready_event.chat.join_room(target_channel)


# Add all new chat messages to the messages dictionary
async def on_message(msg: ChatMessage):
    # Don't add messages from certain users/bots to the dictionary
    for user in ignored_users:
        if msg.user.name == user:
            return

    # Sub-function to find the next message key
    def get_message_no(msg_keys: list):
        try:
            max(msg_keys)
        except Exception as e:
            log.error(e)
            return 0
        return max(msg_keys) + 1

    # Extract useful content from message
    message = ChatMessageData(username=msg.user.name, message=msg.text)

    # Set the next message key to the current key plus one
    message_no = get_message_no(messages.keys())

    # Add the latest message to the dictionary of messages
    messages.update({message_no: message})

    # Delete oldest message after we reach a certain size
    if len(messages) > max_messages:
        del messages[min(messages.keys())]


async def chat_reader():
    # Sub function to handle re-auth
    def reauthorize_twitch():
        settings = backend.pull_settings(False)

        backend.set_app_id(settings.get(KEY_APP_ID, DEFAULT_APP_ID))
        backend.set_app_secret(settings.get(KEY_APP_SECRET, DEFAULT_APP_SECRET))
        backend.set_target_channel(
            settings.get(KEY_TARGET_CHANNEL, DEFAULT_TARGET_CHANNEL)
        )
        backend.auth_updated("backend")

    # Auth with Twitch in user browser if id and secret are not blank
    # try:
    twitch = await Twitch(app_id, app_secret)
    auth = UserAuthenticationStorageHelper(twitch, user_scope, backend.auth_path)
    await auth.bind()
    # except Exception as e:
    #     log.error(e)
    #     print("Something went wrong with Twitch connection")
    #     # Tell frontend we aren't authenticated
    #     # TODO: implement frontend callback function
    #     backend.ready_state(False)

    # create an instance of the chat object
    chat = await Chat(twitch)

    # below are the event handlers

    # Waits for the chat to be ready
    chat.register_event(ChatEvent.READY, on_ready)

    # Waits for messages
    chat.register_event(ChatEvent.MESSAGE, on_message)

    # Start the chat reader
    chat.start()

    if backend.auth_changed:
        chat.stop()
        await twitch.close
        reauthorize_twitch()


backend = BackendChatReader()

backend.pull_settings(True)

while not backend.is_ready:
    pass


asyncio.run(chat_reader())
