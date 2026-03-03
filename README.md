# NoxGram: Your Modular & Secure Telegram Automation Client

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

NoxGram is a powerful, command-line based Telegram client designed for automation and extensibility. It allows you to run custom, event-driven "bots" using your own user account, all managed through a secure, interactive CLI.

## Key Features

- **🔒 Secure Session Management**: Your session is not stored in a plain text file. It's encrypted using PBKDF2-derived keys and Fernet symmetric encryption, requiring a password on each login for maximum security.
- **🔌 Modular & Extensible**: Easily add new functionalities by creating your own "bot" classes. NoxGram's `BotLoader` dynamically and safely discovers and loads your custom scripts from the `data/bots` directory.
- **🤖 Interactive CLI**: A polished command-line interface, powered by `questionary`, guides you through login and bot selection.
- **👥 Multi-Account Support**: The configuration is designed to manage multiple Telegram accounts, allowing you to switch between them effortlessly.
- **⚡ Fully Asynchronous**: Built on `asyncio` and `telethon`, ensuring high performance and non-blocking operations.
- **🛠️ Built-in Helpers**: The `NoxBot` base class provides convenient methods like `send_message` and `send_image`, with built-in handling for Telegram's FloodWait errors.

## Architecture Overview

NoxGram is built with a clean and decoupled architecture, making it easy to understand and extend.

- **`src/core`**: Contains the core business logic, including authentication, encryption, and the base `NoxBot` class.
- **`src/infrastructure`**: Manages supporting tasks like configuration, logging, and the dynamic bot loading mechanism.
- **`src/ui`**: Handles all user interaction through the command-line interface.
- **`data/`**: The default directory for storing configuration (`config.nox`), logs, and your custom bots.

## Getting Started

### Prerequisites

- Python 3.12+
- A Telegram account with **API_ID** and **API_HASH**. You can get these from [my.telegram.org](https://my.telegram.org).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://your-repository-url/NoxGram.git
    cd NoxGram
    ```
2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Use

1.  **Run the application:**
    ```bash
    python nox.py
    ```
2.  **First-time Login:**
    - The application will ask if you want to use auto-login. Select `No` for the first time.
    - You will be prompted to enter your phone number, `API_ID`, and `API_HASH`.
    - After receiving the confirmation code from Telegram, you will be asked to create an **encryption password**. This password is used to secure your session file and will be required every time you log in with this account.

3.  **Automatic Login:**
    - On subsequent runs, you can select `Yes` for auto-login.
    - Choose the account you wish to use and enter the corresponding encryption password.

4.  **Select a Bot:**
    - After a successful login, NoxGram will display a list of all available bots found in the `data/bots` directory.
    - Select the bot you want to run. The bot will start and begin listening for Telegram events.

## Creating Your Own Bot

The real power of NoxGram lies in its extensibility. You can create a bot for almost any automated task.

1.  **Create a Python file** in the `data/bots/` directory (e.g., `data/bots/my_awesome_bot.py`).

2.  **Inherit from `NoxBot`** and implement the `register_handlers` method.

Here is a simple example of a bot that replies "Hello!" to any incoming message.

**`data/bots/echo_bot.py`**
```python
from src.core.base import NoxBot
from telethon import events

# The class name can be anything you like
class EchoBot(NoxBot):
    """
    An example bot that listens for new messages and replies with "Hello!".
    """
    async def register_handlers(self) -> None:
        """
        This is where you register your event handlers.
        """
        # The add_handler method is provided by the NoxBot base class
        self.add_handler(self.message_handler, events.NewMessage(incoming=True))

    async def message_handler(self, event: events.NewMessage.Event) -> None:
        """
        A handler for the NewMessage event.
        """
        chat = await event.get_chat()
        message_text = f"Hello! You said: '{event.message.text}'"
        
        # Use the built-in send_message helper
        await self.send_message(chat_id=chat.id, message=message_text)
        
        # You can also use the client directly
        # await self.client.send_message(chat.id, message_text)

```

3.  **Run NoxGram**. Your new bot, `EchoBot`, will now appear in the selection list!

## Contributing

Contributions are welcome! If you have ideas for new features or improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the GNU License - see the [LICENSE](LICENSE) file for details.
