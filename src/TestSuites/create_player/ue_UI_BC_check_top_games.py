#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging, sys, os, inspect, shutil, locale
from datetime import datetime
import time
from BaseTestCase import BaseCase
from O2oUtility import WriteLog, WriteDebugLog, IniValue
from TestRun import TestRunning

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

locale.setlocale(locale.LC_CTYPE, 'chinese')
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
tooldir = os.path.dirname(os.path.dirname(currentdir))
if tooldir not in sys.path:
    sys.path.insert(0, tooldir)
iniFile = tooldir+'\\ini\\setting.ini'

class TestCase(BaseCase):
    
    def __init__(self,MyTest):
        # ---------------- [QA] Modify these variables for your test case! ----------------------------------       
        self.Feature= currentdir.split('\\')[-1]
        self.CaseTitle= '[UI] BC check top games'
        self.CaseNote= ''
        self.TestCaseID= '150611'
        # (CaseNote: can be blank ''. Use it to leave some notes or description of this case which will be displayed in test report)
        # ----------------------------------------------------------------------------------------------
        self.TestResult = 'FAIL'
        self.CurrentFile = os.path.basename(__file__)
        BaseCase.TestInfo = MyTest
        self.res_log = ''
        self.filename = tooldir+'\\code.jpg'  # I assume you have a way of picking unique filenames
        self.env = IniValue('setting', 'TestEnv.bc_ui_url')
        self.username = IniValue('setting', 'PlayGame.bc_acc')
        self.password = IniValue('setting', 'PlayGame.bc_pwd')
        
    def setPreCondition(self):
        WriteLog('********Test Case: '+self.CurrentFile+'********')
        # [QA] Set up Pre-condition if any
        WriteLog('Set up Pre-condition of this case...')
        chrome_options = Options()
        chrome_options.add_argument('--allow-outdated-plugins')
        self.driver = webdriver.Chrome(tooldir+'\\chromedriver.exe', options=chrome_options)
        self.driver.maximize_window()
        self.driver.implicitly_wait(self.TestInfo.normal_time)
        self.accept_next_alert = True
        self.CaseNote = WriteDebugLog(self.CaseNote, 'Success open browser.')
        self.driver.get(self.env)
        time.sleep(1)
        
        
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
         
        # 2. Run generateResults() of parent class
        else:
            super().generateResults()
        
        
    def teardown(self):
        # [QA] Tear down the environment if it needs
        WriteLog('\t'+'>> Tear Down of this case')
        self.driver.quit()
        WriteLog('\t\t'+'Driver closed')
        WriteLog('\t'+'<< End Tear Down')
        
        
    def run(self, copy_result):
        self.TestCaseStartTime = datetime.now()
        self.setPreCondition()
        result_list = []
        game_title_list = ['hotGameArea', 'slotGameArea', 'livedGameArea', 'fishGameArea', 'pokerGameArea', 'sportGameArea', 'lotteryGameArea', 'eSportGameArea']
        game_title_hover = ['hotpBtn', 'slotpBtn', 'livedpBtn', 'fishpBtn', 'pokerpBtn', 'sportpBtn', 'lotterypBtn', 'eSportpBtn']
        print_tab = '\n\t\t'
        self.CaseNote = WriteDebugLog(self.CaseNote, '\t'+datetime.today().strftime("%m???%d???%H???%M???%S???")+'>> Start to [UI] BC check top games'+'\n')
        bcgameslot = IniValue('setting', 'GameType.bcgameslot')
        bcgamefish = IniValue('setting', 'GameType.bcgamefish')
        bcgamepoker = IniValue('setting', 'GameType.bcgamepoker')
        bcgamelottery = IniValue('setting', 'GameType.bcgamelottery')
        #=======================================================================
        # gameslot = ????????????, ????????????, ????????????, ????????????, ????????????II, ??????????????????II, ???????????????, ???????????????, ????????????-??????????????????, 108??????
        # gamefish = ????????????, ????????????2, ????????????, ????????????
        # gamepoker = ????????????, ?????????, ????????????, ?????????5PK
        # gamelottery = ?????????3, ??????11???5, ????????????, ???????????????
        #=======================================================================
        try:
            for (each_game_title, game_hover) in zip(game_title_list, game_title_hover):
                this_top_games = ''
                if(each_game_title == 'slotGameArea'):
                    this_top_games = bcgameslot
                elif(each_game_title == 'fishGameArea'):
                    this_top_games = bcgamefish
                elif(each_game_title == 'pokerGameArea'):
                    this_top_games = bcgamepoker
                elif(each_game_title == 'lotteryGameArea'):
                    this_top_games = bcgamelottery
                
                if(this_top_games != ''):
                    hover = ActionChains(self.driver).move_to_element(self.driver.find_element_by_id(game_hover))
                    hover.perform()
                    each_game = WebDriverWait(self.driver,self.TestInfo.short_time).until(EC.visibility_of_element_located((By.ID, each_game_title)),each_game_title+' is not visible')
                    
                    each_game_list = each_game.find_elements_by_css_selector('div[class="indpc-game-box"] a[needlogin] span')
#                     for each_game_name in each_game_list:
#                         self.res_log = WriteDebugLog(self.res_log, print_tab+each_game_name.text)
                    for (each_game_name, this_top_game) in zip(each_game_list, this_top_games.split(', ')):
                        if(each_game_name.text.replace(' ','') == this_top_game.replace('_','').replace(' ','')):
                            self.res_log = WriteDebugLog(self.res_log, print_tab+'(Web) '+each_game_name.text.replace(' ','')+' == (Admin) '+this_top_game.replace('_','').replace(' ',''))
                            result_list.append('PASS')
                        else:
                            self.res_log = WriteDebugLog(self.res_log, print_tab+'(Web) '+each_game_name.text.replace(' ','')+' != (Admin) '+this_top_game.replace('_','').replace(' ',''))
                            result_list.append('FAIL')
        except Exception as e:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'Exception: '+ str(e))
            result_list.append('FAIL')
        
        if('FAIL' in result_list or not result_list):
            self.TestResult = 'FAIL'
        else:
            self.TestResult = 'PASS'

        # [QA] Be sure to save result "PASS" or "FAIL" to self.TestResult
        # ----------------------------------------------------------------------------------------------

        self.CaseNote = WriteDebugLog(self.CaseNote, '\n\t'+'#Test Result: ' + self.TestResult)
        self.teardown()

        self.TestCaseEndTime = datetime.now()
        self.TestCaseDuration = ((self.TestCaseEndTime - self.TestCaseStartTime).total_seconds())*1000000
        if (self.TestCaseDuration == 0):
            self.TestCaseDuration = ' less than 1'
        self.TestInfo.setTestRunEndTime()
        
        self.CaseNote = WriteDebugLog(self.CaseNote, '\n\t'+datetime.today().strftime("%m???%d???%H???%M???%S???")+'<< End to [UI] BC check top games')
        # [QA] Set "collectOtherFile = True" if there is any file that should be collected
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