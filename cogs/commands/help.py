import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

import json

#Setting Values
import sys
sys.path.append("./")
from config import *
prefix = config["Prefix"]

def gembed(ctx):
    embed=discord.Embed(title='help', description='available commands.', color = discord.Colour.random(),)
    embed.add_field(
        name=f"{prefix}send - {prefix}s - /send", 
        value=f"```{prefix}s <mention||userid> <link> <number-optional>```", 
        inline=False
        )
    embed.add_field(
        name=f"{prefix}clear - ``only works in dm``"
        , value=f"```{prefix}clear <amount>```", 
        inline=True
        )
    embed.set_footer(
        text=f"Requested by {ctx.author}", 
        icon_url=ctx.author.avatar_url
        )
    return embed

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')

    @commands.command(name='help')
    async def Help_cmd(self, ctx):
        await ctx.send(embed=gembed(ctx))

    @cog_ext.cog_slash(name="help",description="view available commands.")
    async def slashHelp_cmd(self, ctx:SlashContext):
        await ctx.send(embed=gembed(ctx))

def setup(bot):
    bot.add_cog(HelpCog(bot))