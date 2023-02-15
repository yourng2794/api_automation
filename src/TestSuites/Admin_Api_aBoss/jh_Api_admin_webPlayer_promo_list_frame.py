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
from O2oUtility import AdminWebPromoListFrame

locale.setlocale(locale.LC_CTYPE, 'chinese')
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
class TestCase(BaseCase):
    
    def __init__(self, MyTest):
        # ---------------- [QA] Modify these variables for your test case! ----------------------------------       
        self.Feature= currentdir.split('\\')[-1]
        self.CaseTitle= '[Feature] API POST webPlayer promo list frame'
        self.CaseNote= ''
        self.TestCaseID= '106'
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
        ReplaceIniValue('admin_webPlayer_promo_list_frame', 'API.bankerId', '')
        ReplaceIniValue('admin_webPlayer_promo_list_frame', 'API.webId', '')
        ReplaceIniValue('admin_webPlayer_promo_list_frame', 'API.type', '')
        ReplaceIniValue('admin_webPlayer_promo_list_frame', 'API.page', '')
        ReplaceIniValue('admin_webPlayer_promo_list_frame', 'API.promoType', '')
        WriteLog('\t'+'<< End Tear Down')
        
        
    def run(self, copy_result):
        self.TestCaseStartTime = datetime.now()
        self.setPreCondition()
        self.res_log = WriteDebugLog(self.res_log, '\n\tStart >>'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST webPlayer promo list frame'+'\n')
        list_result = []
        
        number = IniValue('setting', 'API.number')
        bankerId = IniValue('setting', 'API.bankerId')
        promoName = IniValue('setting', 'API.promoName')
        webId = IniValue('setting', 'API.webid')
        webName = IniValue('setting', 'API.webname')+number
        ReplaceIniValue('admin_webPlayer_promo_list_frame', 'API.bankerId', bankerId)
        ReplaceIniValue('admin_webPlayer_promo_list_frame', 'API.webId', webId)
        ReplaceIniValue('admin_webPlayer_promo_list_frame', 'API.type', 'all')
        ReplaceIniValue('admin_webPlayer_promo_list_frame', 'API.promoType', '1')
        ReplaceIniValue('admin_webPlayer_promo_list_frame', 'API.page', '')
        
        self.res_log, result, promoId= AdminWebPromoListFrame(self.res_log, 'Boss', webName, promoName, 'Web')
        
        promoName2 = IniValue('setting', 'API.promoName')+'生日'
        ReplaceIniValue('admin_webPlayer_promo_list_frame', 'API.promoType', '2')
        self.res_log, result2, promoId2= AdminWebPromoListFrame(self.res_log, 'Boss', webName, promoName2, 'Web')
        
        promoName3 = IniValue('setting', 'API.promoName')+'救援'
        ReplaceIniValue('admin_webPlayer_promo_list_frame', 'API.promoType', '3')
        self.res_log, result3, promoId3= AdminWebPromoListFrame(self.res_log, 'Boss', webName, promoName3, 'Web')
        
        promoName4 = IniValue('setting', 'API.promoName')+'好友'
        ReplaceIniValue('admin_webPlayer_promo_list_frame', 'API.promoType', '4')
        self.res_log, result4, promoId4= AdminWebPromoListFrame(self.res_log, 'Boss', webName, promoName4, 'Web')
        
        promoName5 = IniValue('setting', 'API.promoName')+'簽到'
        ReplaceIniValue('admin_webPlayer_promo_list_frame', 'API.promoType', '5')
        self.res_log, result5, promoId5= AdminWebPromoListFrame(self.res_log, 'Boss', webName, promoName5, 'Web')
        
        if(result == True):
            ReplaceIniValue('setting', 'API.promoId', promoId)
            list_result.append('PASS')
        else:
            list_result.append('FAIL')
        
        if(result2 == True):
            ReplaceIniValue('setting', 'API.promoId2', promoId2)
            list_result.append('PASS')
        else:
            list_result.append('FAIL')
        
        if(result3 == True):
            ReplaceIniValue('setting', 'API.promoId3', promoId3)
            list_result.append('PASS')
        else:
            list_result.append('FAIL')
        
        if(result4 == True):
            ReplaceIniValue('setting', 'API.promoId4', promoId4)
            list_result.append('PASS')
        else:
            list_result.append('FAIL')
        
        if(result5 == True):
            ReplaceIniValue('setting', 'API.promoId5', promoId5)
            list_result.append('PASS')
        else:
            list_result.append('FAIL')
        
        if('FAIL' in list_result):
            self.TestResult = 'FAIL'
        else:
            self.TestResult = 'PASS'
        
        WriteLog(str(list_result))
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
        self.res_log = WriteDebugLog(self.res_log, '\n\n\tEnd << '+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST webPlayer promo list frame')
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