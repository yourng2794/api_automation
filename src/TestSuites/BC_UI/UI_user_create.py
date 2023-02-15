#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging, sys, os, inspect, shutil, locale
from datetime import datetime
import time
from base64 import b64decode
from BaseTestCase import BaseCase
from O2oUtility import WriteLog, WriteDebugLog, IniValue, ApiCodeDetect, DeleteFile
from O2oUtility import Compare_and_Click
from TestRun import TestRunning

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import openpyxl
from openpyxl.styles import Alignment
from openpyxl.drawing.image import Image

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
        self.CaseTitle= '[UI] User create'
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
        print_tab = '\n\t\t'
        self.CaseNote = WriteDebugLog(self.CaseNote, '\t'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+'>> Start to [UI] User create'+'\n')
        
        register_btn = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'a[href="register.html"]')),'register_btn (very_short_time)')
        register_btn.click()
        
        signAcc_input = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'signAcc')),'signAcc_input not visible')
        if(signAcc_input.get_attribute('placeholder') == '2 - 15 字元，字母开头，限字母和数字'):
            result_list.append('PASS')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Success: signAcc == 2 - 15 字元，字母开头，限字母和数字')
        else:
            result_list.append('FAIL')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Fail: signAcc != 2 - 15 字元，字母开头，限字母和数字')
        
        signName_input = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'signName')),'signName_input not visible')
        if(signName_input.get_attribute('placeholder') == '必须与提款的银行户口相同，否则无法提款'):
            result_list.append('PASS')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Success: signName == 必须与提款的银行户口相同，否则无法提款')
        else:
            result_list.append('FAIL')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Fail: signName != 必须与提款的银行户口相同，否则无法提款')
        
        signPwd_input = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'signPwd')),'signPwd_input not visible')
        if(signPwd_input.get_attribute('placeholder') == '6-30 字元，须包含字母及数字'):
            result_list.append('PASS')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Success: signPwd == 6-30 字元，须包含字母及数字')
        else:
            result_list.append('FAIL')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Fail: signPwd != 6-30 字元，须包含字母及数字')
        
        signCheckPwd_input = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'signCheckPwd')),'signCheckPwd_input not visible')
        if(signCheckPwd_input.get_attribute('placeholder') == '请再次确认密码'):
            result_list.append('PASS')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Success: signCheckPwd == 请再次确认密码')
        else:
            result_list.append('FAIL')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Fail: signCheckPwd != 请再次确认密码')
        
        signPwdWithdraw_input = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'signPwdWithdraw')),'signPwdWithdraw_input not visible')
        if(signPwdWithdraw_input.get_attribute('placeholder') == '请输入取款密码'):
            result_list.append('PASS')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Success: signPwdWithdraw == 请输入取款密码')
        else:
            result_list.append('FAIL')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Fail: signPwdWithdraw != 请输入取款密码')
        
        signPhone_input = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'signPhone')),'signPhone_input not visible')
        if(signPhone_input.get_attribute('placeholder') == '请输入您的手机号码'):
            result_list.append('PASS')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Success: signPhone == 请输入您的手机号码')
        else:
            result_list.append('FAIL')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Fail: signPhone != 请输入您的手机号码')
        
        signEmail_input = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'signEmail')),'signEmail_input not visible')
        if(signEmail_input.get_attribute('placeholder') == '请输入您的电子邮箱'):
            result_list.append('PASS')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Success: signEmail == 请输入您的电子邮箱')
        else:
            result_list.append('FAIL')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Fail: signEmail != 请输入您的电子邮箱')
        
        birth_input = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'birth')),'birth_input not visible')
        if(birth_input.get_attribute('placeholder') == '请填写您的生日'):
            result_list.append('PASS')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Success: birth == 请填写您的生日')
        else:
            result_list.append('FAIL')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Fail: birth != 请填写您的生日')
        
        signQQ_input = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'signQQ')),'signQQ_input not visible')
        if(signQQ_input.get_attribute('placeholder') == '请输入您的QQ号码'):
            result_list.append('PASS')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Success: signQQ == 请输入您的QQ号码')
        else:
            result_list.append('FAIL')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Fail: signQQ != 请输入您的QQ号码')
        
        signWechat_input = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'signWechat')),'signWechat_input not visible')
        if(signWechat_input.get_attribute('placeholder') == '请输入您的微信号'):
            result_list.append('PASS')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Success: signWechat == 请输入您的微信号')
        else:
            result_list.append('FAIL')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Fail: signWechat != 请输入您的微信号')
        
        signAcc_input.send_keys('a')
        signPwd_input.send_keys('1234')
        signCheckPwd_input.send_keys('abcd')
        signPwdWithdraw_input.send_keys('1a2')
        signPhone_input.send_keys('aaa')
        signEmail_input.send_keys('test@test')
        birth_input.click()
        time.sleep(0.5)
        date_picker = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[class="datepicker--cells datepicker--cells-days"] div[class="datepicker--cell datepicker--cell-day -current-"]')),'date_picker not visible')
        date_picker.click()
        time.sleep(1)
        
        if(birth_input.get_attribute('value')):
            result_list.append('PASS')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Success: birth_input == '+birth_input.get_attribute('value'))
        else:
            result_list.append('FAIL')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Fail: birth_input != '+birth_input.get_attribute('value'))
        
        signAcc_error_input = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'signAcc-error')),'signAcc_error_input not visible')
        if(signAcc_error_input.text.replace('\n','') == '2 - 15 字元，字母开头，限字母和数字'):
            result_list.append('PASS')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Success: signAcc_error == 2 - 15 字元，字母开头，限字母和数字')
        else:
            result_list.append('FAIL')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Fail: signAcc_error != 2 - 15 字元，字母开头，限字母和数字')
        
        signPwd_error_input = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'signPwd-error')),'signPwd_error_input not visible')
        if(signPwd_error_input.text.replace('\n','') == '6-30 字元，须包含字母及数字'):
            result_list.append('PASS')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Success: signPwd_error == 6-30 字元，须包含字母及数字')
        else:
            result_list.append('FAIL')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Fail: signPwd_error != 6-30 字元，须包含字母及数字')
        
        signCheckPwd_error_input = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'signCheckPwd-error')),'signCheckPwd_error_input not visible')
        if(signCheckPwd_error_input.text.replace('\n','') == '确认密码不符'):
            result_list.append('PASS')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Success: signCheckPwd_error == 确认密码不符')
        else:
            result_list.append('FAIL')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Fail: signCheckPwd_error != 确认密码不符')
        
        signPwdWithdraw_error_input = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'signPwdWithdraw-error')),'signPwdWithdraw_error_input not visible')
        if(signPwdWithdraw_error_input.text.replace('\n','') == '不足4字元'):
            result_list.append('PASS')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Success: signPwdWithdraw_error == 不足4字元')
        else:
            result_list.append('FAIL')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Fail: signPwdWithdraw_error != 不足4字元')
        
        signPhone_error_input = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'signPhone-error')),'signPhone_error_input not visible')
        if(signPhone_error_input.text.replace('\n','') == '最多30字元，不可字母及特殊符号'):
            result_list.append('PASS')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Success: signPhone_error == 最多30字元，不可字母及特殊符号')
        else:
            result_list.append('FAIL')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Fail: signPhone_error != 最多30字元，不可字母及特殊符号')
        
        signEmail_error_input = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'signEmail-error')),'signEmail_error_input not visible')
        if(signEmail_error_input.text.replace('\n','') == '请输入有效的电子邮件'):
            result_list.append('PASS')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Success: signEmail_error == 请输入有效的电子邮件')
        else:
            result_list.append('FAIL')
            self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Fail: signEmail_error != 请输入有效的电子邮件')
        
        bc_acc = IniValue('setting', 'PlayGame.bc_acc')
        bc_pwd = IniValue('setting', 'PlayGame.bc_pwd')
        pwd_withdraw = IniValue('setting', 'TestData.pwd_withdraw')
        signAcc_input.clear()
        signPwd_input.clear()
        signCheckPwd_input.clear()
        signPwdWithdraw_input.clear()
        signPhone_input.clear()
        signEmail_input.clear()
        time.sleep(1)
        
        signName_input.send_keys('金城舞')
        signAcc_input.send_keys(bc_acc)
        signPwd_input.send_keys(bc_pwd)
        signCheckPwd_input.send_keys(bc_pwd)
        signPwdWithdraw_input.send_keys(pwd_withdraw)
        signPhone_input.send_keys('121354863432')
        signEmail_input.send_keys('test@test.test')
        signQQ_input.send_keys('1019479653')
        signWechat_input.send_keys('yourng2222')
        
        signagreeBtn_input = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'signagreeBtn')),'signagreeBtn_input not visible')
        signagreeBtn_input.click()
        
        self.driver.implicitly_wait(self.TestInfo.very_short_time)
        retry = 0
        while (retry < 10):
            try:
                time.sleep(1)
                signPassBtn = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'signPassBtn')),'signPassBtn not visible')
                signPassBtn.click()
                signPassImg = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'signPassImg')),'signPassImg not visible')
                signPassImg.clear()
                signPassCode = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'signPassCode')),'signPassCode not visible')
                imgdata = b64decode(signPassCode.get_attribute("src").split(',')[1])
                with open(self.filename, 'wb') as decode_response_data:
                    decode_response_data.write(imgdata)
                
                new_code, self.res_log = ApiCodeDetect('\n\t\t', self.res_log, self.filename)
                signPassImg.send_keys(new_code)
                submitReg = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'submitReg')),'submitReg not visible')
                submitReg.click()
                
                id_informLg = WebDriverWait(self.driver,self.TestInfo.very_short_time).until(EC.visibility_of_element_located((By.ID, 'informLg')),'BC_timeout (very_short_time)')
                if('登入成功' in id_informLg.text):
                    result_list.append('PASS')
                    id_informLg.find_element_by_class_name('lg-close').click()
                    self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Success: 登入成功')
                    break
                elif('验证码错误' in id_informLg.text):
                    id_informLg.find_element_by_class_name('lg-close').click()
                    self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Fail: 验证码错误')
                elif('注册帐号重复' in id_informLg.text):
                    result_list.append('FAIL')
                    id_informLg.find_element_by_class_name('lg-close').click()
                    self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Fail: 注册帐号重复')
                    break
                else:
                    result_list.append('FAIL')
                    id_informLg.find_element_by_class_name('lg-close').click()
                    self.CaseNote = WriteDebugLog(self.CaseNote, print_tab+'Fail undefine: '+id_informLg.text)
                    break
            except Exception as e:
                self.CaseNote = WriteDebugLog(self.CaseNote, 'Exception: on "Browser time out"... %s' % str(e))
            finally:
                retry += 1
        if(retry >= 10):
            result_list.append('FAIL')
            self.CaseNote = WriteDebugLog(self.CaseNote, 'Retry browser fail.')
        
            
        WriteLog(result_list)
        if('FAIL' in result_list or not result_list):
            self.TestResult = 'FAIL'
        else:
            self.TestResult = 'PASS'
        self.res_log = WriteDebugLog(self.res_log, print_tab+'# Test Result: '+self.TestResult)
        # [QA] Be sure to save result "PASS" or "FAIL" to self.TestResult
        # ----------------------------------------------------------------------------------------------
        
        self.teardown()

        self.TestCaseEndTime = datetime.now()
        self.TestCaseDuration = ((self.TestCaseEndTime - self.TestCaseStartTime).total_seconds())*1000000
        if (self.TestCaseDuration == 0):
            self.TestCaseDuration = ' less than 1'
        self.TestInfo.setTestRunEndTime()
        
        self.CaseNote = WriteDebugLog(self.CaseNote, '\n\t'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+'<< End to [UI] User create')
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