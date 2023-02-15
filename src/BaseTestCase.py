#!/usr/bin/python
#coding=utf-8
import os,io,shutil, ssl, json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from O2oUtility import ReplaceJsonValue, IniValue
from O2oUtility import WriteLog
from testrail2 import APIClient

class BaseCase:

    def __init__(self):
        self.Feature= ''
        self.CaseTitle= ''
        self.CaseDescription= ''
        self.TestCaseID= ''
        self.TestResult = ''
        self.ResultFolder= ''       
        self.TestInfo = ''        
        self.TestCaseStartTime = datetime.now()
        self.TestCaseEndTime = ''   
        self.TestCaseDuration = 0
        self.CurrentFile =''
    
    def writeXML(self):

        WriteLog('\t'+'>> Start write XML')

        firstcase = True
        
        try:
            if (os.path.exists(self.TestInfo.resultxml)):                
                firstcase = False
            else:
                f = io.open(self.TestInfo.resultxml, 'w', encoding = 'utf-8')
        except Exception as e:            
            WriteLog('\t'+'Exception: on io.open test result XML... %s' % str(e.with_traceback))
            
        # Create XML element when executing the first test case
        if (firstcase):
            root = ET.Element('TestRunning')
            tree = ET.ElementTree(root)
            Info = ET.SubElement(root, 'Info')
            GameProvider = ET.SubElement(root, 'GameProvider')
            GameProviderStatus = ET.SubElement(root, 'GameProviderStatus')
            TestResults = ET.SubElement(root, 'TestResults')
            # Write Info
            TestEnvironment =  ET.SubElement(Info, 'TestEnvironment')
            TestEnvironment.text = self.TestInfo.TestEnvironmrnt
#             TestWebstie =  ET.SubElement(Info, 'TestWebstie')
#             TestWebstie.text = self.TestInfo.TestWebstie
#             TestAccount = ET.SubElement(Info, 'TestAccount')
#             TestAccount.text = self.TestInfo.TestAccount
            ExecutionDate = ET.SubElement(Info, 'ExecutionDate')
            ExecutionDate.text = self.TestInfo.TestRunStartTime.strftime("%Y-%m-%d %H:%M:%S")
            TestRunDuration = ET.SubElement(Info, 'TestRunDuration', StartTime = self.TestInfo.TestRunStartTime.strftime("%Y-%m-%d %H:%M:%S"), EndTime= self.TestInfo.TestRunEndTime.strftime("%Y-%m-%d %H:%M:%S"))
            #TestRunDuration.text = str(self.TestInfo.TestRunDuration) + ' second(s)'
            TestRunDuration.text = str(timedelta(seconds=int(self.TestInfo.TestRunDuration))) + ' (h:m:s)'
            
            # Write Game Provider
            gameTypes = self.TestInfo.game_types
            for gameType in gameTypes.split(', '):
                gameType_element = ET.SubElement(GameProvider, gameType.upper())
                gameType_element.text = IniValue('setting', 'GameType.'+gameType)
            GameOpen = ET.SubElement(GameProviderStatus, 'GameOpen')
            GameOpen.text = self.TestInfo.provider_with_games
            GameClose = ET.SubElement(GameProviderStatus, 'GameClose')
            GameClose.text = self.TestInfo.provider_without_games
            
            
        # Update XML element when executing 2nd and the later test cases
        else:
            try:
                xmlp = ET.XMLParser(encoding="utf-8")
                tree = ET.parse(self.TestInfo.resultxml,parser=xmlp)
                root = tree.getroot()
                Info = root.find('Info')
                TestResults = root.find('TestResults')
                # Update TestRunning Info
                TestRunDuration = Info.find('TestRunDuration')
                TestRunDuration.set('EndTime', self.TestInfo.TestRunEndTime.strftime("%Y-%m-%d %H:%M:%S"))
                #TestRunDuration.text = str(self.TestInfo.TestRunDuration) + '  second(s)'
                TestRunDuration.text = str(timedelta(seconds=int(self.TestInfo.TestRunDuration))) + ' (h:m:s)'
            except Exception as e:
                WriteLog('\t'+'Exception: on XMLParser... %s' % str(e))

        # Create Elements to record Test Results
        TestFeature = TestResults.find("./TestFeature[@Folder='"+self.Feature+"']")
        if (TestFeature == None):
            TestFeature = ET.SubElement(TestResults, 'TestFeature', Folder= self.Feature)
            
        TestCase = ET.SubElement(TestFeature, 'TestCase', File = self.CurrentFile , Title = self.CaseTitle, Result = self.TestResult, TestCaseID = self.TestCaseID)        
