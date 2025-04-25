import discord
from discord.ext import commands
from discord import app_commands
import datetime
import asyncio

def load_help_text():
    try:
        with open('data/usercommands.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Help text file not found."

class UserCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.start_time = datetime.datetime.utcnow()

@app_commands.command(name="help", description="Show help for all commands")
    async def help_command(self, interaction: discord.Interaction):
        help_text = load_help_text()
        await interaction.response.send_message(help_text)

@app_commands.command(name="userinfo", description="Get information about yourself")
    async def userinfo(self, interaction: discord.Interaction):
        user = interaction.user
        embed = discord.Embed(title=f"{user.name}'s Info", color=discord.Color.blue())
        embed.add_field(name="Username", value=user.name, inline=False)
        embed.add_field(name="ID", value=user.id, inline=False)
        embed.add_field(name="Account Created", value=user.created_at.strftime("%B %d, %Y"), inline=False)
        member = interaction.guild.get_member(user.id)
        if member and member.joined_at:
            embed.add_field(name="Joined Server", value=member.joined_at.strftime("%B %d, %Y"), inline=False)
            embed.add_field(name="Roles", value=", ".join([role.name for role in member.roles[1:]]), inline=False)
        await interaction.response.send_message(embed=embed)

@app_commands.command(name="serverinfo", description="Get information about the server")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title=f"{guild.name} Server Info", color=discord.Color.green())
        embed.add_field(name="Server Name", value=guild.name, inline=False)
        embed.add_field(name="Server ID", value=guild.id, inline=False)
        embed.add_field(name="Total Members", value=guild.member_count, inline=False)
        embed.add_field(name="Server Created", value=guild.created_at.strftime("%B %d, %Y"), inline=False)
        embed.add_field(name="Roles", value=", ".join([role.name for role in guild.roles[1:]]), inline=False)
        await interaction.response.send_message(embed=embed)

@app_commands.command(name="ping", description="Check the bot's latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! Latency is {latency}ms")

@app_commands.command(name="vote", description="Create a poll with up to 5 options")
    async def vote(self, interaction: discord.Interaction, question: str, option1: str, option2: str,
                   option3: str = None, option4: str = None, option5: str = None):
        options = [opt for opt in [option1, option2, option3, option4, option5] if opt]
        if len(options) < 2:
            await interaction.response.send_message("You need at least 2 options to create a vote.")
            return

        emojis = ['🇦', '🇧', '🇨', '🇩', '🇪']
        poll_message = f"||**Poll**: {question}||\n\n"
        for i, option in enumerate(options):
            poll_message += f"{emojis[i]}: {option}\n"

        await interaction.response.send_message(f"**Poll started!** {poll_message}")
        msg = await interaction.original_response()

        for i in range(len(options)):
            await msg.add_reaction(emojis[i])

@app_commands.command(name="status", description="Show the bot's current status")
    async def status(self, interaction: discord.Interaction):
        bot_uptime = datetime.datetime.utcnow() - self.bot.start_time
        embed = discord.Embed(title="Bot Status", color=discord.Color.purple())
        embed.add_field(name="Uptime", value=str(bot_uptime).split('.')[0], inline=False)
        embed.add_field(name="Bot Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=False)
        embed.add_field(name="Bot Users", value=len(self.bot.users), inline=False)
        await interaction.response.send_message(embed=embed)

# Setup function to load the cog
async def setup(bot):
    await bot.add_cog(UserCommands(bot))

