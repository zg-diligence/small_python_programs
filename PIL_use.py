from PIL import Image
from PIL import ImageOps
from PIL import ImageFilter
from matplotlib import pyplot as plt

img = Image.open('index.jpg')
img = img.resize((1920,1080), Image.ANTIALIAS)
img.save('index_1.jpg', quality=100)

# 调整图片大小
import os

files = os.listdir('love')

for file in files:
    img = Image.open('love/' + file)
    img = img.resize((200, 200), Image.ANTIALIAS)
    img.save('zip_love/' + file, quality=100)

# # 压缩图片
# for i in range(1, 28):
#     img = Image.open('pics/' + str(i) +'.jpg')
#     if i in [14, 15, 16, 22]:
#         size = (220, 220)
#     else:
#         size = (80, 80)
#     img.thumbnail(size,Image.ANTIALIAS)
#     img = ImageOps.expand(img, border=5, fill='#F5F5F5')  # 加边框
#     img.save('zip_pics/' + str(i) + '.png','JPEG')
#
# # 图片粘贴位置
# sizes = [(0,    90),  (0,   180),   (0,   600),   (0,   690),
#          (90,    0),  (90,   90),   (90,  180),   (90,  270),  (90,  510), (90, 600), (90, 690), (90, 780),
#          (180,   0),  (180,  90),   (180, 320),   (180, 550),  (180, 780),
#          (270,   0),  (270, 780),
#          (410, 140),  (410, 230),   (410, 320),   (410, 550),  (410, 640),
#          (500, 230),  (500, 550),
#          (640, 390)]
# sizes = [(b+100, a+200) for a,b in sizes]
#
# # 读取图片
# imgs = [Image.open('zip_pics/' + str(i) +'.png') for i in range(1, 28)]
#
# # 粘贴图片
# img = Image.new('RGB',(1000,1000),'#AFEEEE')
# for i in range(1, 28):
#     img.paste(imgs[i-1], box=sizes[i-1])
# img = img.resize((1500, 1500))
#
# # 展示保存图片
# img.show()
# img.save('pics/love.jpg')
#
# # 获取图片点坐标
# img = Image.open('pics/love.jpg')
# plt.imshow(img)
# x = plt.ginput(1)
# plt.show()
#
# # 图像增强
# img = Image.open('test.jpg')
# img = img.filter(ImageFilter.DETAIL)
# img.save('new_test.jpg')