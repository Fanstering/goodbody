import sys
sys.path.insert(0, r'D:\program\myPro\goodbody\tools')

import yt_dlp

url = "https://v.douyin.com/Uq__oopUYpU/"
output_path = r'D:\program\myPro\goodbody\video\fitness_video.%(ext)s'

ydl_opts = {
    'outtmpl': output_path,
    'format': 'best',
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

print("下载完成")
