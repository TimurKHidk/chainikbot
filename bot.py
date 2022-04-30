import discord
import string
import aiohttp
from discord.ext import commands
from discord.utils import get
import random
from youtube_dl import YoutubeDL
import asyncio
from googletrans import Translator
import json
from easy_pil import Editor, load_image_async, Font
from discord import File
from typing import Optional
import sqlite3


YDL_OPTIONS = {'format': 'worstaudio/best', 'noplaylist': 'False', 'simulate': 'True',
               'preferredquality': '192', 'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
TOKEN ='OTYzODExMTU0NzE3NzI4Nzc4.YlbhFg.IixX3rh0xIPbNJY94oSkwdZEsV0'
PREFIX = '+'
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=('+'), intents=intents)
bot.remove_command( 'help' )
level = ["Плох", "Неплох", "Хорош", "Ультра Хорош", "Мега Хорош"]
level_num = [5, 10, 15, 20, 30]
slap_gif = ["https://c.tenor.com/LiTeUfKB6HQAAAAC/batman-slap-in-the-face.gif", "https://c.tenor.com/3vxOt6Xi_AEAAAAC/will-smith-chris-rock.gif",
            "https://c.tenor.com/GpZ13hpY0ioAAAAC/slap-slapping.gif"]
slap_name = ["Неплохой вышел удар"]
shoot_gif = ["https://c.tenor.com/ZdUfN4OREUMAAAAC/shooting-a-machine-gun-vanguard.gif", "https://c.tenor.com/7w5mpGst604AAAAC/shooting-rambo.gif",
             "https://c.tenor.com/cEeghP8C-HgAAAAC/shepherds-delight-shephards-delight.gif"]
shoot_name = ["Теперь ты как Николай 2"]
kick_gif = ["https://c.tenor.com/PyMWkVnBTp0AAAAC/dropkick-fight.gif", "https://c.tenor.com/iodpOeOGEkkAAAAC/dropkick-waterboy.gif", 
            "https://c.tenor.com/Gf6UTsRayw4AAAAC/kickers-caught.gif"]
kick_name = ["Как анти air в мк"]


#при писоеденении приветсвует
@bot.event
async def on_member_join(member):
        channel = bot.get_channel(963510501353062453)
        
        background = Editor("WELCOME.png")
       
        profile_image = await load_image_async(str(member.avatar_url))
        profile = Editor(profile_image).resize((150, 150)).circle_image()
        
        poppins = Font.poppins(size=50, variant="bold")
        poppins_small = Font.poppins(size=20, variant="light")
        
        background.paste(profile, (325, 90))
        background.ellipse((325, 90), 150, 150, outline="gold", stroke_width=4)
        
        background.text((400, 260), f"Welcome to our server", color="white", font=poppins, align="center")
        background.text((400, 325), f"{member.name}#{member.discriminator}", color="white", font=poppins_small, align="center")
        
        file = File(fp=background.image_bytes, filename="WELCOME.png")
        await channel.send(file=file)
#при уходе прощается        
@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(963510501353062453)
    await channel.send(f"{member.name} Покинул нас")


