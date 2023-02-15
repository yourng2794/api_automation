#!/usr/bin/python
#coding=utf-8
import os
import sys
import locale
import logging
import inspect
import shutil
import json
from datetime import datetime

from TestRun import TestRunning
from BaseTestCase import BaseCase
from O2oUtility import WriteLog
from O2oUtility import WriteDebugLog
from O2oUtility import IniValue
from O2oUtility import ReplaceIniValue
from O2oUtility import AdminProviderPaymentSetting

locale.setlocale(locale.LC_CTYPE, 'chinese')
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
tooldir = os.path.dirname(os.path.dirname(currentdir))
if tooldir not in sys.path:
    sys.path.insert(0, tooldir)

class TestCase(BaseCase):
    
    def __init__(self, MyTest):
        # ---------------- [QA] Modify these variables for your test case! ----------------------------------       
        self.Feature= currentdir.split('\\')[-1]
        self.CaseTitle= '[Feature] Notify Backend Setting Payment'
        self.CaseNote= ''
        self.TestCaseID= '133'
        # (CaseNote: can be blank ''. Use it to leave some notes or description of this case which will be displayed in test report)
        # ----------------------------------------------------------------------------------------------
        self.TestResult = 'FAIL'
        self.CurrentFile = os.path.basename(__file__)
        self.res_log = ''
        BaseCase.TestInfo = MyTest
        
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
        WriteLog('\t'+'<< End Tear Down')
        
        
    def run(self, copy_result):
        self.TestCaseStartTime = datetime.now()
        self.setPreCondition()
        self.res_log = WriteDebugLog(self.res_log, '\n\tStart >>'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] Notify Backend Setting Payment'+'\n')
        
        paymentId = IniValue('setting', 'API.paymentId')
        ReplaceIniValue('admin_provider_payment_edit_currency_get', 'API.paymentId', paymentId)
#         self.res_log, result, edit_currency = AdminProviderPaymentEditCurrencyGet(self.res_log, 'WebMaster')
        
#         if(result == True):
        api_json = tooldir+'\\JsonFiles\\Api_Json\\admin_payment_setting.json'
        json_dict = {}
        webId = IniValue('setting', 'API.webId')
        payment_name = IniValue('setting', 'API.paymentname')
        paytype_id = IniValue('setting', 'API.paytypeid')
        deposit_acc = '888888'
        deposit_payratio = 5
        deposit_secretkey = 'f455ff77fa023376d810a97b68e54e32'
        max_deposit = 88888
        max_withdraw = 6666
        min_deposit = 10
        pay_option = 3
        withdraw_acc = '666666'
        withdraw_payratio = 5
        withdraw_secretkey = 'f455ff77fa023376d810a97b68e54e33'
        
        json_dict['webId'] = webId
        json_dict['paymentName'] = payment_name
        json_dict['payTypeId'] = paytype_id
        json_dict['url'] = 'https://tw.yahoo.com/'
        json_dict['depositAcc'] = deposit_acc
        json_dict['depositRatio'] = deposit_payratio
        json_dict['withdrawKey'] = deposit_secretkey
        json_dict['maxDeposit'] = max_deposit
        json_dict['maxWithdraw'] = max_withdraw
        json_dict['minDeposit'] = min_deposit
        json_dict['payOption'] = pay_option
        json_dict['withdrawAcc'] = withdraw_acc
        json_dict['withdrawRatio'] = withdraw_payratio
        json_dict['depositKey'] = withdraw_secretkey
        json_dict['currency'] = ["CNY", "EUR", "HKD", "MOP", "USD", "V_BTC"]
        self.res_log = WriteDebugLog(self.res_log, json.dumps(json_dict, indent=4, ensure_ascii=False))
        
        with open(api_json, 'w') as outfile:
            json.dump(json_dict, outfile, indent=4, ensure_ascii=False)
        
        self.res_log, result = AdminProviderPaymentSetting(self.res_log, 'WebMaster')
        
        if(result == True):
            self.TestResult = 'PASS'
        else:
            self.TestResult = 'FAIL'
#         else:
#             self.TestResult = 'FAIL'
        self.res_log = WriteDebugLog(self.res_log, '# Test Result: '+self.TestResult)
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
        self.res_log = WriteDebugLog(self.res_log, '\n\n\tEnd << '+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] Notify Backend Setting Payment') 
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