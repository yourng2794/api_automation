#!/usr/bin/python
#coding=utf-8
import os
import sys
import locale
import logging
import inspect
import shutil
import json
from datetime import datetime, timedelta

from TestRun import TestRunning
from BaseTestCase import BaseCase
from O2oUtility import WriteLog, WriteDebugLog, ReplaceIniValue, ApiResponse, IniValue, ReplaceJsonValue

locale.setlocale(locale.LC_CTYPE, 'chinese')
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
tooldir = os.path.dirname(os.path.dirname(currentdir))
if tooldir not in sys.path:
    sys.path.insert(0, tooldir)
# iniFile = tooldir+'\\ini\\setting.ini'

class TestCase(BaseCase):
    
    def __init__(self,MyTest):
        # ---------------- [QA] Modify these variables for your test case! ----------------------------------       
        self.Feature= currentdir.split('\\')[-1]
        self.CaseTitle= '[Portal] API POST KA login'
        self.CaseNote= ''
        self.TestCaseID= '21'
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
        result_list = []
        self.res_log = WriteDebugLog(self.res_log, '\n\tStart >>'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Portal] POST KA login API'+'\n')
        
        #=======================================================================
        # Current time increase operation.
        # Usage: 
        # a = datetime.now().time() # 09:11:55.775695
        # b = Add_Seconds(a, 300) # 09:16:55
        #=======================================================================
        def Add_Seconds(tm, secs):
            fulldate = datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
            fulldate = fulldate + timedelta(seconds=secs)
            return fulldate.time()
        
        try:
            dt = datetime.now()
            api_json = tooldir+'\\JsonFiles\\Api_Json\\ka_login.json'
            expire_time = int(dt.timestamp())+7200
            ReplaceJsonValue(api_json, 'expiretimespan', str(expire_time)+'000') # Define one our later is expire time
            sessionid = IniValue('setting', 'API.sessionid')
            playerid = IniValue('setting', 'API.playerid')
            walletid = IniValue('setting', 'API.walletid')
            ReplaceJsonValue(api_json, 'sessionid', sessionid)
            ReplaceJsonValue(api_json, 'playerid', playerid)
            ReplaceJsonValue(api_json, 'walletid', walletid)
            
            return_value, response_time, response_data, self.res_log = ApiResponse('\n\t\t', self.res_log, 'ka_login', True, True)
            if(return_value):
                result_list.append('PASS')
                self.res_log = WriteDebugLog(self.res_log, '\n\t\t- API success (status and response are correct).')
                self.res_log = WriteDebugLog(self.res_log, '\n\t\t- Response time: '+ response_time)
                self.res_log = WriteDebugLog(self.res_log, '\n\t\tResponse data: '+ response_data)
                self.res_log = WriteDebugLog(self.res_log, '\n\t\t---')
                response_json = json.loads(response_data)
                ReplaceIniValue(tooldir+'\\ini\\setting', 'API.token', response_json['token'])
            else:
                if('"status":"success","statusCode":"0"' in response_data):
                    result_list.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, '\n\t\t- API success (status and response are correct).')
                    response_json = json.loads(response_data)
                    ReplaceIniValue('setting', 'API.token', response_json['token'])
                else:
                    result_list.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, '\n\t\t- API fail (status or response is incorrect).')
                self.res_log = WriteDebugLog(self.res_log, '\n\t\tResponse data: '+ response_data)
                self.res_log = WriteDebugLog(self.res_log, '\n\t\t---')
                
        except Exception as e:
            result_list.append('FAIL')
            self.res_log = WriteDebugLog(self.res_log, '\n\t\t- Exception: on ka_login... %s' % str(e))
            
        finally:
            self.res_log = WriteDebugLog(self.res_log, '\n\t\t- - - ')
        
        print(result_list)
        if('FAIL' in str(result_list) or not result_list):
            self.TestResult = 'FAIL'
        else:
            self.TestResult = 'PASS'
        self.res_log = WriteDebugLog(self.res_log, '\n\t\t# Test Result: '+self.TestResult)
        # [QA] Be sure to save result "PASS" or "FAIL" to self.TestResult
        # ----------------------------------------------------------------------------------------------
        
        WriteLog('\t'+'Test Result: ' + self.TestResult)
        self.teardown()

        self.TestCaseEndTime = datetime.now()
        self.TestCaseDuration = ((self.TestCaseEndTime - self.TestCaseStartTime).total_seconds())*1000000
        if (self.TestCaseDuration == 0):
            self.TestCaseDuration = ' less than 1'
        self.TestInfo.setTestRunEndTime()
        
        # [QA] Set "collectOtherFile = True" if there is any file that should be collected        
        self.res_log = WriteDebugLog(self.res_log, '\n\n\tEnd << '+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Portal] POST KA login API')
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