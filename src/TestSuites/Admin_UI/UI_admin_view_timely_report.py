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
from selenium.webdriver.support.ui import Select
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
        self.CaseTitle= '[UI] admin create banker'
        self.CaseNote= ''
        self.TestCaseID= '150611'
        # (CaseNote: can be blank ''. Use it to leave some notes or description of this case which will be displayed in test report)
        # ----------------------------------------------------------------------------------------------
        self.TestResult = 'FAIL'
        self.CurrentFile = os.path.basename(__file__)
        BaseCase.TestInfo = MyTest
        self.res_log = ''
        self.filename = tooldir+'\\code.jpg'  # I assume you have a way of picking unique filenames
        self.env = IniValue('setting', 'TestEnv.admin_web_url')
        
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
        username.send_keys(IniValue('setting', 'TestData.admin_boss_acc'))
        password = self.driver.find_element_by_id('pwd')
        password.click()
        password.send_keys(IniValue('setting', 'TestData.admin_boss_pwd'))
        self.driver.implicitly_wait(self.TestInfo.very_short_time)
        retry = 0
        while (retry < 10):
            try:
                self.driver.find_element_by_id("passCode").click()
                time.sleep(1)
                code = self.driver.find_element_by_id("code")
                code.click()
                passCode = self.driver.find_element_by_id("passCode")
                imgdata = b64decode(passCode.get_attribute("src").split(',')[1])
                with open(self.filename, 'wb') as decode_response_data:
                    decode_response_data.write(imgdata)
                
                new_code, self.res_log = ApiCodeDetect('\n\t\t', self.res_log, self.filename)
                code.send_keys(new_code)
                time.sleep(0.5)
                next_btn = self.driver.find_element_by_id('submit')
                next_btn.click()
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
        result_list = []
        result_list2 = []
        print_tab = '\n\t\t'
        self.CaseNote = WriteDebugLog(self.CaseNote, '\t'+datetime.today().strftime("%m???%d???%H???%M???%S???")+'>> Start to admin create banker'+'\n')
        
        timely_report = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'lang898')),'???????????? is not visible')
        search_imm_data = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'lang899')),'???????????? is not visible')
        account_organize_mem_add = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'lang373')),'???????????? is not visible')
        operation_info = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'lang589')),'???????????? is not visible')
        organize_list = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'lang521')),'???????????? is not visible')
        client_manage = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'lang228')),'???????????? is not visible')
        web_member_mange = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'lang556')),'????????????????????? is not visible')
        provider_manage = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'lang72')),'??????????????? is not visible')
        cash_system = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'lang469')),'???????????? is not visible')
        
        if(timely_report.text == '????????????'):
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get timely_report: '+timely_report.text)
            result_list.append('True')
        else:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get timely_report: '+timely_report.text+' != ????????????')
            result_list.append('False')
            
        if(search_imm_data.text == '????????????'):
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get search_imm_data: '+search_imm_data.text)
            result_list.append('True')
        else:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get search_imm_data: '+search_imm_data.text+' != ????????????')
            result_list.append('False')
            
        if(account_organize_mem_add.text == '????????????'):
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get account_organize_mem_add: '+account_organize_mem_add.text)
            result_list.append('True')
        else:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get account_organize_mem_add: '+account_organize_mem_add.text+' != ????????????')
            result_list.append('False')
        
        if(operation_info.text == '????????????'):
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get operation_info: '+operation_info.text)
            result_list.append('True')
        else:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get operation_info: '+operation_info.text+' != ????????????')
            result_list.append('False')
            
        if(organize_list.text == '????????????'):
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get organize_list: '+organize_list.text)
            result_list.append('True')
        else:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get organize_list: '+organize_list.text+' != ????????????')
            result_list.append('False')
            
        if(client_manage.text == '????????????'):
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get client_manage: '+client_manage.text)
            result_list.append('True')
        else:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get client_manage: '+client_manage.text+' != ????????????')
            result_list.append('False')
            
        if(web_member_mange.text == '?????????????????????'):
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get web_member_mange: '+web_member_mange.text)
            result_list.append('True')
        else:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get web_member_mange: '+web_member_mange.text+' != ?????????????????????')
            result_list.append('False')
            
        if(provider_manage.text == '???????????????'):
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get provider_manage: '+provider_manage.text)
            result_list.append('True')
        else:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get provider_manage: '+provider_manage.text+' != ???????????????')
            result_list.append('False')
            
        if(cash_system.text == '????????????'):
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get cash_system: '+cash_system.text)
            result_list.append('True')
        else:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get cash_system: '+cash_system.text+' != ????????????')
            result_list.append('False')
        
        timely_report.click()
        h2_title = WebDriverWait(self.driver,self.TestInfo.short_time).until(EC.visibility_of_element_located((By.TAG_NAME, 'h2')),'???????????? is not visible')
        
        if('False' in result_list or not result_list):
            self.TestResult = 'FAIL'
        else:
            if('False' in result_list2 or not result_list2):
                self.TestResult = 'FAIL'
            else:
                self.TestResult = 'PASS'
        # Part 2 check ????????????
        # [QA] Be sure to save result "PASS" or "FAIL" to self.TestResult
        # ----------------------------------------------------------------------------------------------

        self.CaseNote = WriteDebugLog(self.CaseNote, '\n\t'+'#Test Result: ' + self.TestResult)
        self.teardown()

        self.TestCaseEndTime = datetime.now()
        self.TestCaseDuration = ((self.TestCaseEndTime - self.TestCaseStartTime).total_seconds())*1000000
        if (self.TestCaseDuration == 0):
            self.TestCaseDuration = ' less than 1'
        self.TestInfo.setTestRunEndTime()
        
        self.CaseNote = WriteDebugLog(self.CaseNote, '\n\t'+datetime.today().strftime("%m???%d???%H???%M???%S???")+'<< End to admin create banker')
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