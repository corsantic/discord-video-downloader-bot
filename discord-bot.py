import discord
from discord.ext import commands
import os
import re
from dotenv import load_dotenv

load_dotenv()

TOKEN = str(os.getenv("discord_bot_token"))
SAVE_FOLDER = "videos"
DISCORD_CDN_REGEX = (
    r"https://cdn\.discordapp\.com/attachments/[^\s>]+?\.(mp4|mov|webm|mkv)(\?[^\s>]*)?"
)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.command("ping")
async def ping(ctx):
    print(f"Received ping from {ctx.author}")
    await ctx.send("Pong!")

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@bot.command("get_videos")
async def on_message(ctx):
    discord_message = ctx.message
    user = discord_message.author
    if discord_message.author == bot.user:
        return

    if not user:
        print("Could not retrieve user from the message.")
        await ctx.send("Could not retrieve user from the message.")
        return
    channel = discord_message.channel
    if channel is None:
        print(
            f"Could not find channel. Check bot permissions."
        )
        await ctx.send("Could not find channel. Check bot permissions.")
        return

    try:
        await ctx.send(f"Sending videos to {user.name}")
        async for message in channel.history(limit=None):
            print(f"Checking message {message.id} by {message.author}")
            for attachment in message.attachments:
                if attachment.filename.lower().endswith((".mp4", ".mov", ".webm", ".mkv")):
                    await user.send(f"Attachment from {message.author}: {attachment.url}")
            # Handle CDN links in message content
            for match in re.finditer(DISCORD_CDN_REGEX, message.content):
                url = match.group(0)
                await user.send(f"CDN link from {message.author}: {url}")
        await ctx.send(f"Done sending videos to {user.name}")
    except discord.Forbidden:
        await ctx.send(f"Cannot send messages to {user.name}. Check your privacy settings.")
        print(f"Cannot send messages to {user.name}. Check their privacy settings.")
    except:
        await ctx.send(f"Unexpected error occurred currently cannot send videos")
    return


bot.run(TOKEN)
