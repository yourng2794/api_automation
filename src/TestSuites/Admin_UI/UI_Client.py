#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging, sys, os, inspect, shutil, locale
from datetime import datetime
import time
from base64 import b64decode
from BaseTestCase import BaseCase
from O2oUtility import WriteLog, WriteDebugLog, IniValue, ApiCodeDetect
from TestRun import TestRunning

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

locale.setlocale(locale.LC_CTYPE, 'chinese')
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
tooldir = os.path.dirname(os.path.dirname(currentdir))
if tooldir not in sys.path:
    sys.path.insert(0, tooldir)
iniFile = tooldir+'\\ini\\setting.ini'

class TestCase(BaseCase):
    
    def __init__(self,MyTest):
        # ---------------- [QA] Modify these variables for your test case! ----------------------------------       
        self.Feature= currentdir.split('\\')[-1]
        self.CaseTitle= '[UI] admin UI client'
        self.CaseNote= ''
        self.TestCaseID= '150611'
        # (CaseNote: can be blank ''. Use it to leave some notes or description of this case which will be displayed in test report)
        # ----------------------------------------------------------------------------------------------
        self.TestResult = 'FAIL'
        self.CurrentFile = os.path.basename(__file__)
        BaseCase.TestInfo = MyTest
        self.res_log = ''
        self.filename = tooldir+'\\code.jpg'  # I assume you have a way of picking unique filenames
        self.env = IniValue('setting', 'TestEnv.admin_web_test')
        
    def setPreCondition(self):
        WriteLog('********Test Case: '+self.CurrentFile+'********')
        # [QA] Set up Pre-condition if any
        WriteLog('Set up Pre-condition of this case...')
        self.driver = webdriver.Chrome(tooldir+'\\chromedriver.exe')
        self.driver.maximize_window()
        self.driver.implicitly_wait(self.TestInfo.normal_time)
        self.accept_next_alert = True
        self.CaseNote = WriteDebugLog(self.CaseNote, 'Success open browser.')
        self.driver.get(self.env)
        time.sleep(1)
        username = self.driver.find_element_by_id('acc')
        username.click()
        username.send_keys(IniValue('setting', 'TestData.admin_web_acc'))
        password = self.driver.find_element_by_id('pwd')
        password.click()
        password.send_keys(IniValue('setting', 'TestData.admin_web_pwd'))
        self.driver.implicitly_wait(self.TestInfo.very_short_time)
        retry = 0
        while (retry < 10):
            try:
                self.driver.find_element_by_id("passCode").click()
                time.sleep(3)
                code = self.driver.find_element_by_id("code")
                code.click()
                passCode = self.driver.find_element_by_id("passCode")
                imgdata = b64decode(passCode.get_attribute("src").split(',')[1])
                with open(self.filename, 'wb') as decode_response_data:
                    decode_response_data.write(imgdata)
                
                new_code, self.res_log = ApiCodeDetect('\n\t\t', self.res_log, self.filename)
                code.send_keys(new_code)
                time.sleep(1)
                next_btn = self.driver.find_element_by_id('submit')
                next_btn.click()
#                 if(self.driver.find_element_by_id('errorHint').text == ''):
                WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'pade-logo')),'Admin_timeout (very_short_time)')
                break
            
            except Exception as e:
                self.CaseNote = WriteDebugLog(self.CaseNote, 'Exception: on "Browser time out"... %s' % str(e))
            finally:
                retry += 1
        if(retry >= 10):
            self.CaseNote = WriteDebugLog(self.CaseNote, 'Retry browser fail.')
        
        
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
         
        # 2. Run generateResults() of parent class
        else:
            super().generateResults()
        
        
    def teardown(self):
        # [QA] Tear down the environment if it needs
        WriteLog('\t'+'>> Tear Down of this case')
        self.driver.quit()
        WriteLog('\t\t'+'Driver closed')
        WriteLog('\t'+'<< End Tear Down')
        
        
    def run(self, copy_result):
        self.TestCaseStartTime = datetime.now()
        self.setPreCondition()
        circle_dict = {}
        result_list = []
        self.CaseNote = WriteDebugLog(self.CaseNote, '\t'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+'>> Start to admin UI client'+'\n')
        
        # Part 1 check redirect link
        WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'nav-client')),'icon is not visible').click()
        print('123')
