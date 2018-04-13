import os
import requests
from urllib import request
from bs4 import BeautifulSoup

WALL_PATH = '/home/gzhang/Pictures/Wallpapers/'
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/'
          '537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

def craw_pics():
    opener=request.build_opener()
    opener.addheaders=[('User-Agent', headers['User-Agent'])]
    request.install_opener(opener)

    content = requests.get('https://bing.ioliu.cn/?p=1', headers=headers)
    bsObj = BeautifulSoup(content.text, 'html.parser')
    imgs = bsObj.find_all('img', class_='progressive__img progressive--not-loaded')
    for img in imgs:
        img_url = list(img['src'])
        img_url[-11:-4] = '1920x1080'
        img_url = ''.join(img_url)
        request.urlretrieve(img_url, WALL_PATH + '%s.jpg' % (imgs.index(img)))

def change_wallpaper():
    os.system('export GIO_EXTRA_MODULES=/usr/lib/x86_64-linux-gnu/gio/module/')
    os.system('gsettings set org.gnome.desktop.background picture-uri \"file:' + WALL_PATH + '\"')

if __name__ == '__main__':
    craw_pics()
