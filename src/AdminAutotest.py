#!/usr/bin/python
#coding=utf-8
import os
import locale
import logging
import inspect
import shutil
import json
from datetime import datetime
from datetime import timedelta
from base64 import b64decode

from TestRun import TestRunning
from BaseTestCase import BaseCase
from O2oUtility import WriteLog, WriteDebugLog, ReplaceIniValue, ApiResponse, DeleteFile, ApiCodeDetect
from O2oUtility import IniValue

class AdminAutotest():
    def __init__(self, res_log, feature, permission):
        # ex: feature = Login, Logout, Profile, ...
        # ex: permission = Boss, Banker, WebMaster, Agent
        self.res_log = res_log
        self.feature = feature
        self.permission = permission
    
    #=======================================================================
    # Current time increase operation.
    # Usage: 
    # a = datetime.now().time() # 09:11:55.775695
    # b = Add_Seconds(a, 300) # 09:16:55
    #=======================================================================
    def Add_Seconds(self, tm, secs):
        fulldate = datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
        fulldate = fulldate + timedelta(seconds=secs)
        return fulldate.time()
    
    if(self.feature == 'Login'):
        print_tab = '\n\t\t'
        retry = 0
        while(retry < 10):
            try:
                ReplaceIniValue('admin_login_code', 'API.api_path', 'login/code')
                return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_login_code', False, True)
                WriteLog(print_tab+'Response data: '+ response_data)
                imgdata = b64decode(response_data)
                with open(filename, 'wb') as decode_response_data:
                    decode_response_data.write(imgdata)
                    expired_time = Add_Seconds(datetime.now().time(), 60)
                    res_log = WriteDebugLog(res_log, print_tab+'- Session expired until: '+ str(expired_time))
                    
                if(return_value):
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                    res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                    res_log = WriteDebugLog(res_log, print_tab+'---')
                    
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                    res_log = WriteDebugLog(res_log, print_tab+'---')
                
                new_code, res_log = ApiCodeDetect(print_tab, res_log, filename)
                WriteLog('New code: '+new_code)
    #                 input(print_tab+'- Please enter code (4 digits): ')
                acc = IniValue('setting', 'TestData.admin_boss_acc')
                pwd = IniValue('setting', 'TestData.admin_boss_pwd')
                ReplaceIniValue('admin_login', 'API.code', new_code)
                ReplaceIniValue('admin_login', 'API.acc', acc)
                ReplaceIniValue('admin_login', 'API.pwd', pwd)
                return_value2, response_time2, response_data2, res_log = ApiResponse(print_tab, res_log, 'admin_login', True, True)
                WriteLog(print_tab+'Response data: '+ response_data2)
                json_response = json.loads(response_data2)
                if(return_value2):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                    res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time2)
                    res_log = WriteDebugLog(res_log, print_tab+'---')
                    break
                    
                elif(json_response.get('Error_code')=='E06' or json_response.get('Error_code')=='E08'):
    #                     result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- API fail: '+json_response.get('Error_message'))
                    res_log = WriteDebugLog(res_log, print_tab+'---')
                    continue
                    
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- API fail: '+json_response.get('Error_message'))
                    res_log = WriteDebugLog(res_log, print_tab+'---')
                    break
                    
            except Exception as e:
                result_list2.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_login... %s' % str(e))
                
            finally:
                retry += 1
                res_log = WriteDebugLog(res_log, print_tab+'- - - ')