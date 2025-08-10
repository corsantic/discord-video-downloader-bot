import discord
from discord.ext import commands
import aiohttp
import os
import re
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

TOKEN = str(os.getenv("discord_bot_token"))
# CHANNEL_ID = int(input("Enter the Discord channel ID: "))
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


async def attachment_download(attachments, channel_folder):
    for attachment in attachments:
        print(f"Found attachment: {attachment.filename}")
        if attachment.filename.lower().endswith((".mp4", ".mov", ".webm", ".mkv")):
            filepath = os.path.join(channel_folder, attachment.filename)
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as resp:
                    if resp.status == 200:
                        with open(filepath, "wb") as f:
                            f.write(await resp.read())
                        print(f"Downloaded: {attachment.filename}")

async def download_from_cdn(url, channel_folder, message):
    for match in re.finditer(DISCORD_CDN_REGEX, message.content):
        url = match.group(0)
        filename = urlparse(url).path.split("/")[-1]
        filepath = os.path.join(channel_folder, filename)
        print(f"Attempting to download: {url}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    print(f"HTTP status: {resp.status}")
                    if resp.status == 200:
                        with open(filepath, "wb") as f:
                            f.write(await resp.read())
                        print(f"Downloaded from link: {filename}")
                    else:
                        print(f"Failed to download {filename}: HTTP {resp.status}")
        except Exception as e:
            print(f"Exception while downloading {url}: {e}")
     
bot.run(TOKEN)
