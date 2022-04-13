import discord
import asyncpraw
import asyncio
import config

bot = discord.Client()
reddit = asyncpraw.Reddit(client_id=config.settings['client_id'],
                          client_secret=config.settings['secret_code'],
                          user_agent='random_raddit_bot/0.0.1')

memess = []
timeout = 120
channel_id = 963510501353062453
reddit = 'memes'
limit = 1


@bot.event
async def on_ready():
    channel = bot.get_channel(channel_id)
    while True:
        await asyncio.sleep(timeout)
        memes_submissions = await reddit.subreddit(reddit)
        memes_submissions = memes_submissions.new(limit=limit)
        item = await memes_submissions.__anext__()
        if item.title not in memess:
            memess.append(item.title)
            await channel.send(item.url)


bot.run(config.settings['dc_token'])
