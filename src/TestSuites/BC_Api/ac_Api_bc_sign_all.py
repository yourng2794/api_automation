#!/usr/bin/python
#coding=utf-8
import os
import locale
import logging
import inspect
import shutil
import json
import pickle
import requests
from bs4 import BeautifulSoup
from base64 import b64decode
import threading

from datetime import datetime
from datetime import timedelta
from TestRun import TestRunning
from BaseTestCase import BaseCase
from O2oUtility import WriteLog, WriteDebugLog, ReplaceIniValue, ApiResponse, DeleteFile, ApiCodeDetect, IniValue

locale.setlocale(locale.LC_CTYPE, 'chinese')
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
tooldir = os.path.dirname(os.path.dirname(currentdir))
class TestCase(BaseCase):
    
    def __init__(self, MyTest):
        # ---------------- [QA] Modify these variables for your test case! ----------------------------------       
        self.Feature= currentdir.split('\\')[-1]
        self.CaseTitle= '[Portal] API POST sign in new account in new account'
        self.CaseNote= ''
        self.TestCaseID= '19'
        # (CaseNote: can be blank ''. Use it to leave some notes or description of this case which will be displayed in test report)
        # ----------------------------------------------------------------------------------------------
        self.TestResult = 'FAIL'
        self.CurrentFile = os.path.basename(__file__)
        self.res_log = ''
        BaseCase.TestInfo = MyTest
        self.filename = tooldir+'\\code.jpg'  # I assume you have a way of picking unique filenames
        
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
#         ReplaceIniValue('bc_sign', 'API.code', '')
#         ReplaceIniValue('bc_sign', 'API.acc', '')
#         ReplaceIniValue('bc_sign', 'API.pwd', '')
#         ReplaceIniValue('bc_sign', 'API.checkPwd', '')
#         ReplaceIniValue('bc_sign', 'API.introducerId', '')
#         ReplaceIniValue('bc_sign', 'API.name', '')
#         ReplaceIniValue('bc_sign', 'API.email', '')
#         ReplaceIniValue('bc_sign', 'API.phone', '')
#         ReplaceIniValue('bc_sign', 'API.qq', '')
#         ReplaceIniValue('bc_sign', 'API.wechat', '')
#         ReplaceIniValue('bc_sign', 'API.passport', '')
#         ReplaceIniValue('bc_sign', 'API.agree', '')
#         ReplaceIniValue('bc_sign', 'API.pwdWithdraw', '')
        DeleteFile(self.filename)
        WriteLog('\t'+'<< End Tear Down')
        
        
    def run(self, copy_result):
        self.TestCaseStartTime = datetime.now()
        self.setPreCondition()
        result_list = []
        result_list2 = []
        self.res_log = WriteDebugLog(self.res_log, '\n\tStart >>'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Portal] API POST sign in new account'+'\n')
        
        def load_cookies(filename):
            if os.path.getsize(filename) > 0: 
                with open(filename, 'rb+') as f:
                    return pickle.load(f)
        
        def save_cookies(requests_cookiejar, filename):
            with open(filename, 'wb') as f:
                pickle.dump(requests_cookiejar, f)
        #=======================================================================
        # Current time increase operation.
        # Usage: 
        # a = datetime.now().time() # 09:11:55.775695
        # b = Add_Seconds(a, 300) # 09:16:55
        #=======================================================================
#         def Add_Seconds(tm, secs):
#             fulldate = datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
#             fulldate = fulldate + timedelta(seconds=secs)
#             return fulldate.time()
        
        print_tab = '\n\t\t'
        player_counter_init = int(IniValue('setting', 'BCAPI.player_counter_init'))
        player_counter_total = int(IniValue('setting', 'BCAPI.player_counter_total'))
        bc_acc = IniValue('setting', 'BCAPI.playeracc')
        bc_pwd = IniValue('setting', 'BCAPI.playerpwd')
#                 input(print_tab+'- Please enter code (4 digits): ')
        ReplaceIniValue('bc_sign', 'API.pwd', bc_pwd)
        ReplaceIniValue('bc_sign', 'API.checkPwd', bc_pwd)
        ReplaceIniValue('bc_sign', 'API.code', '0000')
        ReplaceIniValue('bc_sign', 'API.name', 'qatest')
        ReplaceIniValue('bc_sign', 'API.email', 'test@test.test')
        ReplaceIniValue('bc_sign', 'API.agree', '1')
        ReplaceIniValue('bc_sign', 'API.phone', '123456789')
        ReplaceIniValue('bc_sign', 'API.pwdWithdraw', '1234')
        ReplaceIniValue('bc_sign', 'API.birth', '2019-08-27')
        def do_me(num):
            print("Thread", num)
            if(os.path.isfile('session')):
                session = load_cookies('session')
            else:
                session = ''
            try:
                api_params = {}
                api_crud = 'post'
                api_url = 'https://tbcapi1.o2ogt.com/'
                api_path = 'qa/sign'
                playerAcc = bc_acc + str(num)
                api_params[0] = '{acc:'+playerAcc+'}'
                api_params[1] = '{pwd:123456}'
                api_params[2] = '{checkPwd:123456}'
                api_params[3] = '{code:0000}'
                api_params[4] = '{birth:2019-08-27}'
                api_params[5] = '{playerId:}'
                api_params[6] = '{ptId:123456}'
                api_params[7] = '{name:qatest}'
                api_params[8] = '{email:test@test.test}'
                api_params[9] = '{phone:123456789}'
                api_params[10] = '{qq:}'
                api_params[11] = '{wechat:}'
                api_params[12] = '{agree:1}'
                api_params[13] = '{pwdWithdraw:1234}'
                api_data = ''
                api_expect_time = 10
                api_response = '{"Error_code":"S01","Error_message":"success"}'
                # API return content type (JSON/ XML)
                api_headers = {'content-type': 'application/json'}
        #         api_headers = {'content-type': 'application/html'}
        #         api_headers = {'content-type': 'application/x-www-form-urlencoded'}
                
        #         print(str(api_crud))
                if(api_crud == 'post'):
                    self.res_log = WriteDebugLog(self.res_log, print_tab+ '- api url: '+ str(api_url+api_path))
                    self.res_log = WriteDebugLog(self.res_log, print_tab+ '- api params: '+ str(api_params))
                    self.res_log = WriteDebugLog(self.res_log, print_tab+ '- api data: '+ str(api_data).replace("'",'"'))
                    self.res_log = WriteDebugLog(self.res_log, print_tab+ '- api headers: '+ str(api_headers))
        #             res_log = WriteDebugLog(self.res_log, print_tab+ '- api signature: '+ str(api_signature))
                r = requests.post(api_url+api_path, cookies=session, params=api_params, data=json.dumps(api_data), headers=api_headers, timeout=api_expect_time)
                WriteLog(print_tab+ str(r.cookies))
                save_cookies(r.cookies, 'session')
                print(json.dumps(r.url))
                print(str(r.text))
        #         print(r.origin)
                if(r.status_code == 200):
