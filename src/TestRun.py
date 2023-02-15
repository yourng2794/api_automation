#!/usr/bin/python
#coding=utf-8
import os,shutil
import xml.etree.ElementTree as ET
from datetime import datetime
from O2oUtility import IniValue
from O2oUtility import ReplaceIniValue
from O2oUtility import ReplaceJsonValue
from O2oUtility import GetJsonValue
from O2oUtility import WriteLog

from lxml import etree
import smtplib
from email.mime.text import MIMEText 
from email.mime.multipart import MIMEMultipart
import ssl
import json
from testrail2 import APIClient
currentdir = os.path.dirname(os.path.abspath(__file__))

class TestRunning:

    def __init__(self):
        # All these are default value. Use this value if element doesn't exist in readTestConfig() within setting.ini.
        self.TestRunDuration = 0
        self.TestRunStartTime = datetime.now()
        self.TestRunEndTime = ''
        self.TestEnvironmrnt = ''
        self.TestAccount = ''
        self.TestWebstie = ''
        
        self.very_short_time = ''
        self.short_time = ''
        self.normal_time = ''
        self.long_time = ''
        self.very_long_time = ''
        
        self.FoldersToTest='' 
        self.TestResultFolder=''
        self.Log=''
        
        self.SendEmail='True'
        self.EmailTo='tommy@o2ogt.com'
        self.EmailSubject=''
        
        self.TestRailIP=''
        self.FillResultToTestRail='False'
        self.TestRailProjectID=''
        self.TestRailTestPlanID=''
        self.TestRailSuiteID=''
        self.TestRailRunID=''
        self.TestRailUser=''
        self.TestRailPWD=''
        
        self.TestRunFolder='temp'
        self.resultxml = 'testresults.xml'
        
        self.Oauth = ''
        
        self.countAll = 0
        self.countPASS = 0
        self.countFAIL = 0
        
        self.game_types = ''
        self.provider_has_games = ''
        self.provider_without_games = ''
    
    def readTestConfig(self):
        self.TestEnvironmrnt = IniValue('setting','TestEnv.environment')
        self.FoldersToTest = IniValue('setting','TestSetting.FoldersToTest')
        self.TestResultFolder = currentdir+'\\TestResults\\'
#         print(self.TestResultFolder)
        
        self.TestRailIP = IniValue('setting','TestRail.TestRailIP')
        self.FillResultToTestRail = IniValue('setting','TestRail.FillResultToTestRail')
        self.TestRailProjectID = IniValue('setting','TestRail.TestRailProjectID')
        self.TestRailTestPlanID = IniValue('setting','TestRail.TestRailTestPlanID')
        self.TestRailSuiteID = IniValue('setting','TestRail.TestRailSuiteID')
        self.TestRailUser = IniValue('setting','TestRail.TestRailUser')
        self.TestRailPWD = IniValue('setting','TestRail.TestRailPWD')
        
        self.very_short_time = int(IniValue('setting','TestSetting.very_short_time'))
        self.short_time = int(IniValue('setting','TestSetting.short_time'))
        self.normal_time = int(IniValue('setting','TestSetting.normal_time'))
        self.long_time = int(IniValue('setting','TestSetting.long_time'))
        self.very_long_time = int(IniValue('setting','TestSetting.very_long_time'))
        
        self.game_types = IniValue('setting','TestData.gametype')
        self.provider_with_games = IniValue('setting','TestData.provider_with_games')
        self.provider_without_games = IniValue('setting','TestData.provider_without_games')
        ##############################
        # Add test run into testrail #
        ##############################
        if(IniValue('setting','TestSetting.py_or_exe') == 'exe'):
