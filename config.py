import os
from dotenv import load_dotenv
load_dotenv()

config = {
    "TOKEN": '' or os.getenv("TOKEN"), #Discord Bot Token.
    'Prefix': '.',

    "INSTA_USER": '' or os.getenv("IG_USERNAME"), # Instagram Username
    "SESSION-Path": './api', # get session with instaloader -l USERNAME, then copy the session file to this directory.

    "stream_email": '' or os.getenv("stream_email"), # Streamable email https://streamable.com/.
    "stream_pass": '' or os.getenv("stream_pass"), # Streamable pass.

    "proxyip": '' or os.getenv("proxyip"), # Required for tiktok to work, use http proxy, example 0.0.0.0:80 or user:pass@0.0.0.0:80. 

    "path": './api/downloads-cache', # download path.
    "limitsize": 8388608, # 8 mb for file size limit set by discord.
    "sEmoji": '☑',
}