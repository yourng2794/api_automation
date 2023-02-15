#!/usr/bin/python
#coding=utf-8
import os, sys
import locale
import logging
import inspect
import shutil
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
        self.CaseTitle= '[Feature] API POST webPlayer web vip domain edit'
        self.CaseNote= ''
        self.TestCaseID= '473'
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
        self.res_log = WriteDebugLog(self.res_log, '\n\tStart >>'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST webPlayer web vip domain edit'+'\n')
        
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
            api_json = tooldir+'\\JsonFiles\\Api_Json\\admin_web_vip_domain_edit.json'
            webId = IniValue('setting', 'API.webId')
            vipGroupId = IniValue('setting', 'API.vipGroupId')
            vipId = IniValue('setting', 'API.vipId')
            webdomain = IniValue('setting', 'API.webdomain')
            transferSet = IniValue('setting', 'API.transferSet')
            setTime = IniValue('setting', 'API.setTime')
            ReplaceJsonValue(api_json, 'webId', webId)
            ReplaceJsonValue(api_json, 'vipGroupId', vipGroupId)
            
            #===================================================================
            # vipDataList":[
            #     {
            #         vipId: 1914c922185bd2846e16b62fa11d68a5,
            #         webDomainUrl: www.168.com,
            #         timeStart:"",
            #         timeEnd:"",
            #         transferSet:"",
            #         setTime:""
            #     },
            #===================================================================
#             ReplaceIniValue('admin_webPlayer_web_vip_domain_edit', 'API.vipDataList[0][vipId]', vipId)
#             ReplaceIniValue('admin_webPlayer_web_vip_domain_edit', 'API.vipDataList[0][webDomainUrl]', webdomain) 
#             ReplaceIniValue('admin_webPlayer_web_vip_domain_edit', 'API.vipDataList[0][timeStart]', '1')
#             ReplaceIniValue('admin_webPlayer_web_vip_domain_edit', 'API.vipDataList[0][timeEnd]', '2019-04-23 18:35:00')
#             ReplaceIniValue('admin_webPlayer_web_vip_domain_edit', 'API.vipDataList[0][transferSet]', '2019-04-23 18:35:00')
#             ReplaceIniValue('admin_webPlayer_web_vip_domain_edit', 'API.vipDataList[0][setTime]', '00:00')
#             dict_vipDataList = nested_dict()
            dict_vipDataList = {}
            dict_vipDataList['vipId'] = vipId
            dict_vipDataList['webDomainUrl'] = webdomain
            dict_vipDataList['transferSet'] = transferSet
            dict_vipDataList['timeStart'] = ''
            dict_vipDataList['timeEnd'] = ''
            dict_vipDataList['setTime'] = setTime
#             list_of_dict = []
#             [list_of_dict.extend([k+'='+v]) for k,v in dict_vipDataList.items()]
#             print(list_of_dict)
#             print(CheckJsonFile(api_json, 'vipDataList|0|vipId'))
#             '"vipId": "1914c922185bd2846e16b62fa11d68a5", "webDomainUrl": "www.168.com", "timeStart": "", "timeEnd": "", "transferSet": "", "setTime": ""'
            ReplaceJsonValue(api_json, 'vipDataList|0', [dict_vipDataList])
#             ReplaceJsonValue(api_json, 'vipDataList|0|webDomainUrl', webdomain)
#             ReplaceJsonValue(api_json, 'vipDataList|0|transferSet', transferSet)
#             ReplaceJsonValue(api_json, 'vipDataList|0|timeStart', '')
#             ReplaceJsonValue(api_json, 'vipDataList|0|timeEnd', '')
#             ReplaceJsonValue(api_json, 'vipDataList|0|setTime', setTime)
#             ReplaceIniValue('admin_webPlayer_web_vip_domain_edit', 'API.vipDataList[]', str(dict_vipDataList).replace("'",'"').replace(' ',''))
            ReplaceIniValue('admin_webPlayer_web_vip_domain_edit', 'API.api_path', 'api/webPlayer/web/vip/domain/edit')
            return_value, response_time, response_data, self.res_log = ApiResponse(print_tab, self.res_log, 'admin_webPlayer_web_vip_domain_edit', True, False)
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
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on admin_webPlayer_web_vip_domain_edit... %s' % str(e))
            
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
        self.res_log = WriteDebugLog(self.res_log, '\n\n\tEnd << '+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST webPlayer web vip domain edit')
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