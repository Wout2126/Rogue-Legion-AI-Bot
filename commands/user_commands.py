import discord
from discord.ext import commands
import datetime
import asyncio

def load_help_text():
    try:
        with open('data/usercommands.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Help text file not found."

class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.start_time = datetime.datetime.utcnow()

    @commands.command(name="help", help="Show help for all commands")
    async def help_command(self, ctx):
        help_text = load_help_text()
        await ctx.send(help_text)

    @commands.command(name="userinfo", help="Get information about yourself")
    async def userinfo(self, ctx):
        user = ctx.author
        embed = discord.Embed(title=f"{user.name}'s Info", color=discord.Color.blue())
        embed.add_field(name="Username", value=user.name, inline=False)
        embed.add_field(name="ID", value=user.id, inline=False)
        embed.add_field(name="Account Created", value=user.created_at.strftime("%B %d, %Y"), inline=False)
        embed.add_field(name="Joined Server", value=user.joined_at.strftime("%B %d, %Y"), inline=False)
        embed.add_field(name="Roles", value=", ".join([role.name for role in user.roles[1:]]), inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="serverinfo", help="Get information about the server")
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(title=f"{guild.name} Server Info", color=discord.Color.green())
        embed.add_field(name="Server Name", value=guild.name, inline=False)
        embed.add_field(name="Server ID", value=guild.id, inline=False)
        embed.add_field(name="Total Members", value=guild.member_count, inline=False)
        embed.add_field(name="Server Created", value=guild.created_at.strftime("%B %d, %Y"), inline=False)
        embed.add_field(name="Region", value=str(guild.region), inline=False)
        embed.add_field(name="Roles", value=", ".join([role.name for role in guild.roles[1:]]), inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="ping", help="Check the bot's latency")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"Pong! Latency is {latency}ms")

    @commands.command(name="vote", help="Create a poll with options")
    async def vote(self, ctx, question: str, *options: str):
        if len(options) < 2:
            await ctx.send("You need at least 2 options to create a vote.")
            return

        time_limit = None
        if len(options) > 2 and options[-2].startswith("time:"):
            time_limit_str = options[-2][5:]
            try:
                time_limit = datetime.datetime.strptime(time_limit_str, "%Y-%m-%d %H:%M:%S")
                options = options[:-2]
            except ValueError:
                await ctx.send("Invalid date format. Use YYYY-MM-DD HH:MM:SS.")
                return
        elif len(options) > 2 and options[-1].startswith("hours:"):
            try:
                hours = int(options[-1][6:])
                time_limit = datetime.datetime.utcnow() + datetime.timedelta(hours=hours)
                options = options[:-1]
            except ValueError:
                await ctx.send("Invalid number of hours.")
                return

        emojis = ['🇦', '🇧', '🇨', '🇩', '🇪']
        poll_message = f"||**Poll**: {question}||\n\n"
        for i, option in enumerate(options):
            poll_message += f"{emojis[i]}: {option}\n"

        poll_msg = await ctx.send(f"**Poll started!** {poll_message}")

        for i in range(len(options)):
            await poll_msg.add_reaction(emojis[i])

        if time_limit:
            await asyncio.sleep((time_limit - datetime.datetime.utcnow()).total_seconds())
            await poll_msg.channel.send(f"The poll has ended! {question}")

    @commands.command(name="status", help="Show the bot's current status")
    async def status(self, ctx):
        bot_uptime = datetime.datetime.utcnow() - self.bot.start_time
        embed = discord.Embed(title="Bot Status", color=discord.Color.purple())
        embed.add_field(name="Uptime", value=str(bot_uptime).split('.')[0], inline=False)
        embed.add_field(name="Bot Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=False)
        embed.add_field(name="Bot Users", value=len(self.bot.users), inline=False)
        await ctx.send(embed=embed)

# Setup function required to load the cog
async def setup(bot):
    await bot.add_cog(UserCommands(bot))
