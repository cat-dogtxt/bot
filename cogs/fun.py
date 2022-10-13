from pydoc import describe
import discord 
from discord.ext import commands
import googletrans
import requests
from PIL import Image,ImageEnhance
from googletrans import Translator

class Fun(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command()
    async def mrinc(self,ctx,member:discord.Member=None):
        if member == None:
            member = ctx.author
        name = member.display_name
        pfp = member.display_avatar

        response = requests.get(pfp)
        file = open("image1.png","wb")
        file.write(response.content)
        file.close()

        im = Image.open("image1.png")

        enhancer = ImageEnhance.Contrast(im)

        factor = 4 #increase contrast
        im_output = enhancer.enhance(factor)
        im_output.save('mimage1.png')

        await ctx.send(file=discord.File('mimage1.png'))
    @commands.command(describe="Translate everything")
    async def translate(self,ctx:commands.Context,*kargs):
        translator = Translator()
        end_sent = translator.translate(text=' '.join(kargs),src="tr",dest="en")
        print(end_sent.text)
        await ctx.send(f"{end_sent.text}")
async def setup(bot):
    await bot.add_cog(Fun(bot))