#         CaseNote = ET.SubElement(TestCase, 'CaseNote')
#         CaseNote.text = self.CaseNote
#         CaseNote.text = 'RAT'
        ExecutionTime = ET.SubElement(TestCase,'ExecutionTime')
        # If execution time < 1 sec, print 0.XX (sec). otherwise print (hh:mm:ss)
        if (self.TestCaseDuration < 1000000.0):
            ExecutionTime.text = '0.'+ str(self.TestCaseDuration)[:2]+ ' (sec)'
        else:
            ExecutionTime.text = str(timedelta(microseconds=int(self.TestCaseDuration))).split('.')[0] + ' (h:m:s)'

        def convert(times):
            time = float(times)
            temp = time / 1000000
            hr = temp / 3600
            temp = temp % 3600
            secs = temp % 60
            mins = temp / 60
            return (str(int(hr))+':'+str(int(mins))+':'+str(int(secs))+' (h:m:s)')
        # Write XML 
        try:
            if (firstcase):
                tree.write(f, encoding='unicode', method='xml', xml_declaration=True)
                f.close()
            else:
                tree.write(self.TestInfo.resultxml, encoding='utf-8', method='xml', xml_declaration=True)
            WriteLog('\t\t'+'Test result is saved.')
        except Exception as e:
            WriteLog('\t\t'+'Exception: on creating test result in XML... %s' % str(e.with_traceback))
            if (f is not None):
                f.close()
        finally:
            WriteLog('\t'+'<< End write XML')


    def copyTestToolLog(self):
        WriteLog('\t'+'>> Start collect TestDebug.log to Test Run Folder')
        currentdir = os.path.dirname(os.path.abspath(__file__))
        with open('TestDebug3.log', 'w', encoding="utf-8") as f1:
            f = open(currentdir+'\\TestDebug2.log','r', encoding="utf-8")
            lines = f.readlines()[1:]
            for line in lines:
                f1.write(line)
        try:
            shutil.copy("TestDebug3.log", self.TestInfo.TestResultFolder+self.TestInfo.TestRunFolder+self.Feature)
            os.rename(self.TestInfo.TestResultFolder+self.TestInfo.TestRunFolder+self.Feature+"\\"+"TestDebug3.log" , self.TestInfo.TestResultFolder+self.TestInfo.TestRunFolder+self.Feature+"\\"+(str(self.CurrentFile)[:-3]+"_TestDebug.log"))
        except Exception as e:
            WriteLog('\t'+'Exception: on copyTestToolLog... %s' % str(e.with_traceback))
        finally:
            WriteLog('\t'+'<< End collect TestDebug.log to Test Run Folder')
