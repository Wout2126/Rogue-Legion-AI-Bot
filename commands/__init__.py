# Bind the commands to the tree explicitly
self.bot.tree.add_command(self.help_command, guild=discord.Object(id=GUILD_ID))
self.bot.tree.add_command(self.userinfo, guild=discord.Object(id=GUILD_ID))
self.bot.tree.add_command(self.serverinfo, guild=discord.Object(id=GUILD_ID))
self.bot.tree.add_command(self.ping, guild=discord.Object(id=GUILD_ID))
self.bot.tree.add_command(self.vote, guild=discord.Object(id=GUILD_ID))
self.bot.tree.add_command(self.status, guild=discord.Object(id=GUILD_ID))
