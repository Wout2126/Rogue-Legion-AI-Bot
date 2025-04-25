import os
import importlib

async def setup(bot):
    # Dynamically load all Python files in the commands folder, except __init__.py
    for filename in os.listdir(os.path.dirname(__file__)):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"{__package__}.{filename[:-3]}"  # commands.admin_commands → full import path
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, "setup"):
                    await module.setup(bot)
                    bot.logger.info(f"✅ Loaded {module_name}")
                else:
                    bot.logger.warning(f"⚠️ {module_name} has no setup() function.")
            except Exception as e:
                bot.logger.error(f"❌ Failed to load {module_name}: {e}")