#             open('TestDebug2.log', 'w')
# 
# 
#     def copyServerLog(self):
#         WriteLog('>> Collect  Server Log...')
#         try:
#             if os.path.exists(self.TestInfo.ServerLog):
#                 shutil.copy(self.TestInfo.ServerLog , self.TestInfo.TestResultFolder+self.TestInfo.TestRunFolder+self.Feature)
#                 serverLog = self.TestInfo.ServerLog.split("\\")[-1]
#                 os.rename(self.TestInfo.TestResultFolder+self.TestInfo.TestRunFolder+self.Feature+"\\"+serverLog , self.TestInfo.TestResultFolder+self.TestInfo.TestRunFolder+self.Feature+"\\"+self.CurrentFile+"_"+serverLog)
#             else:
#                 WriteLog(" server log (" + self.TestInfo.ServerLog + ") does not exist. Will not collect this file for this case.")
#         except Exception as e:
#             WriteLog("Exception: on ServerLog... %s" % str(e.with_traceback))
#         WriteLog('<< End Collect Server Log')

    def fillTestResultsToTestRail(self):
        # If FillResultToTestRail=True, fill Test Results to TestRail
        
        if (self.TestInfo.FillResultToTestRail == 'True'):
            WriteLog('\t'+'>> Start write to TestRail')
#             retry = 0
#             while(retry <2):
            try:
                ssl._create_default_https_context = ssl._create_unverified_context
                client = APIClient(self.TestInfo.TestRailIP)
                client.user = self.TestInfo.TestRailUser
                client.password = self.TestInfo.TestRailPWD
                build_version = datetime.today().strftime("%b%d_%H%M")
                elapsed = timedelta(microseconds=int(self.TestCaseDuration)).total_seconds()
                testresult = self.TestResult
                case_id = self.TestCaseID
                jsonfile_dir = self.TestInfo.TestResultFolder+'\\..\\JsonFiles\\result.json'
#                     case_note = self.CaseNote
                case_note = self.CaseNote.replace('\t','').replace('subGame: ','\n').replace('Game:','\nGame:')
                # 1. Get least Test Run id
#                     get_runs = client.send_get('get_runs/1')
#                     get_run_id = TestUtility.getJSONValue(json.dumps(get_runs[0]),'id')
#                     TestUtility.replaceiniValue('setting', 'TestRail.TestRailRunID',str(get_run_id))
                get_running_id = self.TestInfo.TestRailRunID
                
                # 2. Replace value of "status_id" , "elapsed" , "version"
                # status_id= 1: Passed, 2: Blocked, 3: Untested (not allowed when adding a result), 4: Retest, 5: Failed
                if(testresult == 'FAIL'):
                    ReplaceJsonValue(jsonfile_dir,'status_id','5', True)
                    ReplaceJsonValue(jsonfile_dir,'comment',case_note, True)
                if(testresult == 'PASS'):
                    ReplaceJsonValue(jsonfile_dir,'status_id','1', True)
                    ReplaceJsonValue(jsonfile_dir,'comment',case_note, True)
                if(str(elapsed).split('.')[0] == '0'):
                    ReplaceJsonValue(jsonfile_dir,'elapsed','1s', True)
                else:
                    ReplaceJsonValue(jsonfile_dir,'elapsed',str(elapsed).split('.')[0]+'s', True)
                ReplaceJsonValue(jsonfile_dir,'version',"Web build "+build_version, True)
                
                # 3. Post test result into each test case
                with open(jsonfile_dir, encoding='utf-8') as jsonfile:
                    inject_result = json.load(jsonfile)
                    
                client.send_post('add_result_for_case/'+str(get_running_id)+'/'+str(case_id), inject_result)
#                     add_result_for_case = client.send_post('add_result_for_case/'+str(get_run_id)+'/'+str(case_id), inject_result)
#                     WriteLog('Result to testrail: '+str(add_result_for_case))
#                 break
            except Exception as e:
                WriteLog('(X) fillTestResultsToTestRail Exception: '+str(e))
#                 retry += 1
            WriteLog('\t'+'<< End write to TestRail')

            
    def generateResults(self):
        WriteLog('\t'+'Generate test result of this case:')

        # Write XML
        # Server log
        # Tool Debug log
        self.writeXML()
        self.fillTestResultsToTestRail()
#         self.copyServerLog()
        self.copyTestToolLog()