class UserContext(commands.Cog):

    def __init__(self, bot):
        self.bot = bot   
    #бот подключает базу данных
    @commands.Cog.listener()
    async def on_ready(self):
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Кинопоиск"))
        
        global base, cur
        base = sqlite3.connect('chainikbot.db')
        cur = base.cursor()
        if base:
            print('База данных подключена')
    #бот выдает статус по полученым пользователем предупреждениям        
    @commands.command()
    async def status(self, ctx):
        base.execute('CREATE TABLE IF NOT EXISTS {}(userid INT, count INT)'.format(ctx.message.guild.name))
        base.commit()
        warning = cur.execute('SELECT * FROM {} WHERE userid == ?'.format(ctx.message.guild.name),(ctx.message.author.id,)).fetchone()
        if warning == None:
            await ctx.send(f'{ctx.message.author.mention},  у вас нет предупреждений')
        else:
            await ctx.send(f'{ctx.message.author.mention},  у вас {warning[1]} предупреждений')
    #за запрещенное слово(слова лежат в json файле) в сообщениях пользователя он получает предупреждение а его сообщение удаляется        
    @commands.Cog.listener()
    async def on_message(self, message):
        if {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.content.split(' ')}.intersection(set(json.load(open('chainikbotdb.json')))) != set():
            await message.channel.send(f'{message.author.mention}, как тебе не стыдно такие слова использовать??')
            await message.delete()
            #создание таблицы в бд
            name = message.guild.name
            base.execute('CREATE TABLE IF NOT EXISTS {}(userid INT, count INT)'.format(name))
            base.commit()
            #предупреждения
            warning = cur.execute('SELECT * FROM {} WHERE userid == ?'.format(name),(message.author.id,)).fetchone()
            #пользователь без предупреждение его получает
            if warning == None:
                cur.execute('INSERT INTO {} VALUES(?, ?)'.format(name),(message.author.id, 1)).fetchone()
                base.commit()
                await message.channel.send(f'{message.author.mention}, первое предупреждение, на 3 - бан')
            #второе предупреждение    
            elif warning[1] == 1:
                cur.execute('UPDATE {} SET count == ? WHERE userid == ?'.format(name),(2,message.author.id))
                base.commit()
                await message.channel.send(f'{message.author.mention}, уже 2 предупреждения, на 3 бан')
            #третье предупреждение и бан    
            elif warning[1] == 2:
                cur.execute('UPDATE {} SET count == ? WHERE userid == ?'.format(name), (3,message.author.id))
                base.commit()
                await message.channel.send(f'{message.author.mention}, забанен за мат в чате')
                await message.author.ban()


