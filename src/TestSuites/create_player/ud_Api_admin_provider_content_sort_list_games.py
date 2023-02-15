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
from O2oUtility import AdminProviderContentSortList

locale.setlocale(locale.LC_CTYPE, 'chinese')
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

class TestCase(BaseCase):
    
    def __init__(self, MyTest):
        # ---------------- [QA] Modify these variables for your test case! ----------------------------------       
        self.Feature= currentdir.split('\\')[-1]
        self.CaseTitle= '[Feature] API POST provider content sort list games'
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
        ReplaceIniValue('admin_provider_content_sort_list', 'API.type', '')
        ReplaceIniValue('admin_provider_content_sort_list', 'API.webid', '')
        ReplaceIniValue('admin_provider_content_sort_list', 'API.lang', '')
        WriteLog('\t'+'<< End Tear Down')
        
        
    def run(self, copy_result):
        self.TestCaseStartTime = datetime.now()
        self.setPreCondition()
        result_list = []
        self.res_log = WriteDebugLog(self.res_log, '\n\tStart >>'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST provider content sort list games'+'\n')
        
        webId = IniValue('setting', 'API.webId')
        language = IniValue('setting', 'TestData.language')
        gameType = IniValue('setting', 'TestData.gameType')
        # gametype = slot, lived, fish, poker, sport, lottery
        list_gameType = gameType.split(', ')
        for each_gmType in list_gameType:
            if(not(each_gmType == 'lived' or each_gmType == 'sport' or each_gmType == 'esport')):
            # each_gmType = slot, fish, poker, lottery
                list_gm_all = []
                list_gm_for_bc_all = []
                game_categories = IniValue('setting', 'GameType.'+each_gmType)
                for game_category in game_categories.split(', '):
                # ===============================================================
                # game_categories(slot) = BB_SLOT, FP, JDB_SLOT, KA, MG_SLOT, PT
                # game_categories(fish) = BB_FISH, JDB_FISH
                #===============================================================
                    if(IniValue('setting', 'GameType.'+game_category)):
                        game_name = IniValue('setting', 'GameType.'+game_category)
                        for each_game_name in game_name.split(', '):
                        #===========================================================
                        # game_category(bb_slot) = 聖獸傳說, 秦皇祕寶
                        # game_category(ka) = 财神爷报到, 神秘金字塔
                        #===========================================================
                            if('BB' in game_category):
                                list_gm_for_bc_all.append('BBIN'+each_game_name)
                            elif('JDB' in game_category):
                                list_gm_for_bc_all.append('JDB'+each_game_name)
                            elif('FP' in game_category):
                                list_gm_for_bc_all.append('FP'+each_game_name)
                            else:
                                list_gm_for_bc_all.append(game_category.replace('_SLOT','').replace('_POKER','').replace('_LOTTERY','')+each_game_name)
                            # bcgamelottery = BB_LOTTERY江蘇快3, BB_LOTTERY廣東11選5, DL快乐十分, DL重庆时时彩
                        list_gm_all.append(game_name)
                ReplaceIniValue('setting', 'GameType.game'+each_gmType, ', '.join(list_gm_all))
                ReplaceIniValue('setting', 'GameType.bcgame'+each_gmType, ', '.join(list_gm_for_bc_all))
            else:
                self.res_log = WriteDebugLog(self.res_log, '\n\t\t- ****No support: '+each_gmType)
                
        for each_gameType in list_gameType:
            if(not(each_gameType == 'lived' or each_gameType == 'sport' or each_gameType == 'esport')):
                gm_list = IniValue('setting', 'GameType.game'+each_gameType)
                ReplaceIniValue('admin_provider_content_sort_list', 'API.type', each_gameType)
                ReplaceIniValue('admin_provider_content_sort_list', 'API.webid', webId)
                ReplaceIniValue('admin_provider_content_sort_list', 'API.lang', language)
                self.res_log, result = AdminProviderContentSortList(self.res_log, 'Boss', each_gameType, 'games', gm_list)
                result_list.append(result)
            else:
                self.res_log = WriteDebugLog(self.res_log, '\n\t\t- ****No support: '+each_gameType)
        
        if(False in result_list):
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
        self.res_log = WriteDebugLog(self.res_log, '\n\n\tEnd << '+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST provider content sort list games')
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