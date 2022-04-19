import discord
import aiohttp
from discord.ext import commands
import random
from youtube_dl import YoutubeDL
import asyncio

YDL_OPTIONS = {'format': 'worstaudio/best', 'noplaylist': 'False', 'simulate': 'True',
               'preferredquality': '192', 'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
TOKEN ='OTYzODExMTU0NzE3NzI4Nzc4.YlbhFg.Dd7I1Df0L4Qggqv56EJsGwcpzAQ'
PREFIX = '+'
bot = commands.Bot(command_prefix=('+'))
intents = discord.Intents.default()
intents.members = True
bot.remove_command( 'help' )

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Кинопоиск"))


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def serverinfo(self, ctx):
        name = str(ctx.guild.name)
        
        owner = str(ctx.guild.owner)
        id = str(ctx.guild.id)
        region = str(ctx.guild.region)
        memberCount = str(ctx.guild.member_count)
        
        icon = str(ctx.guild.icon_url)
        
        embed = discord.Embed(title=" Информация про сервер " + name, description="⬇", )
        embed.set_thumbnail(url=icon)
        embed.add_field(name="Владелец", value=owner, inline=True)
        embed.add_field(name="Сервер ID", value=id, inline=True)
        embed.add_field(name="Регион", value=region, inline=True)
        embed.add_field(name="Кол-во участников", value=memberCount, inline=True)
        
        await ctx.send(embed=embed)
        
    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(color=0x00ffff, title='Help menu')
        embed.add_field(name='{}mem'.format(PREFIX), value='Запуск мембота')
        embed.add_field(name='{}news'.format(PREFIX), value='Запуск новостного бота')
        embed.add_field(name='{}leave'.format(PREFIX), value='выход из звукового чата')
        embed.add_field(name='{}play'.format(PREFIX), value='музыка в войс чат')
        embed.add_field(name='{}clear'.format(PREFIX), value='очистить')
        embed.add_field(name='{}kick'.format(PREFIX), value='кикнуть')
        embed.add_field(name='{}ban'.format(PREFIX), value='забанить')
        embed.add_field(name='{}unban'.format(PREFIX), value='разбанить')
        embed.add_field(name='{}mute'.format(PREFIX), value='замутить')    
        await ctx.send(embed=embed)

    @commands.command()
    async def mute(self, ctx, member: discord.Member):
        if ctx.message.author.server_permissions.administrator:
            role = discord.utils.get(member.server.roles, name='Muted')
            await bot.add_roles(member, role)
            embed=discord.Embed(title="Пользователь замьючен", description="**{0}** был замьючен пользователем **{1}**!".format(member, ctx.message.author), color=discord.Color.red())
            await ctx.send(embed=embed)
        else:
            embed=discord.Embed(title="Нет доступа", description="У вас недостаточно прав для этой команды", color=discord.Color.red())
            await ctx.send(embed=embed)


    @commands.command()
    async def kick(self, ctx, member: discord.Member = None, *, reason:str =None):
        await member.send(f"{member}, пока ")
        if member:
            if reason:
                await member.kick(reason=reason)
                await ctx.send(embed=discord.Embed(description=f'Пользователь {member.mention} был кикнут \nПричина: {reason}' ))
            else:
                await member.kick()
                await ctx.send(embed=discord.Embed(description=f'Пользователь {member.mention} был кикнут'))
        else: 
            await ctx.send('Введите имя пользователя')
            
    @commands.command()
    async def clear(self, ctx, count: int):
        await ctx.channel.purge(limit=count+1)
        await ctx.send(f"Было удаленно {count} сообщений")
        
    @commands.command()
    async def ban(self, ctx, member: discord.Member = None, time = None, *, reason: str = None):
        async def unb(member):
            users = await ctx.guild.bans()
            for ban_user in users:
                if ban_user.user == member:
                    await ctx.guild.unban(ban_user.user)
                
        if member:
            if time: 
                time_letter = time[-1:] 
                time_numbers = int(time[:-1]) 
                
                def t(time_letter): 
                    if time_letter == 's':
                        return 1
                    if time_letter == 'm':
                        return 60
                    if time_letter == 'h':
                        return 60*60
                    if time_letter == 'd':
                        return 60*60*24
                        
                if reason:
                    await member.ban(reason=reason)
                    await ctx.send(embed=discord.Embed(description=f'Пользователь {member.mention} был забанен \nВремя: {time} \nПричина: {reason}' ))
                    
                    await asyncio.sleep(time_numbers*t(time_letter))
                    
                    await unb(member)
                    await ctx.send(f'Пользователь {member.mention} разбанен')
                else:
                    await member.ban()
                    await ctx.send(embed=discord.Embed(description=f'Пользователь {member.mention} был забанен \nВремя: {time}'))
                
                    await asyncio.sleep(time_numbers*t(time_letter))
                
                    await unb(member)
                    await ctx.send(f'Пользователь {member.mention} разбанен')
            else:
                await member.ban()
                await ctx.send(embed=discord.Embed(description=f'Пользователь {member.mention} был забанен'))
        else: 
            await ctx.send('Введите имя пользователя')


class Interactive(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def mem(self, ctx):
        embed = discord.Embed(title="Memes", description="memes from reddit")  
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://www.reddit.com/r/memes/new.json?sort=hot') as r:
                res = await r.json()
                embed.set_image(url=res['data']['children'] [random.randint(0, 25)]['data']['url'])
                await ctx.send(embed=embed)
    
    @commands.command()
    async def news(self, ctx):
        embed = discord.Embed(title="News")  
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://www.reddit.com/r/news/new.json?sort=hot') as r:
                res = await r.json()
                embed.add_field(name='news from reddit', value=res['data']['children'] [random.randint(0, 25)]['data']['url'])
                await ctx.send(embed=embed)


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def leave(self, ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice.is_connected():
            await voice.disconnect()
        else:
            await ctx.send("В данный момент бот не в звуковом канале")
            
    @commands.command()
    async def play(self, ctx, *, arg):
        voice = await ctx.message.author.voice.channel.connect()
        with YoutubeDL(YDL_OPTIONS) as ydl:
            if 'https://' in arg:
                info = ydl.extract_info(arg, download=False)
            else:
                info = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
            
        url = info['formats'][0]['url']
        voice.play(discord.FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=url, **FFMPEG_OPTIONS))
    
    @commands.command()
    async def pause(self, ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.pause()
        else:
            await ctx.send("В данный момент музыка не играет")
    
    @commands.command()
    async def resume(self, ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice.is_paused():
            voice.resume()
        else:
            await ctx.send("Музыка не стоит на паузе")
    
    @commands.command()
    async def stop(self, ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        voice.stop()

bot.add_cog(Moderation(bot))
bot.add_cog(Interactive(bot))
bot.add_cog(Music(bot))
bot.run(TOKEN)
