#!/usr/bin/python
#coding=utf-8
import os, sys
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
from O2oUtility import CheckJsonFile

locale.setlocale(locale.LC_CTYPE, 'chinese')
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
tooldir = os.path.dirname(os.path.dirname(currentdir))
if tooldir not in sys.path:
    sys.path.insert(0, tooldir)
class TestCase(BaseCase):
    
    def __init__(self, MyTest):
        # ---------------- [QA] Modify these variables for your test case! ----------------------------------       
        self.Feature= currentdir.split('\\')[-1]
        self.CaseTitle= '[Feature] API POST webPlayer promo cnr frame m'
        self.CaseNote= ''
        self.TestCaseID= '295'
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
        self.res_log = WriteDebugLog(self.res_log, '\n\tStart >>'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST webPlayer promo cnr frame m'+'\n')
        
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
        try:
            promoid = IniValue('setting', 'API.promoid')
            promoname = IniValue('setting', 'API.promoname')
            ReplaceIniValue('admin_webPlayer_promo_cnr_frame', 'API.promoid', promoid)
            ReplaceIniValue('admin_webPlayer_promo_cnr_frame', 'API.ptid', '')
            ReplaceIniValue('admin_webPlayer_promo_cnr_frame', 'API.api_path', 'api/webPlayer/promo/cnr/frame/m')
            return_value, response_time, response_data, self.res_log = ApiResponse(print_tab, self.res_log, 'admin_webPlayer_promo_cnr_frame', False, False)
            WriteLog(print_tab+'Response data: '+ response_data)
            if(return_value):
                result_list.append('PASS')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API success (status and response are correct).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- Response time: '+ response_time)
                api_json = tooldir+'\\JsonFiles\\Api_Json\\admin_promo_create.json'
                soup = BeautifulSoup(response_data, 'html.parser')
                soup_name = soup.find("input", {"name":"name"})
                soup_stime = soup.find("input", {"name":"stime"})
                soup_etime = soup.find("input", {"name":"etime"})
                stime = CheckJsonFile(api_json, 'stime')
                etime = CheckJsonFile(api_json, 'etime')
                condition_reg = CheckJsonFile(api_json, 'condition|reg')
                condition_login = CheckJsonFile(api_json, 'condition|login')
                condition_trunover = CheckJsonFile(api_json, 'condition|trunover')
                conditionReg = soup.find("input", {"id":"conditionReg"})
                conditionLogin = soup.find("input", {"id":"conditionLogin"})
                conditionTrunover = soup.find("input", {"id":"trunover"})
                if(soup_name.get("value") == promoname):
                    result_list2.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get name: '+soup_name.get("value"))
                else:
                    result_list2.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get name: '+soup_name.get("value")+ ' != '+ promoname)
                
                if(soup_stime.get("value") == stime):
                    result_list2.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get stime: '+soup_stime.get("value"))
                else:
                    result_list2.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get stime: '+soup_stime.get("value")+ ' != '+ stime)
                
                if(soup_etime.get("value") == etime):
                    result_list2.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get etime: '+soup_etime.get("value"))
                else:
                    result_list2.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get etime: '+soup_etime.get("value")+ ' != '+ etime)
                
                if((str(condition_trunover) != 'False') and (conditionTrunover.get("value") == str(condition_trunover))):
                    result_list2.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get conditionTrunover: '+conditionTrunover.get("value"))
                elif(str(condition_trunover) == 'False'):
                    result_list2.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get conditionTrunover: '+str(condition_trunover))
                else:
                    result_list2.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get conditionTrunover: '+conditionTrunover.get("value")+ ' != '+ str(condition_trunover))
                
                if(conditionReg.get("checked") == 'checked' and str(condition_reg) == '1'):
                    result_list2.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get conditionReg: 1')
                elif((not conditionReg.get("checked")) and (str(condition_reg) == '0')):
                    result_list2.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get conditionReg: 0')
                else:
                    result_list2.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get conditionReg')
                
                if(conditionLogin.get("checked") == 'checked' and str(condition_login) == '1'):
                    result_list2.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get conditionLogin: 1')
                elif((not conditionLogin.get("checked")) and (str(condition_login) == '0')):
                    result_list2.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get conditionLogin: 0')
                else:
                    result_list2.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get conditionLogin')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
                
            else:
                result_list.append('FAIL')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API fail (status or response is incorrect).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        except Exception as e:
            result_list.append('FAIL')
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on admin_webPlayer_promo_cnr_frame_m... %s' % str(e))
            
        finally:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        WriteLog(result_list)
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
        self.res_log = WriteDebugLog(self.res_log, '\n\n\tEnd << '+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST webPlayer promo cnr frame m')
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