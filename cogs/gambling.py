import asyncio
import sqlite3
import discord
import datetime
from discord.ext import commands
from discord.utils import get


#sql
import random

class Gambling(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot = bot
    
    def coinflip_r(self):
        return random.randint(0, 1)

    @commands.command()
    async def slot(self,ctx:commands.Context,member:discord.Member=None):
        if member == None:
            member = ctx.author
        name = member.display_name
        pfp = member.display_avatar

        embed = discord.Embed(title="This is embed", description="Cool",colour=discord.Colour.random())
        embed.set_image(url=pfp)
        embed.set_author(name=f"{name}", url="https://www.google.com",icon_url=pfp)
        embed.add_field(name="⭐️1",value="Field 1 value")
        embed.add_field(name="⭐️2",value="Field 1 value inline True",inline=True)
        embed.add_field(name="⭐️3",value="Field 1 value inline False",inline=False)
        embed.set_footer(text=f"{name} Made this banner")
        
        await ctx.send(embed=embed)
    

    @commands.command()
    async def coinflip(self,ctx,money:int):
        cf = self.coinflip_r()
        amount = 100
        if cf:
            amount += money
        else:
            amount -= money     
        await ctx.send(f"{cf} -> {amount}")

    @commands.command()
    async def bj(self,ctx,amount):
        embed = discord.Embed(title="~leaderboard",description="Leaderboard görüntüleme komutları",colour=discord.Colour.random()) 
        embed.add_field(name="1.",value=f"<:2C:1032644926137188433>",inline=True)
        embed.add_field(name="2.",value=f"{amount}",inline=True)

        await ctx.send(embed=embed)
async def setup(bot):
    await bot.add_cog(Gambling(bot))
