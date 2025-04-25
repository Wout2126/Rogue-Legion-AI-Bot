import discord
from discord.ext import commands
import logging
import asyncio
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

# Logger (optional but recommended)
logging.basicConfig(level=logging.INFO)
bot.logger = logging.getLogger("bot")

# Track sync state
has_synced = False

@bot.event
async def on_ready():
    global has_synced

    bot.logger.info(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

    if not has_synced:
        bot.logger.info("🔄 Loading cogs and commands...")
        await load_extensions()

        bot.logger.info("🔄 Syncing slash commands...")
        try:
            synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
            bot.logger.info(f"✅ Synced {len(synced)} slash commands to guild {GUILD_ID}")
            has_synced = True
        except Exception as e:
            bot.logger.error(f"❌ Failed to sync commands: {e}")

    await bot.change_presence(activity=discord.Game(name="Serving Rogue Legion"))

async def load_extensions():
    # Load static cogs
    static_cogs = [
        "cogs.onboarding",
        "cogs.flag_bot"
    ]
    for ext in static_cogs:
        try:
            await bot.load_extension(ext)
            bot.logger.info(f"✅ Loaded: {ext}")
        except Exception as e:
            bot.logger.error(f"❌ Failed to load {ext}: {e}")

    # Load dynamic command groups (admin, user)
    command_groups = [
        "commands.admin_commands",
        "commands.user_commands"  # Add if necessary
    ]
    
    for group in command_groups:
        try:
            await bot.load_extension(group)
            bot.logger.info(f"✅ Loaded: {group}")
        except Exception as e:
            bot.logger.error(f"❌ Failed to load {group}: {e}")

# Run the bot
bot.run(DISCORD_TOKEN)
