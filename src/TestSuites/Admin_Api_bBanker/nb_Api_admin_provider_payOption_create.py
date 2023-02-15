#!/usr/bin/python
#coding=utf-8
import os, sys
import locale
import logging
import inspect
import shutil
import json
from datetime import datetime
from datetime import timedelta

from TestRun import TestRunning
from BaseTestCase import BaseCase
from O2oUtility import WriteLog
from O2oUtility import WriteDebugLog
from O2oUtility import ApiResponse
from O2oUtility import IniValue

locale.setlocale(locale.LC_CTYPE, 'chinese')
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
tooldir = os.path.dirname(os.path.dirname(currentdir))
if tooldir not in sys.path:
    sys.path.insert(0, tooldir)

class TestCase(BaseCase):
    
    def __init__(self, MyTest):
        # ---------------- [QA] Modify these variables for your test case! ----------------------------------       
        self.Feature= currentdir.split('\\')[-1]
        self.CaseTitle= '[Feature] API POST provider payOption create'
        self.CaseNote= ''
        self.TestCaseID= '322'
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
        self.res_log = WriteDebugLog(self.res_log, '\n\tStart >>'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST provider payOption create'+'\n')
        
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
        # Part 1: Set payment bank.
#         try:
#             paymentId = IniValue('setting', 'API.paymentid')
#             partnerId = IniValue('setting', 'API.partnerid')
#             currency = IniValue('setting', 'API.currency')
#             bankName2 = IniValue('setting', 'API.bankname2')
#             api_json = tooldir+'\\JsonFiles\\Api_Json\\admin_payment_bank_link_edit.json'
#             json_dict = {}
#             json_dict['bankerId'] = partnerId
#             json_dict['paymentId'] = paymentId
#             json_dict['withdraw'] = {}
#             json_dict['deposit'] = {}
#             json_dict['withdraw'][currency] = {}
#             json_dict['deposit'][currency] = {}
# #             json_dict['withdraw'][currency]['0'] = list_banknames[0]
#             json_dict['withdraw'][currency]['0'] = bankName2
#             json_dict['deposit'][currency]['0'] = bankName2
#             print(json_dict)
#             with open(api_json, 'w') as outfile:
#                 json.dump(json_dict, outfile, indent=4, ensure_ascii=False)
#             return_value, response_time, response_data, self.res_log = ApiResponse(print_tab, self.res_log, 'admin_provider_payment_bank_link_edit', True, False)
#             WriteLog(print_tab+'Response data: '+ response_data)
#             if(return_value):
#                 result_list.append('PASS')
#                 self.res_log = WriteDebugLog(self.res_log, print_tab+'- API success (status and response are correct).')
#                 self.res_log = WriteDebugLog(self.res_log, print_tab+'- Response time: '+ response_time)
#                 self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
#                 
#             else:
#                 result_list.append('FAIL')
#                 self.res_log = WriteDebugLog(self.res_log, print_tab+'- API fail (status or response is incorrect).')
#                 self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
#                 
#         except Exception as e:
#             result_list.append('FAIL')
#             self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on admin_provider_payment_bank_link_edit... %s' % str(e))
#             
#         finally:
#             self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        try:
            partnerId = IniValue('setting', 'API.partnerid')
            currency = IniValue('setting', 'API.currency')
            paymentId = IniValue('setting', 'API.paymentid')
            payOptionName2 = IniValue('setting', 'API.payoptionname2')
            api_json = tooldir+'\\JsonFiles\\Api_Json\\admin_payOption_create.json'
            json_dict = {}
            json_dict['bankerId'] = partnerId
            json_dict['payName'] = payOptionName2
            json_dict['currency'] = []
            json_dict['currency'] = [currency]
            json_dict['review'] = '1'
            json_dict['reviewAmount'] = '1'
            json_dict['reviewHour'] = '2'
            json_dict['onlinePromo'] = '2'
            json_dict['onlineCount'] = '0'
            json_dict['onlineAmount'] = '4'
            json_dict['onlineRatio'] = '1.1'
            json_dict['onlineMaxdep'] = '6'
            json_dict['onlineMindep'] = '7'
            json_dict['onlineLimit'] = '8'
            json_dict['companyPromo'] = '2'
            json_dict['companyCount'] = '0'
            json_dict['companyAmount'] = '1'
            json_dict['companyRatio'] = '2.1'
            json_dict['companyMaxdep'] = '3'
            json_dict['companyMindep'] = '4'
            json_dict['companyLimit'] = '5'
            json_dict['withdraw'] = {}
            json_dict['deposit'] = {}
            json_dict['deposit'][currency] = []
            json_dict['withdraw'][currency] = []
            json_dict['withdraw'][currency] = [paymentId]
            json_dict['deposit'][currency] = [paymentId]
#             json_dict['withdraw'][currency]['0'] = list_banknames[0]
#             json_dict['withdraw'][currency]['0'] = bankName
            with open(api_json, 'w') as outfile:
                json.dump(json_dict, outfile, indent=4, ensure_ascii=False)
#             ReplaceJsonValue(api_json, 'currency', [currency])
#             ReplaceJsonValue(api_json, 'deposit|currency', [paymentId])
#             ReplaceJsonValue(api_json, 'withdraw|currency', [paymentId])
            return_value, response_time, response_data, self.res_log = ApiResponse(print_tab, self.res_log, 'admin_provider_payOption_create', True, False)
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
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on admin_provider_payOption_create... %s' % str(e))
            
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
        self.res_log = WriteDebugLog(self.res_log, '\n\n\tEnd << '+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST provider payOption create')
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