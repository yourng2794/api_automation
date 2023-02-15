#!/usr/bin/python
#coding=utf-8
import operator
from PIL import Image, ImageFilter, ImageDraw
import queue
import numpy as np
import os
import locale
import logging
import inspect
import shutil
from datetime import datetime
from datetime import timedelta
from base64 import b64decode

from TestRun import TestRunning
from BaseTestCase import BaseCase
from O2oUtility import WriteLog, DeleteFile, WriteDebugLog, ApiResponse

locale.setlocale(locale.LC_CTYPE, 'chinese')
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

class TestCase(BaseCase):
    
    def __init__(self, MyTest):
        # ---------------- [QA] Modify these variables for your test case! ----------------------------------       
        self.Feature= currentdir.split('\\')[-1]
        self.CaseTitle= '[Portal] API POST sign in exist account'
        self.CaseNote= ''
        self.TestCaseID= '16'
        # (CaseNote: can be blank ''. Use it to leave some notes or description of this case which will be displayed in test report)
        # ----------------------------------------------------------------------------------------------
        self.TestResult = 'FAIL'
        self.CurrentFile = os.path.basename(__file__)
        self.res_log = ''
        BaseCase.TestInfo = MyTest
        self.filename = 'code.jpg'  # I assume you have a way of picking unique filenames
        
    def setPreCondition(self):
        WriteLog('********Test Case: '+self.CurrentFile+'********')
        # [QA] Set up Pre-condition if any
        
        
    def generateResults(self, collectOtherFile):
        # 1.[QA] if collectOtherFile == True, Collect temp results or other files if this cases needs...
        if (collectOtherFile):
            WriteLog('\t'+'Collect temp results or other files...')
            
            try:
                filepath1='TestDebug.log'
                if (os.path.exists(filepath1)):
                    shutil.copy(filepath1, self.TestInfo.TestResultFolder+self.TestInfo.TestRunFolder+self.Feature)
                    os.rename(self.TestInfo.TestResultFolder+self.TestInfo.TestRunFolder+self.Feature+"\\"+os.path.basename(filepath1), self.TestInfo.TestResultFolder+self.TestInfo.TestRunFolder+self.Feature+"\\"+self.CurrentFile+"_"+os.path.basename(filepath1))
            except Exception as e:
                WriteLog("Exception: on collectOtherFiles... %s" % str(e.with_traceback))
            WriteLog('...file '+ filepath1 + " copied")
            self.CaseNote = self.res_log
        # 2. Run generateResults() of parent class
        else:
            self.CaseNote = self.res_log
            super().generateResults()
        
        
    def teardown(self):
        # [QA] Tear down the environment if it needs
        WriteLog('\t'+'>> Start Tear Down')
        DeleteFile(self.filename)
        WriteLog('\t'+'<< End Tear Down')
        
        
    def run(self, copy_result):
        self.TestCaseStartTime = datetime.now()
        self.setPreCondition()
        result_list = []
        self.res_log = WriteDebugLog(self.res_log, '\n\tStart >>'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Portal] API POST sign in exist account'+'\n')
        is_fail = True
        #=======================================================================
        # Current time increase operation.
        # Usage: 
        # a = datetime.now().time() # 09:11:55.775695
        # b = Add_Seconds(a, 300) # 09:16:55
        #=======================================================================
        def Add_Seconds(tm, secs):
            fulldate = datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
            fulldate = fulldate + timedelta(seconds=secs)
            return fulldate.time()
        while(is_fail):
            try:
                return_value, response_time, response_data, self.res_log = ApiResponse('\n\t\t', self.res_log, 'admin_login_code', False, True)
                imgdata = b64decode(response_data)
                with open(self.filename, 'wb') as decode_response_data:
                    decode_response_data.write(imgdata)
                    expired_time = Add_Seconds(datetime.now().time(), 60)
                    self.res_log = WriteDebugLog(self.res_log, '\n\t\t- Session expired until: '+ str(expired_time))
                    
                if(return_value):
                    result_list.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, '\n\t\t- API success (status and response are correct).')
                    self.res_log = WriteDebugLog(self.res_log, '\n\t\t- Response time: '+ response_time)
                    self.res_log = WriteDebugLog(self.res_log, '\n\t\tResponse data: '+ response_data)
                    self.res_log = WriteDebugLog(self.res_log, '\n\t\t---')
                    
                else:
                    result_list.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, '\n\t\t- API fail (status or response is incorrect).')
                    self.res_log = WriteDebugLog(self.res_log, '\n\t\tResponse data: '+ response_data)
                    self.res_log = WriteDebugLog(self.res_log, '\n\t\t---')
                    
                im = Image.open('code.jpg')
