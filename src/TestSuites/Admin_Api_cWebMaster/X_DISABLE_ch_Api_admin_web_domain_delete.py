#!/usr/bin/python
#coding=utf-8
import os
import locale
import logging
import inspect
import shutil
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta

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
        self.CaseTitle= '[Feature] API POST web domain delete'
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
        WriteLog('\t'+'<< End Tear Down')
        
        
    def run(self, copy_result):
        self.TestCaseStartTime = datetime.now()
        self.setPreCondition()
        result_list = []
        result_list2 = []
        self.res_log = WriteDebugLog(self.res_log, '\n\tStart >>'+datetime.today().strftime("%m???%d???%H???%M???%S???")+' [Feature] API POST web domain delete'+'\n')
        
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
        
        print_tab = '\n\t\t'
        # Part 1: Create test domain for delete.
        try:
            webDomainId = ''
            webDomainId2 = ''
            webDomain = '221.222.223.224'
            partnerId = IniValue('setting', 'API.partnerid')
            
            ReplaceIniValue('admin_webPlayer_domain_create', 'API.webDomain[]', webDomain)
            ReplaceIniValue('admin_webPlayer_domain_create', 'API.bankerId', partnerId)
            
            return_value, response_time, response_data, self.res_log = ApiResponse(print_tab, self.res_log, 'admin_webPlayer_domain_create', True, False)
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
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on admin_webPlayer_domain_create... %s' % str(e))
            
        finally:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        # Part 2: Get domain ID from web for delete parameter.
        try:
            ReplaceIniValue('admin_webPlayer_domain_list_frame', 'API.webDomain', webDomain)
            ReplaceIniValue('admin_webPlayer_domain_list_frame', 'API.bankerid', partnerId)
            ReplaceIniValue('admin_webPlayer_domain_list_frame', 'API.api_path', 'api/webPlayer/domain/list/frame')
            return_value2, response_time2, response_data2, self.res_log = ApiResponse(print_tab, self.res_log, 'admin_webPlayer_domain_list_frame', False, False)
            WriteLog(print_tab+'Response data: '+ response_data2)
            if(return_value2):
                result_list.append('PASS')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API success (status and response are correct).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- Response time2: '+ response_time2)
                soup2 = BeautifulSoup(response_data2, 'html.parser')
                webDomainId = soup2.find('a',attrs={'href':'web_url_edit.html'}).get('id')
                if(webDomainId):
                    result_list2.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get webDomainId: '+webDomainId)
                else:
                    result_list2.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get webDomainId')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
            else:
                result_list.append('FAIL')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API fail (status or response is incorrect).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        except Exception as e:
            result_list.append('FAIL')
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on admin_webPlayer_domain_list_frame... %s' % str(e))
            
        finally:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        # Part 3: Get domain ID from mobile web for delete parameter.
        try:
            ReplaceIniValue('admin_webPlayer_domain_list_frame', 'API.webDomain', webDomain)
            ReplaceIniValue('admin_webPlayer_domain_list_frame', 'API.bankerid', partnerId)
            ReplaceIniValue('admin_webPlayer_domain_list_frame', 'API.api_path', 'api/webPlayer/domain/list/frame/m')
            return_value3, response_time3, response_data3, self.res_log = ApiResponse(print_tab, self.res_log, 'admin_webPlayer_domain_list_frame', False, False)
            WriteLog(print_tab+'Response data: '+ response_data3)
            if(return_value3):
                result_list.append('PASS')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API success (status and response are correct).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- Response time: '+ response_time3)
                soup3 = BeautifulSoup(response_data3, 'html.parser')
                webDomainId2 = soup3.find('a',attrs={'alt':'??????'}).get('id')
                if(webDomainId == webDomainId2):
                    result_list2.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get webDomainId2: '+webDomainId2)
                else:
                    result_list2.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get webDomainId2')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
            else:
                result_list.append('FAIL')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API fail (status or response is incorrect).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        except Exception as e:
            result_list.append('FAIL')
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on admin_webPlayer_domain_list_frame_m... %s' % str(e))
            
        finally:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        # Part 4: Delete test domain.
        try:
            ReplaceIniValue('admin_webPlayer_domain_delete', 'API.webDomainId', webDomainId)
            
            return_value4, response_time4, response_data4, self.res_log = ApiResponse(print_tab, self.res_log, 'admin_webPlayer_domain_delete', True, False)
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
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on admin_web_domain_delete... %s' % str(e))
            
        finally:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
            
        WriteLog(result_list)
        if('FAIL' in result_list or not result_list):
            self.TestResult = 'FAIL'
        else:
            if('FAIL' in result_list2 or not result_list2):
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
        self.res_log = WriteDebugLog(self.res_log, '\n\n\tEnd << '+datetime.today().strftime("%m???%d???%H???%M???%S???")+' [Feature] API POST web domain delete')
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