# NoxGram: Your Modular & Secure Telegram Automation Client

![NoxGram](https://img.shields.io/badge/NoxGram-Telegram_Automation-blue?style=for-the-badge&logo=telegram)

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: GNU GPL v3](https://img.shields.io/badge/License-GNU_GPL_v3-orange.svg)](https://www.gnu.org/licenses/gpl-3.0)

NoxGram is a powerful, command-line based Telegram client designed for automation and extensibility. It allows you to run custom, event-driven "bots" using your own user account, all managed through a secure, interactive CLI.

## Key Features

- **🔒 Secure Session Management**: Your session is not stored in a plain text file. It's encrypted using PBKDF2-derived keys and Fernet symmetric encryption, requiring a password on each login for maximum security.
- **🔌 Modular & Extensible**: Easily add new functionalities by creating your own "bot" classes. NoxGram's `BotLoader` dynamically and safely discovers and loads your custom scripts from the `data/bots` directory.
- **👥 Multi-Account Support**: The configuration is designed to manage multiple Telegram accounts, allowing you to switch between them effortlessly.
- **🛠️ Built-in Helpers**: The `NoxBot` base class provides convenient methods, with built-in handling for Telegram's FloodWait errors.
- **🤖 Interactive CLI**: A polished command-line interface, powered by `questionary`, guides you through login and bot selection.
- **⚡ Fully Asynchronous**: Built on `asyncio` and `telethon`, ensuring high performance and non-blocking operations.

## Architecture Overview

NoxGram is built with a clean and decoupled architecture, making it easy to understand and extend.

- **`src/infrastructure`**: Manages supporting tasks like configuration, logging, and the dynamic bot loading mechanism.
- **`src/core`**: Contains the core business logic, including authentication, encryption, validation models.
- **`src/ui`**: Handles all user interactions via the command line interface and validates input.
- **`data/`**: The default directory for storing configuration, logs, custom bots.

## Getting Started

### Prerequisites

- Python 3.11+
- A Telegram account with **API_ID** and **API_HASH**. You can get these from [my.telegram.org](https://my.telegram.org).

### Installation

1.  **Clone the NoxGram repository:**
    ```bash
    git clone https://github.com/lamefate22/NoxGram.git
    cd NoxGram
    ```
2. **Use a virtual environment:**
   - Linux:
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```
   - Windows:
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
3. **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

Using a virtual environment is not required, but is **highly recommended** to avoid affecting globally installed packages.

## How to Use

1.  **Run the application:**
    ```bash
    python nox.py
    ```
2.  **First-time Login:**
    - The application will ask if you want to use auto-login. Select `No` for the first time.
    - Enter account phone number, `API_ID`, and `API_HASH`.
    - Enter the authorization confirmation code.
    - Enter 2FA account password if required.
    - Enter new encryption password.
3.  **Automatic Login:**
    - When you launch the application, select "Yes" when asked about automatic login.
    - Select the desired saved account and enter the encryption password.
4.  **Select a Bot:**
    - After a successful login, NoxGram will display a list of all available bots found in the `data/bots` directory.
    - Select the bot you want to run. The bot will start and begin listening for Telegram events.

This password is used to secure your session file and will be required every time you log in with this account.

## Creating Your Own Bot

The real power of NoxGram lies in its extensibility. You can create a bot for almost any automated task.

1.  **Create a Python file** in the `data/bots` directory (e.g., `data/bots/example.py`).
2.  **Inherit from `NoxBot`** and implement the `register_handlers` method.
3.  **Run NoxGram**.

Here is a simple example of a bot that replies "Hello!" to any incoming message.

**`data/bots/echo.py`**
```python
from src.core.base import NoxBot
from telethon import events

# the class name can be anything you like
class EchoBot(NoxBot):
    """
    An example bot that listens for new messages and replies with "Hello!".
    """
    async def register_handlers(self) -> None:
        """
        This is where you register your event handlers.
        """
        # the add_handler method is provided by the NoxBot base class
        self.add_handler(self.message_handler, events.NewMessage(incoming=True))

    async def message_handler(self, event: events.NewMessage.Event) -> None:
        """
        A handler for the NewMessage event.
        """
        message_text = f"Hello! You said: '{event.message.text}'"
        
        # use the built-in send_message helper
        await self.send_message(chat_id=event.chat_id, message=message_text)
```

## License

This project is licensed under the GNU License - see the [LICENSE](LICENSE) file for details.
