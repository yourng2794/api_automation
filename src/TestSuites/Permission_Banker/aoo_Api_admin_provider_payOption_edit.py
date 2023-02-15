#!/usr/bin/python
#coding=utf-8
import os, sys
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
from O2oUtility import AdminProviderPayOptionEdit

locale.setlocale(locale.LC_CTYPE, 'chinese')
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
tooldir = os.path.dirname(os.path.dirname(currentdir))
if tooldir not in sys.path:
    sys.path.insert(0, tooldir)

class TestCase(BaseCase):
    
    def __init__(self, MyTest):
        # ---------------- [QA] Modify these variables for your test case! ----------------------------------       
        self.Feature= currentdir.split('\\')[-1]
        self.CaseTitle= '[Feature] API POST provider payOption edit'
        self.CaseNote= ''
        self.TestCaseID= '155'
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
        self.res_log = WriteDebugLog(self.res_log, '\n\tStart >>'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST provider payOption edit'+'\n')
        
        webId = IniValue('setting', 'API.webId')
        currency = IniValue('setting', 'API.currency')
        payOptionId = IniValue('setting', 'API.payOptionId')
        payOptionName = IniValue('setting', 'API.payOptionName')
        depositIdTemp = IniValue('setting', 'API.depositId')
        depositId = depositIdTemp.split(', ')
        withdrawIdTemp = IniValue('setting', 'API.withdrawId')
        withdrawId = withdrawIdTemp.split(', ')
        api_json = tooldir+'\\JsonFiles\\Api_Json\\admin_payOption_edit.json'
        json_dict = {}
        json_dict['webId'] = webId
        json_dict['payOptionId'] = payOptionId
        json_dict['payName'] = payOptionName
        json_dict['currency'] = []
        json_dict['currency'] = [currency]
        json_dict['duplicateWithdrawHours'] = '2'
        json_dict['freeProcessFeeTimes'] = '1'
        json_dict['withdrawProcessRate'] = '10'
        json_dict['withdrawProcessMax'] = '100'
        json_dict['withdrawMax'] = '10000'
        json_dict['withdrawMin'] = '100'
        json_dict['review'] = '1'
        json_dict['reviewAmount'] = '5000'
        json_dict['reviewHour'] = '1'
        json_dict['onlinePromo'] = '1'
        json_dict['onlineCount'] = ''
        json_dict['onlineAmount'] = '100'
        json_dict['onlineRatio'] = '50'
        json_dict['onlineMaxdep'] = '5000'
        json_dict['onlineMindep'] = '10'
        json_dict['onlineLimit'] = '1000'
        json_dict['preferentialAudit'] = '1'
        json_dict['preferentialAuditTimes'] = '10'
        json_dict['preferentialBalanceAudit'] = '1'
        json_dict['normalAudit'] = '0'
        json_dict['normalAuditPercent'] = '100'
        json_dict['normalAuditRelaxationAmount'] = '10'
        json_dict['normalAuditProcessRate'] = '50'
        json_dict['companyPromo'] = '1'
        json_dict['companyCount'] = ''
        json_dict['companyAmount'] = '100'
        json_dict['companyRatio'] = '50'
        json_dict['companyMaxdep'] = '5000'
        json_dict['companyMindep'] = '10'
        json_dict['companyLimit'] = '100'
        json_dict['transferPreferentialAmount'] = '100'
        json_dict['transferPreferentialRate'] = '1'
        json_dict['transferPreferentialMaximum'] = '500'
        json_dict['transferPreferentialMaximumADay'] = '500'
        json_dict['compPreferentialAudit'] = '1'
        json_dict['compPreferentialAuditTimes'] = '10'
        json_dict['compPreferentialBalanceAudit'] = '1'
        json_dict['compNormalAudit'] = '0'
        json_dict['compNormalAuditPercent'] = '100'
        json_dict['compNormalAuditRelaxationAmount'] = '10'
        json_dict['compNormalAuditProcessRate'] = '50'
        json_dict['withdraw'] = {}
        json_dict['deposit'] = {}
        json_dict['deposit'][currency] = []
        json_dict['withdraw'][currency] = []
        json_dict['withdraw'][currency] = depositId
        json_dict['deposit'][currency] = withdrawId
        with open(api_json, 'w') as outfile:
            json.dump(json_dict, outfile, indent=4, ensure_ascii=False)
        
        self.res_log, result = AdminProviderPayOptionEdit(self.res_log, 'Banker')
        
        if(result == True):
            self.TestResult = 'PASS'
        else:
            self.TestResult = 'FAIL'
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
        self.res_log = WriteDebugLog(self.res_log, '\n\n\tEnd << '+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST provider payOption edit')
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