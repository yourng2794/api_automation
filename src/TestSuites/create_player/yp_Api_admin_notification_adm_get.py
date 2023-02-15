#!/usr/bin/python
#coding=utf-8
import os
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
from O2oUtility import ApiResponse
from O2oUtility import IniValue
from O2oUtility import ReplaceIniValue

locale.setlocale(locale.LC_CTYPE, 'chinese')
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

class TestCase(BaseCase):
    
    def __init__(self, MyTest):
        # ---------------- [QA] Modify these variables for your test case! ----------------------------------       
        self.Feature= currentdir.split('\\')[-1]
        self.CaseTitle= '[Feature] API POST notification adm get'
        self.CaseNote= ''
        self.TestCaseID= '173'
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
        ReplaceIniValue('admin_notification_adm_get', 'API.id', '')
        WriteLog('\t'+'<< End Tear Down')
        
        
    def run(self, copy_result):
        self.TestCaseStartTime = datetime.now()
        self.setPreCondition()
        result_list = []
        self.res_log = WriteDebugLog(self.res_log, '\n\tStart >>'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST notification adm get'+'\n')
        
        print_tab = '\n\t\t'
        try:
            admin_boss_id = IniValue('setting', 'TestData.admin_boss_id')
            adm_title = IniValue('setting', 'API.adm_title')
            adm_msg = IniValue('setting', 'API.adm_msg')
            adm_id = IniValue('setting', 'API.adm_id')
            webId = IniValue('setting', 'API.webId')
            ReplaceIniValue('admin_notification_adm_get', 'API.id', adm_id)
            return_value, response_time, response_data, self.res_log = ApiResponse(print_tab, self.res_log, 'admin_notification_adm_get', False, False)
            WriteLog(print_tab+'Response data: '+ response_data)
            if(return_value):
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API success (status and response are correct).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                modifytime = json_response.get('0').get('modifytime')
                if(str(json_response.get('0').get('id')) == adm_id):
                    result_list.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get adm_id: '+adm_id)
                else:
                    result_list.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get adm_id: '+str(json_response.get('0').get('id'))+' != '+adm_id)
                
                if(json_response.get('0').get('creatorid') == admin_boss_id):
                    result_list.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get creatorid: '+admin_boss_id)
                else:
                    result_list.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get creatorid: '+json_response.get('0').get('creatorid')+' != '+admin_boss_id)
                
                if(json_response.get('0').get('title') == adm_title):
                    result_list.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get adm_title: '+adm_title)
                else:
                    result_list.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get adm_title: '+json_response.get('0').get('title')+' != '+adm_title)
                
                if(json_response.get('0').get('web_id') == webId):
                    result_list.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get web_id: '+webId)
                else:
                    result_list.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get web_id: '+json_response.get('0').get('web_id')+' != '+webId)
                
                if(json_response.get('content') == adm_msg):
                    result_list.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get adm_msg: '+adm_msg)
                else:
                    result_list.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get adm_msg: '+json_response.get('content')+' != '+adm_msg)
            else:
                result_list.append('FAIL')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API fail (status or response is incorrect).')
            self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        except Exception as e:
            result_list.append('FAIL')
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on admin_notification_adm_get... %s' % str(e))
            
        finally:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
            
        WriteLog(result_list)
        if('FAIL' in result_list or not result_list):
            self.TestResult = 'FAIL'
        else:
            ReplaceIniValue('setting', 'API.adm_modifytime', modifytime)
            self.TestResult = 'PASS'
        self.res_log = WriteDebugLog(self.res_log, print_tab+'# Test Result: '+self.TestResult)
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
        self.res_log = WriteDebugLog(self.res_log, '\n\n\tEnd << '+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST notification adm get')
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