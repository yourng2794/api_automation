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
from selenium.webdriver.support.ui import Select
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
        self.CaseTitle= '[UI] admin create member'
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
        self.CaseNote = WriteDebugLog(self.CaseNote, '\t'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+'>> Start to admin create member'+'\n')
        
#         lis = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div[class="nav-bar"] ul li')),'Title is not visible')
#         for li in lis:
#             li_text = li.find_element_by_css_selector('a[class="nav-btn] span b[class^="lang"]').text
#             print(li_text)
        
        timely_report = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'lang898')),'即时报表 is not visible')
        search_imm_data = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'lang899')),'快速查询 is not visible')
        account_organize_mem_add = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'lang373')),'新增帐号 is not visible')
        operation_info = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'lang589')),'营运资讯 is not visible')
        organize_list = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'lang521')),'组织管理 is not visible')
        client_manage = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'lang228')),'客户管理 is not visible')
        web_member_manage = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'lang556')),'网站及会员管理 is not visible')
        provider_manage = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'lang72')),'供应商管理 is not visible')
        cash_system = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'lang469')),'现金系统 is not visible')
        
        if(timely_report.text == '即时报表'):
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get timely_report: '+timely_report.text)
            result_list.append('True')
        else:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get timely_report: '+timely_report.text+' != 即时报表')
            result_list.append('False')
            
        if(search_imm_data.text == '快速查询'):
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get search_imm_data: '+search_imm_data.text)
            result_list.append('True')
        else:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get search_imm_data: '+search_imm_data.text+' != 快速查询')
            result_list.append('False')
            
        if(account_organize_mem_add.text == '新增帐号'):
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get account_organize_mem_add: '+account_organize_mem_add.text)
            result_list.append('True')
        else:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get account_organize_mem_add: '+account_organize_mem_add.text+' != 新增帐号')
            result_list.append('False')
        
        if(operation_info.text == '营运资讯'):
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get operation_info: '+operation_info.text)
            result_list.append('True')
        else:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get operation_info: '+operation_info.text+' != 营运资讯')
            result_list.append('False')
            
        if(organize_list.text == '组织管理'):
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get organize_list: '+organize_list.text)
            result_list.append('True')
        else:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get organize_list: '+organize_list.text+' != 组织管理')
            result_list.append('False')
            
        if(client_manage.text == '客户管理'):
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get client_manage: '+client_manage.text)
            result_list.append('True')
        else:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get client_manage: '+client_manage.text+' != 客户管理')
            result_list.append('False')
            
        if(web_member_manage.text == '网站及会员管理'):
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get web_member_mange: '+web_member_manage.text)
            result_list.append('True')
        else:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get web_member_mange: '+web_member_manage.text+' != 网站及会员管理')
            result_list.append('False')
            
        if(provider_manage.text == '供应商管理'):
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get provider_manage: '+provider_manage.text)
            result_list.append('True')
        else:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get provider_manage: '+provider_manage.text+' != 供应商管理')
            result_list.append('False')
            
        if(cash_system.text == '现金系统'):
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get cash_system: '+cash_system.text)
            result_list.append('True')
        else:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get cash_system: '+cash_system.text+' != 现金系统')
            result_list.append('False')
        
        # Part 2
        web_member_manage.click()
        web_mem_list = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'a[href="web_mem_list.html"]')),'会员列表 is not visible')
        web_mem_list.click()
        bread_list = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'bread')),'bread is not visible')
        h3_title = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.TAG_NAME, 'h3')),'h3_title is not visible')
        if(h3_title.text == '会员列表'):
            result_list2.append('True')
            print(print_tab+bread_list.text.replace(' ','> '))
        else:
            result_list.append('False')
        
        web_mem_add = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'a[href="web_mem_add.html"]')),'新增会员 is not visible')
        web_mem_add.click()
        bread_list2 = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'bread')),'bread is not visible')
        h3_title = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.TAG_NAME, 'h3')),'h3_title is not visible')
        if(h3_title.text == '新增会员帐号'):
            print(print_tab+bread_list2.text.replace(' ','> '))
            result_list2.append('True')
        else:
            result_list.append('False')
        
        userName_edittext = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[id="userName"]')),'userName_edittext is not visible')
        userAcc_edittext = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[id="userAcc"]')),'userAcc_edittext is not visible')
        userPwd_edittext = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[id="userPwd"]')),'userPwd_edittext is not visible')
        checkPwd_edittext = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[id="checkPwd"]')),'checkPwd_edittext is not visible')
        web_select = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'select[id="web"]')),'web_select is not visible')
        memLevel_select = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'select[id="memLevel"]')),'memLevel_select is not visible')
        
        agentacc = IniValue('setting', 'API.agentacc')
        userName_edittext.send_keys(agentacc)
        userAcc_edittext.send_keys(agentacc)
        userPwd_edittext.send_keys(agentacc)
        checkPwd_edittext.send_keys(agentacc)
        
        web_dropdown = Select(web_select)
        web_dropdown.select_by_value('0b2ab3d05417542282220cd5af960b86')
        
        
        memLevel_dropdown = Select(memLevel_select)
        memLevel_dropdown.select_by_value('1914c922185bd2846e16b62fa11d68a5')
        
#         submit_btn = WebDriverWait(self.driver,self.TestInfo.short_time).until(EC.visibility_of_element_located((By.CLASS_NAME, 'btn-submit')),'submit_btn is not visible')
        self.driver.find_element_by_css_selector('input[id="submit"]')
        time.sleep(5)
        
        if('False' in result_list or not result_list):
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
        
        self.CaseNote = WriteDebugLog(self.CaseNote, '\n\t'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+'<< End to admin create member')
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