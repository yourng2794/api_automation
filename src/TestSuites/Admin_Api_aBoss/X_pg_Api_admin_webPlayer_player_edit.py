#!/usr/bin/python
#coding=utf-8
import os
import locale
import logging
import inspect
import shutil
from datetime import datetime

from TestRun import TestRunning
from BaseTestCase import BaseCase
from O2oUtility import WriteLog
from O2oUtility import WriteDebugLog
from O2oUtility import IniValue
from O2oUtility import ReplaceIniValue
from O2oUtility import AdminWebPlayerEdit
from O2oUtility import AdminWebPlayerEditGet

locale.setlocale(locale.LC_CTYPE, 'chinese')
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

class TestCase(BaseCase):
    
    def __init__(self, MyTest):
        # ---------------- [QA] Modify these variables for your test case! ----------------------------------       
        self.Feature= currentdir.split('\\')[-1]
        self.CaseTitle= '[Feature] API POST webPlayer player edit'
        self.CaseNote= ''
        self.TestCaseID= '177'
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
        ReplaceIniValue('admin_webPlayer_player_edit_get', 'API.playerId', '')
        ReplaceIniValue('admin_webPlayer_player_edit', 'API.playerId', '')
        ReplaceIniValue('admin_webPlayer_player_edit', 'API.playerName', '')
        ReplaceIniValue('admin_webPlayer_player_edit', 'API.playerPwd', '')
        ReplaceIniValue('admin_webPlayer_player_edit', 'API.playerStatus', '')
        WriteLog('\t'+'<< End Tear Down')
        
        
    def run(self, copy_result):
        self.TestCaseStartTime = datetime.now()
        self.setPreCondition()
        result_list = []
        self.res_log = WriteDebugLog(self.res_log, '\n\tStart >>'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST webPlayer player edit'+'\n')
        
        # Part 1: Edit to freeze state
        number = IniValue('setting', 'API.number')
        playerAcc = IniValue('setting', 'API.playerAcc')+number
        myName = IniValue('setting', 'API.myName')+number
        playerId = IniValue('setting', 'API.playerid')
        vipId = IniValue('setting', 'API.vipId')
        webId = IniValue('setting', 'API.webId')
        ReplaceIniValue('admin_webPlayer_player_edit', 'API.playerPwd', playerAcc)
        ReplaceIniValue('admin_webPlayer_player_edit', 'API.playerName', myName)
        ReplaceIniValue('admin_webPlayer_player_edit', 'API.playerId', playerId)
        ReplaceIniValue('admin_webPlayer_player_edit', 'API.playerStatus', '3') # 1:啟用 2:停權 3:凍結 4:停用
        
        self.res_log, result = AdminWebPlayerEdit(self.res_log, 'Boss')
        result_list.append(result)
        
        # Part 2: Check state
        state = 3  # 1:啟用 2:停權 3:凍結 4:停用
        ReplaceIniValue('admin_webPlayer_player_edit_get', 'API.playerId', playerId)
        
        self.res_log, result = AdminWebPlayerEditGet(self.res_log, 'Boss', webId, vipId, state)
        result_list.append(result)
        
        # Part 3: Edit to active state
        ReplaceIniValue('admin_webPlayer_player_edit', 'API.playerStatus', '1') # 1:啟用 2:停權 3:凍結 4:停用
        
        self.res_log, result = AdminWebPlayerEdit(self.res_log, 'Boss')
        result_list.append(result)
        
        # Part 4: Check state
        state = 1  # 1:啟用 2:停權 3:凍結 4:停用
        ReplaceIniValue('admin_webPlayer_player_edit_get', 'API.playerId', playerId)
        
        self.res_log, result = AdminWebPlayerEditGet(self.res_log, 'Boss', webId, vipId, state)
        result_list.append(result)
        
        if(False in result_list or not result_list):
            self.TestResult = 'PASS'
        else:
            self.TestResult = 'FAIL'
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
        self.res_log = WriteDebugLog(self.res_log, '\n\n\tEnd << '+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST webPlayer player edit')
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