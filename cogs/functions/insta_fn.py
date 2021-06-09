import requests
import json
import time
from pystreamable import StreamableApi

#Setting Values
import sys
sys.path.append("./")
from config import  *
stream_email = config["stream_email"]
stream_pass = config["stream_pass"]

import discord

class Insta_fn:
    def __init__(self, url, multipost_num=0):
        shortcode = url.split('/')[-2].replace('/', '')
        api_url = f"http://localhost:8080/api/instagram/{shortcode}"
        # Read json array via api
        response = requests.request("get", api_url)
        
        self.datameta = json.loads(response.text)
        self.typeofmedia = self.datameta["__typename"]
        self.multipost_num = multipost_num
        self.multipost_num_chosen = False
        if multipost_num > 0:
            self.multipost_num_chosen = True
        elif self.typeofmedia == "GraphSidecar":
            try:
                self.datameta["edge_sidecar_to_children"]["edges"][self.multipost_num]["node"]["__typename"]
            except:
                print(f"Number {multipost_num} is out of index, ``Setting number back to 1.``")
                self.multipost_num = 0

    def type_media(self):
        if self.typeofmedia != 'GraphSidecar':
            return self.typeofmedia
        elif self.typeofmedia == 'GraphSidecar':
            if self.datameta["edge_sidecar_to_children"]["edges"][self.multipost_num]["node"]["__typename"] == 'GraphVideo':
                return 'GraphVideo'
            else:
                return 'GraphImage'
        elif self.datameta["statusCode"] == 404:
            return '**Error StatusCode 404 \n Account Maybe Private.**'

    def play_number(self):
        if self.type_media() == "GraphVideo":
            try:
                play_number = self.datameta["video_view_count"]
                play_number = ("" + "{:,}".format(play_number))
            except:
                play_number = self.datameta["edge_sidecar_to_children"]["edges"][self.multipost_num]["node"]["video_view_count"] or self.datameta["edge_sidecar_to_children"]["edges"][0]["node"]["video_view_count"]
                play_number = ("" + "{:,}".format(play_number))
            return play_number
    
    def likes_number(self):
        likes_number = self.datameta["edge_media_preview_like"]["count"]
        likes_number = ("" + "{:,}".format(likes_number))
        return likes_number
    
    def comments_number(self):
        comments_number = self.datameta["edge_media_to_comment"]["count"]
        comments_number = ("" + "{:,}".format(comments_number))
        return  comments_number
    
    def caption(self):
        try:
            caption = self.datameta["edge_media_to_caption"]["edges"][0]["node"]["text"]
        except:
            caption = ' '
        return caption
    
    def user_name(self):
        user_name = self.datameta["owner"]["username"]
        return user_name
    
    def user_pfp(self):
        user_pfp = self.datameta["owner"]["profile_pic_url"]
        return user_pfp  
    
    def display_url(self):
        if self.typeofmedia == "GraphVideo":
            display_url = self.datameta["video_url"]
            return display_url
        
        elif self.typeofmedia == "GraphImage":
            display_url = self.datameta["display_url"]
            return display_url
        
        elif self.typeofmedia == "GraphSidecar":
            if self.type_media() == "GraphVideo":
                display_url = self.datameta["edge_sidecar_to_children"]["edges"][self.multipost_num]["node"]["video_url"]
                return display_url
            elif self.type_media() == "GraphImage":
                display_url = self.datameta["edge_sidecar_to_children"]["edges"][self.multipost_num]["node"]["display_url"]
                return display_url

    def video_duration(self):
        video_duration = self.datameta["video_duration"]
        limit_duration = float('600')
        return video_duration

    def video_id(self):
        video_id = self.datameta["id"]
        return video_id

    def video_download(self, path):
        data = requests.get(self.display_url())
        idd = self.datameta["id"]
        with open(path+'/{}.mp4'.format(idd), 'wb') as fb:
            fb.write(data.content)
    
    # Upload To streamable
    def upload_to_streamable(self, path, title):
        streamable_username = stream_email
        streamable_password = stream_pass
        api = StreamableApi(streamable_username, streamable_password)
        deets = api.upload_video(path, title)
        count = 0
        while True:
            count+=1
            test = api.get_info(deets['shortcode'])
            if test['percent'] == 100:
                break
            elif count == 6:
                exit()
            else:
                time.sleep(10)
        global streamable_link
        streamable_link = ("https://streamable.com/" +deets['shortcode'])
        return streamable_link

    def embedgen(self, url, author, author_avatar):

        embed=discord.Embed(title="Instagram", description=self.caption())
        embed.set_author(name=(f'@{self.user_name()}'), url=url, icon_url=self.user_pfp())
        embed.set_thumbnail(url="https://i.imgur.com/9S6AZz8.png")
        embed.add_field(name="Likes", value=self.likes_number(), inline=True)
        embed.add_field(name="Comments", value=self.comments_number(), inline=True)
        embed.set_footer(text=(f'Shared by • @{author}'), icon_url=author_avatar)
 
        # Embed for video
        if self.type_media() == "GraphVideo":
            embed.add_field(name="Views", value=self.play_number(), inline=True)
        #Embed for pic
        if self.type_media() == "GraphImage":        
            embed.set_image(url=self.display_url())
        
        return embed
