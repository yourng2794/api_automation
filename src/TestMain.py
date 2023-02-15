#!/usr/bin/python
#coding=utf-8
import logging, sys, os, shutil, ssl, json, time
from datetime import datetime
from O2oUtility import IniValue
from O2oUtility import ReplaceIniValue
from O2oUtility import GetJsonValue
from O2oUtility import ReplaceJsonValue
from O2oUtility import WriteLog
from TestRun import TestRunning
from testrail2 import APIClient

class Testing:

    def __init__(self, BVT):
#         if (BVT == False):
        self.cleanLog()
#         logging.debug()< logging.info()< logging.warning()< logging.error()< logging.critical()
        root_logger= logging.getLogger()
        root_logger.setLevel(logging.INFO) # or whatever
        handler = logging.FileHandler(os.path.dirname(os.path.abspath(__file__))+'\\TestDebug2.log', 'w', 'utf-8') # or whatever
        handler.setFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s') # or whatever
        root_logger.addHandler(handler)
        open('TestDebug.log', 'w')
#         logging.basicConfig(filename=os.path.dirname(os.path.abspath(__file__))+'\\TestDebug.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
        WriteLog('------------------------ Test Tool is running------------------------')
#         self.isBVT = BVT
#         self.MyTest = None
        
        #-------------Setup steps for whole test run: ----------------------------
        self.readTestConfig()
        
        ##############################
        # Add test run into testrail #
        ##############################
        if(IniValue('setting','TestSetting.py_or_exe') == 'py'):
#             retry = 0
#             while(retry < 2):
            try:
                ssl._create_default_https_context = ssl._create_unverified_context  
                client = APIClient(self.MyTest.TestRailIP)
                client.user = self.MyTest.TestRailUser
                client.password = self.MyTest.TestRailPWD
                 
                # 1. Create Test Run
                jsonfile_dir = os.path.dirname(os.path.abspath(__file__))+'\\JsonFiles\\add_run.json'
                replace_value = datetime.today().strftime("%b%d_%H%M")
                TestReport = IniValue('setting','HEADER.subject')
                ReplaceJsonValue(jsonfile_dir,'name',TestReport+' '+replace_value)
                with open(jsonfile_dir, encoding='utf-8') as jsonfile:
                    jsonfile_src = json.load(jsonfile)
                 
                add_run = client.send_post('add_run/1',jsonfile_src)
                WriteLog(add_run)
             
                # 2. Get least Test Run id and replace setting.ini
                get_runs = client.send_get('get_runs/1')
                get_run_id = GetJsonValue(json.dumps(get_runs[0]),'id')
                ReplaceIniValue('setting', 'TestRail.TestRailRunID',str(get_run_id))
                self.MyTest.TestRailRunID = IniValue('setting','TestRail.TestRailRunID')
#                 break
             
            except Exception as e:
                WriteLog('(X) First TestResultsToTestRail Exception: '+str(e))
#             finally:
#                 retry+=1
#             if(retry >= 2):
#                 WriteLog('Retry= %s, (Fail to post add_run.json)' %str(retry))
            
    def readTestConfig(self):
#         WriteLog('>> readTestConfig')
        # read iVPServerTestConfig.ini:
        
        try:
            self.MyTest = TestRunning()
            self.MyTest.readTestConfig()
            
            if (self.MyTest.createTestRunFolder() == 'Error'):
                WriteLog("Test Tool will exit...")
                if (self.isBVT):
                    self.copyToolDebugLog()
                os._exit(1)
        except Exception as e:  
            WriteLog("Exception: on readTestConfig or creating Test Run Folder... %s" % str(e))
            if (self.isBVT):
                self.copyToolDebugLog()
            os._exit(1)
            
            
    def runModule(self, module):
        WriteLog('>> Enter Test Suites: ' + module)
        f = None
        f2 = None
        files = []
        try:
            time.sleep(0.5)
            #find every file under module
            file_path = os.path.dirname(os.path.abspath(__file__)) +'\\TestSuites\\'+ module
            if not os.path.exists(file_path):
                WriteLog('Module folder path does not Exist!! --> ' + file_path) 
                return
            
            for f in os.listdir(file_path):
                if f.endswith(".py") and (f != "__init__.py") and (not f.startswith("X_")):  # Do Not run __init__.py and the test case marked with "X_"
                    files.append(f)
                    WriteLog('\t'+'find test case: ' + f )
        
        except Exception as e:
            WriteLog('Exception: on "runModule_folder"... %s' % str(e))
            
        for f2 in files:
