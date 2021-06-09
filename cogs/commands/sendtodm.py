import discord
from discord.ext import commands
from discord import file

import os
import random

import sys
sys.path.append("./cogs/functions")
import tik_fn
import insta_fn

# Setting Values
sys.path.append("./")
from config import  *
path_down = config["path"]
limitsize = config["limitsize"] # <-- 8 mb for file size limit set by discord
sEmoji = config["sEmoji"]

class SendtodmCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Delete dms
    @commands.dm_only()
    @commands.command(name='clear',pass_context=True)
    async def clear(self, ctx, limit: int=None):
        passed = 0
        failed = 0
        async for msg in ctx.message.channel.history(limit=limit+1):
            if msg.author.id == self.bot.user.id:
                try:
                    await msg.delete()
                    passed += 1
                except:
                    failed += 1
            else:
                pass
                #ctx.send(f"[Complete] Removed {passed} messages with {failed} fails", delete_after=10)
    
    # send video to dm
    @commands.command(name='send', aliases=['s'],pass_context=True)
    async def sendtodm_cmd(self, ctx, member: discord.Member, link_url, multipost_num=1):
        channel = await member.create_dm()
        
        # Tiktok send to dm
        if link_url.startswith('https://www.tiktok.com') or link_url.startswith('https://vm.tiktok.com'):
            try:
                # Sends url to tik_fn
                t = tik_fn.Tiktok_fn(link_url)  
                
                # Download video
                downloader = tik_fn.TikTokDownloader(t.default_url())
                downloader.download(path_down+'/{}.mp4'.format(t.video_id()))

                mp4_file = (f"{path_down}/{t.video_id()}.mp4")
                file_size = os.path.getsize(mp4_file)   
                
                # Embed
                e = t.embedgen(link_url, ctx.author, ctx.author.avatar_url)

                # Upload to discord
                if file_size <= limitsize:
                    await channel.send(embed=e)
                    await channel.send(file=discord.File(mp4_file))

                # Upload to Streamable
                else:
                    await channel.send(embed=e)
                    mssg = await channel.send(f'Wait Uploading...🔃 {ctx.author}')
                    streamable_link=t.upload_to_streamable(mp4_file, t.video_id())
                    await mssg.edit(content=streamable_link)
                #Delete the file
                os.remove(mp4_file) 
                await ctx.message.add_reaction(sEmoji)
            except:
                embed=discord.Embed(title="Error", description='The video is private, or the api is broken \n make sure to use a proxy.', icon_url=ctx.author.avatar_url)
                embed.set_thumbnail(url="https://i.imgur.com/j3wGKKr.png")
                await ctx.channel.send(embed=embed, delete_after=10)

        # Instagram send to dm
        elif link_url.startswith('https://www.instagram.com/'):
            url = link_url
            multipost_num = (int(multipost_num) - 1)
            try:
                i = insta_fn.Insta_fn(url , multipost_num)
                embed = i.embedgen(link_url, ctx.author, ctx.author.avatar_url)
                # For Videos
                if i.type_media() == "GraphVideo":
                    i.video_download(path_down)
                    file_tosend = (f"{path_down}/{i.video_id()}.mp4")
                    file_size = os.path.getsize(file_tosend)
                    
                    if file_size <= limitsize:
                        await channel.send(embed=embed)
                        await channel.send(file=discord.File(file_tosend))
                        os.remove(file_tosend) # Deletes downloaded file
                        await ctx.message.add_reaction(sEmoji)
                    
                    else: # Upload to streamable if file over size limit
                        await channel.send(embed=embed)
                        msg = await channel.send(f'{message.author} 🔃 Wait Uploading...')
                        streamable_link=i.upload_to_streamable(file_tosend, i.user_name())
                        await msg.edit(content=streamable_link)
                        os.remove(file_tosend) # Deletes downloaded file
                        await ctx.message.add_reaction(sEmoji)

                # For Pictures
                elif i.type_media() == "GraphImage":
                    await channel.send(embed=embed)
                    await ctx.message.add_reaction(sEmoji)
            
            except:
                embed=discord.Embed(title="Error", description='Account Maybe Private.', icon_url=ctx.author.avatar_url)
                embed.set_thumbnail(url="https://i.imgur.com/j3wGKKr.png")
                await ctx.channel.send(embed=embed, delete_after=10)
        else:
            pass

def setup(bot):
    bot.add_cog(SendtodmCog(bot))