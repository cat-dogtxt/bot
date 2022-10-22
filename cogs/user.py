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

import requests
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
            
    @commands.command()
    async def kayit(self,ctx):
        '''
        Kayıt olmak için kullanılır.
        '''
        db = sqlite3.connect("db.sqlite3")
        cursor = db.cursor()
        result = self.db.get_user(ctx.author.id)
        if result is None:
            self.db.add_user(ctx.author.id)
            await ctx.send(f"Kayıt yapıldı.{ctx.author.id}")
            self.db.add_exp(ctx.author.id)     
            await ctx.send(f"Expler yüklendi.{ctx.author.id}")
            self.db.add_url(ctx.author.id)
            await ctx.send(f"Urlleri girmen gerekiyor")
            db.commit()
        else:
            await ctx.send(f"Zaten kayıtlısın id:{ctx.author.id}")
        cursor.close()
    
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
            embed.add_field(name="Exp",value=f"{exp+leetcode_exp}")
            embed.add_field(name="Level",value=f"{level}",inline=True)
            embed.add_field(name="Amount",value=f"{amount}",inline=True)
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
                print(exps,"asdfsaf")
                if exps != 1:
                    print("sss")
                    self.db.set_leetcode_exp(ctx.author.id,exps)
                    await ctx.send("exp yüklendi")
                else:
                    print("s")
                    exps=0
                    self.db.set_leetcode_exp(ctx.author.id,exps)
                    await ctx.send("Yanlış kullanıcı adı")
    
    @leetcode.command()
    async def sign(self,ctx,username:str):
        '''
        Leetcode hesabınızı bağlamak için kullanılır.
        '''
        # db = sqlite3.connect("db.sqlite3")
        # cursor = db.cursor()
        # cursor.execute(f"SELECT user_id FROM main WHERE user_id = {ctx.author.id}")
        # result = cursor.fetchone()
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
                    # sql = (f'UPDATE urls SET leetcode = "{username}" WHERE user_id = {ctx.author.id}')
                    # cursor.execute(sql)
                    self.db.set_url_leetcode(ctx.author.id,username)
                    await ctx.send(f"Leetcode hesabınız {username} olarak ayarlandı")#Exp yüklenecek ve embed gönderilecek
                    # db.commit()
                    exps = self.load_exp(username)
                    # sql = (f'''
                    #     UPDATE exp SET leetcode_exp = {exps} WHERE user_id = {ctx.author.id};
                    # ''')
                    # cursor.execute(sql)
                    # db.commit()
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
            cursor.execute(f"SELECT user_id FROM urls WHERE user_id = {ctx.author.id}")
            r = cursor.fetchone()
            if r is None:
                await ctx.send("Leetcode hesabınız yok, bağlamak için ~leetcode sign komutunu kullanın")
            else:
                cursor.execute(f"SELECT user_id FROM urls WHERE leetcode = '{username}'")
                new_r = cursor.fetchone()
                if new_r is None:
                    self.db.set_url_leetcode(ctx.author.id,username)
                    await ctx.send(f"Leetcode hesabınız {username} olarak değiştirildi")
                    db.commit()
                    cursor.close()
                else:
                    await ctx.send(f"Bu leetcode hesabı başka birisi tarafından kullanılıyor. Kullanan kişi {self.bot.get_user(new_r[0]).mention} ")
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
    
    # @github.command()
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
