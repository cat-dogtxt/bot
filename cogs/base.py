import discord
from discord.ext import commands


class Base(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("BOT IS ONLINE") 

    @commands.Cog.listener()
    async def on_member_join(member):
        channel = member.guild.system_channel
        await channel.send(f"{member.mention} Sunucuya hoşgeldin! Bota özelden öğrenci belgeni(.pdf) veya düzgün çekilmiş öğrenci kartını yolla kaydın tamamlansın!")


    @commands.Cog.listener()
    async def on_member_remove(member):
        channel = member.guild.system_channel
        await channel.send(f"{member.mention} okulu bıraktı sanırım:)) Hayatında başarılar!!")

async def setup(bot):
    await bot.add_cog(Base(bot))