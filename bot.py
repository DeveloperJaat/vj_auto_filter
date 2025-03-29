# Don't Remove Credit @Tonystark_botz
# Ask Doubt on telegram @Spider_Man_02

import sys, glob, importlib, logging, logging.config, pytz, asyncio
from pathlib import Path

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

from pyrogram import Client, idle 
from database.ia_filterdb import Media, Media2, choose_mediaDB, db as clientDB
from database.users_chats_db import db
from info import *
from utils import temp
from typing import Union, Optional, AsyncGenerator
from Script import script 
from datetime import date, datetime 
from aiohttp import web
from sample_info import tempDict
from plugins import web_server

from Naman.bot import NamanBot
from Naman.util.keepalive import ping_server
from Naman.bot.clients import initialize_clients

ppath = "plugins/*.py"
files = glob.glob(ppath)
NamanBot.start()

async def start():
    print('\n')
    print('Initalizing Your Bot')
    bot_info = await NamanBot.get_me()
    await initialize_clients()
    
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("Naman Imported => " + plugin_name)

    if ON_HEROKU:
        asyncio.create_task(ping_server())

    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats

    await Media.ensure_indexes()
    await Media2.ensure_indexes()

    # Choose the right DB by checking the free space
    stats = await clientDB.command('dbStats')
    free_dbSize = round(512 - ((stats['dataSize']/(1024*1024)) + (stats['indexSize']/(1024*1024))), 2)

    if SECONDDB_URI and free_dbSize < 10:
        tempDict["indexDB"] = SECONDDB_URI
        logging.info(f"Primary DB has only {free_dbSize} MB left, using Secondary DB.")
    elif SECONDDB_URI is None:
        logging.error("Missing SECONDDB_URI! Add it now. Exiting...")
        exit()
    else:
        logging.info(f"Primary DB has enough space ({free_dbSize} MB), using it.")

    await choose_mediaDB()

    me = await NamanBot.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name

    logging.info(LOG_STR)
    logging.info(script.LOGO)

    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")

    await NamanBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(temp.U_NAME, temp.B_NAME, today, time))

    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    
    await idle()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start())
