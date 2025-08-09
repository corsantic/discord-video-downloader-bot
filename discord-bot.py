import discord
import aiohttp
import os
import re
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

TOKEN = str(os.getenv("discord_bot_token"))
CHANNEL_ID = int(input("Enter the Discord channel ID: "))
SAVE_FOLDER = "videos"
DISCORD_CDN_REGEX = (
    r"https://cdn\.discordapp\.com/attachments/[^\s>]+?\.(mp4|mov|webm|mkv)(\?[^\s>]*)?"
)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print(
            f"Could not find channel with ID {CHANNEL_ID}. Check bot permissions and channel ID."
        )
        await client.close()
        return

    channel_folder = os.path.join(SAVE_FOLDER, str(channel.id))
    if not os.path.exists(channel_folder):
        os.makedirs(channel_folder, exist_ok=True)

    async for message in channel.history(limit=None):
        print(f"Checking message {message.id} by {message.author}")
        # Handle Attachments
        for attachment in message.attachments:
            print(f"Found attachment: {attachment.filename}")
            if attachment.filename.lower().endswith((".mp4", ".mov", ".webm", ".mkv")):
                filepath = os.path.join(channel_folder, attachment.filename)
                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment.url) as resp:
                        if resp.status == 200:
                            with open(filepath, "wb") as f:
                                f.write(await resp.read())
                            print(f"Downloaded: {attachment.filename}")
        # Handle CDN links in message content
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

    await client.close()


client.run(TOKEN)
