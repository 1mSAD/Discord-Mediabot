import requests
import json

import math
import re
from decimal import Decimal

import os
from urllib.parse import parse_qsl, urlparse
import random

import time
from pystreamable import StreamableApi

import sys
sys.path.append("./")
from config import *
stream_email = config["stream_email"]
stream_pass = config["stream_pass"]

import discord

#For Below Function
def remove_exponent(d):
    """Remove exponent."""
    return d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize()

#To Make Numbers Readable , 1k 1m...
def millify(n, precision=0, drop_nulls=True, prefixes=[]):
    """Humanize number."""
    millnames = ['', 'k', 'M', 'B', 'T', 'P', 'E', 'Z', 'Y']
    if prefixes:
        millnames = ['']
        millnames.extend(prefixes)
    n = float(n)
    millidx = max(0, min(len(millnames) - 1,
                         int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))
    result = '{:.{precision}f}'.format(n / 10**(3 * millidx), precision=precision)
    if drop_nulls:
        result = remove_exponent(Decimal(result))
    return '{0}{dx}'.format(result, dx=millnames[millidx])

class Tiktok_fn:
    def __init__(self, url):
        self.url = url
        # Convert https://vm.tiktok.com to https://www.tiktok.com
        header = {
    'Host': 't.tiktok.com',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0',
    'Referer': 'https://www.tiktok.com/',
}
        tikfull_url = url
        if url.startswith('https://vm.tiktok.com'):
            res = requests.get(url)
            url = (res.url)
            if url.startswith('https://m.tiktok.com'):
                req = requests.get(f"https://www.tiktok.com/oembed?url={url}")
                extr_url = json.loads(req.text)
                extr_url = extr_url["html"]
                m = re.search(" +cite=\"(.*?)\"", extr_url)
                url = m.group(1)
                tikfull_url = url
        self.url = tikfull_url
        video_id = (('{}'.format(*tikfull_url.split('/')[-1:]))).split("?")[0]
        video_username = (('{}'.format(*tikfull_url.split('/')[-3:]))).split("?")[0]
        # Send to api
        api_url = f"http://localhost:8080/api/tiktok/{video_username}/{video_id}"
        # Read json array via api
        response = requests.request("get", api_url)
        self.datameta = json.loads(response.text)
        self.video_url = self.datameta["video"]["playAddr"]
        self.header = header
        self.fll_url = tikfull_url

    def likes_number(self):
        likes_number = (millify(self.datameta["stats"]["diggCount"], precision=1))
        return likes_number

    def comments_number(self):
        comments_number = (millify(self.datameta["stats"]["commentCount"], precision=1))
        return comments_number

    def share_number(self):
        share_number = (millify(self.datameta["stats"]["shareCount"], precision=1))
        return share_number

    def play_number(self):
        play_number = (millify(self.datameta["stats"]["playCount"], precision=1))
        return play_number

    def user_name(self):
        user_name = self.datameta["author"]["uniqueId"]
        return user_name
    
    def author_avatar(self):
        author_avatar = self.datameta["author"]["avatarLarger"]
        return author_avatar
    
    def sound_des(self):
        sound_des = self.datameta["music"]["title"]
        return sound_des

    def caption(self):
        caption = self.datameta["desc"]
        return caption

    def video_id(self):
        video_id = self.datameta["video"]["id"]
        return video_id
    
    def video_url(self):
        video_url = self.datameta["video"]["playAddr"]
        return video_url
    
    def default_url(self):
        return self.fll_url

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
        e=discord.Embed(title="Tiktok", description=self.caption())
        e.set_author(name=(f'@{self.user_name()}'), url=url , icon_url=self.author_avatar())
        e.set_thumbnail(url="https://i.imgur.com/rMollzc.png")
        e.add_field(name="Likes", value=self.likes_number(), inline=True)
        e.add_field(name="Comments", value=self.comments_number(), inline=True)
        e.add_field(name="Sound", value=self.sound_des(), inline=False)
        e.add_field(name="Shares", value=self.share_number(), inline=True)
        e.add_field(name="Views", value=self.play_number(), inline=True)
        e.set_footer(text=(f'Shared by {author}'), icon_url=author_avatar)
        return e


class TikTokDownloader:
    HEADERS = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'DNT': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Dest': 'video',
        'Referer': 'https://www.tiktok.com/',
        'Accept-Language': 'en-US,en;q=0.9,bs;q=0.8,sr;q=0.7,hr;q=0.6',
        'sec-gpc': '1',
        'Range': 'bytes=0-',
    }

    def __init__(self, url: str):
        web_id = str(random.randint(10000, 999999999))
        self.__url = url
        self.__cookies = {
            'tt_webid': web_id,
            'tt_webid_v2': web_id
        }

    def __get_video_url(self) -> str:
        response = requests.get(self.__url, cookies=self.__cookies, headers=TikTokDownloader.HEADERS)
        return response.text.split('"playAddr":"')[1].split('"')[0].replace(r'\u0026', '&')

    def download(self, file_path: str):
        video_url = self.__get_video_url()
        url = urlparse(video_url)
        params = tuple(parse_qsl(url.query))
        request = requests.Request(method='GET',url='{}://{}{}'.format(url.scheme,url.netloc, url.path),cookies=self.__cookies,headers=TikTokDownloader.HEADERS,params=params)
        prepared_request = request.prepare()
        session = requests.Session()
        response = session.send(request=prepared_request)
        response.raise_for_status()
        with open(os.path.abspath(file_path), 'wb') as output_file:
            output_file.write(response.content)