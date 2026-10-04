import urllib.request
import os

save_dir = r'D:\program\myPro\goodbody\assets\images'

images = [
    ('pike_pushup.jpg', 'https://aka.doubaocdn.com/s/yfN51wkgCP'),
    ('standard_pushup.jpg', 'https://aka.doubaocdn.com/s/YzwF1wkgCS'),
    ('plank.jpg', 'https://aka.doubaocdn.com/s/gXh21wkgCW'),
    ('knee_pushup.jpg', 'https://aka.doubaocdn.com/s/zcZ51wkgCd'),
    ('situps_sicily.jpg', 'https://aka.doubaocdn.com/s/o5691wkgCh'),
    ('mountain_climbers.jpg', 'https://aka.doubaocdn.com/s/ZHCG1wkgCk'),
    ('pike_shoulder_push.jpg', 'https://aka.doubaocdn.com/s/lPKR1wkgD5'),
]

for filename, url in images:
    filepath = os.path.join(save_dir, filename)
    try:
        urllib.request.urlretrieve(url, filepath)
        print(f'下载成功: {filename}')
    except Exception as e:
        print(f'下载失败 {filename}: {e}')

print('全部下载完成')
