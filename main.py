import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import sqlite3
from dotenv import load_dotenv
from model import *

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
    model = Models()
    model.create_table()
    await load()
    await bot.start(DC_TOKEN)

asyncio.run(main(),debug=True)
#############################################################################################
