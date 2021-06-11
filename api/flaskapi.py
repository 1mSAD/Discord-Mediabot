from flask import Flask, json, request
import json
import requests
import random
import instaloader

import sys
sys.path.append("./")
#Setting Values
from config import *
USER = config["INSTA_USER"]
session_path = config["SESSION-Path"]
proxyip = config["proxyip"]

app = Flask(__name__)
#app.config.from_mapping(config)

@app.route('/', methods=['GET'])
def home():    
    return {'status': 'Online'}

# TikTok
# Get metadata
@app.route('/api/tiktok/<video_username>/<video_id>', methods=['GET'])
def data(video_username, video_id):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37'}
    web_id = str(random.randint(10000, 999999999))
    cookie = { 'tt_webid': web_id, 'tt_webid_v2': web_id }
    api_url = ('https://www.tiktok.com/node/share/video/@' + video_username + '/' + video_id)
    response = requests.request("get", api_url, headers=headers, cookies=cookie)
    data = json.loads(response.text)
    if data["statusCode"] == 0:
        return data['itemInfo']['itemStruct']
    else:
        proxies = dict(https=f'http://{proxyip}')
        response = requests.request("get", api_url, headers=headers, proxies=proxies, cookies=cookie)
        data = json.loads(response.text)
        if data["statusCode"] == 0:
            return data['itemInfo']['itemStruct']
        else:
            return {"statusCode": 404}


# Instagram
L = instaloader.Instaloader()
# login credentials
try:
    try:
        L.load_session_from_file(USER)
    except:
        L.load_session_from_file(USER, f'{session_path}/session-{USER}')
except:
    print('Instagram Session File Not Found Please Add it, otherwise youll get blocked by instagram.')
# Get metadata
@app.route('/api/instagram/<shortcode>', methods=['GET'])
def gp(shortcode):
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        return json.dumps(post._full_metadata_dict, ensure_ascii=False)
    except instaloader.exceptions.BadResponseException:
        return {"statusCode": 404}

from threading import Thread
def run():
  app.run(host='0.0.0.0',port=8080)

def run_api():  
    t = Thread(target=run)
    t.start()