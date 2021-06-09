import discord
from discord.ext import commands
from discord import file

import os

import sys
sys.path.append("./cogs/functions")
import tik_fn

# Setting Values
sys.path.append("./")
from config import  *
tik_down = config["path"]
limitsize = config["limitsize"] # <-- 8 mb for file size limit set by discord

class TiktokCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.Cog.listener()
    async def on_message(self, message):
        # Listen for Tiktok links
        if message.content.startswith('https://www.tiktok.com') or message.content.startswith('https://vm.tiktok.com'):
            try:
                # Sends url to tik_fn
                t = tik_fn.Tiktok_fn(message.content)  
                
                # Download video
                downloader = tik_fn.TikTokDownloader(t.default_url())
                downloader.download(tik_down+'/{}.mp4'.format(t.video_id()))

                mp4_file = (f"{tik_down}/{t.video_id()}.mp4")
                file_size = os.path.getsize(mp4_file)   
                
                # Embed
                e = t.embedgen(message.content, message.author, message.author.avatar_url)

                # Upload to discord
                if file_size <= limitsize:
                    await message.channel.send(embed=e)
                    await message.channel.send(file=discord.File(mp4_file))

                # Upload to Streamable
                else:
                    await message.channel.send(embed=e)
                    mssg = await message.channel.send(f'Wait Uploading...🔃 {message.author}')
                    streamable_link=t.upload_to_streamable(mp4_file, t.video_id())
                    await mssg.edit(content=streamable_link)
                #Delete the file
                os.remove(mp4_file)  
            except:
                embed=discord.Embed(title="Error", description='The video is private, or the api is broken \n make sure to use a proxy.', icon_url=message.author.avatar_url)
                embed.set_thumbnail(url="https://i.imgur.com/j3wGKKr.png")
                await message.channel.send(embed=embed, delete_after=10)
def setup(bot):
    bot.add_cog(TiktokCog(bot))