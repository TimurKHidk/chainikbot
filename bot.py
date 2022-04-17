import discord
import aiohttp
from discord.ext import commands
import random
from discord.utils import get
from youtube_dl import YoutubeDL
import asyncio

YDL_OPTIONS = {'format': 'worstaudio/best', 'noplaylist': 'False', 'simulate': 'True',
               'preferredquality': '192', 'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
TOKEN ='OTYzODExMTU0NzE3NzI4Nzc4.YlbhFg.Dd7I1Df0L4Qggqv56EJsGwcpzAQ'
bot = commands.Bot(command_prefix=('+'))

@bot.command()
async def kick(ctx, member: discord.Member = None, *, reason:str =None):
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

@bot.command()
async def clear(ctx, count: int):
    await ctx.channel.purge(limit=count+1)
    await ctx.send(f"Было удаленно {count} сообщений")

@bot.command()
async def ban(ctx, member: discord.Member = None, time = None, *, reason: str = None):
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

@bot.command()    
async def mem(ctx):
        embed = discord.Embed(title="Memes", description="memes from reddit")  
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://www.reddit.com/r/memes/new.json?sort=hot') as r:
                res = await r.json()
                embed.set_image(url=res['data']['children'] [random.randint(0, 25)]['data']['url'])
                await ctx.send(embed=embed)

@bot.command()    
async def news(ctx):
        embed = discord.Embed(title="News")  
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://www.reddit.com/r/news/new.json?sort=hot') as r:
                res = await r.json()
                embed.add_field(name='news from reddit', value=res['data']['children'] [random.randint(0, 25)]['data']['url'])
                await ctx.send(embed=embed)

@bot.command()
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild = ctx.guild)
    if voice and voice.is_connected():
        await voice.disconnect()
    else:
        voice = await channel.connect()
        await ctx.send('батя не в здании')

@bot.command()
async def play(ctx, *, arg):
    vc = await ctx.message.author.voice.channel.connect()
 
    with YoutubeDL(YDL_OPTIONS) as ydl:
        if 'https://' in arg:
            info = ydl.extract_info(arg, download=False)
        else:
            info = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
 
    url = info['formats'][0]['url']
    vc.play(discord.FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=url, **FFMPEG_OPTIONS))

bot.run(TOKEN)
