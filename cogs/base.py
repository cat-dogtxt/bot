import discord
from discord.ext import commands
import sys
sys.path.insert(0,"..")
from model import *

class Base(commands.Cog):
    def __init__(self,bot,p_lang="",p_kayit=None):
        self.bot = bot
        self.p_kayit = p_kayit
        self.p_lang = p_lang
        self.db = Models()
        print("BOT IS ONLINE") 

    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        if guild.id == 1018645651241836544:
            a = 0
            for channel in guild.channels:
                if channel.name == "kayit-ol":
                    print("Kayıt ol kanalı var.")
                    messages1 = [msg async for msg in channel.history(limit=5)]
                    self.p_kayit = messages1[-1]
                    print(self.p_kayit)
                    a+=1
                if channel.name == "programming-languages":
                    print("Programming languages kanalı var.")
                    messages2 = [msg async for msg in channel.history(limit=5)]
                    self.p_lang = messages2[-1]
                    print(self.p_lang)
                    a+=1
                    if a == 2:
                        break
            else:
                category = await guild.create_category("KAYIT")
                kayit_channel = await guild.create_text_channel("kayit-ol",category=category)
                lang_channel = await guild.create_text_channel("programming-languages",category=category)
                self.p_kayit = await kayit_channel.send("Kayıt olmak için emojiye tıklayın.")
                await self.p_kayit.add_reaction("✅")
                print("Kayit ol kanalı oluşturuldu")
                channel = lang_channel
                #channel = self.bot.get_channel(1043220744185847811)
                msgs = [msg async for msg in channel.history(limit=100)]
                langs = {
                    "<:swift:1042181807531102378>":"SWIFT",        
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

    @commands.Cog.listener()
    async def on_member_join(self,member):
        print(f"{member} has joined a server.")
        await member.send("Kayıt olmak için öğrenci belgenizi yollayınız!\n E-devlet üzerinden alacağınız öğrenci belgenizi buraya atarak veya düzgün bir şekilde çekilmiş öğrenci kartınızın fotoğrafını buraya atınız.")

    # @commands.Cog.listener()
    # async def on_member_remove(member):
    #     channel = member.guild.system_channel
    #     await channel.send(f"{member.mention} okulu bıraktı sanırım:)) Hayatında başarılar!!")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):
        if payload.message_id == self.p_kayit.id:
            member = self.bot.get_user(payload.user_id)
            print(member)
            await member.send("Kayıt olmak için öğrenci belgenizi yollayınız!\n E-devlet üzerinden alacağınız öğrenci belgenizi buraya atarak veya düzgün bir şekilde çekilmiş öğrenci kartınızın fotoğrafını buraya atınız.")
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