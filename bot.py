import discord
import asyncpraw
import asyncio


TOKEN ='OTYzODExMTU0NzE3NzI4Nzc4.YlbhFg.Dd7I1Df0L4Qggqv56EJsGwcpzAQ'
bot = discord.Client()
reddit = asyncpraw.Reddit(client_id='sT4hZMkd5hT3srsoB_brQg' , 
                          client_secret='SCOzIjdxIvbmev7Y68lVJGAw8QMg8w',
                          user_agent='random_raddit_bot/0.0.1')

mems = []
timeout = 5
channel_id = 963510501353062453
reddit = 'memes'
plimit = 1


@bot.event
async def on_ready():
    channel = bot.get_channel(channel_id)
    while True:
        await asyncio.sleep(timeout)
        memes_submissions = await reddit.subreddit(reddit)
        memes_submissions = memes_submissions.hot(limit=plimit)
        item = await memes_submissions.__anext__()
        if item.title not in mems:
            mems.append(item.title)
            await channel.send(item.url)

bot.run(TOKEN)
