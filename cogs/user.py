import json
import discord
import datetime
from discord.ext import commands
#sql
from discord import *
import sqlite3
import sys
sys.path.insert(0,"..")
from model import *
#from discord_ui import *
from discord.ui import View, Button, Select
from discord.ui import *
import requests
from PyPDF2 import *
import pytesseract
class User(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot = bot
        self.db = Models()
    def get_leetcode_info(self,username):
            '''
            Leetcode'da çözdüğünüz soruları çeker.
            '''

            query = '''
            query getUserProfile($username: String!) {
                allQuestionsCount {
                difficulty
                count
                }
                matchedUser(username: $username) {
                username
                submitStats {
                    acSubmissionNum {
                    difficulty
                    count
                    submissions
                    }
                }
                }
            }
            '''
            username = username
            variables = {'username': username}

            url = 'https://leetcode.com/graphql/'
            r = requests.post(url, json={'query': query, 'variables': variables})
            if "errors" in json.loads(r.text):
                return None
            else:
                json_data = json.loads(r.text)
                #print(json.dumps(json_data, indent=4))
                
                usernameHandle = json_data['data']['matchedUser']['username']
                total = json_data['data']['matchedUser']['submitStats']['acSubmissionNum'][0]['count']
                easy = json_data['data']['matchedUser']['submitStats']['acSubmissionNum'][1]['count']
                med = json_data['data']['matchedUser']['submitStats']['acSubmissionNum'][2]['count']
                hard = json_data['data']['matchedUser']['submitStats']['acSubmissionNum'][3]['count']
                
                context = {'username': usernameHandle, 'total': total, 'easy': easy, 'med':med, 'hard': hard}                
                return context        
    def load_exp(self,username):
        #cursor.execute(f"SELECT * FROM exp WHERE user_id = {user_id}")
        leetcode_info = self.get_leetcode_info(username)
        if leetcode_info is None:
            leetcode_exp = 1
            return leetcode_exp
        else:
            total_point = leetcode_info['easy']*20 + leetcode_info['med']*50 + leetcode_info['hard']*500
            return total_point
            
    # @commands.command()
    # async def kayit(self,ctx):
    #     '''
    #     Kayıt olmak için kullanılır.
    #     '''
    #     db = sqlite3.connect("db.sqlite3")
    #     cursor = db.cursor()
    #     result = self.db.get_user(ctx.author.id)
    #     if result is None:
    #         self.db.add_user(ctx.author.id)
    #         await ctx.send(f"Kayıt yapıldı.{ctx.author.id}")
    #         self.db.add_exp(ctx.author.id)     
    #         await ctx.send(f"Expler yüklendi.{ctx.author.id}")
    #         self.db.add_url(ctx.author.id)
    #         await ctx.send(f"Urlleri girmen gerekiyor")
    #         db.commit()
    #     else:
    #         await ctx.send(f"Zaten kayıtlısın id:{ctx.author.id}")
    #     cursor.close()
    
    @commands.group(describe="Liderlik görüntülemek için kullanılır.")
    async def leaderboard(self,ctx):
        '''
        Liderlik tablosunu görüntülemek için kullanılır.
        '''
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title="~leaderboard",description="Leaderboard görüntüleme komutları",colour=discord.Colour.random())  
            embed.add_field(name="~leaderboard exp",value="Exp liderliğini görüntülemek için kullanılır.",inline=False)
            embed.add_field(name="~leaderboard amount",value="Amount liderliğini görüntülemek için kullanılır.",inline=False)
            await ctx.send(embed=embed)

    @leaderboard.command()
    async def exp(self,ctx):    
        '''
        Exp liderliğini görüntülemek için kullanılır.
        '''
        db = sqlite3.connect("db.sqlite3") 
        cursor = db.cursor()
        cursor.execute(f"SELECT user_id,exp FROM exp ORDER BY exp DESC LIMIT 10")
        result = cursor.fetchall()
        embed = discord.Embed(title="Leaderboard",color=discord.Colour.random())
        for i in result:
            embed.add_field(name=f"{self.bot.get_user(i[0])}",value=f"{i[1]} exp",inline=False)
        embed.set_footer(icon_url=ctx.author.display_avatar,text=f"{ctx.author.name} tarafından sorgulandı.")
        await ctx.send(embed=embed) 
        cursor.close()
    @leaderboard.command()
    async def amount(self,ctx):
        db = sqlite3.connect("db.sqlite3")
        cursor = db.cursor()
        cursor.execute(f"SELECT user_id,amount FROM exp ORDER BY amount DESC LIMIT 10")
        result = cursor.fetchall()
        embed = discord.Embed(title="Leaderboard",color=discord.Colour.random())
        for i in result:
            embed.add_field(name=f"{self.bot.get_user(i[0])}",value=f"{i[1]} amount",inline=False)
        embed.set_footer(icon_url=ctx.author.display_avatar,text=f"{ctx.author.name} tarafından sorgulandı.")
        await ctx.send(embed=embed) 
        cursor.close()
    
    @commands.command()
    async def goruntule(self,ctx:commands.Context,member:discord.Member=None):
        '''
        Profilinizi görüntülemek için kullanılır.(içerik:exp,amount,level,avatar)
        '''
        if member == None:
            member = ctx.author
        name = member.display_name
        pfp = member.display_avatar
        result = self.db.get_user_info(member.id)
        print(result)
        if result is None:
            await ctx.send(f"{member.mention} kayıtlı değil!")
        else:
            user_id,exp,leetcode_exp,level,amount = result
            embed = discord.Embed(title="Üye bilgi", description="Üye",colour=discord.Colour.random())
            #embed.set_image(url=pfp)
            embed.set_author(name=f"{name}",icon_url=pfp)
            embed.add_field(name="Total exp",value=f"{exp+leetcode_exp}",inline=True)
            embed.add_field(name="leetcode exp",value=f"{leetcode_exp}",inline=True)
            embed.add_field(name="Amount",value=f"{amount}",inline=False)
            embed.add_field(name="Level",value=f"{level}",inline=True)
            embed.set_footer(icon_url=ctx.author.display_avatar,text=f"{ctx.author.name} Made this banner")
            
            await ctx.send(embed=embed)

    @commands.command()
    async def daily(self,ctx):
        '''
        Günlük ödül almak için kullanılır.
        '''
        result = self.db.get_user(ctx.author.id)
        if result is None:
            await ctx.send("Kayıt olmadan daily alamazsın")
        else:
            user_id,signDate,takeDate = result
            if takeDate < datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
                result = self.db.get_amount(ctx.author.id)
                amount = result[0]
                reward=100
                amount += reward
                self.db.set_daily(ctx.author.id,amount)
                await ctx.send(f"Daily alındı exp +{reward}")
            else:
                await ctx.send(f"Daily alamazsın {takeDate}")

    @commands.group(describe="Leetcode komutları")
    async def leetcode(self,ctx):
        '''
        Leetcode tablosunu görüntülemek için kullanılır.
        '''
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title="~leetcode",description="Leaderboard görüntüleme komutları",colour=discord.Colour.random())
            embed.add_field(name="~leetcode sign -nickname-",value="Leetcode hesabınızı bağlar.",inline=False)
            embed.add_field(name="~leetcode change -nickname-",value="Leetcode hesabınızı değiştirmek için kullanılır.",inline=False)
            embed.add_field(name="~leetcode update",value="Leetcode'da çözdüğünüz sorulardan exp kazanmak için kullanılır",inline=False)
            await ctx.send(embed=embed)

    
    @leetcode.command()
    async def update(self,ctx):
        '''
        Leetcode'da çözdüğünüz sorulardan discordta exp kazanmak için kullanılır.
        '''
        result= self.db.get_url(ctx.author.id)
        if result[0] is None:
            await ctx.send("Kayıt olmalısın")
        else:
            if result[1] is None:
                await ctx.send("Leetcode hesabını bağlamalısın -> ~leetcode sign -nickname-")
            else:
                print(result[0],result[1])
                exps = self.load_exp(result[1])
                print(exps)
                if exps != 1:
                    self.db.set_leetcode_exp(ctx.author.id,exps)
                    await ctx.send("exp yüklendi")
                else:
                    exps=0
                    self.db.set_leetcode_exp(ctx.author.id,exps)
                    await ctx.send("Yanlış kullanıcı adı")
    
    @leetcode.command()
    async def sign(self,ctx,username:str):
        '''
        Leetcode hesabınızı bağlamak için kullanılır.
        '''
        result = self.db.get_user(ctx.author.id)
        if result is None:
            await ctx.send("Kayıt olmadan leetcode hesabı bağlayamazsın")
        else:
            r = self.db.get_url(ctx.author.id)
            print(r)
            if r[1] is None:
                res = self.db.get_leet_user(username)
                print(res)
                if res is None:
                    self.db.set_url_leetcode(ctx.author.id,username)
                    await ctx.send(f"Leetcode hesabınız {username} olarak ayarlandı")#Exp yüklenecek ve embed gönderilecek
                    exps = self.load_exp(username)
                    self.db.set_exp(ctx.author.id,exps,"leetcode_exp")
                    await ctx.send("exp yüklendi")
                else:
                    await ctx.send(f"Bu leetcode hesabı başka birisi tarafından kullanılıyor {self.bot.get_user(res[0]).mention}")
                
            else:
                await ctx.send("Leetcode hesabınız zaten var, değiştirmek için ~leetcode change komutunu kullanın")

    @leetcode.command()
    async def change(self,ctx,username:str):
        '''
        Leetcode hesabınızı değiştirmek için kullanılır.
        '''
        db = sqlite3.connect("db.sqlite3")
        cursor = db.cursor()
        result = self.db.get_user(ctx.author.id)
        if result is None:
            await ctx.send("Kayıt olmadan leetcode hesabı bağlayamazsın")
        else:
            r = self.db.get_url(ctx.author.id)
            if r[1] is None:
                await ctx.send("Leetcode hesabınız yok, bağlamak için ~leetcode sign komutunu kullanın")
            else:
                new_r = self.db.get_leet_user(username)
                if new_r is None:
                    self.db.set_url_leetcode(ctx.author.id,username)
                    await ctx.send(f"Leetcode hesabınız {username} olarak değiştirildi")
                    db.commit()
                    cursor.close()
                else:
                    await ctx.send(f"Bu leetcode hesabı başka birisi tarafından kullanılıyor. Kullanan kişi {self.bot.get_user(new_r[0]).mention} ")
    @leetcode.command()
    async def challange(self,interaction:discord.Interaction):
        embedList = []
        for i in range(5):
            embed = discord.Embed(title=f"Problem Name",color=discord.Color.blurple())
            embed.add_field(name=f"Problem{i}",value="Problem Description")
            embedList.append(embed)
        embed = discord.Embed(title="Problem Name",color=discord.Color.blurple())
        value = '''
        Problem Description
        '''
        embed.add_field(name="Problem description",value=value,inline=True)
        b_page_up = Button(style=discord.ButtonStyle.gray,emoji="➡️")
        b_page_down = Button(style=discord.ButtonStyle.gray,emoji="⬅️")
        view = View()
        view.add_item(b_page_down)
        view.add_item(b_page_up)
        pagination = 0
        async def b_callback(interaction):
            nonlocal pagination
            pagination -=1
            print(pagination)
            if pagination < 0:
                await interaction.response.send_message("geri dönemezsin",ephemeral=True)
            else:
                await interaction.response.edit_message(embed=embedList[pagination])
        async def u_callback(interaction):
            nonlocal pagination
            pagination +=1
            print(pagination)
            if pagination > 4:
                await interaction.response.send_message("ileri gidemezsin",ephemeral=True)
            else:
                await interaction.response.edit_message(embed=embedList[pagination])
        b_page_down.callback = b_callback
        b_page_up.callback = u_callback
        await interaction.send("Hi",embed=embed,view=view)
    # @commands.command()
    # async def teseract(self,ctx):
    #     print("burdayim")
    #     await ctx.message.attachments[0].save('ogrencibelge.jpg')
    #     print("save")
    #     kontrol=""
    #     pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Samet\AppData\Local\Tesseract-OCR\tesseract'
    #     print(pytesseract.image_to_string(r'C:\Users\Samet\OneDrive\Masaüstü\dccc\cse-discord-bot\ogrencibelge.jpg').split("\n"))
    #     text = pytesseract.image_to_string(r'C:\Users\Samet\OneDrive\Masaüstü\dccc\cse-discord-bot\ogrencibelge.jpg').split("\n")
    #     if any(kontrol in s for s in text):
    #         print("okul öğrencisi")
    #     else:
    #         print("bozuksun")
    @commands.Cog.listener()
    async def on_member_join(self,member):
        result = self.db.get_user(member.id)
        print(result)
        guild_id = 768189401213304892
        roles = ["1.sınıf","2.sınıf","3.sınıf","4.sınıf","hazırlık"]
        server = self.bot.get_guild(guild_id)
        roles = [discord.utils.get(server.roles, name=language.lower()) for language in roles]
        if result is None:
            pass
        else:
            result = self.db.get_user_class(member.id)
            if(result==1):
                self.db.add_user_class(member.id,1)
                await member.add_roles(roles[0], reason="1. Sınıf Ogrencisi")
                await member.send("Başariyla kayit oldunuz")
            elif(result==2):
                self.db.set_user_class(member.id,2)
                await member.add_roles(roles[1], reason="2. Sınıf Ogrencisi")
                await member.send("Başariyla kayit oldunuz")
            elif(result==3):
                self.db.set_user_class(member.id,3)
                await member.add_roles(roles[2], reason="3. Sınıf Ogrencisi")
                await member.send("Başariyla kayit oldunuz")
            elif(result==4):
                self.db.set_user_class(member.id,4)
                await member.add_roles(roles[3], reason="4. Sınıf Ogrencisi")
                await member.send("Başariyla kayit oldunuz")
            elif(result==0):
                self.db.set_user_class(member.id,0)
                await member.add_roles(roles[4], reason="Hazırlık Ogrencisi")
                await member.send("Başariyla kayit oldunuz")
    #############################3
    @commands.Cog.listener()
    async def on_message(self,message):
        if message.author == self.bot.user:
            return
        if message.attachments[0].url.endswith(".pdf"):
            await message.attachments[0].save('C:\\Users\\Samet\\OneDrive\\Masaüstü\\dccc\\cse-discord-bot\\ogrencipdf\\ogrenci'+str(message.author)+'.pdf')
            reader = PdfReader('C:\\Users\\Samet\\OneDrive\\Masaüstü\\dccc\\cse-discord-bot\\ogrencipdf\\ogrenci'+str(message.author)+'.pdf')
            page = reader.pages[0]
            pdfa = page.extract_text(0,90)
            liste = pdfa.split(".")
            sınıf1 =" Kimlik No\nİLGİLİ MAKAMA:\n:\n:\n:\n:\n:\n:\nAKTİF ÖĞRENCİ: Öğrencilik Durumu\nSınıf :1"
            sınıf2 =" Kimlik No\nİLGİLİ MAKAMA:\n:\n:\n:\n:\n:\n:\nAKTİF ÖĞRENCİ: Öğrencilik Durumu\nSınıf :2"
            sınıf3 =" Kimlik No\nİLGİLİ MAKAMA:\n:\n:\n:\n:\n:\n:\nAKTİF ÖĞRENCİ: Öğrencilik Durumu\nSınıf :3"
            sınıf4 =" Kimlik No\nİLGİLİ MAKAMA:\n:\n:\n:\n:\n:\n:\nAKTİF ÖĞRENCİ: Öğrencilik Durumu\nSınıf :4"
            kontrolhaz =" Kimlik No\nİLGİLİ MAKAMA:\n:\n:\n:\n:\n:\n:\nAKTİF ÖĞRENCİ: Öğrencilik Durumu\nSınıf :YABANCI DİL HAZIRLIK\nProgram BURSA TEKNİK ÜNİVERSİTESİ/MÜHENDİSLİK VE DOĞA BİLİMLERİ\nFAKÜLTESİ/BİLGİSAYAR MÜHENDİSLİĞİ BÖLÜMÜ/BİLGİSAYAR"
            kontrol ="SINIF\nProgram BURSA TEKNİK ÜNİVERSİTESİ/MÜHENDİSLİK VE DOĞA BİLİMLERİ\nFAKÜLTESİ/BİLGİSAYAR MÜHENDİSLİĞİ BÖLÜMÜ/BİLGİSAYAR\nMÜHENDİSLİĞİ PR"
            guild_id = 768189401213304892
            roles = ["1.sınıf","2.sınıf","3.sınıf","4.sınıf","hazırlık"]
            server = self.bot.get_guild(guild_id)
            roles = [discord.utils.get(server.roles, name=language.lower()) for language in roles]
            member = await server.fetch_member(message.author.id)
            userid=message.author.id
            if any(kontrol in s for s in liste):
                    if any(sınıf1 in s for s in liste):
                        self.db.add_user_class(userid,1)
                        await member.add_roles(roles[0], reason="1. Sınıf Ogrencisi")
                        await member.send("Başariyla kayit oldunuz")
                    elif any(sınıf2 in s for s in liste):
                        print("aaa")
                        self.db.add_user_class(userid,2)
                        print("bbbb")
                        await member.add_roles(roles[1], reason="2. Sınıf Ogrencisi")
                        await member.send("Başarıyla kayıt oldunuz")
                    elif any(sınıf3 in s for s in liste):
                        self.db.add_user_class(userid,3)
                        await member.add_roles(roles[2], reason="3. Sınıf Ogrencisi")
                        await member.send("Başarıyla kayıt oldunuz")
                    elif any(sınıf4 in s for s in liste):
                        self.db.add_user_class(userid,4)
                        await member.add_roles(roles[3], reason="4. Sınıf Ogrencisi")
                        await member.send("Başarıyla kayıt oldunuz")
                    else:
                        pass
                        
            else:
                if any(kontrolhaz in s for s in liste):
                    await member.add_roles(roles[4], reason="Hazırlık Ogrencisi")
                    self.db.add_user_class(userid,0)
                    await member.send("Başarıyla kayıt oldunuz")
                else:
                    await member.send("Tekrar deneyiniz.Tekrarlanması durumunda yetkililere bildiriniz")
        elif(message.attachments[0].url.endswith(".png") or message.attachments[0].url.endswith(".jpg") or message.attachments[0].url.endswith(".jpeg")):
            await message.attachments[0].save('C:\\Users\\Samet\\OneDrive\\Masaüstü\\dccc\\cse-discord-bot\\ogrenci_karti\\ogrencibelge'+str(message.author)+'.png')
            select = Select(
            placeholder="Select an option",
            options=[
                SelectOption(label="Hazırlık", value=0),
                SelectOption(label="1.Sınıf", value=1),
                SelectOption(label="2.Sınıf", value=2),
                SelectOption(label="3.Sınıf", value=3),
                SelectOption(label="4.Sınıf", value=4),
            ],
        )
        guild_id = 768189401213304892
        roles = ["1.sınıf","2.sınıf","3.sınıf","4.sınıf","hazırlık"]
        server = self.bot.get_guild(guild_id)
        roles = [discord.utils.get(server.roles, name=language.lower()) for language in roles]
        member = await server.fetch_member(message.author.id)
        userid=message.author.id
        async def callback_selected(interaction: Interaction):
            select.disabled = True
            await interaction.response.edit_message(view=view)
            await interaction.followup.send(f"Selected {select.values}")
            a=int(select.values[0])
            print(a)
            if a == 1:
                self.db.add_user_class(userid,1)
                await member.add_roles(roles[0], reason="1. Sınıf Ogrencisi")
                await member.send("Başariyla kayit oldunuz")
            elif a==2:
                self.db.add_user_class(userid,2)
                await member.add_roles(roles[1], reason="2. Sınıf Ogrencisi")
                await member.send("Başarıyla kayıt oldunuz")
            elif a==3:
                self.db.add_user_class(userid,3)
                await member.add_roles(roles[2], reason="3. Sınıf Ogrencisi")
                await member.send("Başarıyla kayıt oldunuz")
            elif a == 4:
                self.db.add_user_class(userid,4)
                await member.add_roles(roles[3], reason="4. Sınıf Ogrencisi")
                await member.send("Başarıyla kayıt oldunuz")
            elif a == 0:
                await member.add_roles(roles[4], reason="Hazırlık Ogrencisi")
                self.db.add_user_class(userid,0)
                await member.send("Başarıyla kayıt oldunuz")
            else:
                await member.send("Hata 404")
            

        select.callback = callback_selected
        view = View()
        view.add_item(select)
        kontrol="BILGISiYAR MUH."
        pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Samet\AppData\Local\Tesseract-OCR\tesseract'
        print(pytesseract.image_to_string(r'C:\Users\Samet\OneDrive\Masaüstü\dccc\cse-discord-bot\ogrenci_karti\ogrencibelge'+str(message.author)+'.png').split("\n"))
        text = pytesseract.image_to_string(r'C:\Users\Samet\OneDrive\Masaüstü\dccc\cse-discord-bot\ogrenci_karti\ogrencibelge'+str(message.author)+'.png').split("\n")
        
        if any(kontrol in s for s in text):
            await message.channel.send(view=view)
            print("dsfaaaaaa")
        else:
            print("Tekrar deneyiniz.Tekrarlanması durumunda yetkililere bildiriniz")

    # @commands.group()
    # async def github(self,ctx):
    #     '''
    #     Github tablosunu görüntülemek için kullanılır.
    #     '''
    #     if ctx.invoked_subcommand is None:
    #         embed = discord.Embed(title="~github",description="Github tablosu görüntüleme komutları",colour=discord.Colour.random())
    #         embed.add_field(name="~github sign -username-",value="Github hesabınızı bağlar.",inline=False)
    #         embed.add_field(name="~github change -username-",value="Github hesabınızı değiştirmek için kullanılır.",inline=False)
    #         embed.add_field(name="~github update",value="Github'da yaptığınız commitlerden exp kazanmak için kullanılır",inline=False)
    #         await ctx.send(embed=embed)
    
    # @github.command()➡️
    # async def sign(self,ctx,username:str):
    #     '''
    #         Github hesabınızı bağlamak için kullanılır.
    #     '''
    #     db = sqlite3.connect("db.sqlite3")
    #     cursor = db.cursor()
    #     cursor.execute(f"SELECT user_id FROM main WHERE user_id = {ctx.author.id}")
    #     result = cursor.fetchone()
    #     if result is None:
    #         await ctx.send("Kayıt olmadan leetcode hesabı bağlayamazsın")
    #     else:
    #         cursor.execute(f"SELECT user_id FROM urls WHERE user_id = {ctx.author.id}")
    #         r = cursor.fetchone()
            
    #         if r is None:
    #             cursor.execute(f"SELECT user_id FROM urls WHERE leetcode = '{username}'")
    #             new_r = cursor.fetchone()
    #             if new_r is None:
    #                 sql = (f'INSERT INTO urls(user_id,github) VALUES(?,?)')
    #                 val = (ctx.author.id,username)
    #                 cursor.execute(sql,val)
    #                 await ctx.send(f"Github hesabınız {username} olarak ayarlandı")#Exp yüklenecek ve embed gönderilecek
    #                 db.commit()
    #                 cursor.close()
    #             else:
    #                 await ctx.send(f"Bu github hesabı başka birisi tarafından kullanılıyor {self.bot.get_user(new_r[0]).mention}")
                
    #         else:
    #             await ctx.send("Github hesabınız zaten var, değiştirmek için ~github change komutunu kullanın")
    #             cursor.close()


async def setup(bot):
    await bot.add_cog(User(bot))