#                     # requests.codes.OK == 200
#                     res_log = WriteDebugLog(self.res_log, print_tab+ '- Status code: 200')
                    if(r.text.lower().replace('\n','').replace(' ','') == api_response):
                        self.res_log = WriteDebugLog(self.res_log, print_tab+ '- Compare response: Success, '+ str(r.elapsed.total_seconds())+' (seconds)')
#                         return (True, str(r.elapsed.total_seconds()), response_data, res_log)
                else:
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Status code: '+str(r.raise_for_status()))
#                     return (False, str(r.elapsed.total_seconds()), response_data, res_log)
#             
            except Exception as e:
                self.res_log = WriteDebugLog(self.res_log, print_tab+ '- (X) Exception (ApiResponse): '+str(e))
#                 return (False, '0.0', '(X) Exception (ApiResponse): '+str(e), res_log)
            try:
#                 return_value, response_time, response_data, self.res_log = ApiResponse(print_tab, self.res_log, 'bc_sign_code', False, True)
#                 self.res_log = WriteDebugLog(self.res_log, print_tab+'Response data: '+ response_data)
#                 imgdata = b64decode(response_data)
#                 with open(self.filename, 'wb') as decode_response_data:
#                     decode_response_data.write(imgdata)
#                     expired_time = Add_Seconds(datetime.now().time(), 60)
#                     self.res_log = WriteDebugLog(self.res_log, print_tab+'- Session expired until: '+ str(expired_time))
#                     
#                 if(return_value):
#                     result_list.append('PASS')
#                     self.res_log = WriteDebugLog(self.res_log, print_tab+'- API success (status and response are correct).')
#                     self.res_log = WriteDebugLog(self.res_log, print_tab+'- Response time: '+ response_time)
#                     self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
#                     
#                 else:
#                     result_list.append('FAIL')
#                     self.res_log = WriteDebugLog(self.res_log, print_tab+'- API fail (status or response is incorrect).')
#                     self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
                
#                 new_code, self.res_log = ApiCodeDetect(print_tab, self.res_log, self.filename)
#                 WriteLog('New code: '+new_code)
                playerAcc = bc_acc + str(num)
#                 input(print_tab+'- Please enter code (4 digits): ')
                ReplaceIniValue('bc_sign', 'API.acc', playerAcc)
                
#                 return_value2, response_time2, response_data2, self.res_log = ApiResponse(print_tab, self.res_log, 'bc_sign', True, True)
#                 WriteLog(print_tab+'Response data: '+ response_data2)
#                 json_response = json.loads(response_data2)
                if(str(r.text)):
                    result_list2.append('PASS')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- API success (status and response are correct).')
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Response time: '+ str(r.elapsed.total_seconds()))
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
                    
#                 elif(json_response.get('Error_code')=='E06'):
# #                     result_list.append('FAIL')
#                     self.res_log = WriteDebugLog(self.res_log, print_tab+'- API fail: '+json_response.get('Error_message'))
#                     self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
#                     
                else:
                    result_list2.append('FAIL')
#                     self.res_log = WriteDebugLog(self.res_log, print_tab+'- API fail: '+json_response.get('Error_message'))
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
                    
            except Exception as e:
#                 result_list.append('FAIL')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on bc_sign... %s' % str(e))
                
            finally:
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- - - ')
        
#         if(retry >= 10):
#             result_list.append('FAIL')
        
        threads = []
        i = 0
        while i < player_counter_total:
            threads.append(threading.Thread(target = do_me, args = (player_counter_init,)))
            threads[i].start()
            player_counter_init += 1
            i += 1
        
        i = 0
        while i < player_counter_total:
            threads[i].join()
            i += 1
        
        ReplaceIniValue('setting', 'BCAPI.player_counter_init', str(player_counter_init))
        WriteLog(result_list2)
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
        self.res_log = WriteDebugLog(self.res_log, '\n\n\tEnd << '+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Portal] API POST sign in new account')
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