import discord
from discord.ext import commands
import logging
import json
from datetime import timedelta
from config import GUILD_ID

logging.basicConfig(level=logging.INFO, filename="data/logs/admin_actions.log", 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        async def has_admin_permissions(interaction: discord.Interaction):
            roles = [role.name.lower() for role in interaction.user.roles]
            return any(role in ['admin', 'moderator', 'founder'] for role in roles)

        async def log_action(action: str, user: discord.User, reason: str = ""):
            logging.info(f"Action: {action} - User: {user} - Reason: {reason}")
            channel = discord.utils.get(user.guild.text_channels, name="leave-messages")
            if channel:
                await channel.send(f"**{action}**: {user} | Reason: {reason}")

        @self.bot.tree.command(name="purge", description="Delete a specified number of messages.")
        @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
        async def purge(interaction: discord.Interaction, amount: int):
            if not await has_admin_permissions(interaction):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            deleted = await interaction.channel.purge(limit=amount)
            await interaction.followup.send(f"🧹 Deleted {len(deleted)} messages.", ephemeral=True)
            await log_action("Purged messages", interaction.user, f"Amount: {amount}")

        @self.bot.tree.command(name="sync", description="Sync commands to this guild.")
        @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
        async def sync(interaction: discord.Interaction):
            if not await has_admin_permissions(interaction):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            try:
                synced = await self.bot.tree.sync(guild=interaction.guild)
                await interaction.followup.send(f"✅ Synced {len(synced)} commands.", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"❌ Failed to sync commands: {e}", ephemeral=True)
            await log_action("Synced commands", interaction.user)

        @self.bot.tree.command(name="clear_roles", description="Clear a role from all members.")
        @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
        async def clear_roles(interaction: discord.Interaction, role: discord.Role):
            if not await has_admin_permissions(interaction):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            count = 0
            for member in interaction.guild.members:
                if role in member.roles:
                    await member.remove_roles(role)
                    count += 1
            await interaction.followup.send(f"🧼 Removed role '{role.name}' from {count} users.", ephemeral=True)
            await log_action("Cleared role", interaction.user, f"Role: {role.name} - Count: {count}")

        @self.bot.tree.command(name="ban", description="Ban a user from the server.")
        @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
        async def ban(interaction: discord.Interaction, user: discord.User, reason: str = None):
            if not await has_admin_permissions(interaction):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            await interaction.guild.ban(user, reason=reason)
            await interaction.followup.send(f"✅ {user} has been banned.", ephemeral=True)
            await log_action("Banned user", interaction.user, f"User: {user} | Reason: {reason}")

        @self.bot.tree.command(name="timeout", description="Put a user in timeout for a specified duration (e.g., 1d 2h 30m).")
        @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
        async def timeout(interaction: discord.Interaction, member: discord.Member, time: str):
            if not await has_admin_permissions(interaction):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
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
                        raise ValueError()
            except Exception:
                await interaction.response.send_message("❌ Invalid time format. Example: `1d 2h 30m`", ephemeral=True)
                return
            try:
                await member.timeout_for(total_time)
                await interaction.response.send_message(f"✅ {member} has been timed out for {total_time}.", ephemeral=True)
                await log_action("Timed out user", interaction.user, f"User: {member} | Duration: {total_time}")
            except Exception as e:
                await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

        @self.bot.tree.command(name="clear_timeout", description="Remove the timeout from a user.")
        @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
        async def clear_timeout(interaction: discord.Interaction, member: discord.Member):
            if not await has_admin_permissions(interaction):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            if member.timed_out_until:
                try:
                    await member.timeout_for(None)
                    await interaction.response.send_message(f"✅ {member}'s timeout has been cleared.", ephemeral=True)
                    await log_action("Cleared timeout", interaction.user, f"User: {member}")
                except Exception as e:
                    await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ {member} is not currently timed out.", ephemeral=True)

        @self.bot.tree.command(name="kick", description="Kick a user from the server.")
        @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
        async def kick(interaction: discord.Interaction, user: discord.User, reason: str = None):
            if not await has_admin_permissions(interaction):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            await interaction.guild.kick(user, reason=reason)
            await interaction.followup.send(f"✅ {user} has been kicked.", ephemeral=True)
            await log_action("Kicked user", interaction.user, f"User: {user} | Reason: {reason}")

        @self.bot.tree.command(name="warn", description="Warn a user and track the warnings.")
        @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
        async def warn(interaction: discord.Interaction, user: discord.User):
            if not await has_admin_permissions(interaction):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            with open("data/warnings.json", "r") as f:
                warnings = json.load(f)
            warnings[str(user.id)] = warnings.get(str(user.id), 0) + 1
            if warnings[str(user.id)] >= 3:
                await user.timeout(timedelta(days=2))
                await interaction.followup.send(f"⚠️ {user} has been warned 3 times and automatically timed out.", ephemeral=True)
            with open("data/warnings.json", "w") as f:
                json.dump(warnings, f)
            await interaction.followup.send(f"⚠️ {user} has been warned. Total warnings: {warnings[str(user.id)]}.", ephemeral=True)
            await log_action("Warned user", interaction.user, f"User: {user} | Total Warnings: {warnings[str(user.id)]}")

        @self.bot.tree.command(name="warnings", description="Check the warning count of a user.")
        @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
        async def warnings_cmd(interaction: discord.Interaction, user: discord.User):
            with open("data/warnings.json", "r") as f:
                warnings = json.load(f)
            warning_count = warnings.get(str(user.id), 0)
            await interaction.response.send_message(f"⚠️ {user} has {warning_count} warnings.", ephemeral=True)

        @self.bot.tree.command(name="remove_warning", description="Remove a specified number of warnings from a user.")
        @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
        async def remove_warning(interaction: discord.Interaction, user: discord.User, count: int):
            if not await has_admin_permissions(interaction):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            with open("data/warnings.json", "r") as f:
                warnings = json.load(f)
            current_warnings = warnings.get(str(user.id), 0)
            warnings[str(user.id)] = max(0, current_warnings - count)
            with open("data/warnings.json", "w") as f:
                json.dump(warnings, f)
            await interaction.response.send_message(f"✅ Removed {count} warnings from {user}.", ephemeral=True)
            await log_action("Removed warning", interaction.user, f"User: {user} | Warnings Removed: {count}")

        @self.bot.tree.command(name="restore_role", description="Restore a user's role based on their previous rank.")
        @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
        async def restore_role(interaction: discord.Interaction, user: discord.User):
            with open("data/ranks.json", "r") as f:
                ranks = json.load(f)
            role_id = ranks.get(str(user.id))
            if role_id:
                role = discord.utils.get(interaction.guild.roles, id=role_id)
                if role:
                    await user.add_roles(role)
                    await interaction.response.send_message(f"✅ Restored {role.name} role to {user}.", ephemeral=True)
                    await log_action("Restored role", interaction.user, f"User: {user} | Role: {role.name}")
                else:
                    await interaction.response.send_message("❌ Role not found.", ephemeral=True)
            else:
                await interaction.response.send_message("❌ No role data found for this user.", ephemeral=True)

        @self.bot.tree.command(name="unban", description="Unban a user from the server.")
        @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
        async def unban(interaction: discord.Interaction, user: discord.User):
            if not await has_admin_permissions(interaction):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"✅ {user} has been unbanned.", ephemeral=True)
            await log_action("Unbanned user", interaction.user, f"User: {user}")

        @self.bot.tree.command(name="adminhelp", description="Get a list of admin commands and their usage.")
        @discord.app_commands.guilds(discord.Object(id=GUILD_ID))
        async def adminhelp(interaction: discord.Interaction):
            if not await has_admin_permissions(interaction):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            try:
                with open("data/admincommands.txt", "r") as f:
                    admin_commands = f.read()
                await interaction.response.send_message(f"Here is the list of admin commands:\n```\n{admin_commands}\n```", ephemeral=True)
            except FileNotFoundError:
                await interaction.response.send_message("❌ Could not find the admin commands file.", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ An error occurred while reading the file: {e}", ephemeral=True)

# Setup function
async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))