#             retry = 0
#             while(retry < 2):
            try:
                ssl._create_default_https_context = ssl._create_unverified_context  
                client = APIClient(self.TestRailIP)
                client.user = self.TestRailUser
                client.password = self.TestRailPWD
                
                # 1. Create Test Run
                jsonfile_dir = os.path.dirname(os.path.abspath(__file__))+'\\JsonFiles\\add_run.json'
                replace_value = datetime.today().strftime("%b%d_%H%M")
                ReplaceJsonValue(jsonfile_dir,'name','Automation test '+replace_value)
                with open(jsonfile_dir, encoding='utf-8') as jsonfile:
                    jsonfile_src = json.load(jsonfile)
                
                add_run = client.send_post('add_run/1',jsonfile_src)
                WriteLog(add_run)
            
                # 2. Get least Test Run id and replace setting.ini
                get_runs = client.send_get('get_runs/1')
                get_run_id = GetJsonValue(json.dumps(get_runs[0]),'id')
                ReplaceIniValue('setting', 'TestRail.TestRailRunID',str(get_run_id))
                self.TestRailRunID = IniValue('setting','TestRail.TestRailRunID')
#                 break
            
            except Exception as e:
                WriteLog('(X) First TestResultsToTestRail Exception: '+str(e))
#                 finally:
#                     retry+=1
#             if(retry >= 2):
#                 WriteLog('Retry= %s, (Fail to post add_run.json)' %str(retry))
            
    def createTestRunFolder(self):
        today = datetime.today()
        self.TestRunFolder=today.strftime("%Y%m%d_%H%M%S") + "\\\\"
        
        try:
            dir2 = self.TestResultFolder+self.TestRunFolder
            if not os.path.exists(dir2):
                os.makedirs(dir2)
                WriteLog('Folder created: '+ dir2)
            else:
                WriteLog('Error: Test Results Folder '+ dir2 + ' already exists.')
                return "Error"
        except Exception as e:
            WriteLog("Exception: on creating Folder... %s" % str(e))
            return "Error"

        self.resultxml = self.TestResultFolder + self.TestRunFolder + self.resultxml 
        WriteLog('Test Result XML: '+self.resultxml )

    def setTestRunEndTime(self):
        self.TestRunEndTime = datetime.now()
        self.TestRunDuration = (self.TestRunEndTime - self.TestRunStartTime).total_seconds()
        return self.TestRunEndTime

    def collectTestRecordFiles(self):
        WriteLog('Collecting test log files...')
        # Collect related test file to TestRunFolder: iVPServerTestDebug.log, iVP server debug log, other temp files...              
        with open('TestDebug.log', 'a', encoding="utf-8") as f1:
            f = open('TestDebug2.log','r', encoding="utf-8")
            lines = f.readlines()[1:]
            for line in lines:
                f1.write(line)
        try:
            # 1. Copy xsl to result folder
            xslt_doc = etree.parse("TestReportFormat.xsl")
            xslt_transformer = etree.XSLT(xslt_doc)
            
            source_doc = etree.parse(self.resultxml)
            output_doc = xslt_transformer(source_doc)
            
            output_doc.write("result.html", pretty_print=True)
            shutil.copy("result.html", self.TestResultFolder+self.TestRunFolder)
#             output_doc.write(self.TestResultFolder+self.TestRunFolder+"result.html", pretty_print=True)

