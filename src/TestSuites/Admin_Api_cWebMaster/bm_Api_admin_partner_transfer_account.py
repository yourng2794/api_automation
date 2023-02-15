#!/usr/bin/python
#coding=utf-8
import os
import locale
import logging
import inspect
import shutil
from bs4 import BeautifulSoup
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
        self.CaseTitle= '[Feature] API POST partner transfer account'
        self.CaseNote= ''
        self.TestCaseID= '482'
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
        result_list2 = []
        self.res_log = WriteDebugLog(self.res_log, '\n\tStart >>'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST partner transfer account'+'\n')
        print_tab = '\n\t\t'
        # Part 1: Create layer 4-2 agent account.
        try:
            agent_level4_2 = IniValue('setting', 'API.agent_level4_2')
            web_master_id = IniValue('setting', 'API.web_master_id')
            webId = IniValue('setting', 'API.webid')
            ReplaceIniValue('admin_partner_create', 'API.ptAcc', agent_level4_2)
            ReplaceIniValue('admin_partner_create', 'API.ptPwd', agent_level4_2)
            ReplaceIniValue('admin_partner_create', 'API.ptTypeId', '')
            ReplaceIniValue('admin_partner_create', 'API.ptParentId', web_master_id)
            ReplaceIniValue('admin_partner_create', 'API.website[]', webId)
            return_value1, response_time1, response_data1, self.res_log = ApiResponse(print_tab, self.res_log, 'admin_partner_create', True, False)
            WriteLog(print_tab+'Response data: '+ response_data1)
            if(return_value1):
                result_list.append('PASS')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API success (status and response are correct).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- Response time: '+ response_time1)
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
                
            else:
                result_list.append('FAIL')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API fail (status or response is incorrect).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
                
        except Exception as e:
            result_list.append('FAIL')
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on admin_partner_create... %s' % str(e))
        
        finally:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        # Part 2: Get id of agent 4-2 agent account.
        try:
            ReplaceIniValue('admin_partner_list_frame', 'API.search', agent_level4_2)
            ReplaceIniValue('admin_partner_list_frame', 'API.api_path', 'api/partner/list/frame')
            return_value2, response_time2, response_data2, self.res_log = ApiResponse(print_tab, self.res_log, 'admin_partner_list_frame', False, False)
            WriteLog(print_tab+'Response data: '+ response_data2)
            if(return_value2):
                result_list.append('PASS')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API success (status and response are correct).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- Response time: '+ response_time2)
                soup1 = BeautifulSoup(response_data2, 'html.parser')
                my_attribute1 = soup1.find('a',attrs={'alt':'新增'}).get('id')
                ReplaceIniValue('setting', 'API.agent_id_level4_2', my_attribute1)
                if(my_attribute1):
                    result_list2.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get agent_id_level4_2: '+my_attribute1)
                else:
                    result_list2.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get agent_id_level4_2')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
                
            else:
                result_list.append('FAIL')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API fail (status or response is incorrect).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        except Exception as e:
            result_list.append('FAIL')
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on admin_partner_list_frame... %s' % str(e))
        
        finally:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        # Part 3: Get transfer in agent account list.
        try:
            agent_level4_2 = IniValue('setting', 'API.agent_level4_2')
            agent_id_level4_2 = IniValue('setting', 'API.agent_id_level4_2')
            agent_id_level4 = IniValue('setting', 'API.agent_id_level4')
            ReplaceIniValue('admin_partner_transfer_list_frame', 'API.searchType', 'acc')
            ReplaceIniValue('admin_partner_transfer_list_frame', 'API.search', agent_level4_2)
            ReplaceIniValue('admin_partner_transfer_list_frame', 'API.id', agent_id_level4)
            ReplaceIniValue('admin_partner_transfer_list_frame', 'API.api_path', 'api/partner/transfer/list/frame')
            return_value3, response_time3, response_data3, self.res_log = ApiResponse(print_tab, self.res_log, 'admin_partner_transfer_list_frame', False, False)
            WriteLog(print_tab+'Response data: '+ response_data3)
            if(return_value3):
                result_list.append('PASS')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API success (status and response are correct).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- Response time: '+ response_time3)
                soup2 = BeautifulSoup(response_data3, 'html.parser')
                my_attribute2 = soup2.find('input',id=True).get('id')
                if(my_attribute2 == agent_id_level4_2):
                    result_list2.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get agent_id_level4_2: '+agent_id_level4_2)
                else:
                    result_list2.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get agent_id_level4_2: '+my_attribute2+' != '+agent_id_level4_2)
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
                
            else:
                result_list.append('FAIL')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API fail (status or response is incorrect).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        except Exception as e:
            result_list.append('FAIL')
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on admin_partner_transfer_list_frame... %s' % str(e))
        
        finally:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        # Part 4: Move layer 5 from agent 4 to agent 4-2
        try:
            agent_id_level4 = IniValue('setting', 'API.agent_id_level4')
            agent_id_level4_2 = IniValue('setting', 'API.agent_id_level4_2')
            ReplaceIniValue('admin_partner_transfer_account', 'API.outId', agent_id_level4)
            ReplaceIniValue('admin_partner_transfer_account', 'API.inId', agent_id_level4_2)
            return_value4, response_time4, response_data4, self.res_log = ApiResponse(print_tab, self.res_log, 'admin_partner_transfer_account', True, False)
            WriteLog(print_tab+'Response data: '+ response_data4)
            if(return_value4):
                result_list.append('PASS')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API success (status and response are correct).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- Response time: '+ response_time4)
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
                
            else:
                result_list.append('FAIL')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API fail (status or response is incorrect).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        except Exception as e:
            result_list.append('FAIL')
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on admin_partner_transfer_account... %s' % str(e))
        
        finally:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
            
        WriteLog(result_list)
        WriteLog(result_list2)
        if('FAIL' in str(result_list) or not result_list):
            self.TestResult = 'FAIL'
        else:
            if('FAIL' in str(result_list2) or not result_list2):
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
        self.res_log = WriteDebugLog(self.res_log, '\n\n\tEnd << '+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST partner transfer account')
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