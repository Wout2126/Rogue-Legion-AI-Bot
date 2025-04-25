import discord
from discord.ext import commands
from discord import app_commands
import logging
import json
from datetime import timedelta
from config import GUILD_ID

logging.basicConfig(level=logging.INFO, filename="data/logs/admin_actions.log",
                    format='%(asctime)s - %(levelname)s - %(message)s')


class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tree = bot.tree
        self.guild = discord.Object(id=GUILD_ID)

        self.tree.command(name="purge", description="Delete a specified number of messages.", guild=self.guild)(self.purge)
        self.tree.command(name="sync", description="Sync commands to this guild.", guild=self.guild)(self.sync)
        self.tree.command(name="clear_roles", description="Clear a role from all members.", guild=self.guild)(self.clear_roles)
        self.tree.command(name="ban", description="Ban a user from the server.", guild=self.guild)(self.ban)
        self.tree.command(name="timeout", description="Put a user in timeout for a duration (e.g., 1d 2h 30m).", guild=self.guild)(self.timeout)
        self.tree.command(name="clear_timeout", description="Remove the timeout from a user.", guild=self.guild)(self.clear_timeout)
        self.tree.command(name="kick", description="Kick a user from the server.", guild=self.guild)(self.kick)
        self.tree.command(name="warn", description="Warn a user and track the warnings.", guild=self.guild)(self.warn)
        self.tree.command(name="warnings", description="Check the warning count of a user.", guild=self.guild)(self.warnings)
        self.tree.command(name="remove_warning", description="Remove a specified number of warnings from a user.", guild=self.guild)(self.remove_warning)
        self.tree.command(name="restore_role", description="Restore a user's role based on their previous rank.", guild=self.guild)(self.restore_role)
        self.tree.command(name="unban", description="Unban a user from the server.", guild=self.guild)(self.unban)
        self.tree.command(name="adminhelp", description="Get a list of admin commands and their usage.", guild=self.guild)(self.adminhelp)

    async def has_admin_permissions(self, interaction: discord.Interaction):
        roles = [role.name.lower() for role in interaction.user.roles]
        return any(role in ['admin', 'moderator', 'founder'] for role in roles)

    async def log_action(self, action: str, user: discord.User, reason: str = ""):
        logging.info(f"Action: {action} - User: {user} - Reason: {reason}")
        channel = discord.utils.get(user.guild.text_channels, name="leave-messages")
        if channel:
            await channel.send(f"**{action}**: {user} | Reason: {reason}")

    async def purge(self, interaction: discord.Interaction):
        if not await self.has_admin_permissions(interaction):
            await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"🧹 Deleted {len(deleted)} messages.", ephemeral=True)
        await self.log_action("Purged messages", interaction.user, f"Amount: {amount}")

    async def sync(self, interaction: discord.Interaction):
        if not await self.has_admin_permissions(interaction):
            await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        try:
            synced = await self.bot.tree.sync(guild=interaction.guild)
            await interaction.followup.send(f"✅ Synced {len(synced)} commands.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to sync: {e}", ephemeral=True)
        await self.log_action("Synced commands", interaction.user)

    async def clear_roles(self, interaction: discord.Interaction, role: discord.Role):
        if not await self.has_admin_permissions(interaction):
            await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        count = 0
        for member in interaction.guild.members:
            if role in member.roles:
                await member.remove_roles(role)
                count += 1
        await interaction.followup.send(f"🧼 Removed '{role.name}' from {count} users.", ephemeral=True)
        await self.log_action("Cleared role", interaction.user, f"Role: {role.name} - Count: {count}")

    async def ban(self, interaction: discord.Interaction, user: discord.User, reason: str = None):
        if not await self.has_admin_permissions(interaction):
            await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        await interaction.guild.ban(user, reason=reason)
        await interaction.followup.send(f"✅ {user} has been banned.", ephemeral=True)
        await self.log_action("Banned user", interaction.user, f"User: {user} | Reason: {reason}")

    async def timeout(self, interaction: discord.Interaction, member: discord.Member, time: str):
        if not await self.has_admin_permissions(interaction):
            await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
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
                    raise ValueError("Invalid time format")
        except Exception:
            await interaction.response.send_message("❌ Invalid time format. Use `1d 2h 30m`.", ephemeral=True)
            return

        try:
            await member.timeout_for(total_time)
            await interaction.response.send_message(f"✅ {member} timed out for {total_time}.", ephemeral=True)
            await self.log_action("Timed out user", interaction.user, f"User: {member} | Duration: {total_time}")
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

    async def clear_timeout(self, interaction: discord.Interaction, member: discord.Member):
        if not await self.has_admin_permissions(interaction):
            await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
            return
        if member.timed_out_until:
            try:
                await member.timeout_for(None)
                await interaction.response.send_message(f"✅ {member}'s timeout cleared.", ephemeral=True)
                await self.log_action("Cleared timeout", interaction.user, f"User: {member}")
            except Exception as e:
                await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)
        else:
            await interaction.response.send_message("❌ User is not timed out.", ephemeral=True)

    async def kick(self, interaction: discord.Interaction, user: discord.User, reason: str = None):
        if not await self.has_admin_permissions(interaction):
            await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        await interaction.guild.kick(user, reason=reason)
        await interaction.followup.send(f"✅ {user} has been kicked.", ephemeral=True)
        await self.log_action("Kicked user", interaction.user, f"User: {user} | Reason: {reason}")

    async def warn(self, interaction: discord.Interaction, user: discord.User):
        if not await self.has_admin_permissions(interaction):
            await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
            return

        with open("data/warnings.json", "r") as f:
            warnings = json.load(f)

        warnings[str(user.id)] = warnings.get(str(user.id), 0) + 1

        with open("data/warnings.json", "w") as f:
            json.dump(warnings, f)

        if warnings[str(user.id)] >= 3:
            await user.timeout(timedelta(days=2))
            await interaction.followup.send(f"⚠️ {user} warned 3 times and timed out.", ephemeral=True)

        await interaction.followup.send(f"⚠️ {user} warned. Total: {warnings[str(user.id)]}.", ephemeral=True)
        await self.log_action("Warned user", interaction.user, f"User: {user} | Total: {warnings[str(user.id)]}")

    async def warnings(self, interaction: discord.Interaction, user: discord.User):
        with open("data/warnings.json", "r") as f:
            warnings = json.load(f)
        await interaction.response.send_message(f"⚠️ {user} has {warnings.get(str(user.id), 0)} warnings.", ephemeral=True)

    async def remove_warning(self, interaction: discord.Interaction, user: discord.User, count: int):
        if not await self.has_admin_permissions(interaction):
            await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
            return
        with open("data/warnings.json", "r") as f:
            warnings = json.load(f)

        current = warnings.get(str(user.id), 0)
        warnings[str(user.id)] = max(0, current - count)

        with open("data/warnings.json", "w") as f:
            json.dump(warnings, f)

        await interaction.response.send_message(f"✅ Removed {count} warnings from {user}.", ephemeral=True)
        await self.log_action("Removed warning", interaction.user, f"User: {user} | Removed: {count}")

    async def restore_role(self, interaction: discord.Interaction, user: discord.User):
        with open("data/ranks.json", "r") as f:
            ranks = json.load(f)
        role_id = ranks.get(str(user.id))
        role = discord.utils.get(interaction.guild.roles, id=role_id)
        if role:
            await user.add_roles(role)
            await interaction.response.send_message(f"✅ Restored {role.name} to {user}.", ephemeral=True)
            await self.log_action("Restored role", interaction.user, f"User: {user} | Role: {role.name}")
        else:
            await interaction.response.send_message("❌ No role data or role not found.", ephemeral=True)

    async def unban(self, interaction: discord.Interaction, user: discord.User):
        if not await self.has_admin_permissions(interaction):
            await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
            return
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"✅ {user} unbanned.", ephemeral=True)
        await self.log_action("Unbanned user", interaction.user, f"User: {user}")

    async def adminhelp(self, interaction: discord.Interaction):
        if not await self.has_admin_permissions(interaction):
            await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
            return
        try:
            with open("data/admincommands.txt", "r") as f:
                commands_text = f.read()
            await interaction.response.send_message(f"```\n{commands_text}\n```", ephemeral=True)
        except FileNotFoundError:
            await interaction.response.send_message("❌ File not found.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))
