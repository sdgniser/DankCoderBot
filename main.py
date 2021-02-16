import discord, praw
import os, random, threading
from discord.ext import commands
from replit import db
from datetime import datetime
from keep_alive import keep_alive


TOKEN = os.getenv("TOKEN")

bot = commands.Bot(command_prefix="def ", help_command=None)

reddit = praw.Reddit()
subreddit = reddit.subreddit("ProgrammerHumor")
trigger_words = ["dank", "dankness"]
spooky_triggers = ["does", "how", "look", "does this", "how is"]
dank_texts = [
    "Don't wanna!",
    "Busy coding. You should be too!",
    "Uh... nah!",
    "Nah!",
    "Go to `/dev/null!`",
    "WHO SUMMONED ME?",
    "Ahh, you think dankness is your ally? You merely adopted the dank. I was born in it. Molded by it.",
]
# RECURSION_THRESHOLD = 1  # Will crash the bot
SPOOKINESS_THRESHOLD = 0.1
DANKNESS_THRESHOLD = 0.2

MEMES_CACHED = False
DEFAULT_MEME = "https://othersideoz.ca/blog_images/eoi.jpg"


# To clear MEMES_CACHED
def resetCache():
    global MEMES_CACHED
    # This function runs periodically every 1 second
    threading.Timer(1, resetCache).start()

    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")

    if current_time == '00:22:00':  # GMT == 0330 IST
        db.clear()
        MEMES_CACHED = False
        print('MEMES_CACHED cleared!')


def cache_memes():
    global MEMES_CACHED

    if "memes" not in db.keys():
        db["memes"] = {
            "urls": [DEFAULT_MEME,],
            "accessed": [False,],
        }

    MEMES = db["memes"]
    posts = subreddit.hot(limit=100)
    exts = ("jpg", "jpeg", "png")
    for submission in posts:
        url = str(submission.url)
        if url.endswith(exts):
            MEMES["urls"].append(url)

    if len(MEMES["urls"]) >= 2:
        db["memes"] = MEMES
        MEMES_CACHED = True


def get_meme():
    global MEMES_CACHED
    if not MEMES_CACHED:
        cache_memes()

    MEMES = db["memes"]
    urls = MEMES["urls"]

    if urls:
        return random.sample(urls, 1)[0]

    return urls[0]

@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready to spread dankness now.")


@bot.command(name="help", help="Shows help message and list of commands")
async def help(ctx):
    file = discord.File('./master.png')
    embed = discord.Embed(
        title="Help for DankCoder",
        description="List of commands for DankCoder",
        colour=discord.Colour.blurple(),
    )
    embed.set_thumbnail(url="attachment://master.png")
    embed.set_image(url="attachment://master.png")
    embed.add_field(name="def help", value="Shows help message and list of commands", inline=False)
    embed.add_field(name="def hello", value="Says hello", inline=False)
    embed.add_field(name="def meme", value="Shares a meme from r/ProgrammerHumor", inline=False)
    await ctx.channel.send(content=None, file=file, embed=embed)


@bot.command(name="hello", help="Says hello")
async def hello(ctx):
    await ctx.channel.send("Hello there!")


@bot.command(name="meme", help="Shares a meme from r/ProgrammerHumor")
async def meme(ctx):
    await ctx.channel.send(get_meme())


@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise


@bot.event
async def on_message(message):
    # Prefix == "def"
    msg = message.content

    # if msg.lower().startswith('recursion'):
    #     i = 0
    #     while i < 5:
    #         if random.random() < RECURSION_THRESHOLD:
    #             await message.channel.send("Recursion?!")
    #         i += 1

    #     await message.channel.send("Aw snap! I am written in Python. Guess I'll die ¯\_(ツ)_/¯.")

    if message.author == bot.user:
        return

    if msg.lower().startswith('general kenobi'):
        await message.channel.send("You are a bold one!")

    if any(word in msg for word in spooky_triggers):
        if random.random() < SPOOKINESS_THRESHOLD:
            await message.channel.send("_It doesn't look like anything to me._"
                                       )

    if any(word in msg for word in trigger_words):
        if random.random() < DANKNESS_THRESHOLD:
            await message.channel.send(random.sample(dank_texts, 1)[0])

        else:
            await message.channel.send(get_meme())

    await bot.process_commands(message)


resetCache()
keep_alive()
bot.run(TOKEN)