class Levels(commands.Cog):
  
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def lhelp(self, ctx):
    embed = discord.Embed(title='Уровни', description="за каждое сообщение по 25Xp")
    embed.add_field(name='{}rank'.format(PREFIX), value='Показывает вашу карточку с уровнем и опытом(чтобы просмтреть чужую укажите ник через @)')
    embed.add_field(name='{}rank_reset'.format(PREFIX), value='Для сброса чужой роли у вас должна быть роль выше')   
    await ctx.send(embed=embed)
  #Команда считывающая все сообщения пользователя и начисляющая за них опыт и уровень
  @commands.Cog.listener()
  async def on_message(self, message):

    #Проверка на использование команд(если используется комманда то очки не начисляются)
    if not message.content.startswith("+"):
      #Проверка, не отправил ли бот сообщение. Считывание файла json
      if not message.author.bot:
        with open("level.json", "r") as f:
          data = json.load(f)
        #Проверка на наличие пользователя и его стат в файле
        if str(message.author.id) in data:
          xp = data[str(message.author.id)]['xp']
          lvl = data[str(message.author.id)]['level']
          #Повышение опыта и условия для нового уровня
          increased_xp = xp+25
          new_level = int(increased_xp/100)
          #Записывание новой статы опыта при его повышении 
          data[str(message.author.id)]['xp']=increased_xp

          with open("level.json", "w") as f:
            json.dump(data, f)
          #проверка на повышение уровня
          if new_level > lvl:
            await message.channel.send(f"{message.author.mention} поднял уровень до {new_level}!!!")
            #записывание в файл новых данных
            data[str(message.author.id)]['level']=new_level
            data[str(message.author.id)]['xp']=0

            with open("level.json", "w") as f:
              json.dump(data, f)
            #Получение роли при достижении уровня
            for i in range(len(level)):
              if new_level == level_num[i]:
                await message.author.add_roles(discord.utils.get(message.author.guild.roles, name=level[i]))
                embed = discord.Embed(title=f"{message.author} Вы получили роль **{level[i]}**!", color = message.author.colour)
                embed.set_thumbnail(url=message.author.avatar_url)
                await message.channel.send(embed=embed)
        else: #если пользователя нет в файле все статы дефолтны
          data[str(message.author.id)] = {}
          data[str(message.author.id)]['xp'] = 0
          data[str(message.author.id)]['level'] = 1

          with open("level.json", "w") as f:
            json.dump(data, f)
  #команда для получения ранга 
  @commands.command()
  async def rank(self, ctx: commands.Context, user: Optional[discord.Member]):
    member = user or ctx.author

    with open("level.json", "r") as f:
      data = json.load(f)
    #отображение уже имеющихся стат
    xp = data[str(member.id)]["xp"]
    lvl = data[str(member.id)]["level"]
    #отображение икспы для след лвла  и кол во имеющийся экспы
    next_level_xp = (lvl+1) * 100
    xp_need = next_level_xp
    xp_have = data[str(member.id)]["xp"]
    #линия экспы
    percentage = int(((xp_have * 100)/ xp_need))
    #если линия заполнена то она сбрасывается
    if percentage < 1:
        percentage = 0
    #карточка ранка
    background = Editor(f"IMAGE.png")
    profile = await load_image_async(str(member.avatar_url))

    profile = Editor(profile).resize((150, 150)).circle_image()
    
    poppins = Font.poppins(size=40)
    poppins_small = Font.poppins(size=30)

    ima = Editor("BLACK.png")
    background.blend(image=ima, alpha=.5, on_top=False)
    background.paste(profile.image, (30, 30))
    background.rectangle((30, 220), width=650, height=40, fill="#fff", radius=20)
    background.bar((30, 220), max_width=650, height=40, percentage=percentage, fill="red", radius=20)
    background.text((200, 40), str(member.name), font=poppins, color="red")
    background.rectangle((200, 100), width=350, height=2, fill="red")
    background.text((200, 130), f"Level : {lvl}   " + f" XP : {xp} / {(lvl+1) * 100}", font=poppins_small, color="red")

    card = File(fp=background.image_bytes, filename="CARD.png")
    await ctx.send(file=card)
  #команда для сброса ранга
  @commands.command()
  async def rank_reset(self, ctx: commands.Context, user: Optional[discord.Member]):
    member = user or ctx.author
    
    if member and member.top_role.position >= ctx.author.top_role.position:
      return await ctx.send("Вы не можете сбрасывать ранг людям чья роль выше вашей")
    
    with open("level.json", "r") as f:
      data = json.load(f)
    #удаление всего связаного с пользователем
    del data[str(member.id)]

    with open("level.json", "w") as f:
      json.dump(data, f)

    await ctx.send(f"{member.mention}'s ранк сброшен")


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mhelp(self, ctx):
        embed = discord.Embed(title='Модерация')
        embed.add_field(name='{}serverinfo'.format(PREFIX), value='Выдает информацию по серверу')
        embed.add_field(name='{}userinfo'.format(PREFIX), value='Выдает информацию по участнику сервера(указать через @)')
        embed.add_field(name='{}mute'.format(PREFIX), value='Мьютит пользователя(при желании указать время и причину через пробел)')
        embed.add_field(name='{}unmute'.format(PREFIX), value='Размьючивает пользователя(указать через @)')
        embed.add_field(name='{}ban'.format(PREFIX), value='Банит пользователя(при желании указать время и причину через пробел)')
        embed.add_field(name='{}kick'.format(PREFIX), value='Кикает пользователя(при желании указать причину через пробел)')
        embed.add_field(name='{}clear'.format(PREFIX), value='Чистит чат (количество сообщений для очистки указать через пробел)')   
        await ctx.send(embed=embed)

    #Выдает инфу по серверу 
    @commands.command()
    async def serverinfo(self, ctx):
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
    #Выдает инфу по указанному пользователю
    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
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
        embed = discord.Embed(title='Help menu')
        embed.add_field(name='{}mhelp'.format(PREFIX), value='Для помощи в модерации')
        embed.add_field(name='{}lhelp'.format(PREFIX), value='Для помощи в системе уровней')
        embed.add_field(name='{}musichelp'.format(PREFIX), value='Для помощи с музыкой')
        embed.add_field(name='{}inthelp'.format(PREFIX), value='Для помощи с интерактивными командами')   
        await ctx.send(embed=embed)
    #команда для мута
    @commands.command()
    async def mute(self, ctx, member: discord.Member = None, time = None,  *, reason=None):          
        #Проверка на мут бота админа самого себя
        if member.bot is True:
                return await ctx.send("Нельзя замьютить бота")
        if member == ctx.author:
            return await ctx.send("Нельзя замьютить самого себя")
        if member and member.top_role.position >= ctx.author.top_role.position:
            return await ctx.send("Вы не можете замьютить человека чья роль выше вашей")
        #Добавляет роль и мутит пользователя
        await member.move_to(channel=None)
        mute = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.add_roles(mute)
        #Проверка на указание участника для мута    
        if member:
            if time:#Проверка на то указано ли время к муту.И постановка определенных букв для указания секунд минут часов дней 
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
                #Проверка на указание причины        
                if reason:
                    await ctx.send(embed=discord.Embed(description=f'Пользователь {member.mention} был замьючен \nВремя: {time} \nПричина: {reason}' ))
                    await member.send(f"{member}, вы были замьючены на {time}  и по причине {reason}")

                    await asyncio.sleep(time_numbers*t(time_letter))

                    await member.remove_roles(mute)
                    await ctx.send(f'Пользователь {member.mention} размьючен')
                else:
                    await ctx.send(embed=discord.Embed(description=f'Пользователь {member.mention} был замьючен \nВремя: {time}'))
                    await member.send(f"{member}, вы были замьючены на {time}")
                
                    await asyncio.sleep(time_numbers*t(time_letter))

                    await member.remove_roles(mute)
                    await ctx.send(f'Пользователь {member.mention} размьючен')
            else:
                await ctx.send(embed=discord.Embed(description=f'Пользователь {member.mention} был замьючен'))
                await member.send(f"{member}, вы были замьючены")
        else: 
            await ctx.send('Введите имя пользователя')
    #Размут пользователя        
    @commands.command() 
    async def unmute(self, ctx, member: discord.Member = None, *, reason=None):
        await member.move_to(channel=None)
        mute = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(mute)
        await ctx.send(f'Пользователь {member.mention} был размьючен по причине {reason}')
    #команда для кика
    @commands.command()
    async def kick(self, ctx, member: discord.Member = None, *, reason:str =None):
        #Проверка на кик бота админа самого себя
        if member.bot is True:
                return await ctx.send("Нельзя кикнуть бота")
        if member == ctx.author:
            return await ctx.send("Нельзя кикнуть самого себя")
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
    #Команда для очистки указаного кол во сообщений        
    @commands.command()
    async def clear(self, ctx, count: int):
        await ctx.channel.purge(limit=count+1)
        await ctx.send(f"Было удаленно {count} сообщений")
    #Банит пользователя    
    @commands.command()
    async def ban(self, ctx, member: discord.Member = None, time = None, *, reason: str = None):
        #Проверка на попытк забанить админов бота самго себя
        if member.bot is True:
            return await ctx.send("Нельзя забанить бота")
        if member == ctx.author:
            return await ctx.send("Нельзя забанить самого себя")
        if member and member.top_role.position >= ctx.author.top_role.position:
            return await ctx.send("Вы не можете забанить человека чья роль выше вашей")
        #Функция автоматического разбана если указано время
        async def unb(member):
            users = await ctx.guild.bans()
            for ban_user in users:
                if ban_user.user == member:
                    await ctx.guild.unban(ban_user.user)
        #Проверка на указание пользователя для бана        
        if member:
            if time:#Проверка на то указано ли время к бану.И постановка определенных букв для указания секунд минут часов дней 
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
                #Проверка на указание причины        
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
    async def inthelp(self, ctx):
        embed = discord.Embed(color=0x00ffff, title='Интерактив')
        embed.add_field(name='{}mem'.format(PREFIX), value='Выдает мем с реддита')
        embed.add_field(name='{}news'.format(PREFIX), value='Выдает новость с реддита и ссылку на нее')
        embed.add_field(name='{}translate'.format(PREFIX), value='Переводит текст(указать язык на который надо переести и сам текст)')
        embed.add_field(name='{}slap'.format(PREFIX), value='Гифки XD(такие же только shoot и akick)')
        embed.add_field(name='{}chnick'.format(PREFIX), value='Смена никнейма(указать пользователя и ник на который менять)')
        embed.add_field(name='{}calc'.format(PREFIX), value='Указать тип операции и 2 числа(все через пробел)')
        await ctx.send(embed=embed)
    #Получаем мем с реддита в json а потом рандомно вытаскиваем его оттуда    
    @commands.command()
    async def mem(self, ctx):
        embed = discord.Embed(title="Memes", description="memes from reddit")  
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://www.reddit.com/r/memes/new.json?sort=hot') as r:
                res = await r.json()
                embed.set_image(url=res['data']['children'] [random.randint(0, 25)]['data']['url'])
                await ctx.send(embed=embed)
    #Получаем новость с реддита в json а потом рандомно вытаскиваем его оттуда
    @commands.command()
    async def news(self, ctx):
        embed = discord.Embed(title="News")  
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://www.reddit.com/r/news/new.json?sort=hot') as r:
                res = await r.json()
                embed.add_field(name='news from reddit', value=res['data']['children'] [random.randint(0, 25)]['data']['url'])
                await ctx.send(embed=embed)
    #Команда для перевода текста написанного пользователем
    @commands.command()
    async def translate(self, ctx, lang, *, args):
        translator = Translator()
        translation = translator.translate(args, dest=lang)
        await ctx.send(translation.text)
    #Эмбед с гифкой
    @commands.command()
    async def slap(self, ctx, member):
        embed = discord.Embed(description= f"{member} {(random.choice(slap_name))}")
        embed.set_image(url=(random.choice(slap_gif)))
        await ctx.send(embed=embed)
    #Эмбед с гифкой
    @commands.command()
    async def akick(self, ctx, member):
        embed = discord.Embed(description= f"{member} {(random.choice(kick_name))}")
        embed.set_image(url=(random.choice(kick_gif)))
        await ctx.send(embed=embed)
    #Эмбед с гифкой
    @commands.command()
    async def shoot(self, ctx, member):
        embed = discord.Embed(description= f"{member} {(random.choice(shoot_name))}")
        embed.set_image(url=(random.choice(shoot_gif)))
        await ctx.send(embed=embed)
    #Меняет ник пользователю
    @commands.command()
    async def chnick(self, ctx, member: discord.Member, nick = None):
        await member.edit(nick=nick)
        await ctx.send(f'Ник поменялся на {member.mention} ')
    #Команда проверяет на наличе оператора и если они есть то считает числа
    @commands.command()
    async def calculate(self, ctx, operation, *, nums):
        if operation not in ['+', '-', '*', '/']:
            await ctx.send('Введите тип операции')     
        var = f' {operation} '.join(nums)
        await ctx.send(f'{var} = {eval(var)}')
    

