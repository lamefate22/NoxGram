from telethon.events.common import EventBuilder
from telethon.errors import FloodWaitError
from src.infrastructure.logger import log
from typing import Callable, Coroutine
from telethon import TelegramClient
from abc import ABC, abstractmethod
from pathlib import Path
import asyncio


class NoxBot(ABC):
    """The abstract base class of bots allows you to inherit from it and expand its functionality."""
    def __init__(self, name: str, client: TelegramClient):
        self.name = name
        self.client = client
        self._is_running = False
        self._registered_handlers = []
        log.info(f"initialized custom bot {name} successfully")

    @abstractmethod
    async def register_handlers(self) -> None:
        """
        This method must be implemented in a specific bot.
        Example: self.add_handler(self.my_message_handler, events.NewMessage(incoming=True))
        """
        pass

    def add_handler(self, handler: Callable[..., Coroutine], event: EventBuilder) -> None:
        """Auxiliary method for adding and tracking event handlers for this instance of the bot."""
        self.client.add_event_handler(handler, event)
        self._registered_handlers.append((handler, event))
        log.debug(f"bot {self.name}: registered handler {handler.__name__} with event {event.__class__.__name__}")

    async def start(self) -> None:
        """
        Launches the bot.
        This method registers the handlers and sets the status is "running". It does not block execution.
        """
        if self._is_running:
            log.warning(f"bot {self.name} is already running")
            return

        log.info(f"starting bot {self.name}...")
        await self.register_handlers()

        if not self._registered_handlers:
            log.warning(f"bot {self.name} has no registered handlers")

        self._is_running = True
        log.info(f"bot {self.name} is now running")

    async def stop(self) -> None:
        """Stops the bot by deleting all the handlers registered by it."""
        if not self._is_running:
            log.warning(f"bot {self.name} is not started yet")
            return

        log.info(f"stopping bot {self.name}...")
        for handler, event in self._registered_handlers:
            self.client.remove_event_handler(handler, event)

        self._registered_handlers.clear()
        self._is_running = False
        log.info(f"bot {self.name} is now stopped")

    async def send_message(self, chat_id: int, message: str, delay: float = 0) -> None:
        """
        A reliable auxiliary method for sending a message with an optional delay.

        :param chat_id: where to send the message
        :param message: text to send
        :param delay: delay in seconds before sending the message
        """
        try:
            if delay > 0:
                await asyncio.sleep(delay)
            await self.client.send_message(chat_id, message)
        except FloodWaitError as e:
            log.warning(f"FloodWaitError: bot {self.name} sleeping for {e.seconds * 1.5} seconds")
            await asyncio.sleep(e.seconds * 1.5)

    async def send_image(self, chat_id: int, caption: str, image: Path, delay: float = 0) -> None:
        """
        A reliable auxiliary method for sending a image with an optional delay.
        :param chat_id: where to send the message
        :param caption: text to send
        :param image: photo to send
        :param delay: delay in seconds before sending the image
        """
        try:
            if delay > 0:
                await asyncio.sleep(delay)
            await self.client.send_file(chat_id, str(image), caption=caption)
        except FloodWaitError as e:
            log.warning(f"FloodWaitError: bot {self.name} sleeping for {e.seconds * 1.5} seconds")
            await asyncio.sleep(e.seconds * 1.5)
