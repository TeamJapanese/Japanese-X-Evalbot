import asyncio
import importlib

from pyrogram import idle
from Japanese.modules import ALL_MODULES


async def evalbot():
    for all_module in ALL_MODULES:
        importlib.import_module(f"Japanese.modules.{all_module}")
    
    LOGGER.info(f"Successfully loaded {len(ALL_MODULES)} Modules.")
    LOGGER.info("Bot Started G!")
    
    await idle()

    try:
        app.stop()
        
    except Exception as e:
        LOGGER.error(f"Error while stopping apps: {e}")
    
    LOGGER.info("Stopping! Goodbye")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(market())
