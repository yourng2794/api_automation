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
from selenium.webdriver.chrome.options import Options


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
        self.CaseTitle= '[UI] BC check adm message'
        self.CaseNote= ''
        self.TestCaseID= '150611'
        # (CaseNote: can be blank ''. Use it to leave some notes or description of this case which will be displayed in test report)
        # ----------------------------------------------------------------------------------------------
        self.TestResult = 'FAIL'
        self.CurrentFile = os.path.basename(__file__)
        BaseCase.TestInfo = MyTest
        self.res_log = ''
        self.filename = tooldir+'\\code.jpg'  # I assume you have a way of picking unique filenames
        self.env = IniValue('setting', 'TestEnv.bc_ui_url')
        self.username = IniValue('setting', 'PlayGame.bc_acc')
        self.password = IniValue('setting', 'PlayGame.bc_pwd')
        
    def setPreCondition(self):
        WriteLog('********Test Case: '+self.CurrentFile+'********')
        # [QA] Set up Pre-condition if any
        WriteLog('Set up Pre-condition of this case...')
        chrome_options = Options()
        chrome_options.add_argument('--allow-outdated-plugins')
        self.driver = webdriver.Chrome(tooldir+'\\chromedriver.exe', options=chrome_options)
        self.driver.maximize_window()
        self.driver.implicitly_wait(self.TestInfo.normal_time)
        self.accept_next_alert = True
        self.CaseNote = WriteDebugLog(self.CaseNote, 'Success open browser.')
        self.driver.get(self.env)
        time.sleep(1)
        id_loginOpen = self.driver.find_element_by_id('loginOpen')
        id_loginOpen.click()
        username = self.driver.find_element_by_id('acc')
        username.click()
        username.send_keys(self.username)
        password = self.driver.find_element_by_id('pwd')
        password.click()
        password.send_keys(self.password)
        self.driver.implicitly_wait(self.TestInfo.very_short_time)
        retry = 0
        while (retry < 10):
            try:
                self.driver.find_element_by_id("lgPassBtn").click()
                time.sleep(1)
                code = self.driver.find_element_by_id("code")
                code.clear()
                passCode = self.driver.find_element_by_id("passCode")
                imgdata = b64decode(passCode.get_attribute("src").split(',')[1])
                with open(self.filename, 'wb') as decode_response_data:
                    decode_response_data.write(imgdata)
                 
                new_code, self.res_log = ApiCodeDetect('\n\t\t', self.res_log, self.filename)
                code.send_keys(new_code)
                time.sleep(0.5)
                next_btn = self.driver.find_element_by_id('loginIn')
                next_btn.click()
#                 id_loginNote = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'loginNote')),'Code fail')
#                 if(id_loginNote.text == '验证码错误'):
#                     continue
#                 else:
                id_informLg = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'informLg')),'BC_timeout (very_short_time)')
                if('登入成功' in id_informLg.text):
                    id_informLg.find_element_by_class_name('lg-close').click()
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
        result_list = []
        adm_list = []
        print_tab = '\n\t\t'
        self.CaseNote = WriteDebugLog(self.CaseNote, '\t'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+'>> Start to [UI] BC check adm message'+'\n')
        adm_title = IniValue('setting', 'API.adm_title')
        adm_modifytime = IniValue('setting', 'API.adm_modifytime')
        try:
            hamBtn = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'hamBtn')),'hamBtn is not visible')
            hamBtn.click()
            navMailBtn = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'navMailBtn')),'navMailBtn is not visible')
            navMailBtn.click()
            mailList = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div[id="mailList"] div[class="mail-list-tit-box"]')),'mailList is not visible')
            for eachMail in mailList:
                comp_title = eachMail.find_element_by_css_selector('div[class="mail-list-tit"] div div[class="mail-tit new getmail"]')
                comp_time = (eachMail.find_elements_by_css_selector('div[class="mail-list-tit"] div'))[-1]
                if(comp_title.text == adm_title):
                    adm_list.append(comp_title.text)
                    if(comp_time.text == adm_modifytime):
                        adm_list.append(comp_time.text)
                        result_list.append('PASS')
                        break
                    else:
                        result_list.append('FAIL')
                else:
                    result_list.append('FAIL')
        except Exception as e:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'Exception: '+ str(e))
            result_list.append('FAIL')
        
        self.res_log = WriteDebugLog(self.res_log, ', '.join(adm_list))
        if('PASS' in result_list):
            self.TestResult = 'PASS'
        else:
            self.TestResult = 'FAIL'

        # [QA] Be sure to save result "PASS" or "FAIL" to self.TestResult
        # ----------------------------------------------------------------------------------------------

        self.CaseNote = WriteDebugLog(self.CaseNote, '\n\t'+'#Test Result: ' + self.TestResult)
        self.teardown()

        self.TestCaseEndTime = datetime.now()
        self.TestCaseDuration = ((self.TestCaseEndTime - self.TestCaseStartTime).total_seconds())*1000000
        if (self.TestCaseDuration == 0):
            self.TestCaseDuration = ' less than 1'
        self.TestInfo.setTestRunEndTime()
        
        self.CaseNote = WriteDebugLog(self.CaseNote, '\n\t'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+'<< End to [UI] BC check adm message')
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