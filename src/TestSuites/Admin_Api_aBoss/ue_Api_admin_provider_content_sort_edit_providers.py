#!/usr/bin/python
#coding=utf-8
import os, sys
import locale
import logging
import inspect
import shutil
import random
import json
from datetime import datetime

from TestRun import TestRunning
from BaseTestCase import BaseCase
from O2oUtility import WriteLog
from O2oUtility import WriteDebugLog
from O2oUtility import IniValue
from O2oUtility import ReplaceIniValue
from O2oUtility import IniGetKeyFromValue
from O2oUtility import AdminProviderContentCommGameList
from O2oUtility import AdminProviderContentSortEdit

locale.setlocale(locale.LC_CTYPE, 'chinese')
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
tooldir = os.path.dirname(os.path.dirname(currentdir))
if tooldir not in sys.path:
    sys.path.insert(0, tooldir)

class TestCase(BaseCase):
    
    def __init__(self, MyTest):
        # ---------------- [QA] Modify these variables for your test case! ----------------------------------       
        self.Feature= currentdir.split('\\')[-1]
        self.CaseTitle= '[Feature] API POST provider content sort edit providers'
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
        WriteLog('\t'+'<< End Tear Down')
        
        
    def run(self, copy_result):
        self.TestCaseStartTime = datetime.now()
        self.setPreCondition()
        json_dict = {}
        dict_data = {}
        list_rule = []
        result_list = []
        result_list2 = []
        self.res_log = WriteDebugLog(self.res_log, '\n\tStart >>'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST provider content sort edit providers'+'\n')
        
        gametypes = IniValue('setting', 'TestData.gametype')
        language = IniValue('setting', 'TestData.language')
        webId = IniValue('setting', 'API.webId')
        api_json = tooldir+'\\JsonFiles\\Api_Json\\admin_provider_content_sort_edit.json'
        
        for gametype in gametypes.split(', '):
            print(gametype)
            providers = IniValue('setting', 'GameType.'+gametype)
            list_providers = providers.split(', ')
            print(len(list_providers))
            if(len(list_providers) > 2):
                list_random = random.sample(range(0, len(list_providers)-1), 2)
                first_key = list_random[0]
                second_key = list_random[1]
                json_dict['type'] = gametype
                json_dict['webid'] = webId
                json_dict['settype'] = 'provider'
                json_dict['lang'] = language
                list_rule.append(list_providers[first_key])
                list_rule.append(list_providers[second_key])
                dict_data['rule'] = list_rule
                json_dict['data'] = dict_data
            elif(len(list_providers) == 2):
                first_key = list_providers[0]
                second_key = list_providers[1]
                json_dict['type'] = gametype
                json_dict['webid'] = webId
                json_dict['settype'] = 'provider'
                json_dict['lang'] = language
                list_rule.append(first_key)
                list_rule.append(second_key)
                dict_data['rule'] = list_rule
                json_dict['data'] = dict_data
            elif(len(list_providers) == 1):
                first_key = list_providers[0]
                json_dict['type'] = gametype
                json_dict['webid'] = webId
                json_dict['settype'] = 'provider'
                json_dict['lang'] = language
                list_rule.append(first_key)
                dict_data['rule'] = list_rule
                json_dict['data'] = dict_data
            else:
                self.res_log = WriteDebugLog(self.res_log, '\n\t\t- (X) len(list_providers): '+ str(len(list_providers))+' ( != 1 or 2)')
            
            ReplaceIniValue('setting', 'TestData.top_providers_'+gametype, ', '.join(list_rule))
            with open(api_json, 'w') as outfile:
                json.dump(json_dict, outfile, indent=4)
            
            json_dict = {}
            dict_data = {}
            list_rule = []
            self.res_log, result2 = AdminProviderContentSortEdit(self.res_log, 'Boss')
            result_list2.append(result2)
        
        if(False in result_list):
            self.TestResult = 'FAIL'
        else:
            if(False in result_list2):
                self.TestResult = 'FAIL'
            else:
                self.TestResult = 'PASS'
        self.res_log = WriteDebugLog(self.res_log, '# Test Result: '+self.TestResult)
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
        self.res_log = WriteDebugLog(self.res_log, '\n\n\tEnd << '+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST provider content sort edit providers')
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