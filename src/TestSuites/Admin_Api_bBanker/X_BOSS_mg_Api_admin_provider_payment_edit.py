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
from O2oUtility import ReplaceIniValue
from O2oUtility import ReplaceJsonValue

locale.setlocale(locale.LC_CTYPE, 'chinese')
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
tooldir = os.path.dirname(os.path.dirname(currentdir))
if tooldir not in sys.path:
    sys.path.insert(0, tooldir)

class TestCase(BaseCase):
    
    def __init__(self, MyTest):
        # ---------------- [QA] Modify these variables for your test case! ----------------------------------       
        self.Feature= currentdir.split('\\')[-1]
        self.CaseTitle= '[Feature] API POST provider payment edit'
        self.CaseNote= ''
        self.TestCaseID= '139'
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
        self.res_log = WriteDebugLog(self.res_log, '\n\tStart >>'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST provider payment edit'+'\n')
        
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
        info_enable = ''
        info_maxdeposit = ''
        info_maxwithdraw = ''
        info_mindeposit = ''
        info_option = ''
        info_payacc = ''
        info_payment_id = ''
        info_payname = ''
        info_payratio = ''
        info_payurl = ''
        info_secretkey = ''
        edit_currency = []
        print_tab = '\n\t\t'
        
        # Part 1: Get origin data by edit_info
        try:
            paymentId = IniValue('setting', 'API.paymentid')
            ReplaceIniValue('admin_provider_payment_edit_info_get', 'API.paymentId', paymentId)
            return_value, response_time, response_data, self.res_log = ApiResponse(print_tab, self.res_log, 'admin_provider_payment_edit_info_get', False, False)
            WriteLog(print_tab+'Response data: '+ response_data)
            if(return_value):
                result_list.append('PASS')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API success (status and response are correct).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- Response time: '+ response_time)
                paymentName = IniValue('setting', 'API.paymentname')
                json_response = json.loads(response_data)
                if(json_response['payment_id'] == paymentId):
                    result_list.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get payment_id: '+paymentId)
                else:
                    result_list.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get payment_id: '+json_response['payment_id']+' != '+paymentId)
                
                if(json_response['payname'] == paymentName):
                    result_list.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get payname: '+paymentName)
                else:
                    result_list.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get payname: '+json_response['payname']+' != '+paymentName)
                
                info_enable = str(json_response['enable'])
                info_maxdeposit = str(json_response['maxdeposit'])
                info_maxwithdraw = str(json_response['maxwithdraw'])
                info_mindeposit = str(json_response['mindeposit'])
                info_option = str(json_response['option'])
                info_payacc = str(json_response['payacc'])
                info_payment_id = str(json_response['payment_id'])
                info_payname = str(json_response['payname'])
                info_payratio = str(json_response['payratio'])
                info_payurl = str(json_response['payurl'])
                info_secretkey = str(json_response['secretkey'])
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
                
            else:
                result_list.append('FAIL')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API fail (status or response is incorrect).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        except Exception as e:
            result_list.append('FAIL')
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on admin_provider_payment_edit_info_get... %s' % str(e))
            
        finally:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        # Part 2: Get currency array by edit_currency
        try:
            ReplaceIniValue('admin_provider_payment_edit_currency_get', 'API.paymentId', paymentId)
            return_value, response_time, response_data, self.res_log = ApiResponse(print_tab, self.res_log, 'admin_provider_payment_edit_currency_get', False, False)
            WriteLog(print_tab+'Response data: '+ response_data)
            if(return_value):
                result_list.append('PASS')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API success (status and response are correct).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                if(len(json_response['currency']) != 0):
                    result_list.append('PASS')
                    for node in json_response['currency']:
                        if(str(list(node.values())[0]) == '1'):
                            edit_currency.append(str(list(node.keys())[0]))
#                     print(edit_currency)
#                     print(', '.join(edit_currency))
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get currency')
                else:
                    result_list.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get currency')
                
                if(len(json_response['v_currency']) != 0):
                    result_list.append('PASS')
                    for node in json_response['v_currency']:
                        if(str(list(node.values())[0]) == '1'):
                            edit_currency.append(str(list(node.keys())[0]))
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get v_currency')
                    print(edit_currency)
                else:
                    result_list.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get v_currency')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
                
            else:
                result_list.append('FAIL')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API fail (status or response is incorrect).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        except Exception as e:
            result_list.append('FAIL')
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on admin_provider_payment_edit_currency_get... %s' % str(e))
            
        finally:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        try:
            partnerid = IniValue('setting', 'API.partnerid')
            api_json = tooldir+'\\JsonFiles\\Api_Json\\admin_payment_edit.json'
            dict_json = {}
            dict_json['bankerId'] = partnerid
            dict_json['paymentId'] = info_payment_id
            dict_json['payname'] = info_payname
            dict_json['payacc'] = info_payacc
            dict_json['key'] = info_secretkey
            dict_json['url'] = info_payurl
            dict_json['ratio'] = info_payratio
            dict_json['enable'] = info_enable
            dict_json['maxwithdraw'] = '1000'
            dict_json['maxdeposit'] = info_maxdeposit
            dict_json['mindeposit'] = info_mindeposit
            dict_json['option'] = info_option
            dict_json['currency'] = edit_currency
            with open(api_json, 'w') as outfile:
                json.dump(dict_json, outfile, indent=4, ensure_ascii=False)
            return_value, response_time, response_data, self.res_log = ApiResponse(print_tab, self.res_log, 'admin_provider_payment_edit', True, False)
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
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on admin_provider_payment_edit... %s' % str(e))
            
        finally:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        try:
            partnerId = IniValue('setting', 'API.partnerid')
            ReplaceIniValue('admin_provider_payment_bank_info', 'API.paymentId', paymentId)
            ReplaceIniValue('admin_provider_payment_bank_info', 'API.bankerId', partnerId)
            
            return_value, response_time, response_data, self.res_log = ApiResponse(print_tab, self.res_log, 'admin_provider_payment_bank_info', False, False)
            WriteLog(print_tab+'Response data: '+ response_data)
            if(return_value):
                result_list.append('PASS')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API success (status and response are correct).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                if(str(json_response['maxwithdraw']) == '1000'):
                    result_list.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get maxwithdraw: 1000')
                else:
                    result_list.append('FAIL')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get maxwithdraw: '+str(json_response['maxwithdraw'])+' != 1000')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
                
            else:
                result_list.append('FAIL')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API fail (status or response is incorrect).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        except Exception as e:
            result_list.append('FAIL')
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on admin_provider_payment_bank_info... %s' % str(e))
            
        finally:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        try:
            ReplaceJsonValue(api_json, 'maxwithdraw', info_maxwithdraw)
            return_value, response_time, response_data, self.res_log = ApiResponse(print_tab, self.res_log, 'admin_provider_payment_edit', True, False)
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
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on admin_provider_payment_edit... %s' % str(e))
            
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
        self.res_log = WriteDebugLog(self.res_log, '\n\n\tEnd << '+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST provider payment edit')
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