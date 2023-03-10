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
from O2oUtility import ReplaceIniValue
from O2oUtility import IniValue

locale.setlocale(locale.LC_CTYPE, 'chinese')
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

class TestCase(BaseCase):
    
    def __init__(self,MyTest):
        # ---------------- [QA] Modify these variables for your test case! ----------------------------------       
        self.Feature= currentdir.split('\\')[-1]
        self.CaseTitle= '[Feature] API POST partner edit agent level 4'
        self.CaseNote= ''
        self.TestCaseID= '391'
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
        self.res_log = WriteDebugLog(self.res_log, '\n\tStart >>'+datetime.today().strftime("%m???%d???%H???%M???%S???")+' [Feature] API POST partner edit'+'\n')
        print_tab = '\n\t\t'
        try:
            agent_id_level4 = IniValue('setting', 'API.agent_id_level4')
            webid = IniValue('setting', 'API.webid')
            permission = IniValue('admin_partner_create', 'API.permission')
            currency = IniValue('admin_partner_create', 'API.currency')
            payment = IniValue('admin_partner_create', 'API.payment')
            provider = IniValue('admin_partner_create', 'API.provider')
            stopbet = IniValue('admin_partner_create', 'API.stopbet')
            handicap = IniValue('admin_partner_create', 'API.handicap')
            json_currency = json.loads(currency)
            del json_currency['HKD']
            del json_currency['EUR']
            del json_currency['GBP']
            
            ReplaceIniValue('admin_partner_edit', 'API.ptid', agent_id_level4)
            ReplaceIniValue('admin_partner_edit', 'API.permission', permission)
            ReplaceIniValue('admin_partner_edit', 'API.currency', json.dumps(json_currency))
            ReplaceIniValue('admin_partner_edit', 'API.payment', payment)
            ReplaceIniValue('admin_partner_edit', 'API.provider', provider)
            ReplaceIniValue('admin_partner_edit', 'API.stopbet', stopbet)
            ReplaceIniValue('admin_partner_edit', 'API.handicap', handicap)
            ReplaceIniValue('admin_partner_edit', 'API.website[]', webid)
            ReplaceIniValue('admin_partner_edit', 'API.ptPwd', '')
            ReplaceIniValue('admin_partner_edit', 'API.ptName', '')
            ReplaceIniValue('admin_partner_edit', 'API.ptState', '1')
            return_value, response_time, response_data, self.res_log = ApiResponse(print_tab, self.res_log, 'admin_partner_edit', True, False)
            WriteLog(print_tab+'Response data: '+ response_data)
            if(return_value):
                result_list.append('PASS')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API success (status and response are correct).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- Response time: '+ response_time)
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
                
            else:
                result_list.append('FAIL')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API fail (status or response is incorrect).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
                
        except Exception as e:
            result_list.append('FAIL')
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on admin_partner_edit... %s' % str(e))
        
        finally:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        try:
            currency = IniValue('admin_partner_edit', 'API.currency')
            json_currency = json.loads(currency)
            json_currency['HKD'] = '1'
            json_currency['EUR'] = '1'
            json_currency['GBP'] = '1'
            ReplaceIniValue('admin_partner_edit', 'API.currency', json.dumps(json_currency))
            return_value, response_time, response_data, self.res_log = ApiResponse(print_tab, self.res_log, 'admin_partner_edit', True, False)
            WriteLog(print_tab+'Response data: '+ response_data)
            if(return_value):
                result_list.append('PASS')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API success (status and response are correct).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- Response time: '+ response_time)
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
                 
            else:
                result_list.append('FAIL')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API fail (status or response is incorrect).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
                 
        except Exception as e:
            result_list.append('FAIL')
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on admin_partner_edit... %s' % str(e))
         
        finally:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        WriteLog(result_list)
        if('FAIL' in str(result_list) or not result_list):
            self.TestResult = 'FAIL'
        else:
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
        self.res_log = WriteDebugLog(self.res_log, '\n\n\tEnd << '+datetime.today().strftime("%m???%d???%H???%M???%S???")+' [Feature] API POST partner edit')
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