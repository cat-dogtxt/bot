from this import d
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()
DC_TOKEN = os.getenv("DC_TOKEN")
guilded = discord.Object(id=1023737742259146772)
bot = commands.Bot(command_prefix="%",intents=discord.Intents.all())

#LOAD
async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    db = sqlite3.connect('db.sqlite3')
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS main(
            user_id TEXT NOT NULL PRIMARY KEY,
            signDate DATETIME,
            takeDate DATETIME
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exp(
        user_id INTEGER PRIMARY KEY,
        exp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 0,
        amount INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks(
        task_id INTEGER PRIMARY KEY NOT NULL,
        task_encrpted TEXT NOT NULL,
        completed_user_id INTEGER DEFAULT O,
        task TEXT,
        zorluk INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls(
        user_id INTEGER PRIMARY KEY,
        leetcode TEXT DEFAULT NULL,
        github TEXT DEFAULT NULL
        )
    ''')
    print("database created and online")
    await load()
    await bot.start(DC_TOKEN)

asyncio.run(main())
#############################################################################################