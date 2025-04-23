import discord
from discord import app_commands
from discord.ext import commands
import logging
import json
from datetime import timedelta

# Set up logging to both file and console
logging.basicConfig(level=logging.INFO, filename="data/logs/admin_actions.log", 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Check if the user has the required roles
    async def has_admin_permissions(self, interaction: discord.Interaction):
        roles = [role.name.lower() for role in interaction.user.roles]
        if any(role in ['admin', 'moderator', 'founder'] for role in roles):
            return True
        return False

    # Log actions to both file and channel
    async def log_action(self, action: str, user: discord.User, reason: str = ""):
        logging.info(f"Action: {action} - User: {user} - Reason: {reason}")
        
        # Log to channel (Leave-messages or similar)
        channel = discord.utils.get(user.guild.text_channels, name="leave-messages")
        if channel:
            await channel.send(f"**{action}**: {user} | Reason: {reason}")

    # /purge command
    @app_commands.command(name="purge", description="Delete a specified number of messages.")
    async def purge(self, interaction: discord.Interaction, amount: int):
        if not await self.has_admin_permissions(interaction):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"🧹 Deleted {len(deleted)} messages.", ephemeral=True)
        await self.log_action("Purged messages", interaction.user, f"Amount: {amount}")

    # /sync command
    @app_commands.command(name="sync", description="Sync commands to this guild.")
    async def sync(self, interaction: discord.Interaction):
        if not await self.has_admin_permissions(interaction):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        try:
            synced = await self.bot.tree.sync(guild=interaction.guild)
            await interaction.followup.send(f"✅ Synced {len(synced)} commands.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to sync commands: {e}", ephemeral=True)
        await self.log_action("Synced commands", interaction.user)

    # /status command
    @app_commands.command(name="status", description="Set the bot's playing status.")
    async def status(self, interaction: discord.Interaction, *, status: str):
        if not await self.has_admin_permissions(interaction):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
        
        await self.bot.change_presence(activity=discord.Game(name=status))
        await interaction.response.send_message(f"✅ Status updated to: {status}", ephemeral=True)
        await self.log_action("Changed status", interaction.user, f"New Status: {status}")

    # /clear_roles command
    @app_commands.command(name="clear_roles", description="Clear a role from all members.")
    async def clear_roles(self, interaction: discord.Interaction, role: discord.Role):
        if not await self.has_admin_permissions(interaction):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        count = 0
        for member in interaction.guild.members:
            if role in member.roles:
                await member.remove_roles(role)
                count += 1
        await interaction.followup.send(f"🧼 Removed role '{role.name}' from {count} users.", ephemeral=True)
        await self.log_action("Cleared role", interaction.user, f"Role: {role.name} - Count: {count}")

    # /ban command
    @app_commands.command(name="ban", description="Ban a user from the server.")
    async def ban(self, interaction: discord.Interaction, user: discord.User, reason: str = None):
        if not await self.has_admin_permissions(interaction):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        await interaction.guild.ban(user, reason=reason)
        await interaction.followup.send(f"✅ {user} has been banned.", ephemeral=True)
        await self.log_action("Banned user", interaction.user, f"User: {user} | Reason: {reason}")

   # /timeout command - Timeout a user for a specified duration (days:hours:minutes format)
@app_commands.command(name="timeout", description="Put a user in timeout for a specified duration (e.g., 1d 2h 30m).")
async def timeout(self, interaction: discord.Interaction, member: discord.Member, time: str):
    if not await self.has_admin_permissions(interaction):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return

    # Parse the time string into days, hours, and minutes
    try:
        time_parts = time.lower().split()
        total_time = timedelta()
        for part in time_parts:
            if part.endswith('d'):
                total_time += timedelta(days=int(part[:-1]))
            elif part.endswith('h'):
                total_time += timedelta(hours=int(part[:-1]))
            elif part.endswith('m'):
                total_time += timedelta(minutes=int(part[:-1]))
            else:
                raise ValueError(f"Invalid time format: {part}")
    except Exception as e:
        await interaction.response.send_message(f"❌ Invalid time format. Example: `1d 2h 30m`", ephemeral=True)
        return

    # Timeout the user
    try:
        await member.timeout_for(total_time)
        await interaction.response.send_message(f"✅ {member} has been timed out for {total_time}.", ephemeral=True)

        # Log the action
        await self.log_action("Timed out user", interaction.user, f"User: {member} | Duration: {total_time}")

    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

   # /clear_timeout command - Clear the timeout from a user