#                 im.show()
                
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
                        im_sommth.crop(box).save(str(i) + "_.jpg")
                
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
                            img.crop(box).save(str(i) + "_.jpg")
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
                result_list.append('FAIL')
                self.res_log = WriteDebugLog(self.res_log, '\n\t\t- Exception: on solve pic... %s' % str(e))
                
            finally:
                self.res_log = WriteDebugLog(self.res_log, '\n\t\t- - - ')
        
            try:
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
                
                compare_code = ''
                for i in range(4):
                    dict1 = {}
                    a=getImgHash(str(i)+"_.jpg")#图片地址自行替换
                    files = os.listdir(currentdir+"\\compare")#图片文件夹地址自行替换
                    for file in files:
                        b=getImgHash(currentdir+"\\compare\\"+str(file))
                        compare=getMH(a,b)
                        dict1[str(file)] = int(compare)
                #         print (file,u'相似度',str(compare)+'%')
                    right_key = max(dict1.items(), key=operator.itemgetter(1))[0]
                    print(right_key.split('_')[0])
                    print(str(dict1[right_key])+' %')
                    print('----------------------------------------------')
                    compare_code += str(right_key.split('_')[0])
                
                is_fail = False
            
            except Exception as e:
                is_fail = True
                result_list.append('FAIL')
                self.res_log = WriteDebugLog(self.res_log, '\n\t\t- Exception: on compare pic... %s' % str(e))
                  
            finally:
                self.res_log = WriteDebugLog(self.res_log, '\n\t\t- - - ')
            
        return compare_code
#===============================================================================
# Traninig data and store into \\compare
# Create by Tommy Han 2019/03/15
#===============================================================================
#         def copy_file(dest_dir, file, rec_id, num_index):
# #                 print(dest_dir+file.split('_')[0]+'_'+str(rec_id)+'.jpg')
#             if (os.path.exists(dest_dir+file.split('_')[0]+'_'+str(rec_id)+'.jpg')):
#                 rec_id += 1
#                 copy_file(dest_dir, file, rec_id, num_index)
#             else:
#                 print(dest_dir+file.split('_')[0]+'_'+str(rec_id)+'.jpg')
#                 os.rename(currentdir+'\\'+str(num_index)+'_.jpg' , dest_dir+file.split('_')[0]+'_'+str(rec_id)+'.jpg')
# #                 shutil.move(currentdir+'\\'+file.split('_')[0]+'_'+str(rec_id)+'.jpg', dest_dir+file.split('_')[0]+'_'+str(rec_id)+'.jpg')
#         
#         new_code = input('\n\t\t- Please enter code (4 digits): ')
#         list_new = list(new_code)
#         mov_dir = currentdir+'\\compare\\'
#         number_index = 0
#         for each_char in list_new:
#             index_id = 0
#             copy_file(mov_dir, str(each_char)+'_.jpg', index_id, number_index)
#             number_index += 1
        
        WriteLog(result_list)
        if('FAIL' in str(result_list) or not result_list):
            self.TestResult = 'FAIL'
        else:
            self.TestResult = 'PASS'
        self.res_log = WriteDebugLog(self.res_log, '\n\t\t# Test Result: '+self.TestResult)
        # [QA] Be sure to save result "PASS" or "FAIL" to self.TestResult
        # ----------------------------------------------------------------------------------------------

#         WriteLog('\t'+'Test Result: ' + self.TestResult)
        self.teardown()

        self.TestCaseEndTime = datetime.now()
        self.TestCaseDuration = ((self.TestCaseEndTime - self.TestCaseStartTime).total_seconds())*1000000
        if (self.TestCaseDuration == 0):
            self.TestCaseDuration = ' less than 1'
        self.TestInfo.setTestRunEndTime()
        
        # [QA] Set "collectOtherFile = True" if there is any file that should be collected        
        self.res_log = WriteDebugLog(self.res_log, '\n\n\tEnd << '+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Portal] API POST sign in exist account')
        TestCase.generateResults(self, copy_result)
        
        
# [QA] Be sure to test this case before it's merged to TestSuites
if __name__ == "__main__":
#             logging.debug()< logging.info()< logging.warning()< logging.error()< logging.critical()
    root_logger= logging.getLogger()
    root_logger.setLevel(logging.INFO) # or whatever
    handler = logging.FileHandler('TestDebug.log', 'w', 'utf-8') # or whatever
    handler.setFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s') # or whatever
    root_logger.addHandler(handler)
    
    WriteLog(" -------------------- Running a single Test Case --------------------")

    MyTest = TestRunning()
    MyTest.readTestConfig()
    if (MyTest.createTestRunFolder() == 'Error'):
        WriteLog("Test Tool will exit...")
        os._exit(1)
    
    thiscase = TestCase(MyTest)
    dir2 = MyTest.TestResultFolder + MyTest.TestRunFolder + thiscase.Feature
    if not os.path.exists(dir2):
        os.makedirs(dir2)
    
    thiscase.run(True)

    WriteLog('Test Case: ' + thiscase.CaseTitle + ', Test Result: ' + thiscase.TestResult)
    # Clear Test Tool Debug Log
    f = open("TestDebug.log", "w")
    f.flush()
    f.close()