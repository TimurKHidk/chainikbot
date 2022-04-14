import discord
import aiohttp
from discord.ext import commands
import random


TOKEN ='OTYzODExMTU0NzE3NzI4Nzc4.YlbhFg.Dd7I1Df0L4Qggqv56EJsGwcpzAQ'
bot = commands.Bot(command_prefix=('+'))

@bot.command()    
async def mem(ctx):
        embed = discord.Embed(title="Memes", description="memes from reddit")  
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://www.reddit.com/r/memes/new.json?sort=hot') as r:
                res = await r.json()
                embed.set_image(url=res['data']['children'] [random.randint(0, 25)]['data']['url'])
                await ctx.send(embed=embed)

bot.run(TOKEN)
