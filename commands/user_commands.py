import discord
from discord.ext import commands
import datetime
import asyncio

# Bot setup
intents = discord.Intents.default()
intents.message_content = True  # Make sure the bot can read message content
bot = commands.Bot(command_prefix='/', intents=intents)

# Load usercommands.txt file for /help
def load_help_text():
    try:
        with open('data/usercommands.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Help text file not found."

# Commands

# /help command to show help text
@bot.command(name="help", help="Get a list of all available commands")
async def help_command(ctx):
    help_text = load_help_text()
    await ctx.send(help_text)

# /userinfo command to display user information
@bot.command(name="userinfo", help="Get information about yourself")
async def userinfo(ctx):
    user = ctx.author
    embed = discord.Embed(title=f"{user.name}'s Info", color=discord.Color.blue())
    embed.add_field(name="Username", value=user.name, inline=False)
    embed.add_field(name="ID", value=user.id, inline=False)
    embed.add_field(name="Account Created", value=user.created_at.strftime("%B %d, %Y"), inline=False)
    embed.add_field(name="Joined Server", value=user.joined_at.strftime("%B %d, %Y"), inline=False)
    embed.add_field(name="Roles", value=", ".join([role.name for role in user.roles[1:]]), inline=False)
    await ctx.send(embed=embed)

# /serverinfo command to display server information
@bot.command(name="serverinfo", help="Get information about the server")
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"{guild.name} Server Info", color=discord.Color.green())
    embed.add_field(name="Server Name", value=guild.name, inline=False)
    embed.add_field(name="Server ID", value=guild.id, inline=False)
    embed.add_field(name="Total Members", value=guild.member_count, inline=False)
    embed.add_field(name="Server Created", value=guild.created_at.strftime("%B %d, %Y"), inline=False)
    embed.add_field(name="Region", value=guild.region, inline=False)
    embed.add_field(name="Roles", value=", ".join([role.name for role in guild.roles[1:]]), inline=False)
    await ctx.send(embed=embed)

# /ping command to check bot's latency
@bot.command(name="ping", help="Check the bot's latency")
async def ping(ctx):
    latency = round(bot.latency * 1000)  # Convert to ms
    await ctx.send(f"Pong! Latency is {latency}ms")

# /vote command to create a vote with emoji reactions
@bot.command(name="vote", help="Create a poll with options")
async def vote(ctx, question: str, *options: str):
    if len(options) < 2:
        await ctx.send("You need at least 2 options to create a vote.")
        return

    # Get time limit if provided
    time_limit = None
    if len(options) > 2 and options[-2].startswith("time:"):
        time_limit_str = options[-2][5:]
        try:
            time_limit = datetime.datetime.strptime(time_limit_str, "%Y-%m-%d %H:%M:%S")
            options = options[:-2]  # Remove the time option from the list
        except ValueError:
            await ctx.send("Invalid date format. Please use YYYY-MM-DD HH:MM:SS.")
            return
    elif len(options) > 2 and options[-1].startswith("hours:"):
        try:
            hours = int(options[-1][6:])
            time_limit = datetime.datetime.utcnow() + datetime.timedelta(hours=hours)
            options = options[:-1]  # Remove the time option from the list
        except ValueError:
            await ctx.send("Invalid number of hours.")
            return

    # Prepare the poll message with formatting
    poll_message = f"||**Poll**: {question}||\n\n"
    emojis = ['🇦', '🇧', '🇨', '🇩', '🇪']
    for i, option in enumerate(options):
        poll_message += f"{emojis[i]}: {option}\n"

    # Send the message with the poll question
    poll_message = await ctx.send(f"**Poll started!** {poll_message}")

    # Add reactions for each option
    for i in range(len(options)):
        await poll_message.add_reaction(emojis[i])

    # Wait for the timeout if any
    if time_limit:
        await asyncio.sleep((time_limit - datetime.datetime.utcnow()).total_seconds())
        await poll_message.channel.send(f"The poll has ended! {question}")
        # Optionally, you can tally the votes here

# /status command to show bot status (could include custom statuses, up-time, etc.)
@bot.command(name="status", help="Show the bot's current status")
async def status(ctx):
    bot_uptime = datetime.datetime.utcnow() - bot.start_time
    embed = discord.Embed(title="Bot Status", color=discord.Color.purple())
    embed.add_field(name="Uptime", value=str(bot_uptime).split('.')[0], inline=False)
    embed.add_field(name="Bot Latency", value=f"{round(bot.latency * 1000)}ms", inline=False)
    embed.add_field(name="Bot Users", value=len(bot.users), inline=False)
    await ctx.send(embed=embed)

# Event for bot startup (to set start time)
@bot.event
async def on_ready():
    bot.start_time = datetime.datetime.utcnow()
    print(f"Logged in as {bot.user}")

# Run the bot with your token
bot.run('YOUR_BOT_TOKEN')