#             retry = 0
#             while(retry <2):
            try:
                importstring = 'from TestSuites.' + module + '.' + os.path.splitext(f2)[0] + ' import TestCase'
                exec(importstring)
                time.sleep(0.5)
                WriteLog('\n\n'+'* Run test case: ' + f2)
                execstring = 'Case = TestCase(self.MyTest)'
                exec(execstring)
                time.sleep(0.5)
                exec('Case.run(False)')
                time.sleep(0.5)
                                        
                with open('TestDebug.log', 'a', encoding="utf-8") as f1:
                    f = open('TestDebug2.log','r', encoding="utf-8")
                    lines = f.readlines()[1:]
                    for line in lines:
                        f1.write(line)
#                         for line in open('TestDebug2.log', 'r', encoding="utf-8"):
#                             f1.write(line.readlines()[1:])
#                 break
            except Exception as e:
#                 if(retry == 0):
#                     WriteLog('Retry again')
                WriteLog('Exception: on "runModule_import"... %s' % str(e))
#                 retry += 1
            finally:
                open('TestDebug2.log', 'w')
                        
#             if(retry >=2):
#                 WriteLog('Exception: on "each test case import fail" ... %s' % str(e))
        
        WriteLog('\n'+'<< End Test Suites: ' + module)
        WriteLog('----------------------------------------------------------------'+'\n')
        
        
    def teardownAll(self):
        # Tear down the environment if it needs
        WriteLog('>> Tear Down for whole test run...')
        WriteLog('<< End of Tear Down for whole test run')
        
        
    @staticmethod
    def cleanLog():
        # Clear Test Tool Debug Log
        f = open(os.path.dirname(os.path.abspath(__file__))+"\\TestDebug.log", "w")
        f.flush()
        f.close()
        
        f = open(os.path.dirname(os.path.abspath(__file__))+"\\result.html", "w")
        f.flush()
        f.close()
        
        
    @staticmethod
    def copyToolDebugLog():
        # Used in BVT scenario. When os._exit(1), still copy iVPServerTestDebug.log to result folder
#         WriteLog("Copy TestDebug.log to TestResults folder")
        shutil.copy2(os.path.dirname(os.path.abspath(__file__))+"\\TestDebug.log", os.path.dirname(os.path.abspath(__file__)) + "\\TestResults\\")
        
        
    def runMain(self):
        WriteLog('------------------------ Test is started------------------------')
        
        WriteLog('Set up Pre-condition of this case...')
        
#         WriteLog('*** Start to run Test Suites')  
        try:              
            #Start to run test cases according to ini
            #Run all modules: loop each module
            features = []
            features = self.MyTest.FoldersToTest.split(',')

            #Add basic install and uninstall to module list
#             features = ['ServerInstall_Basic']+ features
#             if (self.MyTest.UninstalliVPServerAfterTest == 'True'):
#                 features = features + ['ServerUninstall_Basic']
#             else:
#                 WriteLog('note: According to iVPServerTestConfig.ini, Test Tool will not uninstall your iVP server after all test cases are executed.')

            for feature in features:
                feature = feature.replace(" ", "")
#                 WriteLog('* Pick Test Folder: ' + feature)

                dir2 = self.MyTest.TestResultFolder+self.MyTest.TestRunFolder+feature
                if not os.path.exists(dir2):
                    os.makedirs(dir2)
                self.runModule(feature)

        except Exception as e:
            WriteLog("Exception: error when a module is selected to run... %s" % str(e.with_traceback))
            WriteLog("Feature = "+feature) 
        finally:
            WriteLog('------------------------Test is finished------------------------')
        
        self.teardownAll()
        self.MyTest.setTestRunEndTime()
        self.MyTest.generateTestResults()
        self.MyTest.collectTestRecordFiles()
        self.MyTest.sendTestResults()
        
if __name__ == "__main__":
    
    WriteLog("Test Tool is running...")
    test = Testing(False)
    test.runMain()
    
    WriteLog("Exit Test Tool")
    sys.exit(0)
