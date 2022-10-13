import discord
import datetime
from discord.ext import commands
#sql
import sqlite3
class User(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot = bot

    @commands.command()
    async def kayit(self,ctx):
        db = sqlite3.connect("db.sqlite3")
        cursor = db.cursor()
        cursor.execute(f"SELECT user_id FROM main WHERE user_id = {ctx.author.id}")
        result = cursor.fetchone()
        if result is None:
            sql = (f'''
                INSERT INTO main(user_id,signDate,takeDate) VALUES(?,?,?)
            ''')
            val = (ctx.author.id,datetime.datetime.now(),datetime.datetime.now())
            cursor.execute(sql,val)
            await ctx.send(f"Kayıt yapıldı.{ctx.author.id}")
            sql1 = (f'''
                INSERT INTO exp(user_id,exp,level,amount) VALUES(?,?,?,?)
            ''')
            val = (ctx.author.id,100,0,100)
            cursor.execute(sql1,val)
            await ctx.send(f"Expler yüklendi.{ctx.author.id}")
            db.commit()
        else:
            await ctx.send(f"Zaten kayıtlısın id:{ctx.author.id}")
        cursor.close()
        
    @commands.command()
    async def goruntule(self,ctx:commands.Context,member:discord.Member=None):
        if member == None:
            member = ctx.author
        name = member.display_name
        pfp = member.display_avatar
        
        db = sqlite3.connect("db.sqlite3")
        cursor = db.cursor()
        cursor.execute(f"SELECT exp,level,amount FROM exp WHERE user_id = {member.id}")
        result = cursor.fetchone()
        print(result)
        print(member.id)
        exp,level,amount = result
        if result is None:
            await ctx.send("Böyle bir kullanıcı yok")
        else:
            embed = discord.Embed(title="Üye bilgi", description="Üye",colour=discord.Colour.random())
            #embed.set_image(url=pfp)
            embed.set_author(name=f"{name}",icon_url=pfp)
            embed.add_field(name="Exp",value=f"{exp}")
            embed.add_field(name="Level",value=f"{level}",inline=True)
            embed.add_field(name="Amount",value=f"{amount}",inline=False)
            embed.set_footer(text=f"{name} Made this banner")
            
            await ctx.send(embed=embed)
    



async def setup(bot):
    await bot.add_cog(User(bot))
