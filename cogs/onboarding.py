import discord
from discord.ext import commands
import json
import os
from datetime import datetime

# Define paths for data storage
ONBOARDING_FILE = "data/onboarding.json"
RULES_FILE = "data/rules.txt"

# Function to load onboarding data
def load_onboarding_data():
    if os.path.exists(ONBOARDING_FILE):
        with open(ONBOARDING_FILE, "r") as f:
            return json.load(f)
    return {}

# Function to save onboarding data
def save_onboarding_data(data):
    with open(ONBOARDING_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Function to send onboarding message to new member
async def send_onboarding_message(member):
    try:
        # Load the rules from the rules.txt file
        if not os.path.exists(RULES_FILE):
            raise FileNotFoundError(f"Rules file not found at {RULES_FILE}")
        with open(RULES_FILE, 'r') as file:
            rules = file.read()

        # Send a welcome message along with the rules
        welcome_message = await member.send(
            f"Welcome {member.name}! Please review the server rules and guidelines:\n\n{rules}\n\n"
            "Please react with ✅ if you accept the rules."
        )

        # Add a reaction to the message (green check mark)
        await welcome_message.add_reaction("✅")

        # Define a check to ensure the member reacts with the check mark emoji
        def check(reaction, user):
            return user == member and str(reaction.emoji) == "✅" and reaction.message.id == welcome_message.id

        # Wait for the member to react with the check mark (timeout of 2 minutes)
        await member.client.wait_for('reaction_add', check=check, timeout=120.0)

        # After they accept the rules, ask for their gamertag
        await member.send("Thank you for accepting the rules! Please tell me your gamertag so I can set it as your nickname (max 32 characters).")

        def gamertag_check(msg):
            return msg.author == member and isinstance(msg.channel, discord.DMChannel)

        # Wait for the user to send their gamertag (timeout of 2 minutes)
        gamertag_message = await member.client.wait_for('message', check=gamertag_check, timeout=120.0)
        gamertag = gamertag_message.content.strip()

        if len(gamertag) > 32:
            await member.send("Your gamertag is too long. Please contact a moderator to set your nickname manually.")
        else:
            # Set the member's nickname
            await member.edit(nick=gamertag)

            # Give the member the "Member" role
            member_role = discord.utils.get(member.guild.roles, name="Member")
            if member_role:
                await member.add_roles(member_role)

            await member.send(f"Your nickname has been set to **{gamertag}** and you have been given the Member role!")

        # Record that the user has completed the onboarding
        onboarding_data = load_onboarding_data()
        onboarding_data[str(member.id)] = {"completed": True, "timestamp": str(datetime.utcnow())}
        save_onboarding_data(onboarding_data)

    except Exception as e:
        print(f"Error during onboarding process: {e}")

# Onboarding cog class
class Onboarding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Check if the member has already completed onboarding
        onboarding_data = load_onboarding_data()
        if str(member.id) not in onboarding_data or not onboarding_data[str(member.id)]["completed"]:
            await send_onboarding_message(member)

# Setup function to load the cog
async def setup(bot):
    await bot.add_cog(Onboarding(bot))

