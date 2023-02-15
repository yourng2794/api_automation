from locust import HttpLocust, TaskSet
import pickle
import os
import inspect
from base64 import b64decode
from datetime import datetime, timedelta
import operator
from PIL import Image, ImageFilter, ImageDraw
import cv2
import queue
import numpy as np
from O2oUtility import WriteLog, ReplaceIniValue

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
tooldir = os.path.dirname(os.path.dirname(currentdir))
compare_path = currentdir+'\\compare'

def save_cookies(requests_cookiejar, filename):
    with open(filename, 'wb') as f:
        pickle.dump(requests_cookiejar, f)

def Add_Seconds(tm, secs):
    fulldate = datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    fulldate = fulldate + timedelta(seconds=secs)
    return fulldate.time()

def ApiCodeDetect(src_file):
    print_tab = '\n\t\t'
    is_fail = True
    while(is_fail):
        try:
            im = Image.open(src_file) #code.jpg
#             im.show()
            
            gray = im.convert('L')
            # gray.show()
#             binary = im.convert('1')
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
                    im_sommth.crop(box).save(currentdir+'\\'+str(i) + "_.jpg")
            
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
                        img.crop(box).save(currentdir+'\\'+str(i) + "_.jpg")
#                             img.crop(box).show() # show corp image 
            
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
            is_fail = False
            
        except Exception as e:
            is_fail = True
            WriteLog('\n\t\t- Exception: on solve pic... %s' % str(e))
            
        finally:
            res_log = WriteLog('\n\t\t- - - ')
          
        try:
            compare_code = ''  
            def getGray(image_file):
                tmpls=[]
                for h in range(0,  image_file.size[1]):#h
                    for w in range(0, image_file.size[0]):#w
                        tmpls.append( image_file.getpixel((w,h)))
                return tmpls
               
            def getAvg(ls):#获取平均灰度值
                return sum(ls)/len(ls)
               
            def getMH(a,b):#比较100个字符有几个字符相同
                dist = 0;
                for i in range(0,len(a)):
                    if a[i]==b[i]:
                        dist=dist+1
                return dist
               
            def getImgHash(fne):
                image_file = Image.open(fne) # 打开
                image_file=image_file.resize((12, 12))#重置图片大小我12px X 12px
                image_file=image_file.convert("L")#转256灰度图
                Grayls=getGray(image_file)#灰度集合
                avg=getAvg(Grayls)#灰度平均值
                bitls=''#接收获取0或1
                #除去变宽1px遍历像素
                for h in range(1,  image_file.size[1]-1):#h
                    for w in range(1, image_file.size[0]-1):#w
                        if image_file.getpixel((w,h))>=avg:#像素的值比较平均值 大于记为1 小于记为0
                            bitls=bitls+'1'
                        else:
                            bitls=bitls+'0'
                return bitls
            
            for i in range(4):
                dict1 = {}
                a=getImgHash(currentdir+'\\'+str(i)+"_.jpg")#图片地址自行替换
                files = os.listdir(compare_path)#图片文件夹地址自行替换
                for file in files:
                    b=getImgHash(compare_path+"\\"+str(file))
                    compare=getMH(a,b)
                    dict1[str(file)] = int(compare)
            #         print (file,u'相似度',str(compare)+'%')
                right_key = max(dict1.items(), key=operator.itemgetter(1))[0]
                WriteLog(print_tab+'- '+right_key.split('_')[0]+', accurate: '+str(dict1[right_key])+' %')
#                 print('----------------------------------------------')
                compare_code += str(right_key.split('_')[0])
            
            is_fail = False
            return (compare_code, res_log)
        
        except Exception as e:
            is_fail = True
            WriteLog(print_tab+'- Exception: on compare pic... %s' % str(e))
              
        finally:
            res_log = WriteLog(print_tab+'- - - ')
            
def login(l):
    i = 0
    while (i < 10):
        r = l.client.post("/login/code", {})
        save_cookies(r.cookies, 'session')
        imgdata = b64decode(r)
        with open(tooldir+'\\code.jpg' , 'wb') as decode_response_data:
            decode_response_data.write(imgdata)
    #         expired_time = Add_Seconds(datetime.now().time(), 60)
        new_code = ApiCodeDetect(tooldir+'\\code.jpg')
        response_data = l.client.post("/login", {"acc":"tommy", "pwd":"123456", "code":new_code})
        if(response_data):
            break
        i += 1
    
def logout(l):
    l.client.post("/logout", {})

def index(l):
    l.client.get("/")

def profile(l):
    l.client.get("/profile")

class UserBehavior(TaskSet):
    tasks = {index: 2, profile: 1}

    def on_start(self):
        login(self)

    def on_stop(self):
        logout(self)

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000