#         circle_boxs_list = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div.circle-group a[class="circle-box"]:not([style="display: none;"])')),'circle_box is not visible')
#         circle_boxs_list = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div[class="circle-group"] a[class="circle-box"]')),'circle_box is not visible')
        
        circle_boxs_list = self.driver.find_elements_by_css_selector('div[class="circle-group"] a[class="circle-box"]')
        
#         circle_boxs_list = circle_group.find_elements_by_class_name('circle-box')
        print(len(circle_boxs_list))
        for circle_box in circle_boxs_list:
            circle_dict[(circle_box.find_element_by_tag_name('span').text)] = (circle_box.get_attribute('href').replace(self.env,''))
        
        if((circle_dict['客户列表'] == 'client_mem_list.html') and (circle_dict['帐号转移'] == 'client_transfer_out_list.html') 
           and (circle_dict['客户类型'] == 'client_type_list.html')):
            result_list.append('True')
#             self.TestResult = 'PASS'
        else:
            result_list.append('False')
#             self.TestResult = 'FAIL'
        print(result_list)
        
        circle_len = len(circle_boxs_list)
        # Part 2 check 会员列表
        for i in range(circle_len):
            bread_title = []
            circle_boxs_list = self.driver.find_elements_by_css_selector('div[class="circle-group"] a[class="circle-box"]')
            print(circle_boxs_list[i].text)
            if((circle_boxs_list[i].get_attribute('href').replace(self.env,'') == 'client_mem_list.html')):
                circle_boxs_list[i].click()
#                 self.driver.find_element_by_css_selector('ul[class="list"][id="datalist"]')
                WebDriverWait(self.driver,self.TestInfo.short_time).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul[class="list"][id="datalist"]')),'list-group is not visible')
                bread_titles_list = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div.bread span')),'bread title is not visible')
                for bread_title_list in bread_titles_list:
                    bread_title.append(bread_title_list.text)
                
                if(bread_title[-1] == '客户列表'):
                    result_list.append('True')
                else:
                    result_list.append('False')
                
#             elif((circle_boxs_list[i].get_attribute('href').replace(self.env,'') == 'client_transfer_out_list.html')):
#                 circle_boxs_list[i].click()
#                 WebDriverWait(self.driver,self.TestInfo.short_time).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul[class="list"][id="dataList"]')),'list-group is not visible')
#                 bread_titles_list = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div.bread span')),'bread title is not visible')
#                 for bread_title_list in bread_titles_list:
#                     bread_title.append(bread_title_list.text)
#                 
#                 if(bread_title[-1] == '帐号转移'):
#                     result_list.append('True')
#                 else:
#                     result_list.append('False')
                
            elif((circle_boxs_list[i].get_attribute('href').replace(self.env,'') == 'client_type_list.html')):
                circle_boxs_list[i].click()
                WebDriverWait(self.driver,self.TestInfo.short_time).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul[class="list"][id="sortList"]')),'list-group is not visible')
                bread_titles_list = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div.bread span')),'bread title is not visible')
                for bread_title_list in bread_titles_list:
                    bread_title.append(bread_title_list.text)
                
                if(bread_title[-1] == '客户类型'):
                    result_list.append('True')
                else:
                    result_list.append('False')
                    
            print(bread_title)
            # Back to previous page
            self.driver.find_element_by_class_name('nav-client').click()
#             WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'nav-client')),'icon is not visible').click()
#             WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div.circle-group a.circle-box')),'circle_box is not visible')
            
        print(result_list)
        
        if('False' in str(result_list) or not result_list):
            self.TestResult = 'FAIL'
        else:
            self.TestResult = 'PASS'
        # Part 2 check 会员列表
        # [QA] Be sure to save result "PASS" or "FAIL" to self.TestResult
        # ----------------------------------------------------------------------------------------------

        self.CaseNote = WriteDebugLog(self.CaseNote, '\n\t'+'#Test Result: ' + self.TestResult)
        self.teardown()

        self.TestCaseEndTime = datetime.now()
        self.TestCaseDuration = ((self.TestCaseEndTime - self.TestCaseStartTime).total_seconds())*1000000
        if (self.TestCaseDuration == 0):
            self.TestCaseDuration = ' less than 1'
        self.TestInfo.setTestRunEndTime()
        
        self.CaseNote = WriteDebugLog(self.CaseNote, '\n\t'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+'<< End to admin UI client')
        # [QA] Set "collectOtherFile = True" if there is any file that should be collected
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