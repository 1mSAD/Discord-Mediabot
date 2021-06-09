import discord
from discord.ext import commands
from discord import file

import os

import sys
sys.path.append("./cogs/functions")
import insta_fn

#Setting Values
sys.path.append("./")
from config import  *
instapath = config["path"]
limitsize = config["limitsize"] # <-- 8 mb for file size limit set by discord

class InstagramCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    @commands.Cog.listener()
    async def on_message(self, message, multipost_num=1):
        if message.content.startswith('https://www.instagram.com/'):
            split_url = message.content.split(' ') #Seperates url and num if there is
            url = split_url[0] 
            # Check if the user entered a number after the url
            try:
                split_url[1]
            except IndexError:
                multipost_num = 0
            else:
                multipost_num = (int(split_url[1]) - 1) # -1 from number 
            try:
                i = insta_fn.Insta_fn(url , multipost_num)
                embed = i.embedgen(message.content, message.author, message.author.avatar_url)
                # For Videos
                if i.type_media() == "GraphVideo":
                    i.video_download(instapath)
                    file_tosend = (f"{instapath}/{i.video_id()}.mp4")
                    file_size = os.path.getsize(file_tosend)

                    if file_size <= limitsize:
                        await message.channel.send(embed=embed)
                        await message.channel.send(file=discord.File(file_tosend))
                        os.remove(file_tosend) # Delete the file
                    
                    else: # Upload to streamable if file over size limit
                        await message.channel.send(embed=embed)
                        msg = await message.channel.send(f'{message.author} 🔃 Wait Uploading...')
                        streamable_link=i.upload_to_streamable(file_tosend, i.user_name())
                        await msg.edit(content=streamable_link)
                        os.remove(file_tosend) # Delete the file

                # For Pictures
                elif i.type_media() == "GraphImage":
                    await message.channel.send(embed=embed)
            except:
                embed=discord.Embed(title="Error", description='Account Maybe Private.', icon_url=message.author.avatar_url)
                embed.set_thumbnail(url="https://i.imgur.com/j3wGKKr.png")
                await message.channel.send(embed=embed, delete_after=10)
        
def setup(bot):
    bot.add_cog(InstagramCog(bot))