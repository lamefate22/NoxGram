from src.infrastructure.config import NoxConfig
from src.infrastructure.loader import BotLoader
from src.infrastructure.logger import log
from src.ui.console import NoxConsole
from src.core.auth import NoxAuth
from src.core.exceptions import *
import nest_asyncio
import asyncio

nest_asyncio.apply()


async def main(config: NoxConfig, console: NoxConsole) -> None:
    client = NoxAuth(config=config, console=console)
    client = await client.login()

    instance = None
    loader = BotLoader()
    try:
        bots = loader.search_bots()
        bot_choices = {cls["class_name"]: cls for cls in bots}
        selected_bot_name = console.ask_select("Select one of the available bots", choices=list(bot_choices.keys()))

        if selected_bot_name:
            selected_bot_info = bot_choices[selected_bot_name]
            imported_bot = loader.import_bot(selected_bot_info)

            if imported_bot:
                instance = imported_bot(client=client, name=selected_bot_info["class_name"])
            await instance.start()
            await client.run_until_disconnected()
    except (AuthError, CryptoError, ConfigError) as e:
        log.exception(f"custom NoxGram exception occured: {e}")
    except KeyboardInterrupt:
        console.qprint("Goodbye")
    finally:
        if instance and instance._is_running:
            await instance.stop()
        await client.disconnect()


if __name__ == "__main__":
    nconfig = NoxConfig()
    nconsole = NoxConsole()
    asyncio.run(main(config=nconfig, console=nconsole))
