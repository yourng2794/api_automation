#!/usr/bin/python
#coding=utf-8
import os, sys
import locale
import logging
import inspect
import shutil
import json
from datetime import datetime

from TestRun import TestRunning
from BaseTestCase import BaseCase
from O2oUtility import WriteLog
from O2oUtility import WriteDebugLog
from O2oUtility import ApiResponse
from O2oUtility import ReplaceIniValue
from O2oUtility import IniValue

locale.setlocale(locale.LC_CTYPE, 'chinese')
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
tooldir = os.path.dirname(os.path.dirname(currentdir))
if tooldir not in sys.path:
    sys.path.insert(0, tooldir)

class TestCase(BaseCase):
    
    def __init__(self,MyTest):
        # ---------------- [QA] Modify these variables for your test case! ----------------------------------       
        self.Feature= currentdir.split('\\')[-1]
        self.CaseTitle= '[Feature] API POST partner type info'
        self.CaseNote= ''
        self.TestCaseID= '158'
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
        result_list2 = []
        self.res_log = WriteDebugLog(self.res_log, '\n\tStart >>'+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST partner type info'+'\n')
        print_tab = '\n\t\t'
        try:
            partnerId = IniValue('setting', 'API.partnerid')
            bankerTypeId = IniValue('setting', 'API.bankertypeid')
            ReplaceIniValue('admin_partner_type_info', 'API.ptTypeId', bankerTypeId)
            ReplaceIniValue('admin_partner_type_info', 'API.ptParentId', partnerId)
            return_value, response_time, response_data, self.res_log = ApiResponse(print_tab, self.res_log, 'admin_partner_type_info', False, False)
            WriteLog(print_tab+'Response data: '+ response_data)
            if(return_value):
                result_list.append('PASS')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API success (status and response are correct).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                json_permission = json_response.get('permission')
                json_currency = json_permission.get('currency')
                json_currency.update(json_permission.get('v_currency'))
                
                json_provider = json_permission.get('pro_e')
                json_provider.update(json_permission.get('pro_s'))
                json_provider.update(json_permission.get('pro_t'))
                json_provider.update(json_permission.get('pro_v'))
                
                json_stopbet = json_permission.get('sb_e')
                json_stopbet.update(json_permission.get('sb_s'))
                json_stopbet.update(json_permission.get('sb_t'))
                json_stopbet.update(json_permission.get('sb_v'))
                
                json_payment = json_permission.get('payment')
                json_handicap = json_permission.get('hc_s')
                
                pt = json_permission.get('pt_acc_status')
                pt.update(json_permission.get('pt_del'))
                pt.update(json_permission.get('pt_export'))
                pt.update(json_permission.get('pt_management'))
                pt.update(json_permission.get('pt_name'))
                pt.update(json_permission.get('pt_player_level'))
                
                pyd = json_permission.get('pyd_display')
                pyd.update(json_permission.get('pyd_maintain'))
                
                pyf = json_permission.get('pyf_cash')
                pyf.update(json_permission.get('pyf_detail_set'))
                pyf.update(json_permission.get('pyf_edit'))
                pyf.update(json_permission.get('pyf_edit_pwd'))
                pyf.update(json_permission.get('pyf_handi_set'))
                pyf.update(json_permission.get('pyf_op_record'))
                pyf.update(json_permission.get('pyf_player_info'))
                pyf.update(json_permission.get('pyf_stop_set'))
                
                og = json_permission.get('og')
                op = json_permission.get('op')
                ot = json_permission.get('ot')
                ws = json_permission.get('ws')
                pd = json_permission.get('pd')
                json_permission_final = {}
                json_permission_final['og'] = og
                json_permission_final['op'] = op
                json_permission_final['ot'] = ot
                json_permission_final['pd'] = pd
                json_permission_final['pt'] = pt
                json_permission_final['pyd'] = pyd
                json_permission_final['pyf'] = pyf
                json_permission_final['ws'] = ws
                
                ReplaceIniValue('admin_partner_create', 'API.currency', str(json_currency).replace("'",'"').replace(' ',''))
                ReplaceIniValue('admin_partner_create', 'API.provider', str(json_provider).replace("'",'"').replace(' ',''))
                ReplaceIniValue('admin_partner_create', 'API.stopbet', str(json_stopbet).replace("'",'"').replace(' ',''))
                ReplaceIniValue('admin_partner_create', 'API.payment', str(json_payment).replace("'",'"').replace(' ',''))
                ReplaceIniValue('admin_partner_create', 'API.handicap', str(json_handicap).replace("'",'"').replace(' ',''))
                ReplaceIniValue('admin_partner_create', 'API.permission', str(json_permission_final).replace("'",'"').replace(' ',''))
                result_list.append('PASS')
                ReplaceIniValue('admin_partner_edit', 'API.currency', str(json_currency).replace("'",'"').replace(' ',''))
                ReplaceIniValue('admin_partner_edit', 'API.provider', str(json_provider).replace("'",'"').replace(' ',''))
                ReplaceIniValue('admin_partner_edit', 'API.stopbet', str(json_stopbet).replace("'",'"').replace(' ',''))
                ReplaceIniValue('admin_partner_edit', 'API.payment', str(json_payment).replace("'",'"').replace(' ',''))
                ReplaceIniValue('admin_partner_edit', 'API.handicap', str(json_handicap).replace("'",'"').replace(' ',''))
                ReplaceIniValue('admin_partner_edit', 'API.permission', str(json_permission_final).replace("'",'"').replace(' ',''))
                result_list.append('PASS')
                ReplaceIniValue('admin_partner_type_create', 'API.currency', str(json_currency).replace("'",'"').replace(' ',''))
                ReplaceIniValue('admin_partner_type_create', 'API.provider', str(json_provider).replace("'",'"').replace(' ',''))
                ReplaceIniValue('admin_partner_type_create', 'API.stopbet', str(json_stopbet).replace("'",'"').replace(' ',''))
                ReplaceIniValue('admin_partner_type_create', 'API.payment', str(json_payment).replace("'",'"').replace(' ',''))
                ReplaceIniValue('admin_partner_type_create', 'API.handicap', str(json_handicap).replace("'",'"').replace(' ',''))
                ReplaceIniValue('admin_partner_type_create', 'API.permission', str(json_permission_final).replace("'",'"').replace(' ',''))
                result_list.append('PASS')
                ReplaceIniValue('admin_partner_type_edit', 'API.currency', str(json_currency).replace("'",'"').replace(' ',''))
                ReplaceIniValue('admin_partner_type_edit', 'API.provider', str(json_provider).replace("'",'"').replace(' ',''))
                ReplaceIniValue('admin_partner_type_edit', 'API.stopbet', str(json_stopbet).replace("'",'"').replace(' ',''))
                ReplaceIniValue('admin_partner_type_edit', 'API.payment', str(json_payment).replace("'",'"').replace(' ',''))
                ReplaceIniValue('admin_partner_type_edit', 'API.handicap', str(json_handicap).replace("'",'"').replace(' ',''))
                ReplaceIniValue('admin_partner_type_edit', 'API.permission', str(json_permission_final).replace("'",'"').replace(' ',''))
                result_list.append('PASS')
                current_user = IniValue('setting', 'API.agentacc2')
                if(json_response.get('parent_acc') == current_user):
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Success get parent_banker_acc: '+current_user)
                    result_list2.append('PASS')
                else:
                    self.res_log = WriteDebugLog(self.res_log, print_tab+'- Fail get parent_banker_acc: '+json_response.get('parent_acc')+' != '+current_user)
                    result_list2.append('FAIL')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
                
            else:
                result_list.append('FAIL')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'- API fail (status or response is incorrect).')
                self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
        
        except Exception as e:
            result_list.append('FAIL')
            self.res_log = WriteDebugLog(self.res_log, print_tab+'- Exception: on admin_partner_type_info... %s' % str(e))
        
        finally:
            self.res_log = WriteDebugLog(self.res_log, print_tab+'---')
            
        WriteLog(result_list)
        WriteLog(result_list2)
        if('FAIL' in str(result_list) or not result_list):
            self.TestResult = 'FAIL'
        else:
            if('FAIL' in str(result_list2) or not result_list2):
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
        self.res_log = WriteDebugLog(self.res_log, '\n\n\tEnd << '+datetime.today().strftime("%m月%d日%H時%M分%S秒")+' [Feature] API POST partner type info')
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