#             shutil.copy("TestReportFormat.xsl", self.TestResultFolder+self.TestRunFolder)

            #2. Copy the final iVPServerTestDebug.log
            shutil.copy("TestDebug.log", self.TestResultFolder+self.TestRunFolder)
        except Exception as e:
            WriteLog("Exception: on collectTestRecordFiles... %s" % str(e.with_traceback))


    def generateTestResults(self):
        WriteLog('Generating overall test results...')
                
        try:
            if (os.path.exists(self.resultxml)):
                xmlp = ET.XMLParser(encoding="utf-8")
                tree = ET.parse(self.resultxml,parser=xmlp)
                root = tree.getroot()
                self.countAll = len(root.findall(".//TestCase"))
                self.countPASS = len(root.findall(".//TestCase[@Result='PASS']"))
                self.countFAIL = len(root.findall(".//TestCase[@Result='FAIL']"))
                
                WriteLog('Test Case Number: ' + str(self.countAll))
                WriteLog('Test Case PASS: ' + str(self.countPASS))
                WriteLog('Test Case FAIL: ' + str(self.countFAIL))

                Info = root.find('Info')
                ExecutionCaseCount = ET.SubElement(Info, 'ExecutionCaseCount', AllCase = str(self.countAll))
                CountPASS = ET.SubElement(ExecutionCaseCount, 'CountPASS')
                CountPASS.text = str(self.countPASS)
                CountFAIL = ET.SubElement(ExecutionCaseCount, 'CountFAIL')
                CountFAIL.text = str(self.countFAIL)
                # http://10.10.208.139/index.php?/runs/view/{testrun_id}
                TestRail = ET.SubElement(Info, 'TestRail')
                TestRail.text = str(self.TestRailIP)+'index.php?/runs/view/'+str(self.TestRailRunID)
                
                tree.write(self.resultxml , encoding='utf-8', xml_declaration=True)

                # 2
                f = open(self.resultxml , 'r')
#                 lines = f.readlines()
                f.close()
#                 lines.insert(1, '<?xml-stylesheet type="text/xsl" href=".\TestReportFormat.xsl"?>\n')
#                 fw = open(self.resultxml , 'w', encoding = 'utf-8')
#                 fw.write(''.join(lines))
#                 fw.close()

            else:
                WriteLog("Fail to find test result xml file: " + self.resultxml )
        except Exception as e:
            WriteLog("Exception: on process test result XML... %s" % str(e.with_traceback))


    def sendTestResults(self):
        # If EmailTo is not empty, send test results to the email addresses
        if ((self.EmailTo == '') or (self.SendEmail =='False')):
            WriteLog('No need to send email.')
        else:
            WriteLog('Prepare to send test results by email...')
            sender = IniValue('setting', 'MAIL.From') # 设置发件邮箱，一定要自己注册的邮箱
            receiver = IniValue('setting', 'MAIL.To').replace(" ","").split(',') # 设置邮件接收人，可以是扣扣邮箱
            gmail_user = IniValue('setting', 'MAIL.User')
            gmail_pwd = IniValue('setting', 'MAIL.Pwd')
            smtpserver = smtplib.SMTP("smtp.gmail.com",587)
            smtpserver.ehlo()
            smtpserver.starttls()
            smtpserver.ehlo()
            
            with open("result.html", "r", encoding='utf-8') as f:
                text= f.read()
                
            body = text # 设置邮件正文，这里是支持HTML的
            msg = MIMEMultipart()
            msg.attach(MIMEText(body, 'html')) # 设置正文为符合邮件格式的HTML内容
            msg['subject'] = IniValue('setting', 'HEADER.Subject') # 设置邮件标题
            msg['from'] = sender  # 设置发送人
            msg['to'] = ",".join(receiver)  # 设置接收人
            
            # 构造附件1，传送当前目录下的 test.txt 文件
#             for f in files or []:
#                 with open(f, "rb") as fil:
#                     part = MIMEApplication(
#                         fil.read(),
#                         Name=basename(f)
#                     )
#                 # After the file is closed
#                 part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
#                 msg.attach(part)
                
            att1 = MIMEText(open('TestDebug.log', 'rb').read(), 'base64', 'utf-8')
            att1["Content-Type"] = 'application/octet-stream'
            # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
            att1["Content-Disposition"] = 'attachment; filename="TestDebug.log"'
            msg.attach(att1)
            
            try:
                smtpserver.login(gmail_user, gmail_pwd)  # 登陆邮箱
                smtpserver.sendmail(sender, receiver, msg.as_string())  # 发送邮件！                
                WriteLog('\t'+'Success to send email.')
                #記得要登出
                smtpserver.quit()
                
            except smtplib.SMTPException as e:
                WriteLog("Exception: on sendTestResults... %s" % str(e.with_traceback))