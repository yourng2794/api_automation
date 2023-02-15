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
from O2oUtility import AdminWebPromoTypeEdit
from O2oUtility import AdminWebPromoTypeEditFriend

locale.setlocale(locale.LC_CTYPE, 'chinese')
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

class TestCase(BaseCase):
    
    def __init__(self, MyTest):
        # ---------------- [QA] Modify these variables for your test case! ----------------------------------       
        self.Feature= currentdir.split('\\')[-1]
        self.CaseTitle= '[Feature] API POST webPlayer promo type edit'
        self.CaseNote= ''
        self.TestCaseID= '69'
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
#         ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.promoName', '')
#         ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.promoTypeId', '')
#         ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.condition', '')
#         ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.reward', '')
        WriteLog('\t'+'<< End Tear Down')
        
        
    def run(self, copy_result):
        self.TestCaseStartTime = datetime.now()
        self.setPreCondition()
        self.res_log = WriteDebugLog(self.res_log, '\n\tStart >>'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST webPlayer promo type edit'+'\n')
        list_result = []
        
        promoTypeName = IniValue('setting', 'API.promoTypeName')+'T'
        promoTypeId = IniValue('setting', 'API.promoTypeId')
        condition = IniValue('setting', 'API.condition')
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.promoName', promoTypeName)
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.promoTypeId', promoTypeId)
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.condition', condition)
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.rewards', '2.50')
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.promoType', '1')
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.promoAudit', '10.00')
        self.res_log, result= AdminWebPromoTypeEdit(self.res_log, 'Boss')
        
        promoTypeName2 = IniValue('setting', 'API.promoTypeName2')+'T'
        promoTypeId2 = IniValue('setting', 'API.promoTypeId2')
        condition2 = IniValue('setting', 'API.condition2')
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.promoName', promoTypeName2)
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.promoTypeId', promoTypeId2)
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.condition', condition2)
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.rewards', '2.50')
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.promoType', '2')
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.promoAudit', '10.00')
        self.res_log, result2= AdminWebPromoTypeEdit(self.res_log, 'Boss')
        
        promoTypeName3 = IniValue('setting', 'API.promoTypeName3')+'T'
        promoTypeId3 = IniValue('setting', 'API.promoTypeId3')
        condition3 = IniValue('setting', 'API.condition3')
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.promoName', promoTypeName3)
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.promoTypeId', promoTypeId3)
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.condition', condition3)
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.rewards', '2.50')
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.promoType', '3')
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.promoAudit', '10.00')
        self.res_log, result3= AdminWebPromoTypeEdit(self.res_log, 'Boss')
        
        promoTypeName4 = IniValue('setting', 'API.promoTypeName4')+'T'
        promoTypeId4 = IniValue('setting', 'API.promoTypeId4')
        condition4 = IniValue('setting', 'API.condition4')
        ReplaceIniValue('admin_webPlayer_promo_type_edit_friend', 'API.promoName', promoTypeName4)
        ReplaceIniValue('admin_webPlayer_promo_type_edit_friend', 'API.promoTypeId', promoTypeId4)
        ReplaceIniValue('admin_webPlayer_promo_type_edit_friend', 'API.condition', condition4)
        ReplaceIniValue('admin_webPlayer_promo_type_edit_friend', 'API.promoType', '4')
        ReplaceIniValue('admin_webPlayer_promo_type_edit_friend', 'API.promoAudit', '10.00')
        self.res_log, result4= AdminWebPromoTypeEditFriend(self.res_log, 'Boss')
        
        promoTypeName5 = IniValue('setting', 'API.promoTypeName5')+'T'
        promoTypeId5 = IniValue('setting', 'API.promoTypeId5')
        condition5 = IniValue('setting', 'API.condition5')
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.promoName', promoTypeName5)
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.promoTypeId', promoTypeId5)
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.condition', condition5)
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.rewards', '2.50')
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.promoType', '5')
        ReplaceIniValue('admin_webPlayer_promo_type_edit', 'API.promoAudit', '10.00')
        self.res_log, result5= AdminWebPromoTypeEdit(self.res_log, 'Boss')
        
        if(result == True):
            list_result.append('PASS')
        else:
            list_result.append('FAIL')
        
        if(result2 == True):
            list_result.append('PASS')
        else:
            list_result.append('FAIL')
        
        if(result3 == True):
            list_result.append('PASS')
        else:
            list_result.append('FAIL')
        
        if(result4 == True):
            list_result.append('PASS')
        else:
            list_result.append('FAIL')
        
        if(result5 == True):
            list_result.append('PASS')
        else:
            list_result.append('FAIL')
        
        if('FAIL' in list_result):
            self.TestResult = 'FAIL'
        else:
            self.TestResult = 'PASS'
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
        self.res_log = WriteDebugLog(self.res_log, '\n\n\tEnd << '+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST webPlayer promo type edit')
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