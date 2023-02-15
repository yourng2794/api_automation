# 1 Show image
import pytesseract
from PIL import Image, ImageFilter, ImageDraw
import queue
import numpy as np
import hashlib
import os

im = Image.open('code.jpg')
# im.show()

gray = im.convert('L')
# gray.show()
binary = im.convert('1')
# binary.show()

def getPixel(image,x,y,G,N):
    L = image.getpixel((x,y))
    if L > G:
        L = True
    else:
        L = False
 
    nearDots = 0
    if L == (image.getpixel((x - 1,y - 1)) > G):
        nearDots += 1
    if L == (image.getpixel((x - 1,y)) > G):
        nearDots += 1
    if L == (image.getpixel((x - 1,y + 1)) > G):
        nearDots += 1
    if L == (image.getpixel((x,y - 1)) > G):
        nearDots += 1
    if L == (image.getpixel((x,y + 1)) > G):
        nearDots += 1
    if L == (image.getpixel((x + 1,y - 1)) > G):
        nearDots += 1
    if L == (image.getpixel((x + 1,y)) > G):
        nearDots += 1
    if L == (image.getpixel((x + 1,y + 1)) > G):
        nearDots += 1
 
    if nearDots < N:
        return image.getpixel((x,y-1))
    else:
        return None

def clearNoise(image,G,N,Z):
    draw = ImageDraw.Draw(image)
    for i in range(0,Z):
        for x in range(1,image.size[0] - 1):
            for y in range(1,image.size[1] - 1):
                color = getPixel(image,x,y,G,N)
                if (color != None):
                    draw.point((x,y),color)

clearNoise(gray,150,4,5)
# gray.show()


def dec_noise(img, threshold):
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    out = img.point(table, '1')
    return out

# dec_noise(gray, 180).show()

im_sommth = dec_noise(gray, 180).filter(ImageFilter.MedianFilter(size=3))
# im_sommth.show()
# dec_noise(im_sommth, 160).show()
# dec_noise(im_sommth, 160).save("black_white.jpg")

def depoint(img):
    """传入二值化后的图片进行降噪"""
    pixdata = img.load()
    w,h = img.size
    for y in range(1,h-1):
        for x in range(1,w-1):
            count = 0
            if pixdata[x,y-1] > 245:#上
                count = count + 1
            if pixdata[x,y+1] > 245:#下
                count = count + 1
            if pixdata[x-1,y] > 245:#左
                count = count + 1
            if pixdata[x+1,y] > 245:#右
                count = count + 1
            if pixdata[x-1,y-1] > 245:#左上
                count = count + 1
            if pixdata[x-1,y+1] > 245:#左下
                count = count + 1
            if pixdata[x+1,y-1] > 245:#右上
                count = count + 1
            if pixdata[x+1,y+1] > 245:#右下
                count = count + 1
            if count > 4:
                pixdata[x,y] = 255
    return img

def vertical(img):
    """传入二值化后的图片进行垂直投影"""
    pixdata = img.load()
    w,h = img.size
    ver_list = []
    # 开始投影
    for x in range(w):
        black = 0
        for y in range(h):
            if pixdata[x,y] == 0:
                black += 1
        ver_list.append(black)
    # 判断边界
    l,r = 0,0
    flag = False
    cuts = []
    for i,count in enumerate(ver_list):
        # 阈值这里为0
        if flag is False and count >50:
            l = i
            flag = True
        if flag and count == 5:
            r = i-1
            flag = False
            cuts.append((l,r))
    return cuts

v = vertical(im_sommth)
w, h = im_sommth.size
for i, item in enumerate(v):
    if(i <4):
        box = (item[0], 0, item[1], h)
        im_sommth.crop(box).save(str(i) + ".jpg")

def cfs(img):
    """传入二值化后的图片进行连通域分割"""
    pixdata = img.load()
    w, h = img.size
    visited = set()
    q = queue.Queue()
    offset = [(-2,-2),(-2,-1),(-1,-2),(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1),(1,2),(2,1),(2,2)]
    cuts = []
    for x in range(w):
        for y in range(h):
            x_axis = []
            # y_axis = []
            if pixdata[x, y] == 0 and (x, y) not in visited:
                q.put((x, y))
                visited.add((x, y))
            while not q.empty():
                x_p, y_p = q.get()
                for x_offset, y_offset in offset:
                    x_c, y_c = x_p + x_offset, y_p + y_offset
                    if (x_c, y_c) in visited:
                        continue
                    visited.add((x_c, y_c))
                    try:
                        if pixdata[x_c, y_c] == 0:
                            q.put((x_c, y_c))
                            x_axis.append(x_c)
                            # y_axis.append(y_c)
                    except:
                        pass
            if x_axis:
                min_x, max_x = min(x_axis), max(x_axis)
                if max_x - min_x > 3:
                    # 宽度小于3的认为是噪点，根据需要修改
                    cuts.append((min_x, max_x + 1))
    return cuts

def saveSmall(img, cuts):
    w, h = img.size
#     pixdata = img.load()
    for i, item in enumerate(cuts):
        if(i <4):
            box = (item[0], 0, item[1], h)
            img.crop(box).save(str(i) + ".jpg")
            img.crop(box).show()

def get_fratures(array):
    #拿到数组的高度和宽度
#     qq = array.shape
    h, w = array.shape
    data= []
    for x in range(0, w//4):
        offset_y = x*4
        temp = []
        for y in range(0, h//4):
            offset_xx = y*4
            temp.append(sum(sum(array[0+offset_y:4+offset_y, 0+offset_xx:4+offset_xx])))
            data.append(temp)
            return np.asarray(data)
    
saveSmall(im_sommth, cfs(im_sommth))

for i in range(4):
    img = Image.open(str(i)+".jpg")
    img = img.resize((15,30))
    img = img.point(lambda x:1 if x > 120 else 0)
    img_array = np.asarray(img)
    print(img_array)
#     features_array = get_fratures(img_array)
    features_vector =img_array.reshape(img_array.shape[0]*img_array.shape[1])
    print(features_vector)
#     img.save(str(i) + ".jpg")


def recognize_captcha(img_path):
    im = Image.open(img_path)
    # threshold = 140
    # table = []
    # for i in range(256):
    #     if i < threshold:
    #         table.append(0)
    #     else:
    #         table.append(1)
    #
    # out = im.point(table, '1')
    num = pytesseract.image_to_string(im)
    return (num)