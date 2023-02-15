#!/usr/bin/python
#coding=utf-8
import os
import locale
import logging
import inspect
import shutil
from datetime import datetime

from TestRun import TestRunning
from BaseTestCase import BaseCase
from O2oUtility import WriteLog
from O2oUtility import WriteDebugLog
from O2oUtility import IniValue
from O2oUtility import ReplaceIniValue
from O2oUtility import AdminWebPromoCommissionTypeCreate

locale.setlocale(locale.LC_CTYPE, 'chinese')
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
tooldir = os.path.dirname(os.path.dirname(currentdir))
class TestCase(BaseCase):
    
    def __init__(self, MyTest):
        # ---------------- [QA] Modify these variables for your test case! ----------------------------------       
        self.Feature= currentdir.split('\\')[-1]
        self.CaseTitle= '[Feature] API POST webPlayer promo commission type create'
        self.CaseNote= ''
        self.TestCaseID= '617'
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
#         ReplaceIniValue('admin_webPlayer_promo_commission_type_create', 'API.bankerId', '')
#         ReplaceIniValue('admin_webPlayer_promo_commission_type_create', 'API.webCommissionName', '')
#         ReplaceIniValue('admin_webPlayer_promo_commission_type_create', 'API.commissionTimes', '')
#         ReplaceIniValue('admin_webPlayer_promo_commission_type_create', 'API.receiveTimesDaily', '')
#         ReplaceIniValue('admin_webPlayer_promo_commission_type_create', 'API.totalBet', '')
#         ReplaceIniValue('admin_webPlayer_promo_commission_type_create', 'API.promotionLimit', '')
#         ReplaceIniValue('admin_webPlayer_promo_commission_type_create', 'API.maxReceiveAmount', '')
#         ReplaceIniValue('admin_webPlayer_promo_commission_type_create', 'API.singleMinReceiveAmount', '')
        WriteLog('\t'+'<< End Tear Down')
        
        
    def run(self, copy_result):
        self.TestCaseStartTime = datetime.now()
        self.setPreCondition()
        self.res_log = WriteDebugLog(self.res_log, '\n\tStart >>'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST webPlayer promo commission type create'+'\n')
        
        partnerid = IniValue('setting', 'API.partnerid')
        commissionTypeName = IniValue('setting', 'API.commissionTypeName')
        ReplaceIniValue('admin_webPlayer_promo_commission_type_create', 'API.bankerId', partnerid)
        ReplaceIniValue('admin_webPlayer_promo_commission_type_create', 'API.webCommissionName', commissionTypeName)
        ReplaceIniValue('admin_webPlayer_promo_commission_type_create', 'API.commissionTimes', '200') # 打碼倍數
        ReplaceIniValue('admin_webPlayer_promo_commission_type_create', 'API.receiveTimesDaily', '5') # 每日領取次數
        ReplaceIniValue('admin_webPlayer_promo_commission_type_create', 'API.totalBet', '400') # 有效總投注
        ReplaceIniValue('admin_webPlayer_promo_commission_type_create', 'API.promotionLimit', '500') # 優惠上限
        ReplaceIniValue('admin_webPlayer_promo_commission_type_create', 'API.maxReceiveAmount', '600') # 單日最高領取金額
        ReplaceIniValue('admin_webPlayer_promo_commission_type_create', 'API.singleMinReceiveAmount', '100') # 單次最低領取金額
        
        self.res_log, result = AdminWebPromoCommissionTypeCreate(self.res_log, 'Agent')
        
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
        self.res_log = WriteDebugLog(self.res_log, '\n\n\tEnd << '+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST webPlayer promo commission type create')
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