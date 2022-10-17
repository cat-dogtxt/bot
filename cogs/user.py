import json
import discord
import datetime
from discord.ext import commands
#sql
from discord import *
import sqlite3

import requests
class User(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot = bot
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
            json_data = json.loads(r.text)
            #print(json.dumps(json_data, indent=4))
            
            usernameHandle = json_data['data']['matchedUser']['username']
            total = json_data['data']['matchedUser']['submitStats']['acSubmissionNum'][0]['count']
            easy = json_data['data']['matchedUser']['submitStats']['acSubmissionNum'][1]['count']
            med = json_data['data']['matchedUser']['submitStats']['acSubmissionNum'][2]['count']
            hard = json_data['data']['matchedUser']['submitStats']['acSubmissionNum'][3]['count']

            context = {'username': usernameHandle, 'total': total, 'easy': easy, 'med':med, 'hard': hard}

            return context    
    def load_exp(self,user_id,username):
        db = sqlite3.connect('db.sqlite3')
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM exp WHERE user_id = {user_id}")
        leetcode_info = self.get_leetcode_info(username)
        total_point = leetcode_info['easy']*20 + leetcode_info['med']*50 + leetcode_info['hard']*500
        print(total_point)
        sql = (f'''
            UPDATE exp SET leetcode_exp = {total_point} WHERE user_id = {user_id}
        ''')
        cursor.execute(sql)
        db.commit()
        db.close()
    @commands.command()
    async def kayit(self,ctx):
        '''
        Kayıt olmak için kullanılır.
        '''
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
            sql2 = (f'''
                INSERT INTO urls(user_id) VALUES({ctx.author.id})
            ''')
            cursor.execute(sql2)
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
        embed.set_footer(text=f"{ctx.author.name} tarafından sorgulandı.")
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
        embed.set_footer(text=f"{ctx.author.name} tarafından sorgulandı.")
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
        
        db = sqlite3.connect("db.sqlite3")
        cursor = db.cursor()
        cursor.execute(f"SELECT exp,level,amount,leetcode_exp FROM exp WHERE user_id = {member.id}")
        result = cursor.fetchone()
        print(result)
        print(member.id)
        if result is None:
            await ctx.send(f"{member.mention} kayıtlı değil!")
        else:
            exp,level,amount,l_exp = result
            embed = discord.Embed(title="Üye bilgi", description="Üye",colour=discord.Colour.random())
            #embed.set_image(url=pfp)
            embed.set_author(name=f"{name}",icon_url=pfp)
            embed.add_field(name="Exp",value=f"{exp+l_exp}")
            embed.add_field(name="Level",value=f"{level}",inline=True)
            embed.add_field(name="Amount",value=f"{amount}",inline=False)
            embed.set_footer(text=f"{name} Made this banner")
            
            await ctx.send(embed=embed)

    @commands.command()
    async def daily(self,ctx):
        '''
        Günlük ödül almak için kullanılır.
        '''
        db = sqlite3.connect("db.sqlite3")
        cursor = db.cursor()
        cursor.execute(f"SELECT user_id,takeDate FROM main WHERE user_id = {ctx.author.id}")
        result = cursor.fetchone()
        if result is None:
            await ctx.send("Kayıt olmadan daily alamazsın")
        else:
            user_id,takeDate = result
            print(result)
            print(takeDate)
            print(datetime.datetime.now())
            if datetime.datetime.strptime(takeDate,'%Y-%m-%d %H:%M:%S.%f') < datetime.datetime.now():
                cursor.execute(f"SELECT exp,amount FROM exp WHERE user_id = {ctx.author.id}")
                result = cursor.fetchone()
                exp,amount = result
                reward=100
                amount += reward
                sql = (f'''
                    UPDATE exp SET amount = ? WHERE user_id = ?
                ''')
                val = (amount,ctx.author.id)
                cursor.execute(sql,val)
                await ctx.send(f"Daily alındı exp +{reward}")
                sql1 = (f'''
                    UPDATE main SET takeDate = ? WHERE user_id = ?
                ''')
                val = (datetime.datetime.now() + datetime.timedelta(days=1),ctx.author.id)
                cursor.execute(sql1,val)
                db.commit()
            else:
                await ctx.send(f"Daily alamazsın {takeDate}")
        cursor.close()
    
    
        
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
        
        db = sqlite3.connect("db.sqlite3")
        cursor = db.cursor()
        cursor.execute(f"SELECT user_id,leetcode FROM urls WHERE user_id = {ctx.author.id}")
        result = cursor.fetchone()
        print(result)
        if result is None:
            await ctx.send("Kayıt olmalısın")
        else:
            if result[1] is None:
                await ctx.send("Leetcode hesabını bağlamalısın -> ~leetcode sign -nickname-")
            else:
                self.load_exp(result[0],result[1])
                await ctx.send("exp yüklendi")
                cursor.close()
    @leetcode.command()
    async def sign(self,ctx,username:str):
        '''
        Leetcode hesabınızı bağlamak için kullanılır.
        '''
        db = sqlite3.connect("db.sqlite3")
        cursor = db.cursor()
        cursor.execute(f"SELECT user_id FROM main WHERE user_id = {ctx.author.id}")
        result = cursor.fetchone()
        if result is None:
            await ctx.send("Kayıt olmadan leetcode hesabı bağlayamazsın")
        else:
            cursor.execute(f"SELECT leetcode FROM urls WHERE user_id = {ctx.author.id}")
            r = cursor.fetchone()
            
            if r is None:
                cursor.execute(f"SELECT user_id FROM urls WHERE leetcode = '{username}'")
                new_r = cursor.fetchone()
                if new_r is None:
                    sql = (f'UPDATE urls SET leetcode = "{username}" WHERE user_id = {ctx.author.id}')
                    cursor.execute(sql)
                    await ctx.send(f"Leetcode hesabınız {username} olarak ayarlandı")#Exp yüklenecek ve embed gönderilecek
                    self.load_exp(ctx.author.id,username)
                    await ctx.send(f"exp yüklendi")
                    db.commit()
                    cursor.close()
                else:
                    await ctx.send("Bu leetcode hesabı başka birisi tarafından kullanılıyor")
                
            else:
                await ctx.send("Leetcode hesabınız zaten var, değiştirmek için ~leetcode change komutunu kullanın")
                cursor.close()
    
    @leetcode.command()
    async def change(self,ctx,username:str):
        '''
        Leetcode hesabınızı değiştirmek için kullanılır.
        '''
        db = sqlite3.connect("db.sqlite3")
        cursor = db.cursor()
        cursor.execute(f"SELECT user_id FROM main WHERE user_id = {ctx.author.id}")
        result = cursor.fetchone()
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
                    sql = (f'''
                        UPDATE urls SET leetcode = ? WHERE user_id = ?
                    ''')
                    val = (username,ctx.author.id)
                    cursor.execute(sql,val)
                    await ctx.send(f"Leetcode hesabınız {username} olarak değiştirildi")
                    db.commit()
                    cursor.close()
                else:
                    await ctx.send(f"Bu leetcode hesabı başka birisi tarafından kullanılıyor. Kullanan kişi {self.bot.get_user(new_r[0]).mention} ")
    @commands.group()
    async def github(self,ctx):
        '''
        Github tablosunu görüntülemek için kullanılır.
        '''
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title="~github",description="Github tablosu görüntüleme komutları",colour=discord.Colour.random())
            embed.add_field(name="~github sign -username-",value="Github hesabınızı bağlar.",inline=False)
            embed.add_field(name="~github change -username-",value="Github hesabınızı değiştirmek için kullanılır.",inline=False)
            embed.add_field(name="~github update",value="Github'da yaptığınız commitlerden exp kazanmak için kullanılır",inline=False)
            await ctx.send(embed=embed)
    
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
