import discord
import aiohttp
from discord.ext import commands
import random
from youtube_dl import YoutubeDL
import asyncio
from googletrans import Translator
import json
from typing import Optional
from easy_pil import Editor, load_image_async, Font
from discord import File


YDL_OPTIONS = {'format': 'worstaudio/best', 'noplaylist': 'False', 'simulate': 'True',
               'preferredquality': '192', 'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
TOKEN ='OTYzODExMTU0NzE3NzI4Nzc4.YlbhFg.Dd7I1Df0L4Qggqv56EJsGwcpzAQ'
PREFIX = '+'
bot = commands.Bot(command_prefix=('+'))
intents = discord.Intents.default()
intents.members = True
bot.remove_command( 'help' )
level = ["Плох", "Неплох", "Хорош", "Ультра Хорош", "Мега Хорош"]
level_num = [5, 10, 15, 20, 30]
current_language = "ru"
slap_gif = ["https://c.tenor.com/LiTeUfKB6HQAAAAC/batman-slap-in-the-face.gif", "https://c.tenor.com/3vxOt6Xi_AEAAAAC/will-smith-chris-rock.gif",
            "https://c.tenor.com/GpZ13hpY0ioAAAAC/slap-slapping.gif"]
slap_name = ["Неплохой вышел удар"]
shoot_gif = ["https://c.tenor.com/ZdUfN4OREUMAAAAC/shooting-a-machine-gun-vanguard.gif", "https://c.tenor.com/7w5mpGst604AAAAC/shooting-rambo.gif",
             "https://c.tenor.com/cEeghP8C-HgAAAAC/shepherds-delight-shephards-delight.gif"]
shoot_name = ["Теперь ты как Николай 2"]
kick_gif = ["https://c.tenor.com/PyMWkVnBTp0AAAAC/dropkick-fight.gif", "https://c.tenor.com/iodpOeOGEkkAAAAC/dropkick-waterboy.gif", 
            "https://c.tenor.com/Gf6UTsRayw4AAAAC/kickers-caught.gif"]
kick_name = ["Как анти air в мк"]

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Кинопоиск"))


class Levels(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    print("Leveling Cog Ready!")

  @commands.Cog.listener()
  async def on_message(self, message):


    if not message.content.startswith("+"):

      if not message.author.bot:
        with open("level.json", "r") as f:
          data = json.load(f)
        
        if str(message.author.id) in data:
          xp = data[str(message.author.id)]['xp']
          lvl = data[str(message.author.id)]['level']

          increased_xp = xp+25
          new_level = int(increased_xp/100)

          data[str(message.author.id)]['xp']=increased_xp

          with open("level.json", "w") as f:
            json.dump(data, f)

          if new_level > lvl:
            await message.channel.send(f"{message.author.mention} Just Leveled Up to Level {new_level}!!!")

            data[str(message.author.id)]['level']=new_level
            data[str(message.author.id)]['xp']=0

            with open("level.json", "w") as f:
              json.dump(data, f)
            
            for i in range(len(level)):
              if new_level == level_num[i]:
                await message.author.add_roles(discord.utils.get(message.author.guild.roles, name=level[i]))

                mbed = discord.Embed(title=f"{message.author} You Have Gotten role **{level[i]}**!", color = message.author.colour)
                mbed.set_thumbnail(url=message.author.avatar_url)
                await message.channel.send(embed=mbed)
        else:
          data[str(message.author.id)] = {}
          data[str(message.author.id)]['xp'] = 0
          data[str(message.author.id)]['level'] = 1

          with open("level.json", "w") as f:
            json.dump(data, f)

  @commands.command(name="rank")
  async def rank(self, ctx: commands.Context, user: Optional[discord.Member]):
    userr = user or ctx.author

    with open("level.json", "r") as f:
      data = json.load(f)

    xp = data[str(userr.id)]["xp"]
    lvl = data[str(userr.id)]["level"]

    next_level_xp = (lvl+1) * 100
    xp_need = next_level_xp
    xp_have = data[str(userr.id)]["xp"]

    percentage = int(((xp_have * 100)/ xp_need))

    if percentage < 1:
      percentage = 0
    
    background = Editor(f"zIMAGE.png")
    profile = await load_image_async(str(userr.avatar_url))

    profile = Editor(profile).resize((150, 150)).circle_image()
    
    poppins = Font.poppins(size=40)
    poppins_small = Font.poppins(size=30)

    ima = Editor("zBLACK.png")
    background.blend(image=ima, alpha=.5, on_top=False)

    background.paste(profile.image, (30, 30))

    background.rectangle((30, 220), width=650, height=40, fill="#fff", radius=20)
    background.bar(
        (30, 220),
        max_width=650,
        height=40,
        percentage=percentage,
        fill="#ff9933",
        radius=20,
    )
    background.text((200, 40), str(userr.name), font=poppins, color="#ff9933")

    background.rectangle((200, 100), width=350, height=2, fill="#ff9933")
    background.text(
        (200, 130),
        f"Level : {lvl}   "
        + f" XP : {xp} / {(lvl+1) * 100}",
        font=poppins_small,
        color="#ff9933",
    )

    card = File(fp=background.image_bytes, filename="zCARD.png")
    await ctx.send(file=card)

  @commands.command(name="leaderboard")
  async def leaderboard(self, ctx, range_num=5):
    with open("level.json", "r") as f:
      data = json.load(f)

    l = {}
    total_xp = []

    for userid in data:
      xp = int(data[str(userid)]['xp']+(int(data[str(userid)]['level'])*100))

      l[xp] = f"{userid};{data[str(userid)]['level']};{data[str(userid)]['xp']}"
      total_xp.append(xp)

    total_xp = sorted(total_xp, reverse=True)
    index=1

    mbed = discord.Embed(
      title="Leaderboard Command Results"
    )

    for amt in total_xp:
      id_ = int(str(l[amt]).split(";")[0])
      level = int(str(l[amt]).split(";")[1])
      xp = int(str(l[amt]).split(";")[2])

      member = await self.bot.fetch_user(id_)

      if member is not None:
        name = member.name
        mbed.add_field(name=f"{index}. {name}",
        value=f"**Level: {level} | XP: {xp}**", 
        inline=False)

        if index == range_num:
          break
        else:
          index += 1

    await ctx.send(embed = mbed)

  @commands.command("rank_reset")
  async def rank_reset(self, ctx, user: Optional[discord.Member]):
    member = user or ctx.author

    if not member == ctx.author:
      role = discord.utils.get(ctx.author.guild.roles, name="Bot-Mod")

      if not role in member.roles:
        await ctx.send(f"You can only reset your data, to reset other data you must have {role.mention} role")
        return 
    
    with open("level.json", "r") as f:
      data = json.load(f)

    del data[str(member.id)]

    with open("level.json", "w") as f:
      json.dump(data, f)

    await ctx.send(f"{member.mention}'s Data Got reset")


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def serverinfo(ctx):
        region = ctx.guild.region
        owner = ctx.guild.owner.mention
        memberCount = ctx.guild.member_count
        all = len(ctx.guild.members)
        icon = ctx.guild.icon_url
        id = ctx.guild.id
        members = len(list(filter(lambda m: not m.bot, ctx.guild.members)))
        bots = len(list(filter(lambda m: m.bot, ctx.guild.members)))
        statuses = [len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "idle", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))]
        channels = [len(list(filter(lambda m: str(m.type) == "text", ctx.guild.channels))),
                    len(list(filter(lambda m: str(m.type) == "voice", ctx.guild.channels)))]
        embed = discord.Embed(title=f"{ctx.guild} information")
        embed.add_field(name="Статусы", value=f"Онлайн: {statuses[0]},   Неактивен: {statuses[1]},   Не беспокоить: {statuses[2]},   Не в сети: {statuses[3]}")
        embed.add_field(name="Участники", value=f"Все: {all},   Люди: {members},   Боты: {bots}")
        embed.add_field(name="Каналы", value=f"Все: {channels[0] + channels[1]},   Текстовые каналы: {channels[0]},   Звуковые каналы: {channels[1]}")
        embed.add_field(name="Сервер ID", value=id, inline=True)
        embed.set_thumbnail(url=icon)
        embed.add_field(name="Регион", value=region)
        embed.add_field(name="Владелец", value=owner)
        embed.add_field(name="Кол-во участников", value=memberCount, inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def userinfo(ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        roles = [role for role in member.roles]
        embed = discord.Embed(title=f"Info {member.name}")
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Ник", value=member.display_name, inline=True)
        embed.add_field(name="Аккаунт создан", value=member.created_at.strftime("%d.%m.%Y %H:%M:%S"), inline=True)
        embed.add_field(name="Присоединился", value=member.joined_at.strftime("%d.%m.%Y %H:%M:%S"), inline=True)
        embed.add_field(name="Роли", value="".join(role.mention for role in roles), inline=True)
        embed.add_field(name="Лучшая роль", value=member.top_role.mention, inline=True)
        embed.add_field(name="Бот?", value=member.bot, inline=True)
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
    async def mute(ctx, member: discord.Member = None, time = None,  *, reason=None):          
        if member is None:
            return await ctx.send("Участник для мьюта не указан")
        if member.bot is True:
                return await ctx.send("Нельзя замьютить бота")
        if member == ctx.author:
            return await ctx.send("Нельзя замьютить самого себя")
        if len(reason) > 70:
            return await ctx.send("Причина слишком большая")
        if member and member.top_role.position >= ctx.author.top_role.position:
            return await ctx.send("Вы не можете замьютить человека чья роль выше вашей")
        
        await member.move_to(channel=None)
        mute = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.add_roles(mute)
        await member.send(f"{member}, вы были замьючены")
        async def unm(member: discord.Member = None):
            mute = discord.utils.get(ctx.guild.roles, name="Muted")
            await member.remove_roles(mute)
            
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
                    await ctx.send(embed=discord.Embed(description=f'Пользователь {member.mention} был замьючен \nВремя: {time} \nПричина: {reason}' ))
                    
                    await asyncio.sleep(time_numbers*t(time_letter))

                    await unm(member)
                    await ctx.send(f'Пользователь {member.mention} размьючен')
                else:
                    await ctx.send(embed=discord.Embed(description=f'Пользователь {member.mention} был замьючен \nВремя: {time}'))
                
                    await asyncio.sleep(time_numbers*t(time_letter))

                    await unm(member)
                    await ctx.send(f'Пользователь {member.mention} размьючен')
            else:
                await ctx.send(embed=discord.Embed(description=f'Пользователь {member.mention} был замьючен'))

                await unm(member)
                await ctx.send(f'Пользователь {member.mention} размьючен')
        else: 
            await ctx.send('Введите имя пользователя')
            
    @commands.command() 
    async def unmute(ctx, member: discord.Member = None, *, reason=None):
        await member.move_to(channel=None)
        mute = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(mute)
        await ctx.send(f'Пользователь {member.mention} был размьючен по причине {reason}')

    @commands.command()
    async def kick(self, ctx, member: discord.Member = None, *, reason:str =None):
        await member.send(f"{member}, вы были кикнуты")
        if member is None:
            return await ctx.send("Участник для кика не указан")
        if member.bot is True:
                return await ctx.send("Нельзя кикнуть бота")
        if member == ctx.author:
            return await ctx.send("Нельзя кикнуть самого себя")
        if len(reason) > 70:
            return await ctx.send("Причина слишком большая")
        if member and member.top_role.position >= ctx.author.top_role.position:
            return await ctx.send("Вы не можете кикнуть человека чья роль выше вашей")
        
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
        if member is None:
            return await ctx.send("Участник для бана не указан")
        if member.bot is True:
            return await ctx.send("Нельзя забанить бота")
        if member == ctx.author:
            return await ctx.send("Нельзя забанить самого себя")
        if member and member.top_role.position >= ctx.author.top_role.position:
            return await ctx.send("Вы не можете забанить человека чья роль выше вашей")

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
                    await member.send(f"{member}, вы были забанены")
                    
                    await asyncio.sleep(time_numbers*t(time_letter))
                    
                    await unb(member)
                    await ctx.send(f'Пользователь {member.mention} разбанен')
                else:
                    await member.ban()
                    await ctx.send(embed=discord.Embed(description=f'Пользователь {member.mention} был забанен \nВремя: {time}'))
                    await member.send(f"{member}, вы были забанены")
                
                    await asyncio.sleep(time_numbers*t(time_letter))
                
                    await unb(member)
                    await ctx.send(f'Пользователь {member.mention} разбанен')
            else:
                await member.ban()
                await ctx.send(embed=discord.Embed(description=f'Пользователь {member.mention} был забанен'))
                await member.send(f"{member}, вы были забанены")
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

    @commands.command()
    async def translate(self, ctx, lang, *, args):
        translator = Translator()
        translation = translator.translate(args, dest=lang)
        await ctx.send(translation.text)
    
    @commands.command()
    async def slap(self, ctx, member):
        embed = discord.Embed(description= f"{member} {(random.choice(slap_name))}")
        embed.set_image(url=(random.choice(slap_gif)))
        await ctx.send(embed=embed)

    @commands.command()
    async def akick(self, ctx, member):
        embed = discord.Embed(description= f"{member} {(random.choice(kick_name))}")
        embed.set_image(url=(random.choice(kick_gif)))
        await ctx.send(embed=embed)

    @commands.command()
    async def shoot(self, ctx, member):
        embed = discord.Embed(description= f"{member} {(random.choice(shoot_name))}")
        embed.set_image(url=(random.choice(shoot_gif)))
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
bot.add_cog(Levels(bot))
bot.run(TOKEN)