class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def musichelp(self, ctx):
        embed = discord.Embed(color=0x00ffff, title='Помощь с музыкой', description="вы должны быть в звуковом канале")
        embed.add_field(name='{}play'.format(PREFIX), value='Заходит в канал и включает аудио по ссылке ютуба(или по его названию)')
        embed.add_field(name='{}stop'.format(PREFIX), value='останавливает аудио')
        embed.add_field(name='{}pause'.format(PREFIX), value='ставит аудио на паузу')
        embed.add_field(name='{}resume'.format(PREFIX), value='снимает аудио с паузы')
        embed.add_field(name='{}join'.format(PREFIX), value='бот заходит в звуковой канал')
        embed.add_field(name='{}leave'.format(PREFIX), value='бот покидает звуковой канал')   
        await ctx.send(embed=embed) 
    #Присоединяется к звуковому каналу
    @commands.command()
    async def join(self, ctx):
        global voice
        channel = ctx.message.author.voice.channel
        voice = discord.utils.get(bot.voice_clients, guild = ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()
    #Покидает звуковой канал
    @commands.command()
    async def leave(self, ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice.is_connected():
            await voice.disconnect()
        else:
            await ctx.send("В данный момент бот не в звуковом канале")
    #Проигрывает музыку с ютуба. Проверяет на то что прислал пользователь(ссылку или название)        
    @commands.command()
    async def play(self, ctx, *, arg):
        with YoutubeDL(YDL_OPTIONS) as ydl:
            voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            if 'https://' in arg:
                info = ydl.extract_info(arg, download=False)
            else:
                info = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]            
        
        url = info['formats'][0]['url']
        voice.play(discord.FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=url, **FFMPEG_OPTIONS))
    #Ставит музыку на паузу 
    @commands.command()
    async def pause(self, ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.pause()
        else:
            await ctx.send("В данный момент музыка не играет")
    #Если музыка на паузе то снимает
    @commands.command()
    async def resume(self, ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice.is_paused():
            voice.resume()
        else:
            await ctx.send("Музыка не стоит на паузе")
    #Останавливает проигрыш музыки
    @commands.command()
    async def stop(self, ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        voice.stop()


bot.add_cog(Moderation(bot))
bot.add_cog(Interactive(bot))
bot.add_cog(Music(bot))
bot.add_cog(Levels(bot))
bot.add_cog(UserContext(bot))
bot.run(TOKEN)
