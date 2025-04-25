import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from config import DISCORD_TOKEN, GUILD_ID

# Load environment variables
load_dotenv()

# Set up intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Initialize bot
bot = commands.Bot(command_prefix="/", intents=intents)
bot.remove_command("help")

# Track whether we've synced already
has_synced = False

@bot.event
async def on_ready():
    global has_synced

    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

    if not has_synced:
        print("🔄 Loading cogs...")
        await load_extensions()

        print("🔄 Syncing slash commands...")
        try:
            synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
            print(f"✅ Synced {len(synced)} slash commands to guild {GUILD_ID}")
            has_synced = True
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")

    await bot.change_presence(activity=discord.Game(name="Serving Rogue Legion"))

async def load_extensions():
    extensions = [
        "cogs.onboarding",
        "cogs.flag_bot",
        "commands.user_commands",
        "commands.admin_commands"
    ]
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"✅ Loaded: {ext}")
        except Exception as e:
            print(f"❌ Failed to load {ext}: {e}")

# Run the bot
async def main():
    async with bot:
        await bot.start(DISCORD_TOKEN)

import asyncio
asyncio.run(main())