import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from config import DISCORD_TOKEN, GUILD_ID

# Load environment variables
load_dotenv()

# Set up intents (includes member events for onboarding, etc.)
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Initialize the bot
bot = commands.Bot(command_prefix="/", intents=intents)
bot.remove_command("help")  # Remove default help command

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="Serving Rogue Legion"))

# Load extensions/cogs
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

    # Sync slash commands to specific guild
    print("🔄 Syncing slash commands...")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"✅ Synced {len(synced)} slash commands to guild {GUILD_ID}")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

# Main bot runner
async def main():
    async with bot:
        await load_extensions()
        await bot.start(DISCORD_TOKEN)

import asyncio
asyncio.run(main())