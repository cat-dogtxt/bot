import discord
from discord.ext import commands
import sys
sys.path.insert(0,"..")
from model import *

class Base(commands.Cog):
    def __init__(self,bot,p_lang=""):
        self.bot = bot
        self.p_lang = p_lang
        self.db = Models()

    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        if guild.id == 768189401213304892:
            channel = self.bot.get_channel(1043220744185847811)
            msgs = [msg async for msg in channel.history(limit=100)]
            langs = {
                "<:swift:1042181807531102378>":"Swift",        
                "<:cpp:1042181794012872864>":"C++",
                "<:css3:1042181795501854811>":"CSS",
                "<:dotnet:1042181466685186118>":".NET",
                "<:go:1042181802959314955>":"GO",
                "<:html5:1042181804444102728>":"HTML",
                "<:java:1042181469604434002>":"JAVA",
                "<:linux:1042181800853766215>":"LINUX",
                "<:nodejs:1042181798500769892>":"NODEJS",
                "<:php:1042181475627434054>":"PHP",
                "<:python:1042181465020039300>":"PYTHON",
                "<:ruby:1042181468086079508>":"RUBY",
                "<:typesc:1042181471147925554>":"TYPESCRIPT",
                "<:js:1043963837919002775>":"JAVASCRIPT",
                "<:objc:1043965823963889744>":"C",
                "<:csharp:1043965055055712329>":"C#"
            }
            if not msgs:
                _message = '\n'.join('-->'.join((key,val)) for (key,val) in langs.items())
                self.p_lang = await channel.send(_message)
            else:
                self.p_lang = msgs[-1]
                print(msgs[-1].id)
            for emoji in langs:
                await self.p_lang.add_reaction(emoji)
        print("BOT IS ONLINE") 

    # @commands.Cog.listener()
    # async def on_member_join(member):
    #     channel = member.guild.system_channel
    #     await channel.send(f"{member.mention} Sunucuya hoşgeldin! Bota özelden öğrenci belgeni(.pdf) veya düzgün çekilmiş öğrenci kartını yolla kaydın tamamlansın!")


    # @commands.Cog.listener()
    # async def on_member_remove(member):
    #     channel = member.guild.system_channel
    #     await channel.send(f"{member.mention} okulu bıraktı sanırım:)) Hayatında başarılar!!")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):
        if payload.message_id == self.p_lang.id:
            guild = self.bot.get_guild(payload.guild_id)
            langs = {
                "cpp":"C++",
                "python":"PYTHON",
                "java":"JAVA",
                "csharp":"C#",
                "html5":"HTML",
                "css3":"CSS",
                "php":"PHP",
                "ruby":"RUBY",
                "js":"JAVASCRIPT",
                "cbasic":"C",
                "swift":"SWIFT",
                "go":"GO",
                "nodejs":"NODEJS",
                "typesc":"TYPESCRIPT",
                "linux":"LINUX",
            }
            if payload.emoji.name in langs:
                role = discord.utils.get(guild.roles,name=langs[payload.emoji.name])
                await payload.member.add_roles(role)
                self.db.add_language(payload.member.id,role.id)
                print(f"{payload.member} added {role}")
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self,payload):
        
        if payload.message_id == self.p_lang.id:
            guild = self.bot.get_guild(payload.guild_id)
            member = discord.utils.get(guild.members,id=payload.user_id)
            langs = {
                "cpp":"C++",
                "python":"PYTHON",
                "java":"JAVA",
                "csharp":"C#",
                "html5":"HTML",
                "css3":"CSS",
                "php":"PHP",
                "ruby":"RUBY",
                "js":"JAVASCRIPT",
                "cbasic":"C",
                "swift":"SWIFT",
                "go":"GO",
                "nodejs":"NODEJS",
                "typesc":"TYPESCRIPT",
                "linux":"LINUX",
            }
            if payload.emoji.name in langs:
                role = discord.utils.get(guild.roles,name=langs[payload.emoji.name])
                await member.remove_roles(role)
                self.db.remove_language(payload.member.id,role.id)
async def setup(bot):
    await bot.add_cog(Base(bot))