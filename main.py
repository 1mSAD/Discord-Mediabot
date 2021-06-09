import discord
from discord.ext import commands
from discord import file
from discord_slash import SlashCommand

#Setting Values
from config import *
client = commands.Bot(command_prefix=config["Prefix"])
slash = SlashCommand(client, sync_commands=True, sync_on_cog_reload=True)
TOKEN = config["TOKEN"]

events_extensions = ['cogs.events.tiktok',
                      'cogs.events.instagram',
                      'cogs.commands.sendtodm',
                      'cogs.commands.slash-sendtodm',
                      'cogs.commands.help']

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game(f'{config["Prefix"]}help'))
    print("\u001b[32mMediabot is Ready to go. \u001b[0m")

if __name__ == "__main__":
    # Loads Extentions (Cogs)
    for extension in events_extensions:
        print(f"Loaded \u001b[32m{extension}\u001b[0m")
        client.load_extension(extension)

    from api.flaskapi import run_api
    run_api()

    client.run(TOKEN)