@app_commands.command(name="clear_timeout", description="Remove the timeout from a user.")
async def clear_timeout(self, interaction: discord.Interaction, member: discord.Member):
    if not await self.has_admin_permissions(interaction):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
        return

    # Clear the timeout from the user
    if member.timed_out:
        try:
            await member.timeout_for(None)  # Removes the timeout
            await interaction.response.send_message(f"✅ {member}'s timeout has been cleared.", ephemeral=True)

            # Log the action
            await self.log_action("Cleared timeout", interaction.user, f"User: {member}")

        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ {member} is not currently timed out.", ephemeral=True)


    # /kick command
    @app_commands.command(name="kick", description="Kick a user from the server.")
    async def kick(self, interaction: discord.Interaction, user: discord.User, reason: str = None):
        if not await self.has_admin_permissions(interaction):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        await interaction.guild.kick(user, reason=reason)
        await interaction.followup.send(f"✅ {user} has been kicked.", ephemeral=True)
        await self.log_action("Kicked user", interaction.user, f"User: {user} | Reason: {reason}")

    # /warn command
    @app_commands.command(name="warn", description="Warn a user and track the warnings.")
    async def warn(self, interaction: discord.Interaction, user: discord.User):
        if not await self.has_admin_permissions(interaction):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
        
        with open("data/warnings.json", "r") as f:
            warnings = json.load(f)
        
        warnings[str(user.id)] = warnings.get(str(user.id), 0) + 1

        # Auto-timeout after 3 warnings
        if warnings[str(user.id)] >= 3:
            await user.timeout(timedelta(days=2))  # Timeout for 2 days
            await interaction.followup.send(f"⚠️ {user} has been warned 3 times and automatically timed out.", ephemeral=True)
        
        with open("data/warnings.json", "w") as f:
            json.dump(warnings, f)

        await interaction.followup.send(f"⚠️ {user} has been warned. Total warnings: {warnings[str(user.id)]}.", ephemeral=True)
        await self.log_action("Warned user", interaction.user, f"User: {user} | Total Warnings: {warnings[str(user.id)]}")

    # /warnings command
    @app_commands.command(name="warnings", description="Check the warning count of a user.")
    async def warnings(self, interaction: discord.Interaction, user: discord.User):
        with open("data/warnings.json", "r") as f:
            warnings = json.load(f)

        warning_count = warnings.get(str(user.id), 0)
        await interaction.response.send_message(f"⚠️ {user} has {warning_count} warnings.", ephemeral=True)

    # /remove_warning command
    @app_commands.command(name="remove_warning", description="Remove a specified number of warnings from a user.")
    async def remove_warning(self, interaction: discord.Interaction, user: discord.User, count: int):
        if not await self.has_admin_permissions(interaction):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        with open("data/warnings.json", "r") as f:
            warnings = json.load(f)

        current_warnings = warnings.get(str(user.id), 0)
        warnings[str(user.id)] = max(0, current_warnings - count)

        with open("data/warnings.json", "w") as f:
            json.dump(warnings, f)

        await interaction.response.send_message(f"✅ Removed {count} warnings from {user}.", ephemeral=True)
        await self.log_action("Removed warning", interaction.user, f"User: {user} | Warnings Removed: {count}")

    # /restore_role command
    @app_commands.command(name="restore_role", description="Restore a user's role based on their previous rank.")
    async def restore_role(self, interaction: discord.Interaction, user: discord.User):
        with open("data/ranks.json", "r") as f:
            ranks = json.load(f)

        role_id = ranks.get(str(user.id))
        if role_id:
            role = discord.utils.get(interaction.guild.roles, id=role_id)
            if role:
                await user.add_roles(role)
                await interaction.response.send_message(f"✅ Restored {role.name} role to {user}.", ephemeral=True)
                await self.log_action("Restored role", interaction.user, f"User: {user} | Role: {role.name}")
            else:
                await interaction.response.send_message("❌ Role not found.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ No role data found for this user.", ephemeral=True)

    # /unban command
    @app_commands.command(name="unban", description="Unban a user from the server.")
    async def unban(self, interaction: discord.Interaction, user: discord.User):
        if not await self.has_admin_permissions(interaction):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
        
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"✅ {user} has been unbanned.", ephemeral=True)
        await self.log_action("Unbanned user", interaction.user, f"User: {user}")

    # /adminhelp command
    @app_commands.command(name="adminhelp", description="Get a list of admin commands and their usage.")
    async def adminhelp(self, interaction: discord.Interaction):
        # Check if the user has permission
        if not await self.has_admin_permissions(interaction):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        # Try to read the admin commands file and send it
        try:
            with open("data/admincommands.txt", "r") as f:
                admin_commands = f.read()

            # Send the file content to the user
            await interaction.response.send_message(f"Here is the list of admin commands:\n```\n{admin_commands}\n```", ephemeral=True)

        except FileNotFoundError:
            await interaction.response.send_message("❌ Could not find the admin commands file.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ An error occurred while reading the file: {e}", ephemeral=True)


# Set up cog
async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))

