#!/usr/bin/python
#coding=utf-8
import os
import locale
import logging
import configparser
import requests
import pickle
import json
from collections import OrderedDict
import hmac
import hashlib
import shutil
import random
from bs4 import BeautifulSoup

from datetime import datetime, timedelta
from base64 import b64decode

# for image parse
import operator
from PIL import Image, ImageFilter, ImageDraw
import cv2
import queue
import numpy as np
#===============================================================================
# O2O Utility
# Used by: 
# 1. Test tool can import this file and call the functions here
# 2. Command Line trigger and pass commands for one of these functions: >>> python O2oUtility.py 
#===============================================================================
# config = configparser.ConfigParser()
currentdir = os.path.dirname(os.path.abspath(__file__))
ErrorSnapShot_path = currentdir+'\\ErrorSnapShot\\'
compare_path = currentdir+'\\compare'
locale.setlocale(locale.LC_CTYPE, 'chinese')
result_list = []
result_list2 = []
print_tab = '\n\t\t'
#===============================================================================
# Debug Log Function
# Input: debug_log
# Output: Record log in log_file
# Created by Tommy_Han 2016/12/6
#===============================================================================
def WriteLog (input_log):
#     print(input_log)
    print(input_log)
    logging.info(input_log)

def WriteDebugLog (res_log, input_log):
    print(input_log)
    logging.info(input_log)
    res_log = res_log+ input_log
    return res_log

#===============================================================================
# Delete file or folder while exist
# Input: Path
# Output: Boolean True / False
# Created by Tommy_Han 2016/12/6
#===============================================================================
def DeleteFile(path_A):
    #WriteLog('\t'+'>> START delete: '+path_A)
    try:
        if CheckFileExist(path_A):
            #WriteLog('\t\t'+'File is exist!')
            os.remove(path_A)
            if(not CheckFileExist(path_A)):
                #WriteLog('\t'+path_A+" delete success.")
                #WriteLog('\t'+'<< END Success, delete')
                return True
            else:
                #WriteLog('\t'+'<< END Fail, delete')
                return False
        elif(CheckFolderExist(path_A)):
            #WriteLog('\t\t'+'Folder is exist!')
            shutil.rmtree(path_A)
            if(not CheckFileExist(path_A)):
                #WriteLog('\t'+path_A+" delete success.")
                #WriteLog('\t'+'<< END Success, delete')
                return True
            else:
                #WriteLog('\t'+'<< END Fail, delete')
                return False
        else:
            WriteLog("\t\t"+"File/Folder is not exist.")
            #WriteLog('\t'+'<< END delete')
            WriteLog('\t'+'<< END Fail, delete')
            return False
    except Exception as e:
        WriteLog('(X) delete Exception: ' + str(e))
        return False

def CheckFileExist(path):
    #WriteLog('\t'+'>> START CheckFileExist')
    try:
        if os.path.isfile(path):
            #WriteLog('\t'+'<< END CheckFileExist: File exist')
            return True
        else:
            #WriteLog('\t'+'<< END CheckFileExist: No File exist')
            return False
    except Exception as e:
        WriteLog('(X) CheckFileExist Exception: ' + str(e))
        return False

def CheckFolderExist(path):
    #WriteLog('\t'+'>> START CheckFolderExist')
    try:
        if os.path.isdir(path):
            #WriteLog('\t'+'<< END CheckFolderExist: File exist')
            return True
        else:
            #WriteLog('\t'+'<< END CheckFolderExist: No File exist')
            return False
    except Exception as e:
        WriteLog('(X) CheckFolderExist Exception: ' + str(e))
        return False

#===============================================================================
# Parse ini Function
# Input: ini_FileName, key
# Output: String 'value'
# ex: ini_FileName = IniValue "settings" "OSCE.InstallationDir"
# Created by Tommy_Han 2017/4/24
# Last update by Tomme 2018/07/13
#===============================================================================
def IniValue (ini_FileName, key):
    config = configparser.ConfigParser()
    try:
        config.read(currentdir+'\\ini\\%s.ini' %ini_FileName, encoding='UTF-8')
        if (config.has_section(key.split('.')[0]) == False):
            WriteLog('\t'+'No [%s] in ini_file' %(key.split('.')[0]))
            WriteLog('False')
        
        value = config.get(key.split('.')[0],key.split('.')[1])
        return str(value)
    
    except Exception as e:
        WriteLog('(X) IniValue Exception: '+str(e))
        WriteLog('False')

#===============================================================================
# Get ini key from value
# Input: ini_FileName, ini_section, desire_value
# Output: String 'ini_key'
# ex: IniGetKeyFromValue('setting', 'GameType', 'KA'):
# Created by Tommy_Han 2019/7/15
#===============================================================================
def IniGetKeyFromValue(ini_FileName, ini_section, desire_value):
    config = configparser.ConfigParser()
    config.read(currentdir+'\\ini\\%s.ini' %ini_FileName, encoding='UTF-8')
    for ini_key, ini_value in config.items(ini_section):
        if (desire_value in ini_value):
            return str(ini_key)

#===============================================================================
# Replace ini value of key
# Input: ini_FileName, key, new_value
# Output: String 'False', and show 'New value' (if success)
# ex: ReplaceIniValue "settings" "OSCE.InstallationDir" "yes"
# Created by Tommy_Han 2017/4/24
#===============================================================================
def ReplaceIniValue (ini_FileName, key, new_value):
    config = configparser.ConfigParser()
    try:
        iniFile = (currentdir+'\\ini\\%s.ini' %ini_FileName)
        config.read(iniFile, encoding='UTF-8')
        if (config.has_section(key.split('.')[0]) == False):
            WriteLog('\t\t'+'No [%s] in ini_file' %(key.split('.')[0]))
            return 'False'
        
        config.set(key.split('.')[0], key.split('.')[1], new_value)
        config.write(open(iniFile, 'w', encoding='UTF-8'))
        
        WriteLog('\t\t'+'New ini value is: %s = %s' %(key, IniValue(ini_FileName,key)))
        
    except Exception as e:
        WriteLog('(X) ReplaceIniValue Exception: '+str(e))
        return 'False'

#===============================================================================
# Get JSON value by string
# Input: json_string(String), key(String)
# Output: return Value(String), False(String) 
# EX: GetJsonValue(json_string, 'permission|og')
# Created by Tommy_Han 2016/11/29
#===============================================================================
def GetJsonValue(json_string, key):
#     WriteLog('\t'+'>> START checkJSONValue: '+ str(json_string))
    if (json_string):
        parse_json_string = json.loads(json_string, strict=False)
        i = 0
        argu = key.split('|')
        try:
            for each in argu:
                if (type(parse_json_string) == dict and parse_json_string.get(each)):
                    parse_json_string = parse_json_string.get(each)
                elif (type(parse_json_string) == list and isInt(argu[i])):
                    parse_json_string = parse_json_string[int(each)]
                else:
#                     WriteLog('\t\t'+'Key "%s" does not exist.' %(argu[i]))
#                     WriteLog('\t'+'<< Fail, END checkJSONValue')
                    return "False"
                i+=1
#             WriteLog(parse_json_string)
#             WriteLog('\t'+'<< END Success, checkJSONValue: %s = %s' %(str(key),str(parse_json_string)))
            return parse_json_string
        except Exception as e:
            WriteLog('\t'+'- (X) checkJSONValue Exception: '+str(e))
            return "False"
    else:
        WriteLog('\t'+'- Fail checkJSONValue, value: ' + str(json_string))
#         WriteLog('\t'+'<< Fail, END checkJSONValue')
        return "False"

#===============================================================================
# Compare JSON all value is equal_value or not by string
# Input: json_string(String), key(String)
# Output: if equal return PASS(String), else return FAIL(String)
# EX: jsonValueCompare(json_string, 'permission|og', '0')
# Created by Tommy_Han 2019/04/29
#===============================================================================
def JsonValueCompare(json_string, compare_value_of_key, equal_value):
#     WriteLog('>> START jsonValueCompare')
    result_list = []
    if (json_string):
        parse_json_string = json.loads(json_string)
        i = 0
        argus = compare_value_of_key.split('|')
        try:
            for each in argus:
                if (type(parse_json_string) is dict and parse_json_string.get(each)):
                    parse_json_string = parse_json_string.get(each)
                # for jobtitle permission
                elif (type(parse_json_string) is dict and type(parse_json_string.get(each)) is list):
                    parse_json_string = parse_json_string.get(each)
                elif (type(parse_json_string) is list and isInt(argus[i])):
                    parse_json_string = parse_json_string[int(each)]
                else:
                    return 'FAIL'
                i+=1
            
            if(type(parse_json_string) is list):
                if(str(parse_json_string) == equal_value):
                    result_list.append('True')
                else:
                    result_list.append('False')
            else:
                for each_value in parse_json_string.values():
                    if(str(each_value) == equal_value):
                        result_list.append('True')
                    else:
                        result_list.append('False')
                        
            WriteLog('\t'+str(result_list))
            if('False' in result_list or not result_list):
                return 'FAIL'
            else:
                return 'PASS'
        
        except Exception as e:
            WriteLog('\t'+'- (X) jsonValueCompare Exception: '+str(e))
            return "FAIL"
        finally:
            WriteLog('<< END Success, jsonValueCompare')
    else:
        WriteLog('\t'+'<< END Fail, value: ' + str(json_string))
        return "FAIL"

def isInt(value):
#     WriteLog('>> START isInt')
    try:
        int(value)
        WriteLog('\t'+'<< END Success, isInt')
        return True
    except ValueError:
        WriteLog('\t'+'<< END Fail, isInt')
        return False
    except Exception as e:
        WriteLog('\t'+'(X) isInt Exception: ' + str(e))
        return False


#===============================================================================
# ReplaceJson(parse_json_string, keys, replace_value)
#===============================================================================
def ReplaceJsonString(json_string, k, v):
    adict = json.loads(json_string)
    if(len(k.split('|')) == 1):
        for key1 in adict.keys():
            if type(adict[key1]) is OrderedDict:
                ReplaceJson(adict[key1], k, v)
            elif key1 == k:
                if (type(adict[key1]) == list and type(v) == str):
                    adict[key1] = v.split()
                elif(type(adict[key1]) == str):
                    adict[key1] = v
                elif(type(adict[key1]) == int):
                    adict[key1] = int(v)
    else:
        k = k.split('|',1)
        for key1 in adict.keys():
            if type(adict[key1]) is OrderedDict:
                ReplaceJson(adict[key1], k[1], v)
            elif key1 == k[0]:
                if (type(adict[key1]) == list and type(v) == str):
                    adict[key1] = v.split()
                else:
                    adict[key1] = v
    return(json.dumps(adict))
    
#===============================================================================
# Replace JSON value
# Input: JSON_file_path(String), key(String), replace_value(String)
# Ex: replaceJSONValue "C:\\updateClientSetting_enableVP.txt" "clientSettings|networkEngineSettings|settings.configuration.packetlog.size" "1024"
# Output: return String
# Created by Tommy_Han 2017/9/13
#===============================================================================
def ReplaceJsonValue(json_file, keys, replace_value, to_UTF8 =False):
    with open(json_file, 'r+') as f:
        parse_json_string = json.loads(f.read(), strict=False, object_pairs_hook=OrderedDict)
#         def str_to_bool(s):
#             if (s == 'TRUE' or s == 'True' or s == 'true'):
#                 return 1
#             elif (s == 'FALSE' or s == 'False' or s == 'false'):
#                 return 0
#             else:
#                 raise ValueError
        def ReplaceJson(adict, k, v):
            if(len(k.split('|')) == 1):
                for key1 in adict.keys():
                    if type(adict[key1]) is OrderedDict:
                        ReplaceJson(adict[key1], k, v)
                    elif key1 == k:
                        #print(type(adict[key1]))
                        if (type(adict[key1]) == list and type(v) == str):
                            adict[key1] = v.split()
                        elif(type(adict[key1]) == str):
                            adict[key1] = v
                        elif(type(adict[key1]) == int):
                            adict[key1] = int(v)
#                         else:
#                             adict[key1] = str_to_bool(v)
#                 f.seek(0)
#                 json.dump(adict, f, indent=4, ensure_ascii=to_UTF8)
# #                 json.dump(adict, f, indent=4, ensure_ascii=False)
#                 f.truncate()
            else:
                k = k.split('|',1)
                for key1 in adict.keys():
                    if type(adict[key1]) is OrderedDict:
                        ReplaceJson(adict[key1], k[1], v)
                    elif key1 == k[0]:
                        if (type(adict[key1]) == list and type(v) == str):
                            adict[key1] = v.split()
                        else:
                            adict[key1] = v
            f.seek(0)
            json.dump(adict, f, indent=4, ensure_ascii=to_UTF8)
#                 json.dump(adict, f, indent=4, ensure_ascii=False)
            f.truncate()
        try:

#             old_value = checkJSONFile(json_file,keys) # Get old value
#             key = keys.split('|')[-1]
            ReplaceJson(parse_json_string, keys, replace_value)
            new_value = CheckJsonFile(json_file,keys) # Get new value
            
            if (str(new_value).replace('[','').replace(']','').replace('\'','') == str(replace_value).replace('[','').replace(']','').replace('\'','')):
#                 WriteLog('\t'+'%s (old)-> %s (new)' %(str(old_value),str(new_value)))
                WriteLog('\t'+'<< END Success, replaceJSONValue.')
                return json_file
            else:
                WriteLog('\t'+'<< END Fail, replaceJSONValue: '+str(new_value))
                return 'False'
        except Exception as e:
            WriteLog('\t'+'(X) replaceJSONValue Exception: '+str(e))
            return 'False'


def AddJsonValue(JsonFile, key, value):
    try:
        with open(JsonFile) as json_file:
            json_decoded = json.load(json_file)
        
        json_decoded[key] = value
        
        with open(JsonFile, 'w', encoding='UTF-8') as json_file:
            json.dump(json_decoded, json_file, encoding='UTF-8')
            
    except Exception as e:
        WriteLog('(X) AddJsonValue Exception: '+str(e))

#===============================================================================
# Compare Replace all value to a same value.
# Input: json_string(String), (k)ey, (v)alue
# Output: json string
# EX-1: ReplaceAllJsonValue(json_string, '', '0')
# EX-2: ReplaceAllJsonValue(json_string, 'og', '1')
# 'og': { 'og_1': '1', 'og_10': '1', 'og_11': '1', 'og_2': '1', 'og_4': '1', 'og_5': '1', 'og_6': '1', 'og_7': '1', 'og_8': '1', 'og_9': '1'}
# Created by Tommy_Han 2019/05/02
#===============================================================================
def ReplaceAllJsonValue(json_string, k, v):
    WriteLog('>> START ReplaceAllJsonValue')
    if (json_string):
        if(type(json_string) is dict):
            parse_json_string = json_string
        else:
            parse_json_string = json.loads(json_string, strict=False)
        
        try:
            replace_key = k.split('|', 1)
            if(k==''):
                if (type(parse_json_string) is dict):
                    for json_key in parse_json_string.keys():
                        parse_json_string[json_key] = v
                else:
                    parse_json_string[json_key] = v
                
            elif(len(replace_key) == 1):
                new_parse_json_string = parse_json_string[replace_key]
                print(type(new_parse_json_string))
                if (type(new_parse_json_string) is dict):
                    for json_key in new_parse_json_string.keys():
                        print(parse_json_string[json_key])
                        new_parse_json_string[json_key] = v
                else:
                    parse_json_string[json_key] = v
            else:
                parse_json_string2 = parse_json_string.get(replace_key[0]).get(replace_key[1])
                if(type(parse_json_string2) is dict):
                    for json_key2 in parse_json_string2:
                        parse_json_string2[json_key2] = v
            str_json = json.dumps(parse_json_string)
            return str_json
        
        except Exception as e:
            WriteLog('\t'+'- (X) ReplaceAllJsonValue Exception: '+str(e))
            return "FAIL"
        finally:
            WriteLog('<< END Success, ReplaceAllJsonValue')
    else:
        WriteLog('\t'+'<< END Fail, Not Json format')
        return "FAIL"

#===============================================================================
# Get JSON value by file
# Input: JSON_file_path(String), key(String)
# Output: return Value
# Created by Tommy_Han 2016/11/29
#===============================================================================
def CheckJsonFile(json_file,key):
#     WriteLog('\t'+'>> START checkJSONFile')
    if (os.path.exists(json_file)):
        json_data = open(json_file, 'r+', encoding='UTF-8')
        parse_json = json.loads(json_data.read(), strict=False, encoding='UTF-8')

        i = 0
        argu = key.split('|')
        try:
            for each in argu:
                if (type(parse_json) == dict and parse_json.get(each)):
                    parse_json = parse_json.get(each)
                elif (type(parse_json) == dict and parse_json.get(each)==0):
                    parse_json = parse_json.get(each)
                elif (type(parse_json) == list and isInt(argu[i])):
                    parse_json = parse_json[int(each)]
                else:
#                     WriteLog('\t'+'\t'+'Key "%s" does not exist.' %(argu[i]))
#                     WriteLog('\t'+'<< Fail, END checkJSONFile')
                    return False
                i+=1
            #WriteLog(str(parse_json))
#             WriteLog('\t'+'<< Success, END checkJSONFile')
            return parse_json
        except Exception as e:
            WriteLog('\t'+'(X) checkJSONFile Exception: '+str(e))
            return False
        finally:
            WriteLog('\t'+'<< END Success, checkJSONFile: '+str(parse_json))
    else:
        WriteLog('\t'+'\t'+'END Fail, file: ' + json_file )
#         WriteLog('\t'+'<< Fail, END checkJSONFile')
        return False


def save_cookies(requests_cookiejar, filename):
    with open(filename, 'wb') as f:
        pickle.dump(requests_cookiejar, f)

def load_cookies(filename):
    if os.path.getsize(filename) > 0: 
        with open(filename, 'rb+') as f:
            return pickle.load(f)

def create_sha256_signature(key, file):
#     f = open(file, 'r')
#     new_message = f.read().replace('\n','').replace(' ','')
    with open(file) as json_file:  
        message = json.load(json_file)
    key_bytes = bytes(key,'utf-8')
#     new_message_bytes = bytes(str(new_message),'utf-8')
    new_message_bytes = bytes(str(json.dumps(message)),'utf-8')
    return hmac.new(key_bytes, new_message_bytes, hashlib.sha256).hexdigest()

# Get HTML attribute by other attributes
# soup.find("meta", {"name":"City"})
# out: <meta name="City" content="Austin" />
# soup.find("meta", {"name":"City"})['content']
# out: u'Austin'
def GetHtmlAttribute(print_tab, res_log, html_string, html_tag, element_key, element_value, html_attribute):
    dict_html_element = {}
    dict_html_element[element_key] = element_value
    soup = BeautifulSoup(html_string)
    my_attribute = soup.find(html_tag, dict_html_element)[html_attribute]
    res_log = WriteDebugLog(res_log, print_tab+ '- Attribute (key, value): '+html_attribute+', '+my_attribute)
    print(my_attribute)
    return (res_log, my_attribute)

#===============================================================================
# Call API and verify status code, response data, response time
# Input: (String)'\n\t\t', (String)ini_file_path, (Boolean)verify_response_or_not, (Boolean)save_cookies_or_not
# ini file contains: 
# admin_api_url, bc_api_url, ref_api_url, api_path, api_crud, api_data, api_params, hash, api_expect_time, api_signature
# api_response, api_expect_time
# Output: (Boolean)True/False, (String)Time_Stamp, (String)Response
# Created by Tommy_Han 2019/3/7
#===============================================================================
def ApiResponse(print_tab, res_log, api_ini, verify_response_or_not, save_cookies_or_not):
    if(os.path.isfile('session')):
        session = load_cookies('session')
    else:
        session = ''
#     try:
#         api_signature  = IniValue(api_ini, 'API.api_signature ')
#         if((api_signature  != '{}')and (api_signature  != '')):
#             signature  = hmac.new(api_signature, msg='{ test: "json", use: "actual"}', digestmode=hashlib.sha256).hexdigest()
#     except Exception as e:
#         WriteLog(print_tab+ 'No signature): '+str(e))
    
    try:
        # API parameters repository
        
        api_ref_url = IniValue(api_ini, 'API.ref_api_url')
#         api_url = IniValue(api_ini, 'API.'+api_ref_url)
        api_url = IniValue('setting', 'TestEnv.'+api_ref_url)
        api_path = IniValue(api_ini, 'API.api_path')
        api_crud = IniValue(api_ini, 'API.api_crud')
        api_response = IniValue(api_ini, 'API.api_response').lower()
        api_data = {}
        api_data_path = IniValue(api_ini, 'API.api_data')
#         print(api_data_path == '{}')
        if((api_data_path != '{}') and (api_data_path != '')):
#             WriteLog('\n\t\texist_params: '+api_data_path)
            with open(currentdir+'\\JsonFiles\\'+api_data_path) as f: # JsonFiles\Api_Json\java_login.json
                WriteLog(print_tab+ 'exist_data: '+str(currentdir+'\\JsonFiles\\'+api_data_path))
                api_data = json.load(f)
                
        api_expect_time = int(IniValue(api_ini, 'API.api_expect_time'))
        
        api_signature = {}
        api_signature = IniValue(api_ini, 'API.api_signature')
        if((api_signature != '{}') and (api_signature != '')):
            signature = create_sha256_signature(api_signature, currentdir+'\\JsonFiles\\'+api_data_path)
            res_log = WriteDebugLog(res_log, print_tab+ '- signature exist, goto hash.')
            if(not ('hash' in IniValue(api_ini, 'API.api_params'))):
                res_log = WriteDebugLog(res_log, print_tab+ '- hash is not in params')
                ReplaceIniValue(api_ini, 'API.api_params', 'hash')
            ReplaceIniValue(api_ini, 'API.hash', signature)
        api_params = {}
        exist_params = IniValue(api_ini, 'API.api_params')
        if((exist_params != '{}') and (exist_params != '')):
#             WriteLog('\n\t\texist_params: '+str(exist_params))
            for key in exist_params.split(', '):
                ini_value = IniValue(api_ini, 'API.'+key)
#                 print('---------------'+ini_value)
#                 print(list(ini_value.split(", ")))
                if('[]' in key):
                    api_params[key] = list(ini_value.split(", "))
                else:
                    api_params[key] = ini_value
        
        # API return content type (JSON/ XML)
        api_headers = {'content-type': 'application/json'}
#         api_headers = {'content-type': 'application/html'}
#         api_headers = {'content-type': 'application/x-www-form-urlencoded'}
        
#         print(str(api_crud))
        if(api_crud == 'post'):
            res_log = WriteDebugLog(res_log, print_tab+ '- api url: '+ str(api_url+api_path))
            res_log = WriteDebugLog(res_log, print_tab+ '- api params: '+ str(api_params))
            res_log = WriteDebugLog(res_log, print_tab+ '- api data: '+ str(api_data).replace("'",'"'))
            res_log = WriteDebugLog(res_log, print_tab+ '- api headers: '+ str(api_headers))
#             res_log = WriteDebugLog(res_log, print_tab+ '- api signature: '+ str(api_signature))
            r = requests.post(api_url+api_path, cookies=session, params=api_params, data=json.dumps(api_data), headers=api_headers, timeout=api_expect_time)
            WriteLog(print_tab+ str(r.cookies))
            if(save_cookies_or_not):
                save_cookies(r.cookies, 'session')
        elif(api_crud == 'get'):
            r = requests.post(api_url+api_path, cookies=session, params=api_params, data=json.dumps(api_data), headers=api_headers, timeout=api_expect_time)
        elif(api_crud == 'put'):
            r = requests.post(api_url+api_path, cookies=session, params=api_params, data=json.dumps(api_data), headers=api_headers, timeout=api_expect_time)
        elif(api_crud == 'delete'):
            r = requests.post(api_url+api_path, cookies=session, params=api_params, data=json.dumps(api_data), headers=api_headers, timeout=api_expect_time)
#             r = requests.delete(api_url+api_path, params=api_params, data=json.dumps(api_data), headers=api_headers, timeout=api_expect_time)
        # print (r.history)
        print(json.dumps(r.url))
        if(str(r.text)[:1]=='{'):
            json_response = json.loads(r.text, strict=False)
            # For convert unicode -> UTF-8: Use ensure_ascii = False
            response_data = json.dumps(json_response, sort_keys=True, indent=4, ensure_ascii=False)
#             response_data = '\n'+json.dumps(json_response, sort_keys=True, indent=4)
        elif(str(r.text)[:1]=='<'):
            soup = BeautifulSoup(r.text, 'html.parser')
            response_data = soup.prettify()
        elif(str(r.text)[:1]=='['):
            json_response = json.loads(r.text, strict=False)
            # For convert unicode -> UTF-8: Use ensure_ascii = False
            response_data = json.dumps(json_response, sort_keys=True, ensure_ascii=False)
        else:
            response_data = str(r.text)
#         print(r.origin)
        if(r.status_code == 200):
            # requests.codes.OK == 200
            res_log = WriteDebugLog(res_log, print_tab+ '- Status code: 200')
            if(not verify_response_or_not):
                res_log = WriteDebugLog(res_log, print_tab+ '- Don\'t compare response: Success, '+ str(r.elapsed.total_seconds())+' (seconds)')
#                 res_log = WriteDebugLog(res_log, print_tab+ '- api response: \n'+ str(response_data))
                return (True, str(r.elapsed.total_seconds()), response_data, res_log)
            elif(verify_response_or_not and r.text.lower().replace('\n','').replace(' ','') == api_response):
                res_log = WriteDebugLog(res_log, print_tab+ '- Compare response: Success, '+ str(r.elapsed.total_seconds())+' (seconds)')
#                 res_log = WriteDebugLog(res_log, print_tab+ '- api response: \n'+ str(response_data))
                return (True, str(r.elapsed.total_seconds()), response_data, res_log)
            else:
                res_log = WriteDebugLog(res_log, print_tab+ '- Compare response: Fail, '+ str(r.elapsed.total_seconds())+' (seconds)')
#                 res_log = WriteDebugLog(res_log, print_tab+ '- api response: \n'+ str(response_data))
                return (False, str(r.elapsed.total_seconds()), response_data, res_log)
        else:
            res_log = WriteDebugLog(res_log, print_tab+'- Status code: '+str(r.raise_for_status()))
            return (False, str(r.elapsed.total_seconds()), response_data, res_log)
    
    except Exception as e:
#         res_log = WriteDebugLog(res_log, print_tab+ '- (X) Exception (ApiResponse): '+str(e))
        return (False, '0.0', '(X) Exception (ApiResponse): '+str(e), res_log)


def CheckPermissionDenied(print_tab, res_log, json_string, error_code='E05', error_message='No Permission'):
    try:
        json_response = json.loads(json_string)
        if(error_code == 'E05'):
#         if(json_response['Error_code'] == error_code and json_response['Error_message'] == error_message):
            if(json_response.get('Error_at') == '/var/www/PHP/phpadmin/app/Http/Middleware/PermissionFilter.php'):
                # 判斷錯誤的地方是否為權限問題，是的話暫時先PASS，不是的話代表程式的問題FAIL
                res_log = WriteDebugLog(res_log, print_tab+'- Success (Error_code, Error_message): ('+error_code+', '+error_message+')')
                return (True, res_log)
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- Success (Error_code, Error_message): ('+error_code+', '+error_message+')')
                return (False, res_log)
        else:
            if(json_response['Error_code'] == error_code and json_response['Error_message'] == error_message):
                res_log = WriteDebugLog(res_log, print_tab+'- Success (Error_code, Error_message): ('+error_code+', '+error_message+')')
                return (True, res_log)
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- Fail (Error_code, Error_message): ('+json_response['Error_code']+', '+json_response['Error_message']+')')
                return (False, res_log)
    except Exception as e:
        res_log = WriteDebugLog(res_log, print_tab+'Exception: on CheckPermissionDenied... %s' % str(e))
        return (False, res_log)
        
#===============================================================================
# ApiCodeDetect: Convert code image to string.
# Input: print_tab, res_log, code_image(.jpg)
# Output: (String) new_code, (String)res_log
# Created by Tommy_Han 2019/3/9
#===============================================================================
def ApiCodeDetect(print_tab, res_log, src_file):
    is_fail = True
    while(is_fail):
        try:
            im = Image.open(src_file) #code.jpg
#             im.show()
            
            gray = im.convert('L')
            # gray.show()
#             binary = im.convert('1')
            # binary.show()
            
            def getPixel(image,x,y,G,N):
                L = image.getpixel((x,y))
                if L > G:
                    L = True
                else:
                    L = False
             
                nearDots = 0
                if L == (image.getpixel((x - 1,y - 1)) > G):
                    nearDots += 1
                if L == (image.getpixel((x - 1,y)) > G):
                    nearDots += 1
                if L == (image.getpixel((x - 1,y + 1)) > G):
                    nearDots += 1
                if L == (image.getpixel((x,y - 1)) > G):
                    nearDots += 1
                if L == (image.getpixel((x,y + 1)) > G):
                    nearDots += 1
                if L == (image.getpixel((x + 1,y - 1)) > G):
                    nearDots += 1
                if L == (image.getpixel((x + 1,y)) > G):
                    nearDots += 1
                if L == (image.getpixel((x + 1,y + 1)) > G):
                    nearDots += 1
             
                if nearDots < N:
                    return image.getpixel((x,y-1))
                else:
                    return None
            
            def clearNoise(image,G,N,Z):
                draw = ImageDraw.Draw(image)
                for i in range(0,Z):
                    for x in range(1,image.size[0] - 1):
                        for y in range(1,image.size[1] - 1):
                            color = getPixel(image,x,y,G,N)
                            if (color != None):
                                draw.point((x,y),color)
            
            clearNoise(gray,150,4,5)
            # gray.show()
            
            
            def dec_noise(img, threshold):
                table = []
                for i in range(256):
                    if i < threshold:
                        table.append(0)
                    else:
                        table.append(1)
                out = img.point(table, '1')
                return out
            
            # dec_noise(gray, 180).show()
            
            im_sommth = dec_noise(gray, 180).filter(ImageFilter.MedianFilter(size=3))
            # im_sommth.show()
            # dec_noise(im_sommth, 160).show()
            # dec_noise(im_sommth, 160).save("black_white.jpg")
            
            def depoint(img):
                """传入二值化后的图片进行降噪"""
                pixdata = img.load()
                w,h = img.size
                for y in range(1,h-1):
                    for x in range(1,w-1):
                        count = 0
                        if pixdata[x,y-1] > 245:#上
                            count = count + 1
                        if pixdata[x,y+1] > 245:#下
                            count = count + 1
                        if pixdata[x-1,y] > 245:#左
                            count = count + 1
                        if pixdata[x+1,y] > 245:#右
                            count = count + 1
                        if pixdata[x-1,y-1] > 245:#左上
                            count = count + 1
                        if pixdata[x-1,y+1] > 245:#左下
                            count = count + 1
                        if pixdata[x+1,y-1] > 245:#右上
                            count = count + 1
                        if pixdata[x+1,y+1] > 245:#右下
                            count = count + 1
                        if count > 4:
                            pixdata[x,y] = 255
                return img
            
            def vertical(img):
                """传入二值化后的图片进行垂直投影"""
                pixdata = img.load()
                w,h = img.size
                ver_list = []
                # 开始投影
                for x in range(w):
                    black = 0
                    for y in range(h):
                        if pixdata[x,y] == 0:
                            black += 1
                    ver_list.append(black)
                # 判断边界
                l,r = 0,0
                flag = False
                cuts = []
                for i,count in enumerate(ver_list):
                    # 阈值这里为0
                    if flag is False and count >50:
                        l = i
                        flag = True
                    if flag and count == 5:
                        r = i-1
                        flag = False
                        cuts.append((l,r))
                return cuts
            
            v = vertical(im_sommth)
            w, h = im_sommth.size
            for i, item in enumerate(v):
                if(i <4):
                    box = (item[0], 0, item[1], h)
                    im_sommth.crop(box).save(currentdir+'\\'+str(i) + "_.jpg")
            
            def cfs(img):
                """传入二值化后的图片进行连通域分割"""
                pixdata = img.load()
                w, h = img.size
                visited = set()
                q = queue.Queue()
                offset = [(-2,-2),(-2,-1),(-1,-2),(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1),(1,2),(2,1),(2,2)]
                cuts = []
                for x in range(w):
                    for y in range(h):
                        x_axis = []
                        # y_axis = []
                        if pixdata[x, y] == 0 and (x, y) not in visited:
                            q.put((x, y))
                            visited.add((x, y))
                        while not q.empty():
                            x_p, y_p = q.get()
                            for x_offset, y_offset in offset:
                                x_c, y_c = x_p + x_offset, y_p + y_offset
                                if (x_c, y_c) in visited:
                                    continue
                                visited.add((x_c, y_c))
                                try:
                                    if pixdata[x_c, y_c] == 0:
                                        q.put((x_c, y_c))
                                        x_axis.append(x_c)
                                        # y_axis.append(y_c)
                                except:
                                    pass
                        if x_axis:
                            min_x, max_x = min(x_axis), max(x_axis)
                            if max_x - min_x > 3:
                                # 宽度小于3的认为是噪点，根据需要修改
                                cuts.append((min_x, max_x + 1))
                return cuts
            
            def saveSmall(img, cuts):
                w, h = img.size
            #     pixdata = img.load()
                for i, item in enumerate(cuts):
                    if(i <4):
                        box = (item[0], 0, item[1], h)
                        img.crop(box).save(currentdir+'\\'+str(i) + "_.jpg")
#                             img.crop(box).show() # show corp image 
            
            def get_fratures(array):
                #拿到数组的高度和宽度
            #     qq = array.shape
                h, w = array.shape
                data= []
                for x in range(0, w//4):
                    offset_y = x*4
                    temp = []
                    for y in range(0, h//4):
                        offset_xx = y*4
                        temp.append(sum(sum(array[0+offset_y:4+offset_y, 0+offset_xx:4+offset_xx])))
                        data.append(temp)
                        return np.asarray(data)
                
            saveSmall(im_sommth, cfs(im_sommth))
            is_fail = False
            
        except Exception as e:
            is_fail = True
            res_log = WriteDebugLog(res_log, '\n\t\t- Exception: on solve pic... %s' % str(e))
            
        finally:
            res_log = WriteDebugLog(res_log, '\n\t\t- - - ')
          
        try:
            compare_code = ''  
            def getGray(image_file):
                tmpls=[]
                for h in range(0,  image_file.size[1]):#h
                    for w in range(0, image_file.size[0]):#w
                        tmpls.append( image_file.getpixel((w,h)))
                return tmpls
               
            def getAvg(ls):#获取平均灰度值
                return sum(ls)/len(ls)
               
            def getMH(a,b):#比较100个字符有几个字符相同
                dist = 0;
                for i in range(0,len(a)):
                    if a[i]==b[i]:
                        dist=dist+1
                return dist
               
            def getImgHash(fne):
                image_file = Image.open(fne) # 打开
                image_file=image_file.resize((12, 12))#重置图片大小我12px X 12px
                image_file=image_file.convert("L")#转256灰度图
                Grayls=getGray(image_file)#灰度集合
                avg=getAvg(Grayls)#灰度平均值
                bitls=''#接收获取0或1
                #除去变宽1px遍历像素
                for h in range(1,  image_file.size[1]-1):#h
                    for w in range(1, image_file.size[0]-1):#w
                        if image_file.getpixel((w,h))>=avg:#像素的值比较平均值 大于记为1 小于记为0
                            bitls=bitls+'1'
                        else:
                            bitls=bitls+'0'
                return bitls
            
            for i in range(4):
                dict1 = {}
                a=getImgHash(currentdir+'\\'+str(i)+"_.jpg")#图片地址自行替换
                files = os.listdir(compare_path)#图片文件夹地址自行替换
                for file in files:
                    b=getImgHash(compare_path+"\\"+str(file))
                    compare=getMH(a,b)
                    dict1[str(file)] = int(compare)
            #         print (file,u'相似度',str(compare)+'%')
                right_key = max(dict1.items(), key=operator.itemgetter(1))[0]
                res_log = WriteDebugLog(res_log, print_tab+'- '+right_key.split('_')[0]+', accurate: '+str(dict1[right_key])+' %')
#                 print('----------------------------------------------')
                compare_code += str(right_key.split('_')[0])
            
            is_fail = False
            return (compare_code, res_log)
        
        except Exception as e:
            is_fail = True
            res_log = WriteDebugLog(res_log, print_tab+'- Exception: on compare pic... %s' % str(e))
              
        finally:
            res_log = WriteDebugLog(res_log, print_tab+'- - - ')
        
def Compare_and_Click(driver, image_dir, comp_image_path, is_corp, corp_img, output_path):
    if(is_corp):
        corp_size = cv2.imread(corp_img)
        corp_height, corp_width, channels = corp_size.shape
        
    driver.save_screenshot(image_dir+'\\web_screen.png')
    img_rgb = cv2.imread(image_dir+'\\web_screen.png')
    template = cv2.imread(comp_image_path)
#     w, h = template.shape[:-1]
    height, width, channels = template.shape
    
    res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.6
    loc = np.where(res >= threshold)
    pt = [0, 0]
    for pt in zip(*loc[::-1]):  # Switch collumns and rows
        if(is_corp):
            cv2.rectangle(img_rgb, pt, (pt[0] + corp_width, pt[1] + corp_height), (0, 0, 255), 2)
        else:
            cv2.rectangle(img_rgb, pt, (pt[0] + width, pt[1] + height), (0, 0, 255), 2)
    
    if(pt[0] ==0 and pt[1] ==0 ):
        return(0, 0)
    else:
        cv2.imwrite(image_dir+'\\result.png', img_rgb)
        if(is_corp):
            crop_img = img_rgb[pt[1]:(pt[1]+corp_height), pt[0]:(pt[0]+corp_width)]
            cv2.imwrite(output_path, crop_img)
            return(pt[0] + corp_width/2, pt[1] + corp_height/2)
        else:
            return(pt[0] + width/2, pt[1] + height/2)

def Snap_by_Point(driver, image_dir, output_path, org_width, to_my_width, org_height, to_my_height):
    driver.save_screenshot(image_dir+'\\my_web_screen.png')
    img_rgb = cv2.imread(image_dir+'\\my_web_screen.png')
    crop_img = img_rgb[org_width:to_my_width, org_height:to_my_height]
    cv2.imwrite(output_path, crop_img)
    return (True)

#===============================================================================
# For Sun version.
# Html2Chinese: Convert Chinese words to string corresponding to excel convert table.
# Input: (String)src_html_path, (String)src_excel_path, (String)dest_path
# Output: No output, just convert file.
# Usage: Html2Chinese('C:\\Users\\tommy\\Documents\\admin_web\\', 'C:\\Users\\tommy\\Documents\\admin_web.xlsx', 'C:\\Users\\tommy\\Documents\\replace_admin_web\\')
# Created by Tommy_Han 2019/4/9
#===============================================================================
def Html2Chinese(src_html_folder, src_excel_path, dest_folder):
    import re
    import glob
    import xlrd
    re_words = re.compile(u"[\u4e00-\u9fff\u2E80-\u2FDF\u3400-\u4DBF\uF900-\uFAFF\u31A0-\u31BF]+")
    excel_file_open = xlrd.open_workbook(src_excel_path)
    
    excel_file_col1 = excel_file_open.sheet_by_index(0).col(1)
    excel_file_col0 = excel_file_open.sheet_by_index(0).col(0)
    
    excel_dict = {}
    for i,j in zip(excel_file_col1, excel_file_col0):
        excel_dict[i.value]= j.value
    
    for filename in glob.glob(os.path.join(src_html_folder, '*.kit')):
        replace_list = []
        print('\t'+filename.split('\\')[-1])
#         html_mobile = open(filename.split('.')[0]+"_replace.html", "w", encoding="utf-8")
        dest_file = dest_folder+filename.split('\\')[-1].replace('.kit','.kit')
        output_html = open(dest_file, "w", encoding="utf-8")
        with open(filename, encoding="utf8") as f:
            html_file = f.read()
            soup = BeautifulSoup(html_file, 'html.parser')
            strhtm = soup.prettify()
            for x in re.findall(re_words, strhtm):
                if(excel_dict.get(x) != None):
                    if(not (excel_dict.get(x) in replace_list)):
                        replace_list.append(excel_dict.get(x))
                    # 1st Replace string START with single quote ', and end with single quote
                    strhtm = re.sub(r'="\b'+x+r'\b"','="'+excel_dict.get(x), strhtm)
                    strhtm = re.sub(r"='\b"+x+r"\b'","='"+excel_dict.get(x), strhtm)
                    strhtm = re.sub(r"'\b"+x+r"'","'"+excel_dict.get(x)+"'", strhtm) # lang.set(lang636);
                    # 2st Replace string START with double quote ", and end with double quote
                    strhtm = re.sub(r'"\b'+x+r'"','"'+excel_dict.get(x)+'"', strhtm)
                    strhtm = re.sub(r"'\b"+x+r"：'","'"+excel_dict.get(x)+"：'", strhtm)
                    strhtm = re.sub(r'"\b'+x+r'："','"'+excel_dict.get(x)+'："', strhtm)
                    
                    # 3rd Replace string START with ('
                    strhtm = re.sub(r"'\(\b"+x+r"\b\)'","'('+<b class=\""+excel_dict.get(x)+"\"></b>+')'", strhtm)
                    strhtm = re.sub(r"\(\b"+x+r"\b\)","+'('+<b class=\""+excel_dict.get(x)+"\"></b>+')'", strhtm)
                    
                    # 3rd Replace string START with single quote ', but not end with single quote
                    strhtm = re.sub(r"'\b"+x+r"\b","<b class=\""+excel_dict.get(x)+"\"></b>+'", strhtm)
                    # 4th Replace string START with double quote ", but not end with double quote
                    strhtm = re.sub(r'"\b'+x+r'\b','<b class="'+excel_dict.get(x)+'"></b>+"', strhtm)
                    
                    # Replace string without comment (//)
                    strhtm = re.sub(r"//\b"+x+r"\b",'//暫定'+x, strhtm)
                    strhtm = re.sub(r"<!--\b"+x+r"\b",'<!--暫定'+x, strhtm)
                    strhtm = re.sub(r"<!-- \b"+x+r"\b",'<!-- 暫定'+x, strhtm)
                    strhtm = re.sub(r'\b'+x+r'\b'+'"','"+<b class="'+excel_dict.get(x)+'"></b>', strhtm)
                    strhtm = re.sub(r"\b"+x+r"\b</option>'","'+<b class=\""+excel_dict.get(x)+"\"></b>+'</option>'", strhtm)
                    strhtm = re.sub(r"、\b"+x+r"\b",'+"、"+<b class="'+excel_dict.get(x)+'"></b>', strhtm)
                    strhtm = re.sub(r"！\b"+x+r"\b",'+"！"+<b class="'+excel_dict.get(x)+'"></b>', strhtm)
                    strhtm = re.sub(r"\b"+x+r"\b!",'<b class="'+excel_dict.get(x)+'"></b>+"!"', strhtm)
                    strhtm = re.sub(r"-\b"+x+r"\b",'+"-"+<b class="'+excel_dict.get(x)+'"></b>', strhtm)
                    strhtm = re.sub(r"\b"+x+r"\b",'<b class="'+excel_dict.get(x)+'"></b>', strhtm)
            output_html.write('lang.replaceTxT('+str(replace_list)+');\n')
            output_html.write(strhtm)
    print('Finish replace!!!')

#===============================================================================
# For Robert version
# Convert HTML Chinese to variable.
# 2019/4/1
#===============================================================================
def TempHtml2Chinese(src_html_folder, src_excel_path, dest_folder):
    import re
    import glob
    import xlrd
    re_words = re.compile(u"[\u4e00-\u9fff\u2E80-\u2FDF\u3400-\u4DBF\uF900-\uFAFF\u31A0-\u31BF]+")
    excel_file_open = xlrd.open_workbook(src_excel_path)
    
    excel_file_col1 = excel_file_open.sheet_by_index(0).col(1)
    excel_file_col0 = excel_file_open.sheet_by_index(0).col(0)
    
    excel_dict = {}
    for i,j in zip(excel_file_col1, excel_file_col0):
        excel_dict[i.value]= j.value
    
    for filename in glob.glob(os.path.join(src_html_folder, '*.html')):
        print('\t'+filename.split('\\')[-1])
#         html_mobile = open(filename.split('.')[0]+"_replace.html", "w", encoding="utf-8")
        dest_file = dest_folder+filename.split('\\')[-1].replace('.html','_replace.html')
        output_html = open(dest_file, "w", encoding="utf-8")
        with open(filename, encoding="utf8") as f:
            html_file = f.read()
            soup = BeautifulSoup(html_file, 'html.parser')
            strhtm = soup.prettify()
            for x in re.findall(re_words, strhtm):
                if(excel_dict.get(x) != None):
                    # 1st Replace string START with single quote ', and end with single quote
                    strhtm = re.sub(r'="\b'+x+r'\b"','=""+lang.set('+excel_dict.get(x)+')', strhtm)
                    strhtm = re.sub(r"='\b"+x+r"\b'","=''+lang.set("+excel_dict.get(x)+")", strhtm)
                    strhtm = re.sub(r"'\b"+x+r"'","lang.set("+excel_dict.get(x)+")", strhtm) # lang.set(lang636);
                    # 2st Replace string START with double quote ", and end with double quote
                    strhtm = re.sub(r'"\b'+x+r'"','lang.set('+excel_dict.get(x)+')', strhtm)
                    
                    # 3rd Replace string START with ('
                    strhtm = re.sub(r"'\(\b"+x+r"\b\)'","'('+lang.set("+excel_dict.get(x)+")+')'", strhtm)
                    strhtm = re.sub(r"\(\b"+x+r"\b\)","+'('+lang.set("+excel_dict.get(x)+")+')'", strhtm)
                    
                    # 3rd Replace string START with single quote ', but not end with single quote
                    strhtm = re.sub(r"'\b"+x+r"\b","lang.set("+excel_dict.get(x)+")+'", strhtm)
                    # 4th Replace string START with double quote ", but not end with double quote
                    strhtm = re.sub(r'"\b'+x+r'\b','lang.set('+excel_dict.get(x)+')+"', strhtm)
                    
                    # Replace string without comment (//)
                    strhtm = re.sub(r"//\b"+x+r"\b",'//暫定'+x, strhtm)
                    strhtm = re.sub(r"<!--\b"+x+r"\b",'<!--暫定'+x, strhtm)
                    strhtm = re.sub(r"<!-- \b"+x+r"\b",'<!-- 暫定'+x, strhtm)
                    strhtm = re.sub(r'\b'+x+r'\b'+'"','"+lang.set('+excel_dict.get(x)+')', strhtm)
                    strhtm = re.sub(r"\b"+x+r"\b</option>'","'+lang.set("+excel_dict.get(x)+")+'</option>'", strhtm)
                    strhtm = re.sub(r"、\b"+x+r"\b",'+"、"+lang.set('+excel_dict.get(x)+')', strhtm)
                    strhtm = re.sub(r"！\b"+x+r"\b",'+"！"+lang.set('+excel_dict.get(x)+')', strhtm)
                    strhtm = re.sub(r"\b"+x+r"\b!",'lang.set('+excel_dict.get(x)+')+"!"', strhtm)
                    strhtm = re.sub(r"-\b"+x+r"\b",'+"-"+lang.set('+excel_dict.get(x)+')', strhtm)
                    strhtm = re.sub(r"\b"+x+r"\b",'lang.set('+excel_dict.get(x)+')', strhtm)
            output_html.write(strhtm)
    print('Finish replace!!!')
    
#===============================================================================
# Html2Text: Extract Chinese words and save into .txt file.
# Input: (String)src_html_path, (String)dest_path
# Output: No output, just extract string.
# Usage: Html2Text('C:\\Users\\tommy\\Documents\\admin_web\\', 'C:\\Users\\tommy\\Documents\\txt_admin_web\\')
# Created by Tommy_Han 2019/4/1
#===============================================================================
def Html2Text(src_html_folder, dest_folder):
    import re
    import glob
    re_words = re.compile(u"[\u4e00-\u9fff\u2E80-\u2FDF\u3400-\u4DBF\uF900-\uFAFF\u31A0-\u31BF]+")
    text_file = open(dest_folder+"111_ALL_111.txt", "w",encoding="utf-8")
    for filename in glob.glob(os.path.join(src_html_folder, '*.html')):
        print('\t'+filename.split('\\')[-1])
        alist = []
        dest_file = dest_folder+filename.split('\\')[-1].replace('.html','.txt')
        output_text = open(dest_file, "w", encoding="utf-8")
        with open(filename, encoding="utf8") as f:
            html_line = str(f.readlines())
            for n in re.findall(re_words, html_line):
                alist.append(n)
            text_file.write(str(filename.split('\\')[-1])+'\n')
            output_text.write(str(filename.split('\\')[-1])+'\n')
            text_file.write(str(set(alist)).replace('\'','').replace('{','').replace('}','').replace(', ','\n'))
            output_text.write(str(set(alist)).replace('\'','').replace('{','').replace('}','').replace(', ','\n'))
        text_file.write('\n-------------------------------------------------------------------\n\n')
        output_text.write('\n-------------------------------------------------------------------\n\n')
    print('Finish extract!!!')


#===============================================================================
# ADMIN ALL API TEST
#===============================================================================
def AdminLogin(res_log, permission, filename, web_or_mobile = 'Web'):
    #=======================================================================
    # Current time increase format.
    # Usage: 
    # a = datetime.now().time() # 09:11:55.775695
    # b = Add_Seconds(a, 300) # 09:16:55
    #=======================================================================
    def Add_Seconds(tm, secs):
        fulldate = datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
        fulldate = fulldate + timedelta(seconds=secs)
        return fulldate.time()
    
    retry = 0
    while(retry < 10):
        try:
            result_list = []
            result_list2 = []
            if(web_or_mobile == 'Web'):
                ReplaceIniValue('admin_login_code', 'API.api_path', 'login/code')
            elif(web_or_mobile == 'Mobile'):
                ReplaceIniValue('admin_login_code', 'API.api_path', 'login/code/m')
            
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
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
            new_code, res_log = ApiCodeDetect(print_tab, res_log, filename)
            WriteLog('New code: '+new_code)
            ReplaceIniValue('admin_login', 'API.code', new_code)
#             elif(permission =='WebMaster'):
#                 WebMasterAcc = IniValue('setting', 'API.WebMasterAcc')
#                 ReplaceIniValue('admin_login', 'API.acc', WebMasterAcc)
#                 ReplaceIniValue('admin_login', 'API.pwd', WebMasterAcc)
#             elif(permission =='Agent'):
#                 agentacc = IniValue('setting', 'API.agentacc')
#                 ReplaceIniValue('admin_login', 'API.acc', agentacc)
#                 ReplaceIniValue('admin_login', 'API.pwd', agentacc)
#             else:
#                 res_log = WriteDebugLog(res_log, print_tab+'-No login permission.')
#                 return (res_log, False)
            return_value2, response_time2, response_data2, res_log = ApiResponse(print_tab, res_log, 'admin_login', True, True)
            WriteLog(print_tab+'Response data: '+ response_data2)
            json_response = json.loads(response_data2)
            if(return_value2):
                result_list2.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time2)
                break
                
            elif(json_response.get('Error_code')=='E06' or json_response.get('Error_code')=='E08' or json_response.get('Error_code')=='E02'):
                res_log = WriteDebugLog(res_log, print_tab+'- API fail: '+json_response.get('Error_message'))
                continue
            
            else:
                result_list2.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail: '+json_response.get('Error_message'))
                break
        except Exception as e:
            result_list2.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_login... %s' % str(e))
        finally:
            retry += 1
            res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    if(retry >= 10):
        result_list.append('FAIL')
        result_list2.append('FAIL')
        
    WriteLog(result_list)
    WriteLog(result_list2)
    if(('PASS' in result_list) and ('PASS' in result_list2)):
        return (res_log, True)
    else:
        return (res_log, False)


def AdminProfile(res_log, permission, current_user, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_profile', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(return_value):
            res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
            res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            json_response = json.loads(response_data)
#             if (permission == 'Boss'):
#                 current_user = 'Bonnie'
#             elif (permission == 'Banker'):
#                 current_user = IniValue('setting', 'API.bankeracc')
#             elif(permission =='WebMaster'):
#                 current_user = IniValue('setting', 'API.agentacc')
#             elif(permission =='Agent'):
#                 current_user = IniValue('setting', 'API.agentacc')
#             else:
#                 res_log = WriteDebugLog(res_log, print_tab+'-No login permission.')
#                 return (res_log, False)
            if(json_response.get('login_id') == current_user):
                res_log = WriteDebugLog(res_log, print_tab+'- This is Boss Account')
                ReplaceIniValue('setting', 'TestData.admin_boss_id', json_response.get('login_id'))
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- This is not Boss Account')
            
            if (permission == 'Boss'):
                if(json_response.get('login_rank') == 1):
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get login_rank: 1 (Boss)')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get login_rank: '+json_response.get('login_rank')+' != 1')
            
            elif (permission == 'Banker'):
                if(json_response.get('login_rank') == 2):
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get login_rank: 2 (Banker)')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get login_rank: '+json_response.get('login_rank')+' != 2')
            
            elif (permission == 'WebMaster'):
                if(json_response.get('login_rank') == 3):
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get login_rank: 3 (WebMaster)')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get login_rank: '+json_response.get('login_rank')+' != 3')
            
            elif (permission == 'Agent'):
                if(json_response.get('login_rank') == 0):
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get login_rank: 0 (Agent')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get login_rank: '+json_response.get('login_rank')+' != 0)')
                
        else:
            result_list.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_profile... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminPartnerTypeList(res_log, permission, typeName, typeId, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_partner_type_list', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(return_value):
            result_list.append('PASS')
            res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
            res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            json_response = json.loads(response_data)
            if (permission == 'Boss'):
                for json_type in list(json_response):
                    if(json_type['pt_type_name'] == typeName):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get pt_type_name: '+json_type['pt_type_name'])
                        if(json_type['pt_type_id'] == typeId):
                            res_log = WriteDebugLog(res_log, print_tab+'- Success get pt_type_id: '+json_type['pt_type_id'])
                            result_list2.append('PASS')
                            break
                        else:
                            result_list2.append('FAIL')
                            res_log = WriteDebugLog(res_log, print_tab+'- Fail get pt_type_id: '+json_type['pt_type_id']+' != '+typeId)
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail get pt_type_name: '+json_type['pt_type_name']+' != '+typeName)
                        result_list2.append('FAIL')
            elif (permission == 'Banker'):
                for json_type in list(json_response):
                    if(json_type['pt_type_name'] == typeName):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get pt_type_name: '+json_type['pt_type_name'])
                        if(json_type['pt_type_id'] == typeId):
                            res_log = WriteDebugLog(res_log, print_tab+'- Success get pt_type_id: '+json_type['pt_type_id'])
                            result_list2.append('PASS')
                            break
                        else:
                            result_list2.append('FAIL')
                            res_log = WriteDebugLog(res_log, print_tab+'- Fail get pt_type_id: '+json_type['pt_type_id']+' != '+typeId)
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail get pt_type_name: '+json_type['pt_type_name']+' != '+typeName)
                        result_list2.append('FAIL')
            elif(permission =='WebMaster' or permission =='Agent'):
                result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
                if(result):
                    typeId = ''
                    result_list2.append('PASS')
                else:
                    result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'-No login permission.')
                return (res_log, False, '')
        else:
            result_list.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_partner_type_list... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('PASS' in result_list2):
            return (res_log, True)
        else:
            return (res_log, False)


def AdminPartnerTypeInfo(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_partner_type_info', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(return_value):
            if(permission =='WebMaster' or permission == 'Agent'):
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
                if(result):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                if(json_response.get('accCont07').get('bc')):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
        else:
            result_list.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_partner_type_info... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminPartnerCreate(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_partner_create', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(return_value):
            result_list.append('PASS')
            res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
            res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
        else:
            result_list.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_partner_create... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminPartnerListFrame(res_log, permission, searchAcc, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_partner_list_frame', 'API.api_path', 'api/partner/list/frame')
        elif(web_or_mobile == 'Mobile'):
            ReplaceIniValue('admin_partner_list_frame', 'API.api_path', 'api/partner/list/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_partner_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        
        if(return_value):
            result_list.append('PASS')
            res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
            res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            soup = BeautifulSoup(response_data, 'html.parser')
            if(web_or_mobile =='Web'):
                partnerId = soup.find('a',attrs={'alt':'新增'}).get('id')
                if(permission == 'Boss'):
#                     ReplaceIniValue('setting', 'API.partnerid', my_attribute)
                    if(partnerId):
                        result_list2.append('PASS')
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get partnerId: '+partnerId)
                    else:
                        result_list2.append('FAIL')
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail get partnerId')
                
                elif(permission == 'Banker'):
#                     ReplaceIniValue('setting', 'API.agentid2', my_attribute)
                    if(partnerId):
                        result_list2.append('PASS')
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get webMasterId2: '+partnerId)
                    else:
                        result_list2.append('FAIL')
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail get webMasterId2')
                
                elif(permission == 'WebMaster'):
#                     ReplaceIniValue('setting', 'API.agent_id_level4', my_attribute)
                    if(partnerId):
                        result_list2.append('PASS')
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get agent_id_level4: '+partnerId)
                    else:
                        result_list2.append('FAIL')
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail get agent_id_level4')
                
                elif(permission =='Agent'):
                    # Should be modified
#                     current_user = IniValue('setting', 'API.agentacc')
                    res_log = WriteDebugLog(res_log, print_tab+'-No login permission.')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'-No login permission.')
                    return (res_log, False)
            else:
                my_attribute2 = soup.find('div', class_='crm-name')
                partnerId = my_attribute2.get('id')
                my_string = str(my_attribute2.string).replace('\n','').replace(' ','')
                if(partnerId):
                    if(permission == 'Boss'):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get partnerId: '+partnerId)
                        if(my_string == searchAcc):
                            result_list2.append('PASS')
#                             ReplaceIniValue('setting', 'API.partnerid', my_attribute2.get('id'))
                            res_log = WriteDebugLog(res_log, print_tab+'- Success get partnerName: '+searchAcc)
                        else:
                            result_list2.append('FAIL')
                            res_log = WriteDebugLog(res_log, print_tab+'- Fail get partnerName')
                    elif(permission == 'Banker'):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get webMasterId2: '+partnerId)
                        if(my_string == searchAcc):
                            result_list2.append('PASS')
#                             ReplaceIniValue('setting', 'API.agentid2', my_attribute2.get('id'))
                            res_log = WriteDebugLog(res_log, print_tab+'- Success get webMasterAcc2: '+searchAcc)
                        else:
                            result_list2.append('FAIL')
                            res_log = WriteDebugLog(res_log, print_tab+'- Fail get webMasterAcc2')
                    
                    elif(permission == 'WebMaster'):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get agent_id_level4: '+partnerId)
                        if(my_string == searchAcc):
                            result_list2.append('PASS')
#                             ReplaceIniValue('setting', 'API.agent_id_level4', my_attribute2.get('id'))
                            res_log = WriteDebugLog(res_log, print_tab+'- Success get agent_level4: '+searchAcc)
                        else:
                            result_list2.append('FAIL')
                            res_log = WriteDebugLog(res_log, print_tab+'- Fail get agent_level4')
                    elif(permission =='Agent'):
                        # Should be modified
#                         current_user = IniValue('setting', 'API.agentacc')
                        res_log = WriteDebugLog(res_log, print_tab+'-No login permission.')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'-No login permission.')
                        return (res_log, False)
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'-my_attribute2 getid: None')
                    return (res_log, False)
        else:
            result_list.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_partner_list_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, '')
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False, '')
        else:
            return (res_log, True, partnerId)


def AdminDomainDelete(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_domain_delete', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'WebMaster' or permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_domain_delete... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminDomainCreate(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_domain_create', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Banker'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'WebMaster' or permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_domain_create... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminDomainListFrame(res_log, permission, webName, webId, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_webPlayer_domain_list_frame', 'API.api_path', 'api/webPlayer/domain/list/frame')
        else:
            ReplaceIniValue('admin_webPlayer_domain_list_frame', 'API.api_path', 'api/webPlayer/domain/list/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_domain_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss' or permission == 'Banker'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                soup = BeautifulSoup(response_data, 'html.parser')
                if(web_or_mobile == 'Web'):
                    my_attribute = soup.find('a',attrs={'href':'web_url_edit.html'}).get('id')
                else:
                    my_attribute = soup.find('a',attrs={'alt':'修改'}).get('id')
                if(my_attribute):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get webdomainid: '+my_attribute)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get webdomainid')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                my_attribute = ''
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                my_attribute = ''
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_domain_list_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, '')
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False, '')
        else:
            return (res_log, True, my_attribute)


# def AdminDomainCreateGet(res_log, permission, web_or_mobile = 'Web'):
#     try:
#         result_list = []
#         return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_domain_create_get', True, False)
#         WriteLog(print_tab+'Response data: '+ response_data)
#         if(permission == 'Boss' or permission == 'Banker'):
#             if(return_value):
#                 result_list.append('PASS')
#                 res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
#                 res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
#             else:
#                 result_list.append('FAIL')
#                 res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
#         elif(permission == 'WebMaster' or permission == 'Agent'):
#             result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
#             if(result):
#                 res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
#                 result_list.append('PASS')
#             else:
#                 res_log = WriteDebugLog(res_log, print_tab+'- System error')
#                 result_list.append('FAIL')
#         else:
#             result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
#             if(result):
#                 res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
#                 result_list.append('FAIL')
#             else:
#                 res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
#                 result_list.append('PASS')
#     except Exception as e:
#         result_list.append('FAIL')
#         res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_domain_create_get... %s' % str(e))
#     finally:
#         res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
#     WriteLog(result_list)
#     if('FAIL' in result_list or not result_list):
#         return (res_log, False)
#     else:
#         return (res_log, True)


def AdminDomainEditGet(res_log, permission, CompareAcc, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_domain_edit_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                Boss_Acc = json_response['pt_acc']
                if(Boss_Acc == CompareAcc):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get BossAcc: '+CompareAcc)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get BossAcc: '+Boss_Acc+' != '+CompareAcc)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Banker'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                banker_Acc = json_response['pt_acc']
                if(banker_Acc == CompareAcc):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get bankerAcc: '+CompareAcc)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get bankerAcc: '+banker_Acc+' != '+CompareAcc)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_web_domain_edit_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminDomainEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_domain_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss' or permission == 'Banker'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_domain_edit... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebCreateGetFrame(res_log, permission, webDomain, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_webPlayer_web_create_get_frame', 'API.api_path', 'api/webPlayer/web/create/get/frame')
        else:
            ReplaceIniValue('admin_webPlayer_web_create_get_frame', 'API.api_path', 'api/webPlayer/web/create/get/frame/m')
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_web_create_get_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        
        if(permission == 'Boss' or permission == 'Banker'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                soup = BeautifulSoup(response_data, 'html.parser')
                for each_webDomain in webDomain.split(', '):
                    soup_lis = soup.find_all('li')
                    for soup_li in soup_lis:
                        soup_divs = soup_li.find_all('div', id=True)
                        for soup_div in soup_divs:
                            web_domain = str(soup_div.string).replace('\n','').replace(' ','')
                            if(web_domain == each_webDomain):
                                webdomain_id = soup_div.get('id')
                                res_log = WriteDebugLog(res_log, print_tab+'- Available webDomain for mount: '+each_webDomain)
                                res_log = WriteDebugLog(res_log, print_tab+'- Available webDomainId for mount: '+webdomain_id)
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
                        if('PASS' in result_list2):
                            break
                    if('PASS' in result_list2):
                        break
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_web_create_get_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('PASS' in result_list2):
            return (res_log, True)
        else:
            return (res_log, False)


def AdminWebCreate(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_web_create', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss' or permission == 'Banker'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'WebMaster' or permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_web_create... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebListFrame(res_log, permission, webName, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_webPlayer_web_list_frame', 'API.api_path', 'api/webPlayer/web/list/frame')
        else:
            ReplaceIniValue('admin_webPlayer_web_list_frame', 'API.api_path', 'api/webPlayer/web/list/frame/m')
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_web_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss' or permission == 'Banker'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                soup = BeautifulSoup(response_data, 'html.parser')
                soup_lis = soup.find_all("li")
                for soup_li in soup_lis:
                    soup_divs = soup_li.find_all("div")
                    for soup_div in soup_divs:
                        if(str(soup_div.string).replace('\n','').replace(' ','') == webName):
                            res_log = WriteDebugLog(res_log, print_tab+'- Success get webName: '+webName)
                            webId = soup_li.find('a', id=True).get('id')
                            if(permission == 'Boss'):
    #                             ReplaceIniValue('setting', 'API.webId', webId)
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get webId: '+webId)
                            elif(permission == 'Banker'):
    #                             ReplaceIniValue('setting', 'API.webId2', webId)
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get webId2: '+webId)
                            elif(permission == 'WebMaster' or permission == 'Agent'):
    #                             ReplaceIniValue('setting', 'API.webId', webId)
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get webId: '+webId)
                            else:
                                res_log = WriteDebugLog(res_log, print_tab+'-No permission.')
                                return (res_log, False)
                            result_list2.append('PASS')
                            break
                        else:
                            result_list2.append('FAIL')
                    if('PASS' in result_list2):
                        break
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                webId = ''
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                webId = ''
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_web_list_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, '')
    else:
        if('PASS' in result_list2):
            return (res_log, True, webId)
        else:
            return (res_log, False, '')


def AdminWebEditGetFrame(res_log, permission, webDomain, webDomainId, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_webPlayer_web_list_frame', 'API.api_path', 'api/webPlayer/web/list/frame')
        else:
            ReplaceIniValue('admin_webPlayer_web_list_frame', 'API.api_path', 'api/webPlayer/web/list/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_web_edit_get_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss' or permission == 'Banker'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
    #             webdomainid = IniValue('setting', 'API.webdomainid')
    #             webdomain = IniValue('setting', 'API.webdomain')
                soup = BeautifulSoup(response_data, 'html.parser')
                soup_webdomainid = soup.find("div", id=webDomainId)
                webdomain_name = str(soup_webdomainid.string).replace(' ','').replace('\n','')
                if(webdomain_name == webDomain):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get webDomain: '+webDomain)
                    result_list2.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get webDomain: '+webdomain_name+' != '+webDomain)
                    result_list2.append('FAIL')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_web_edit_get_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        #===================================================================
        # use = 0: UI status = 申請
        # use = 1: UI status = 建置
        # use = 2: UI status = 完成
        # use = 3: UI status = 啟用
        # use = 4: UI status = 停用
        #===================================================================
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_web_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss' or permission == 'Banker'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_web_edit... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminPartnerTypePermissionGet(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        str_permission_final = ''
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_partner_type_permission_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss' or permission == 'Banker'):
            if(return_value):
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                accCont01 = json_response.get('accCont01')
                if(accCont01.get('ir').get('ir_r') == 1):
                    result_list.append(JsonValueCompare(response_data, 'accCont01|ir', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont02|qs', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|orp', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|orpvd', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|orb', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|orw', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|ord', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|orplr', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|prr', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|wr', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|plrr', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|or', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|gl', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont04|ee', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont04|dp', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont05|pt', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont05|prt', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont05|ptt', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont05|ptr', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|dm', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|lv', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|wb', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|plr', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|plrt', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|plrd', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|promo', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|cms', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|nt', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|ms', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|ma', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|st', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|risk', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|gs', '1'))
    #                 result_list.append(JsonValueCompare(response_data, 'accCont06|pr', '1'))
    #                 result_list.append(JsonValueCompare(response_data, 'accCont07|pvd', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont07|bc', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont07|pm', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont07|po', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont08|md', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont08|mw', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont08|bh', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont08|er', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont08|bt', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont08|rs', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont08|rp', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont08|rfs', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont08|wa', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont08|ia', '1'))
                    
                    ir_ = json_response.get('accCont01').get('ir')
                    qs_ = json_response.get('accCont02').get('qs')
                    orp_ = json_response.get('accCont03').get('orp')
                    orpvd_ = json_response.get('accCont03').get('orpvd')
                    orb_ = json_response.get('accCont03').get('orb')
                    orw_ = json_response.get('accCont03').get('orw')
                    ord_ = json_response.get('accCont03').get('ord')
                    orplr_ = json_response.get('accCont03').get('orplr')
                    prr_ = json_response.get('accCont03').get('prr')
                    wr_ = json_response.get('accCont03').get('wr')
                    plrr_ = json_response.get('accCont03').get('plrr')
                    or_ = json_response.get('accCont03').get('or')
                    gl_ = json_response.get('accCont03').get('gl')
                    ee_ = json_response.get('accCont04').get('ee')
                    dp_ = json_response.get('accCont04').get('dp')
                    pt_ = json_response.get('accCont05').get('pt')
                    prt_ = json_response.get('accCont05').get('prt')
                    ptt_ = json_response.get('accCont05').get('ptt')
                    ptr_ = json_response.get('accCont05').get('ptr')
                    dm_ = json_response.get('accCont06').get('dm')
                    lv_ = json_response.get('accCont06').get('lv')
                    wb_ = json_response.get('accCont06').get('wb')
                    plr_ = json_response.get('accCont06').get('plr')
                    plrt_ = json_response.get('accCont06').get('plrt')
                    plrd_ = json_response.get('accCont06').get('plrd')
                    promo_ = json_response.get('accCont06').get('promo')
                    cms_ = json_response.get('accCont06').get('cms')
                    nt_ = json_response.get('accCont06').get('nt')
                    ms_ = json_response.get('accCont06').get('ms')
                    ma_ = json_response.get('accCont06').get('ma')
                    risk_ = json_response.get('accCont06').get('risk')
                    st_ = json_response.get('accCont06').get('st')
                    gs_ = json_response.get('accCont06').get('gs')
                    bc_ = json_response.get('accCont07').get('bc')
                    pm_ = json_response.get('accCont07').get('pm')
                    po_ = json_response.get('accCont07').get('po')
                    md_ = json_response.get('accCont08').get('md')
                    mw_ = json_response.get('accCont08').get('mw')
                    bh_ = json_response.get('accCont08').get('bh')
                    er_ = json_response.get('accCont08').get('er')
                    bt_ = json_response.get('accCont08').get('bt')
                    rs_ = json_response.get('accCont08').get('rs')
                    rp_ = json_response.get('accCont08').get('rp')
                    rfs_ = json_response.get('accCont08').get('rfs')
                    wa_ = json_response.get('accCont08').get('wa')
                    ia_ = json_response.get('accCont08').get('ia')
    #                 pr_ = json_response.get('accCont06').get('pr')
    #                 pvd_ = json_response.get('accCont07').get('pvd')
                    json_permission_final = {}
                    json_permission_final = ({**ir_, **qs_, **orp_, **orpvd_, **orb_, **orw_, **ord_, **orplr_, **prr_, **wr_, **plrr_, **or_, **gl_, **ee_, **dp_, 
                                              **pt_, **prt_, **ptt_, **dm_, **lv_, **wb_, **plr_, **plrt_, **plrd_, **promo_, **cms_, **nt_, **ms_, **ma_, **risk_, 
                                              **st_, **gs_, **ptr_, **bc_, **pm_, **po_, **md_, **mw_, **bh_, **er_, **bt_, **rs_, **rp_, **rfs_, **wa_, **ia_})
                    str_permission_final = str(json_permission_final).replace("'",'"').replace(' ','')
                
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- JSON response error.')
                
        elif(permission =='WebMaster' or permission =='Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_partner_type_permission_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, str_permission_final)
    else:
        return (res_log, True, str_permission_final)


def AdminPartnerTypeCreate(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_partner_type_create', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss' or permission == 'Banker'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                if(permission =='WebMaster' or permission =='Agent'):
                    result_denine, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
                    if(result_denine):
                        result_list.append('PASS')
                    else:
                        result_list.append('FAIL')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_partner_type_create... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminPartnerTypeListFrame(res_log, permission, typeName, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_partner_type_list_frame', 'API.api_path', 'api/partner/type/list/frame')
            return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_partner_type_list_frame', False, False)
            WriteLog(print_tab+'Response data: '+ response_data)
            if(return_value):
                if(permission == 'Boss'):
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                    res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                    soup = BeautifulSoup(response_data, 'html.parser')
                    soup_lis = soup.find_all("li")
                    for soup_li in soup_lis:
                        soup_divs = soup_li.find_all("div", class_=True)
                        for soup_div in soup_divs:
                            if((str(soup_div.string).replace('\n','').replace(' ','')) == typeName):
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get typeName: '+typeName)
                                typeId = soup_li.find("a",attrs={'href':'client_type_edit.html'}).get('id')
#                                 ReplaceIniValue('setting', 'API.typeid', typeId)
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get typeId: '+typeId)
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
                        if('PASS' in result_list2):
                            break
                elif(permission == 'Banker'):
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                    res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                    soup = BeautifulSoup(response_data, 'html.parser')
                    soup_lis = soup.find_all("li")
                    for soup_li in soup_lis:
                        soup_divs = soup_li.find_all("div", class_=True)
                        for soup_div in soup_divs:
                            if((str(soup_div.string).replace('\n','').replace(' ','')) == typeName):
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get typeName: '+typeName)
                                typeId = soup_li.find("a",attrs={'href':'client_type_edit.html'}).get('id')
#                                 ReplaceIniValue('setting', 'API.typeid2', typeId)
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get typeId2: '+typeId)
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
                        if('PASS' in result_list2):
                            break
                elif(permission == 'WebMaster' or permission == 'Agent'):
                    result_list.append('PASS')
                    result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
                    if(result):
                        typeId = ''
                        result_list2.append('PASS')
                    else:
                        result_list2.append('FAIL')
                
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            ReplaceIniValue('admin_partner_type_list_frame', 'API.api_path', 'api/partner/type/list/frame/m')
            return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_partner_type_list_frame', False, False)
            WriteLog(print_tab+'Response data: '+ response_data)
            if(return_value):
                if(permission == 'Boss'):
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                    res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                    soup = BeautifulSoup(response_data, 'html.parser')
                    soup_lis = soup.find_all("li")
                    for soup_li in soup_lis:
                        soup_divs = soup_li.find_all("div", class_=True)
                        for soup_div in soup_divs:
                            if((str(soup_div.string).replace('\n','').replace(' ','')) == typeName):
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get typeName: '+typeName)
                                typeId = soup_li.find("a",class_=True).get('id')
#                                 ReplaceIniValue('setting', 'API.typeid2', typeId)
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get typeId2: '+typeId)
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
                        if('PASS' in result_list2):
                            break
                elif(permission == 'Banker'):
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                    res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                    soup = BeautifulSoup(response_data, 'html.parser')
                    soup_lis = soup.find_all("li")
                    for soup_li in soup_lis:
                        soup_divs = soup_li.find_all("div", class_=True)
                        for soup_div in soup_divs:
                            if((str(soup_div.string).replace('\n','').replace(' ','')) == typeName):
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get typeName2: '+typeName)
                                typeId = soup_li.find("a",class_=True).get('id')
#                                 ReplaceIniValue('setting', 'API.typeid2', typeId)
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get typeId2: '+typeId)
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
                        if('PASS' in result_list2):
                            break
                elif(permission == 'WebMaster' or permission == 'Agent'):
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                    res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                    result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
                    if(result):
                        typeId = ''
                        result_list2.append('PASS')
                    else:
                        result_list2.append('FAIL')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_partner_type_list_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, '')
    else:
        if('PASS' in result_list2):
            return (res_log, True, typeId)
        else:
            return (res_log, False, '')


def AdminPartnerTypeGet(res_log, permission, typeName, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_partner_type_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(return_value):
            if(permission == 'WebMaster' or permission == 'Agent'):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
                if(result):
                    result_list2.append('PASS')
                else:
                    result_list2.append('FAIL')
            else:
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                if(json_response.get('typeName') == typeName):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get typeName: '+typeName)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get typeName: '+json_response.get('typeName')+' != '+typeName)
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_partner_type_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminPartnerTypeEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_partner_type_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(return_value):
            result_list.append('PASS')
            res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
            res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
        else:
            result_list.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_partner_type_edit... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminPartnerPermissionGet(res_log, permission, webId, typeName, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        typeId = ''
        str_currency = ''
        str_permission_final = ''
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_partner_permission_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        currency = GetJsonValue(response_data, 'currency')
        v_currency = GetJsonValue(response_data, 'v_currency')
        print(currency == 'True')
        if(v_currency == 'True'):
            all_currency = list(currency.keys())+list(v_currency.keys())
        else:
            all_currency = list(currency.keys())
        if(permission == 'Initial'):
            if(return_value):
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                
                web_id = GetJsonValue(response_data, 'web_list')
                parent_acc = GetJsonValue(response_data, 'parent_acc')
                parent_rank = GetJsonValue(response_data, 'parent_rank')
                percent = GetJsonValue(response_data, 'percent')
                if(web_id== webId):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get webid: '+web_id)
                    str_currency = ', '.join(all_currency)
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get currency: '+str_currency)
                    result_list.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get webid: '+web_id+' != '+webId)
                    result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- Success get Parent Acc: '+parent_acc)
                res_log = WriteDebugLog(res_log, print_tab+'- Success get Parent Rank (1: Boss): '+str(parent_rank))
                res_log = WriteDebugLog(res_log, print_tab+'- Success get percent: '+percent)
                
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        
        elif(permission == 'Boss'):
            if(return_value):
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                percent = GetJsonValue(response_data, 'percent')
                res_log = WriteDebugLog(res_log, print_tab+'- Success get percent: '+percent)
                list_webs = json_response.get('web_list')
                for list_web in list_webs:
                    if(list_web['web_id'] == webId):
                        str_currency = ', '.join(all_currency)
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get webId: '+webId)
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get currency: '+str_currency)
                        result_list.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail get webId: '+list_web['web_id']+' != '+webId)
                        result_list.append('FAIL')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        
        elif(permission == 'Banker'):
            if(return_value):
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                percent = GetJsonValue(response_data, 'percent')
                res_log = WriteDebugLog(res_log, print_tab+'- Success get percent: '+percent)
                list_webs = json_response.get('web_list')
                for list_web in list_webs:
                    if(list_web['web_id'] == webId):
                        str_currency = ', '.join(all_currency)
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get webId2: '+webId)
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get currency: '+str_currency)
                        result_list.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail get webId2: '+list_web['web_id']+' != '+webId)
                        result_list.append('FAIL')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
            
        result_list2.append(JsonValueCompare(response_data, 'accCont01|ir', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont02|qs', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont03|orp', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont03|orpvd', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont03|orb', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont03|orw', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont03|ord', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont03|orplr', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont03|prr', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont03|wr', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont03|plrr', '1'))
        if(permission == 'Initial'):
            result_list2.append(JsonValueCompare(response_data, 'accCont03|or', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont03|gl', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont04|ee', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont04|dp', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont05|pt', '1'))
        if(permission == 'Initial'):
            result_list2.append(JsonValueCompare(response_data, 'accCont05|prt', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont05|ptt', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont05|ptr', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont06|dm', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont06|lv', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont06|wb', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont06|plr', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont06|plrt', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont06|plrd', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont06|promo', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont06|cms', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont06|nt', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont06|ms', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont06|ma', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont06|st', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont06|risk', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont06|gs', '1'))
#                 result_list2.append(JsonValueCompare(response_data, 'accCont06|pr', '1'))
#                 result_list2.append(JsonValueCompare(response_data, 'accCont07|pvd', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont07|bc', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont07|pm', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont07|po', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont08|md', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont08|mw', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont08|bh', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont08|er', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont08|bt', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont08|rs', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont08|rp', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont08|rfs', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont08|wa', '1'))
        result_list2.append(JsonValueCompare(response_data, 'accCont08|ia', '1'))
        
        json_response = json.loads(response_data)
        type_lists = list(json_response.get('type_list'))
        for each_type_list in type_lists:
            if(each_type_list.get('pt_type_name') == typeName):
                typeId = each_type_list.get('pt_type_id')
                res_log = WriteDebugLog(res_log, print_tab+'- Success get (typeName, typeId): ('+typeName+', '+typeId+')')
                break
        ir_ = json_response.get('accCont01').get('ir')
        qs_ = json_response.get('accCont02').get('qs')
        orp_ = json_response.get('accCont03').get('orp')
        orpvd_ = json_response.get('accCont03').get('orpvd')
        orb_ = json_response.get('accCont03').get('orb')
        orw_ = json_response.get('accCont03').get('orw')
        ord_ = json_response.get('accCont03').get('ord')
        orplr_ = json_response.get('accCont03').get('orplr')
        prr_ = json_response.get('accCont03').get('prr')
        wr_ = json_response.get('accCont03').get('wr')
        plrr_ = json_response.get('accCont03').get('plrr')
        if(permission == 'Initial'):
            or_ = json_response.get('accCont03').get('or')
        gl_ = json_response.get('accCont03').get('gl')
        ee_ = json_response.get('accCont04').get('ee')
        dp_ = json_response.get('accCont04').get('dp')
        pt_ = json_response.get('accCont05').get('pt')
        if(permission == 'Initial'):
            prt_ = json_response.get('accCont05').get('prt')
        ptt_ = json_response.get('accCont05').get('ptt')
        ptr_ = json_response.get('accCont05').get('ptr')
        dm_ = json_response.get('accCont06').get('dm')
        lv_ = json_response.get('accCont06').get('lv')
        wb_ = json_response.get('accCont06').get('wb')
        plr_ = json_response.get('accCont06').get('plr')
        plrt_ = json_response.get('accCont06').get('plrt')
        plrd_ = json_response.get('accCont06').get('plrd')
        promo_ = json_response.get('accCont06').get('promo')
        cms_ = json_response.get('accCont06').get('cms')
        nt_ = json_response.get('accCont06').get('nt')
        ms_ = json_response.get('accCont06').get('ms')
        ma_ = json_response.get('accCont06').get('ma')
        risk_ = json_response.get('accCont06').get('risk')
        st_ = json_response.get('accCont06').get('st')
        gs_ = json_response.get('accCont06').get('gs')
        bc_ = json_response.get('accCont07').get('bc')
        pm_ = json_response.get('accCont07').get('pm')
        po_ = json_response.get('accCont07').get('po')
        md_ = json_response.get('accCont08').get('md')
        mw_ = json_response.get('accCont08').get('mw')
        bh_ = json_response.get('accCont08').get('bh')
        er_ = json_response.get('accCont08').get('er')
        bt_ = json_response.get('accCont08').get('bt')
        rs_ = json_response.get('accCont08').get('rs')
        rp_ = json_response.get('accCont08').get('rp')
        rfs_ = json_response.get('accCont08').get('rfs')
        wa_ = json_response.get('accCont08').get('wa')
        ia_ = json_response.get('accCont08').get('ia')
#                 pr_ = json_response.get('accCont06').get('pr')
#                 pvd_ = json_response.get('accCont07').get('pvd')
        json_permission_final = {}
        if(permission == 'Initial'):
            json_permission_final = ({**ir_, **qs_, **orp_, **orpvd_, **orb_, **orw_, **ord_, **orplr_, **prr_, **wr_, **plrr_, **or_, **gl_, **ee_, **dp_, 
                                      **pt_, **prt_, **ptt_, **dm_, **lv_, **wb_, **plr_, **plrt_, **plrd_, **promo_, **cms_, **nt_, **ms_, **ma_, **risk_, 
                                      **st_, **gs_, **ptr_, **bc_, **pm_, **po_, **md_, **mw_, **bh_, **er_, **bt_, **rs_, **rp_, **rfs_, **wa_, **ia_})
        elif(permission == 'Boss'):
            json_permission_final = ({**ir_, **qs_, **orp_, **orpvd_, **orb_, **orw_, **ord_, **orplr_, **prr_, **wr_, **plrr_, **gl_, **ee_, **dp_, 
                                      **pt_, **ptt_, **dm_, **lv_, **wb_, **plr_, **plrt_, **plrd_, **promo_, **cms_, **nt_, **ms_, **ma_, **risk_, 
                                      **st_, **gs_, **ptr_, **bc_, **pm_, **po_, **md_, **mw_, **bh_, **er_, **bt_, **rs_, **rp_, **rfs_, **wa_, **ia_})
#         elif(permission == 'Banker'):
#             json_permission_final = ({**ir_, **qs_, **orp_, **orpvd_, **orb_, **orw_, **ord_, **orplr_, **prr_, **wr_, **plrr_, **gl_, **ee_, **dp_, 
#                                       **pt_, **ptt_, **dm_, **lv_, **wb_, **plr_, **plrt_, **plrd_, **promo_, **cms_, **nt_, **ms_, **ma_, **risk_, 
#                                       **st_, **gs_, **ptr_, **bc_, **pm_, **po_, **md_, **mw_, **bh_, **er_, **bt_, **rs_, **rp_, **rfs_, **wa_, **ia_})
        str_permission_final = str(json_permission_final).replace("'",'"').replace(' ','')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_partner_permission_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, str_currency, str_permission_final, typeId)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False, str_currency, str_permission_final, typeId)
        else:
            return (res_log, True, str_currency, str_permission_final, typeId)


def AdminPartnerListSubFrame(res_log, permission, agent_acc, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_partner_list_sub_frame', 'API.api_path', 'api/partner/list/sub/frame')
        else:
            ReplaceIniValue('admin_partner_list_sub_frame', 'API.api_path', 'api/partner/list/sub/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_partner_list_sub_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(return_value):
            result_list.append('PASS')
            res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
            res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
#             agent_acc = IniValue('setting', 'API.agentacc')
            soup = BeautifulSoup(response_data, 'html.parser')
            soup_lis = soup.find_all('li')
            if(web_or_mobile == 'Web'):
                for soup_li in soup_lis:
                    soup_divs = soup_li.find_all('div', class_=True)
                    for soup_div in soup_divs:
                        if(str(soup_div.string).replace('\n','').replace(' ','') == agent_acc):
                            res_log = WriteDebugLog(res_log, print_tab+'- Success get agent_acc: '+agent_acc)
                            soup_id = soup_li.find('a', attrs={'alt':'新增'})
                            agent_id = soup_id.get('id')
                            res_log = WriteDebugLog(res_log, print_tab+'- Success get agent_id: '+agent_id)
#                             ReplaceIniValue('setting', 'API.webMasterId', agent_id)
                            result_list2.append('PASS')
                            break
                        else:
                            result_list2.append('FAIL')
                    if('PASS' in result_list2):
                        break
                
            else:
                for soup_li in soup_lis:
                    soup_divs = soup_li.find_all('div', class_=True)
                    for soup_div in soup_divs:
                        if(str(soup_div.string).replace('\n','').replace(' ','') == agent_acc):
                            res_log = WriteDebugLog(res_log, print_tab+'- Success get agent_acc: '+agent_acc)
                            agent_id = soup_div.get('id')
                            res_log = WriteDebugLog(res_log, print_tab+'- Success get agent_id: '+agent_id)
#                             ReplaceIniValue('setting', 'API.webMasterId', agent_id)
                            result_list2.append('PASS')
                            break
                        else:
                            result_list2.append('FAIL')
                    if('PASS' in result_list2):
                        break
        else:
            result_list.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_partner_list_sub_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, '')
    else:
        if('PASS' in result_list2):
            return (res_log, True, agent_id)
        else:
            return (res_log, False, '')


def AdminPartnerInfoGet(res_log, permission, ptId, acc, webId, banker_percent, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_partner_info_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(return_value):
            res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
            res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            json_response = json.loads(response_data)
            
            if(permission == 'Initial'):
                if(json_response.get('rank') == 2):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get rank: 2 (Banker)')
                    result_list.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get rank: '+json_response.get('rank')+' != 2')
                    result_list.append('FAIL')
            
            elif(permission == 'Boss'):
                if(json_response.get('rank') == 3):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get rank: 3 (WebMaster)')
                    result_list.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get rank: '+json_response.get('rank')+' != 2')
                    result_list.append('FAIL')
            
            elif(permission == 'Banker'):
                if(json_response.get('rank') == 3):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get rank: 3 (WebMaster2)')
                    result_list.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get rank: '+json_response.get('rank')+' != 2')
                    result_list.append('FAIL')
            
            if(json_response.get('pt_acc') == acc):
                res_log = WriteDebugLog(res_log, print_tab+'- Success get pt_acc: '+acc)
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- Fail get pt_acc: '+json_response.get('pt_acc')+' != '+acc)
                result_list.append('FAIL')
            
            if(json_response.get('pt_pwd') == acc):
                res_log = WriteDebugLog(res_log, print_tab+'- Success get pt_pwd: '+acc)
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- Fail get pt_pwd: '+json_response.get('pt_pwd')+' != '+acc)
                result_list.append('FAIL')
            
            if(json_response.get('pt_id') == ptId):
                res_log = WriteDebugLog(res_log, print_tab+'- Success get pt_id: '+ptId)
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- Fail get pt_id: '+json_response.get('pt_id')+' != '+ptId)
                result_list.append('FAIL')
            
            if(json_response.get('percent') == banker_percent):
                res_log = WriteDebugLog(res_log, print_tab+'- Success get percent: '+banker_percent)
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- Fail get percent: '+json_response.get('percent')+' != '+banker_percent)
                result_list.append('FAIL')
            
            result_list2.append(JsonValueCompare(response_data, 'accCont01|ir', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont02|qs', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont03|orp', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont03|orpvd', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont03|orb', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont03|orw', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont03|ord', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont03|orplr', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont03|prr', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont03|wr', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont03|plrr', '1'))
            if(permission == 'Initial'):
                result_list2.append(JsonValueCompare(response_data, 'accCont03|or', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont03|gl', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont04|ee', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont04|dp', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont05|pt', '1'))
            if(permission == 'Initial'):
                result_list2.append(JsonValueCompare(response_data, 'accCont05|prt', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont05|ptt', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont05|ptr', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont06|dm', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont06|lv', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont06|wb', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont06|plr', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont06|plrt', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont06|plrd', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont06|promo', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont06|cms', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont06|nt', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont06|ms', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont06|ma', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont06|st', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont06|risk', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont06|gs', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont07|bc', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont07|pm', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont07|po', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont08|md', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont08|mw', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont08|bh', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont08|er', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont08|bt', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont08|rs', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont08|rp', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont08|rfs', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont08|wa', '1'))
            result_list2.append(JsonValueCompare(response_data, 'accCont08|ia', '1'))
            result_list2.append(GetJsonValue(response_data, 'currency|CNY') == 1)
#             result_list2.append(JsonValueCompare(response_data, 'v_currency', '1'))
#                 if(json_response.get('banker_website')[0].get('web_id') == webId):
#                     res_log = WriteDebugLog(res_log, print_tab+'- Success get banker_website: '+webId)
#                     result_list2.append('PASS')
#                 else:
#                     res_log = WriteDebugLog(res_log, print_tab+'- Fail get banker_website: '+json_response.get('banker_website')[0].get('web_id')+' != '+webId)
#                     result_list2.append('FAIL')
        else:
            result_list.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_partner_info_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminPartnerTypeDelete(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_partner_type_delete', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(return_value):
            res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
            res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            result_response, res_log = CheckPermissionDenied(print_tab, res_log, response_data, 'E04', 'Cannot be deleted')
            if(result_response == True):
                result_list.append('PASS')
            else:
                result_list.append('FAIL')
        else:
            result_list.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_partner_type_delete... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminVipCreateGet(res_log, permission, webName, webDomain, webId, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_vip_create_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        json_response = json.loads(response_data)
        if(permission == 'Boss' or permission == 'Banker'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                if(json_response.get('domain_list').get(webId) == webDomain):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get webDomain: '+webDomain)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get webDomain: '+json_response.get('domain_list').get(webId)+' != '+webDomain)
                
                if(json_response.get('web_name') == webName):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get webName: '+webName)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get webName: '+json_response.get('web_name')+' == '+webName)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_vip_create_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminVipCreate(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_vip_create', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss' or permission == 'Banker'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_vip_create... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in str(result_list) or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminVipListFrame(res_log, permission, vipName, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_webPlayer_vip_list_frame', 'API.api_path', 'api/webPlayer/vip/list/frame')
        else:
            ReplaceIniValue('admin_webPlayer_vip_list_frame', 'API.api_path', 'api/webPlayer/vip/list/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_vip_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss' or permission == 'Banker'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                
                soup = BeautifulSoup(response_data, 'html.parser')
                soup_vipids = soup.find_all("div")
                for soup_vipid in soup_vipids:
                    if(str(soup_vipid.string).replace('\n','').replace(' ','') == vipName):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get vipname: '+vipName)
                        vipId = soup_vipid.get('id')
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get vipid: '+vipId)
                        result_list2.append('PASS')
                        break
                    else:
                        result_list2.append('FAIL')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                vipId = ''
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_vip_list_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, '')
    else:
        if('PASS' in result_list2):
            return (res_log, True, vipId)
        else:
            return (res_log, False, '')


def AdminVipEditGet(res_log, permission, webName, vipId, webdomainId, deposit_times, deposit_total, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_vip_edit_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        json_response = json.loads(response_data)
        if(permission == 'Boss' or permission == 'Banker'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                if(str(json_response.get('deposit_times')) == deposit_times):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success deposit_times: '+deposit_times)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get deposit_times: '+ str(json_response.get('deposit_times'))+' != '+deposit_times)
                
                if(str(json_response.get('deposit_total')) == deposit_total):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success deposit_total: '+deposit_total)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get deposit_total: '+ str(json_response.get('deposit_total'))+' != '+deposit_total)
                
                if(json_response.get('vip_id') == vipId):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get vipId: '+ vipId)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get vipId: '+ json_response.get('vip_id')+' != '+vipId)
                
                if(json_response.get('web_domain_id') == webdomainId):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get webdomainId: '+ webdomainId)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get webdomainId: '+ json_response.get('web_domain_id')+' != '+webdomainId)
                
                if(json_response.get('web_name') == webName):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get webName: '+ webName)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get webName: '+ json_response.get('web_name')+' != '+webName)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_vip_edit_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminVipEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_vip_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss' or permission == 'Banker'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_vip_edit... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminVipDelete(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_vip_delete', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss' or permission == 'Banker'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_vip_delete... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminVipGroupCreateGetFrame(res_log, permission, vipName, vipId, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_webPlayer_vip_group_create_get_frame', 'API.api_path', 'api/webPlayer/vip/group/create/get/frame')
        else:
            ReplaceIniValue('admin_webPlayer_vip_group_create_get_frame', 'API.api_path', 'api/webPlayer/vip/group/create/get/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_vip_group_create_get_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                soup = BeautifulSoup(response_data, 'html.parser')
                if(str(soup.find("div", id=vipId).string).replace('\n','').replace(' ','') == vipName):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get : '+vipName)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get vipName: '+soup.find("div", id=vipId).string.replace('\n','').replace(' ','')+' != '+vipName)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_vip_group_create_get_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminVipGroupCreate(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_vip_group_create', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'WebMaster' or permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_vip_group_create... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminVipGroupListFrame(res_log, permission, vipGroupName, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_webPlayer_vip_group_list_frame', 'API.api_path', 'api/webPlayer/vip/group/list/frame')
        else:
            ReplaceIniValue('admin_webPlayer_vip_group_list_frame', 'API.api_path', 'api/webPlayer/vip/group/list/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_vip_group_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                if(vipGroupName in response_data):
                    soup = BeautifulSoup(response_data, 'html.parser')
                    soup_vipGroupIds = soup.find_all("div")
                    for soup_vipGroupId in soup_vipGroupIds:
                        if(str(soup_vipGroupId.string).replace('\n','').replace(' ','') == vipGroupName):
                            res_log = WriteDebugLog(res_log, print_tab+'- Success get vipGroupName: '+vipGroupName)
                            vipGroupId = soup_vipGroupId.get('id')
                            res_log = WriteDebugLog(res_log, print_tab+'- Success get vipGroupId: '+vipGroupId)
                            result_list2.append('PASS')
                            break
                        else:
                            result_list2.append('FAIL')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                vipGroupId = ''
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                vipGroupId = ''
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_vip_group_list_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, '')
    else:
        if('PASS' in result_list2):
            return (res_log, True, vipGroupId)
        else:
            return (res_log, False, '')


def AdminVipGroupEditGetFrame(res_log, permission, vipName, vipId, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        ReplaceIniValue('admin_webPlayer_vip_group_edit_get_frame', 'API.api_path', 'api/webPlayer/vip/group/edit/get/frame')
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_vip_group_edit_get_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                soup = BeautifulSoup(response_data, 'html.parser')
                if(soup.find("div", id=vipId).string.replace('\n','').replace(' ','') == vipName):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get: '+vipName)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get vipName: '+soup.find("div", id=vipId).string.replace('\n','').replace(' ','')+' != '+vipName)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_vip_group_edit_get_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminVipGroupEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value2, response_time2, response_data2, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_vip_group_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data2)
        if(permission == 'Boss'):
            if(return_value2):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time2)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data2)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data2)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_vip_group_edit... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminVipWebDomainEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_web_vip_domain_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_web_vip_domain_edit... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebVipDomainList(res_log, permission, webdomain, webdomainid, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_web_vip_domain_list', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        json_response = json.loads(response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
#                 {"2922f64a6ff9bcbf73fe114874689309":"10.10.10.220"}
#                 python_dict = {}
#                 python_dict.get(webdomainid) = webdomain
                if(json_response.get(webdomainid) == webdomain):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get webdomain: '+json_response.get(webdomainid))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get webdomain: '+json_response.get(webdomainid)+' != '+webdomain)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_web_vip_domain_list... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminWebVipGroupEditFrame(res_log, permission, vipId, vipName, webDomain, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_webPlayer_web_vip_group_edit_frame', 'API.api_path', 'api/webPlayer/web/vip/group/edit/frame')
        else:
            ReplaceIniValue('admin_webPlayer_web_vip_group_edit_frame', 'API.api_path', 'api/webPlayer/web/vip/group/edit/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_web_vip_group_edit_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                if((vipId in response_data) and (vipName in response_data) and (webDomain in response_data)):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_web_vip_group_edit_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)

def AdminWebVipDomainEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_web_vip_domain_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_web_vip_domain_edit... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)

def AdminWebVipListFrame(res_log, permission, vipGroupName, transferSet, setTime, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_webPlayer_web_vip_list_frame', 'API.api_path', 'api/webPlayer/web/vip/list/frame')
        else:
            ReplaceIniValue('admin_webPlayer_web_vip_list_frame', 'API.api_path', 'api/webPlayer/web/vip/list/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_web_vip_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                soup = BeautifulSoup(response_data, 'html.parser')
                soup_selecteds = soup.find_all("option", selected=True)
                if(web_or_mobile == 'Web'):
                    if(str(soup_selecteds[0].string).replace('\n','').replace(' ','') == vipGroupName):
                        result_list2.append('PASS')
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get vipGroupName: '+vipGroupName)
                    else:
                        result_list2.append('FAIL')
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail get vipGroupName: '+str(soup_selecteds[0].string).replace('\n','').replace(' ','')+' != '+vipGroupName)
                        
                    if(soup_selecteds[1].get('value') == transferSet):
                        result_list2.append('PASS')
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get transferSet: '+transferSet)
                    else:
                        result_list2.append('FAIL')
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail get transferSet: '+soup_selecteds[1].get('value')+' != '+transferSet)
                        
                    if(str(soup_selecteds[2].string).replace('\n','').replace(' ','') == setTime):
                        result_list2.append('PASS')
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get setTime: '+setTime)
                    else:
                        result_list2.append('FAIL')
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail get setTime: '+str(soup_selecteds[2].string).replace('\n','').replace(' ','')+' != '+setTime)
                else:
                    if(str(soup_selecteds[0].string).replace('\n','').replace(' ','') == vipGroupName):
                        result_list2.append('PASS')
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get vipGroupName: '+vipGroupName)
                    else:
                        result_list2.append('FAIL')
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail get vipGroupName: '+str(soup_selecteds[0].string).replace('\n','').replace(' ','')+' != '+vipGroupName)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_web_vip_list_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminVipDomainGet(res_log, permission, webDomainId, webDomain, vipName, transferSet, setTime, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_web_vip_domain_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                if(json_response['domainId'] == webDomainId):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get webDomainId: '+webDomainId)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get webDomainId: '+webDomainId)
                    
                if(json_response['domainUrl'] == webDomain):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get webDomain: '+webDomain)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get webDomain: '+webDomain)
                    
                if(json_response['vipName'] == vipName):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get vipName: '+vipName)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get vipName: '+vipName)
                    
                if(str(json_response['transferSet']) == transferSet):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get transferSet: '+transferSet)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get transferSet: '+transferSet)
                    
                if(json_response['setTime'] == setTime):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get setTime: '+setTime)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get setTime: '+setTime)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_web_vip_domain_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)

def AdminWebProviderListFrame(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_webPlayer_web_provider_list_frame', 'API.api_path', 'api/webPlayer/web/provider/list/frame')
        else:
            ReplaceIniValue('admin_webPlayer_web_provider_list_frame', 'API.api_path', 'api/webPlayer/web/provider/list/frame/m')
        
        provider_ids = ''
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_web_provider_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                soup = BeautifulSoup(response_data, 'html.parser')
                soup_lis = soup.find_all("li")
                if(web_or_mobile == 'Web'):
                    for soup_li in soup_lis:
                        soup_div = soup_li.find('div', class_='operate-box')
                        if(soup_div):
                            provider_id = soup_div.find("a", id=True).get('id')
                            if(provider_id):
                                provider_status = str(soup_li.find("div", class_="status-tag").string).replace('\n','').replace(' ','')
                                provider_name = str(soup_li.find("div", class_="box-15").string).replace('\n','').replace(' ','')
                                if(soup_lis.index(soup_li) > 1):
                                    provider_ids = provider_ids+ ', '+ provider_id
                                else:
                                    provider_ids = provider_ids+ provider_id
                                result_list.append('PASS')
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get provider (name, id, status): ('+provider_name+', '+provider_id+', '+provider_status+')')
                else:
                    for soup_li in soup_lis:
                        soup_divs = soup_li.find_all('div', class_=True)
                        for soup_div in soup_divs:
                            if(soup_div.find("a", id=True)):
                                provider_id = soup_div.find("a", id=True).get('id')
                                if(provider_id):
                                    soup_status = soup_li.find("div", class_="box-15")
                                    provider_status = str(soup_status.find("span", class_=True).string).replace('\n','').replace(' ','')
                                    provider_name = str(soup_li.find("div", class_="box-55").string).replace('\n','').replace(' ','')
                                    if(soup_lis.index(soup_li) > 1):
                                        provider_ids = provider_ids+ ', '+ provider_id
                                    else:
                                        provider_ids = provider_ids+ provider_id
                                    result_list.append('PASS')
                                    res_log = WriteDebugLog(res_log, print_tab+'- Success get provider (name, id, status): ('+provider_name+', '+provider_id+', '+provider_status+')')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                provider_ids = ''
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                provider_ids = ''
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_web_provider_list_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, '')
    else:
        return (res_log, True, provider_ids)


def AdminWebProviderGet(res_log, permission, webName, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_web_provider_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        provider_name = ''
        number_of_game = ''
        if(permission == 'Boss'):
            if(return_value):
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                if(json_response.get('webName') == webName):
                    result_list.append('PASS')
                    provider_name = json_response.get('provider')
                    number_of_game = len(list(json_response.get('gameList')))
#                     res_log = WriteDebugLog(res_log, print_tab+'- Number of Game: '+str(number_of_game))
                else:
                    provider_name = IniValue('admin_webPlayer_web_provider_get', 'API.providerId')
                    number_of_game = 'FAIL'
                    result_list.append('FAIL')
            else:
                provider_name = IniValue('admin_webPlayer_web_provider_get', 'API.providerId')
                number_of_game = 'FAIL'
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_web_provider_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, provider_name, str(number_of_game))
    else:
        return (res_log, True, provider_name, str(number_of_game))


def AdminWebProviderEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_web_provider_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_web_provider_edit... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebPromoProviderContentList(res_log, permission, list_type, web_or_mobile = 'Web'):
    try:
        result_list = []
        json_dict = {}
        i = 0
        for gm_type in list_type:
            if(permission == 'Boss'):
                ReplaceIniValue('admin_webPlayer_promo_providerContent_list', 'API.type', gm_type)
                return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_providerContent_list', False, False)
                WriteLog(print_tab+'Response data: '+ response_data)
                if(return_value):
                    res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                    res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                    json_response = json.loads(response_data)
                    if(type(json_response) is list):
                        gm_name = json_response[0]['name']
                        provider_id = json_response[0]['provider_id']
                        result_list.append('PASS')
                    elif(type(json_response) is dict):
                        if(CheckPermissionDenied(print_tab, res_log, response_data, 'S02', 'No Data')):
                            res_log = WriteDebugLog(res_log, print_tab+'- No data')
                            result_list.append('PASS')
                        else:
                            res_log = WriteDebugLog(res_log, print_tab+'- System error')
                            result_list.append('FAIL')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- type(json_response) != list and dict')
                        result_list.append('FAIL')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
            else:
                return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_providerContent_list', False, False)
                WriteLog(print_tab+'Response data: '+ response_data)
                result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
                if(result):
                    res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                    result_list.append('FAIL')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                    result_list.append('PASS')
            
            if(permission == 'Boss'):
                if(gm_name):
                    ReplaceIniValue('admin_webPlayer_promo_providerContent_gameType_list', 'API.providerId', provider_id)
                    return_value2, response_time2, response_data2, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_providerContent_gameType_list', False, False)
                    WriteLog(print_tab+'Response data: '+ response_data2)
                    if(return_value2):
                        res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                        res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time2)
                        json_response2 = json.loads(response_data2)
                        type_key = json_response2[0]['game_type_key']
                        json_dict[i] = {}
                        json_dict[i]['game_type'] = type_key
                        json_dict[i]['name'] = gm_name
                        json_dict[i]['providerid'] = provider_id
                        json_dict[i]['type'] = gm_type
                        result_list.append('PASS')
                        i += 1
                    else:
                        result_list.append('FAIL')
                        res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
            else:
                return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_providerContent_gameType_list', False, False)
                WriteLog(print_tab+'Response data: '+ response_data)
                result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
                if(result):
                    res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                    result_list.append('FAIL')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                    result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_providerContent_list... %s' % str(e))
         
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    try:
        if(permission == 'Boss'):
            list_json = []
            
            j = 0
            while(j < len(json_dict)):
                list_json.append(json_dict[j])
                j+=1
            
            dict_condition = {}
            dict_condition['reg'] = '0'
            dict_condition['login'] = '1'
            dict_condition['trunover'] = '1000'
            dict_condition['trunover_list'] = list_json
            ReplaceIniValue('admin_webPlayer_promo_create', 'API.condition', str(dict_condition).replace("'",'"'))
            ReplaceIniValue('setting', 'API.condition', str(dict_condition).replace("'",'"'))
            ReplaceIniValue('admin_webPlayer_promo_type_create', 'API.condition', str(dict_condition).replace("'",'"'))
#             dict_reward = {}
#             dict_reward['rio'] = '1'
#             dict_reward['cash'] = ''
#             ReplaceIniValue('admin_webPlayer_promo_create', 'API.reward', str(dict_reward).replace("'",'"'))
#             ReplaceIniValue('admin_webPlayer_promo_type_create', 'API.reward', str(dict_reward).replace("'",'"'))
        else:
            result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_providerContent_gameType_list... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebPromoTypeCreate(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_type_create', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_type_create... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebPromoTypeCreateFriend(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_type_create_friend', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_type_create... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebPromoTypeListFrame(res_log, permission, promoTypeName, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_webPlayer_promo_type_list_frame', 'API.api_path', 'api/webPlayer/promo/type/list/frame')
        else:
            ReplaceIniValue('admin_webPlayer_promo_type_list_frame', 'API.api_path', 'api/webPlayer/promo/type/list/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_type_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                soup = BeautifulSoup(response_data, 'html.parser')
                soup_lis = soup.find_all('li')
                for soup_li in soup_lis:
                    soup_divs = soup_li.find_all('div', class_=True)
                    if(web_or_mobile == 'Web'):
                        for soup_div in soup_divs:
                            if(str(soup_div.string).replace('\n','').replace(' ','') == promoTypeName):
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get promoTypeName: '+promoTypeName)
                                soup_a = soup_li.find('a', id=True)
                                promoTypeId = soup_a.get('id')
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get promoTypeId: '+promoTypeId)
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
                        if('PASS' in result_list2):
                            break
                    else:
                        for soup_li in soup_lis:
                            soup_divs = soup_li.find_all('div', class_=True)
                            for soup_div in soup_divs:
                                if(str(soup_div.string).replace('\n','').replace(' ','') == promoTypeName):
                                    res_log = WriteDebugLog(res_log, print_tab+'- Success get promoTypeName: '+promoTypeName)
                                    soup_a = soup_li.find('div', id=True)
                                    promoTypeId = soup_a.get('id')
                                    res_log = WriteDebugLog(res_log, print_tab+'- Success get promoTypeId: '+promoTypeId)
                                    result_list2.append('PASS')
                                    break
                                else:
                                    result_list2.append('FAIL')
                            if('PASS' in result_list2):
                                break
                        if('PASS' in result_list2):
                            break
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                promoTypeId = ''
    except Exception as e:
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_type_list_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, '')
    else:
        if('PASS' in result_list2):
            return (res_log, True, promoTypeId)
        else:
            return (res_log, False, '')


def AdminWebPromoCreateGet(res_log, permission, webname, webid, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_create_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                web_list = list(json_response['web_list'])
                for element in web_list:
                    web_id = element.get('web_id')
                    web_name = element.get('web_name')
                    if(web_id == webid and web_name == webname):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get (web_name, web_id): ('+webname+', '+webid+')')
                        result_list.append('PASS')
                        break
                    else:
                        result_list.append('FAIL')
#                         res_log = WriteDebugLog(res_log, print_tab+'- Fail get (web_name, web_id): ('+web_name+', '+web_id+') != ('+webname+', '+webid+')')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_create_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('PASS' in result_list):
        return (res_log, True)
    else:
        return (res_log, False)


def AdminWebPromoCreate(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_create', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_create... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebPromoCreateFriend(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_create_friend', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_create_friend... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebPromoListFrame(res_log, permission, webName, promoName, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_webPlayer_promo_list_frame', 'API.api_path', 'api/webPlayer/promo/list/frame')
        else:
            ReplaceIniValue('admin_webPlayer_promo_list_frame', 'API.api_path', 'api/webPlayer/promo/list/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                if(promoName in response_data):
                    result_list.append('PASS')
                    soup = BeautifulSoup(response_data, 'html.parser')
                    soup_lis = soup.find_all("li")
                    if(web_or_mobile == 'Web'):
                        for soup_li in soup_lis:
                            soup_divs = soup_li.find_all("div")
                            for soup_div in soup_divs:
                                if(str(soup_div.string).replace('\n','').replace(' ','') == promoName):
                                    res_log = WriteDebugLog(res_log, print_tab+'Success get promoName: '+promoName)
                                    promoId = soup_li.find('a', id=True).get('id')
                                    res_log = WriteDebugLog(res_log, print_tab+'Success get promoId: '+promoId)
                                    result_list2.append('PASS')
                                    break
                                else:
                                    result_list2.append('FAIL')
                    else:
                        for soup_li in soup_lis:
                            soup_divs = soup_li.find_all("div")
                            for soup_div in soup_divs:
                                if(str(soup_div.string).replace('\n','').replace(' ','') == webName+'-'+promoName):
                                    res_log = WriteDebugLog(res_log, print_tab+'Success get webName-promoName: '+webName+'-'+promoName)
                                    promoId = soup_li.find('div', class_='crm-edit').get('id')
                                    res_log = WriteDebugLog(res_log, print_tab+'Success get promoId: '+promoId)
                                    result_list2.append('PASS')
                                    break
                                else:
                                    result_list2.append('FAIL')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                promoId = ''
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_list_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, '')
    else:
        if('PASS' in result_list2):
            return (res_log, True, promoId)
        else:
            return (res_log, False, '')


# def AdminWebPromoTypeEditGet(res_log, permission, promoTypeName, promoTypeId, web_or_mobile = 'Web'):
#     try:
#         result_list = []
#         result_list2 = []
#         return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_type_edit_get', False, False)
#         WriteLog(print_tab+'Response data: '+ response_data)
#         if(permission == 'Boss'):
#             if(return_value):
#                 result_list.append('PASS')
#                 res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
#                 res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
#                 str_condition = IniValue('admin_webPlayer_promo_type_create', 'API.condition')
#                 json_condition = json.loads(str_condition)
#                 condition_reg = json_condition['reg']
#                 condition_login = json_condition['login']
#                 condition_trunover = json_condition['trunover']
#                 json_response = json.loads(response_data)
#                 if(json_response['conditions']['reg'] == str(condition_reg)):
#                     res_log = WriteDebugLog(res_log, print_tab+'- Success compare condition_reg: '+str(condition_reg))
#                     result_list2.append('PASS')
#                 else:
#                     res_log = WriteDebugLog(res_log, print_tab+'- Fail compare condition_reg: '+json_response['conditions']['reg']+' != '+str(condition_reg))
#                     result_list2.append('FAIL')
#                 
#                 if(json_response['conditions']['login'] == str(condition_login)):
#                     res_log = WriteDebugLog(res_log, print_tab+'- Success compare condition_login: '+str(condition_login))
#                     result_list2.append('PASS')
#                 else:
#                     res_log = WriteDebugLog(res_log, print_tab+'- Fail compare condition_login: '+json_response['conditions']['login']+' != '+str(condition_login))
#                     result_list2.append('FAIL')
#                     
#                 if(str(json_response['conditions']['trunover']) == str(condition_trunover)):
#                     res_log = WriteDebugLog(res_log, print_tab+'- Success compare condition_trunover: '+str(condition_trunover))
#                     result_list2.append('PASS')
#                 else:
#                     res_log = WriteDebugLog(res_log, print_tab+'- Fail compare condition_trunover: '+str(json_response['conditions']['trunover'])+' != '+str(condition_trunover))
#                     result_list2.append('FAIL')
#                 
#                 str_reward = IniValue('admin_webPlayer_promo_type_create', 'API.rewards')
#                 if(str(json_response['rewards']) == str(str_reward)):
#                     res_log = WriteDebugLog(res_log, print_tab+'- Success compare rewards: '+str(str_reward))
#                     result_list2.append('PASS')
#                 else:
#                     res_log = WriteDebugLog(res_log, print_tab+'- Fail compare rewards: '+str(json_response['rewards'])+' != '+str(str_reward))
#                     result_list2.append('FAIL')
#                 
# #                 json_reward = json.loads(str_reward)
# #                 reward_rio = json_reward['rio']
# #                 reward_cash = json_reward['cash']
# #                 if((json_response['rewards']['rio'] != None) and json_response['rewards']['rio'] == str(reward_rio)):
# #                     res_log = WriteDebugLog(res_log, print_tab+'- Success compare reward_rio: '+str(reward_rio))
# #                     result_list2.append('PASS')
# #                 elif((json_response['rewards']['rio'] == None) and str(reward_rio) ==''):
# #                     res_log = WriteDebugLog(res_log, print_tab+'- Success compare reward_rio: None')
# #                     result_list2.append('PASS')
# #                 else:
# #                     res_log = WriteDebugLog(res_log, print_tab+'- Fail compare reward_rio: '+json_response['rewards']['rio']+' != '+str(reward_rio))
# #                     result_list2.append('FAIL')
# #                 
# #                 if((json_response['rewards']['cash'] != None) and json_response['rewards']['cash'] == str(reward_cash)):
# #                     res_log = WriteDebugLog(res_log, print_tab+'- Success compare reward_cash: '+str(reward_cash))
# #                     result_list2.append('PASS')
# #                 elif((json_response['rewards']['cash'] == None) and str(reward_cash) == ''):
# #                     res_log = WriteDebugLog(res_log, print_tab+'- Success compare reward_cash: None')
# #                     result_list2.append('PASS')
# #                 else:
# #                     res_log = WriteDebugLog(res_log, print_tab+'- Fail compare reward_cash: '+json_response['rewards']['cash']+' != '+str(reward_cash))
# #                     result_list2.append('FAIL')
#                 
#                 if(json_response['promo_name'] == promoTypeName and str(json_response['promo_type_id']) == promoTypeId):
#                     res_log = WriteDebugLog(res_log, print_tab+'- Success compare (promoTypeName, promoTypeId): ('+promoTypeName+', '+promoTypeId+')')
#                     result_list2.append('PASS')
#                 else:
#                     result_list2.append('FAIL')
#                     res_log = WriteDebugLog(res_log, print_tab+'- Fail compare (promoTypeName, promoTypeId): ('+json_response['promo_name']+', '+str(json_response['promo_type_id'])+') != ('+promoTypeName+', '+promoTypeId+')')
#                 
#                 list_test = []
#                 for element in json_response['trunover_list']:
#                     if('game_type_name' in element):
#                         del element['game_type_name']
#                     list_test.append(element)
#                 condition_trunover_list = str(json_condition['trunover_list'])
#                 
#                 if(str(list_test) == str(condition_trunover_list)):
#                     res_log = WriteDebugLog(res_log, print_tab+'- Success compare trunover_list: '+str(condition_trunover_list))
#                     result_list2.append('PASS')
#                 else:
#                     result_list2.append('FAIL')
#                     res_log = WriteDebugLog(res_log, print_tab+'- Fail compare trunover_list: '+str(list_test)+' != '+str(condition_trunover_list))
#             else:
#                 result_list.append('FAIL')
#                 res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
#         else:
#             result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
#             if(result):
#                 res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
#                 result_list.append('FAIL')
#                 result_list2.append('FAIL')
#             else:
#                 res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
#                 result_list.append('PASS')
#                 result_list2.append('PASS')
#     except Exception as e:
#         result_list.append('FAIL')
#         res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_type_edit_get... %s' % str(e))
#     finally:
#         res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
#     WriteLog(result_list)
#     WriteLog(result_list2)
#     if('FAIL' in result_list or not result_list):
#         return (res_log, False)
#     else:
#         if('FAIL' in result_list2 or not result_list2):
#             return (res_log, False)
#         else:
#             return (res_log, True)


def AdminWebPromoTypeEditGet(res_log, permission, promo_type, promoName, promoId, str_condition, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_type_edit_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_condition = json.loads(str_condition)
                json_response = json.loads(response_data)
                
                if(promo_type != 4):
                    str_reward = IniValue('admin_webPlayer_promo_type_create', 'API.rewards')
                    if(str(json_response['rewards']) == str(str_reward)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare rewards: '+str(str_reward))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare rewards: '+str(json_response['rewards'])+' != '+str(str_reward))
                        result_list2.append('FAIL')
                
                if(json_response['promo_name'] == promoName and str(json_response['promo_type_id']) == promoId):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success compare (promoTypeName, promoTypeId): ('+promoName+', '+promoId+')')
                    result_list2.append('PASS')
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail compare (promoTypeName, promoTypeId): ('+json_response['promo_name']+', '+str(json_response['promo_type_id'])+') != ('+promoName+', '+promoId+')')
                
                if(promo_type == 1):
                    condition_reg = json_condition['reg']
                    condition_login = json_condition['login']
                    condition_trunover = json_condition['trunover']
                    if(json_response['conditions']['reg'] == str(condition_reg)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare condition_reg: '+str(condition_reg))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare condition_reg: '+json_response['conditions']['reg']+' != '+str(condition_reg))
                        result_list2.append('FAIL')
                    
                    if(json_response['conditions']['login'] == str(condition_login)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare condition_login: '+str(condition_login))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare condition_login: '+json_response['conditions']['login']+' != '+str(condition_login))
                        result_list2.append('FAIL')
                        
                    if(str(json_response['conditions']['trunover']) == str(condition_trunover)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare condition_trunover: '+str(condition_trunover))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare condition_trunover: '+str(json_response['conditions']['trunover'])+' != '+str(condition_trunover))
                        result_list2.append('FAIL')
                    
                    list_test = []
                    for element in json_response['trunover_list']:
                        if('game_type_name' in element):
                            del element['game_type_name']
                        list_test.append(element)
                    condition_trunover_list = str(json_condition['trunover_list'])
                
                    if(str(list_test) == str(condition_trunover_list)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare trunover_list: '+str(condition_trunover_list))
                        result_list2.append('PASS')
                    else:
                        result_list2.append('FAIL')
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare trunover_list: '+str(list_test)+' != '+str(condition_trunover_list))
                
                elif(promo_type == 2):
                    condition_currentDepositAmount = json_condition['currentDepositAmount']
                    condition_relaxationDays = json_condition['relaxationDays']
                    if(str(json_response['conditions']['currentDepositAmount']) == str(condition_currentDepositAmount)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare currentDepositAmount: '+str(condition_currentDepositAmount))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare currentDepositAmount: '+str(json_response['conditions']['currentDepositAmount'])+' != '+str(condition_currentDepositAmount))
                        result_list2.append('FAIL')
                    
                    if(str(json_response['conditions']['relaxationDays']) == str(condition_relaxationDays)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare relaxationDays: '+str(condition_relaxationDays))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare relaxationDays: '+str(json_response['conditions']['relaxationDays'])+' != '+str(condition_relaxationDays))
                        result_list2.append('FAIL')
                
                elif(promo_type == 3):
                    condition_sendTime = json_condition['sendTime']
                    condition_sendMin = json_condition['sendMin']
                    condition_sendMax = json_condition['sendMax']
                    if(str(json_response['conditions']['sendTime']) == str(condition_sendTime)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare sendTime: '+str(condition_sendTime))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare sendTime: '+str(json_response['conditions']['sendTime'])+' != '+str(condition_sendTime))
                        result_list2.append('FAIL')
                    
                    if(str(json_response['conditions']['sendMin']) == str(condition_sendMin)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare sendMin: '+str(condition_sendMin))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare sendMin: '+str(json_response['conditions']['sendMin'])+' != '+str(condition_sendMin))
                        result_list2.append('FAIL')
                    
                    if(str(json_response['conditions']['sendMax']) == str(condition_sendMax)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare sendMax: '+str(condition_sendMax))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare sendMax: '+str(json_response['conditions']['sendMax'])+' != '+str(condition_sendMax))
                        result_list2.append('FAIL')
                
                elif(promo_type == 4):
                    condition_countNumbers = json_condition[0]['countNumbers']
                    condition_countDepositAmount = json_condition[0]['countDepositAmount']
                    condition_receiveAmount = json_condition[0]['receiveAmount']
                    if(str(json_response['conditions'][0]['countNumbers']) == str(condition_countNumbers)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare countNumbers: '+str(condition_countNumbers))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare countNumbers: '+str(json_response['conditions'][0]['countNumbers'])+' != '+str(condition_countNumbers))
                        result_list2.append('FAIL')
                    
                    if(str(json_response['conditions'][0]['countDepositAmount']) == str(condition_countDepositAmount)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare countDepositAmount: '+str(condition_countDepositAmount))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare countDepositAmount: '+str(json_response['conditions'][0]['countDepositAmount'])+' != '+str(condition_countDepositAmount))
                        result_list2.append('FAIL')
                    
                    if(str(json_response['conditions'][0]['receiveAmount']) == str(condition_receiveAmount)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare receiveAmount: '+str(condition_receiveAmount))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare receiveAmount: '+str(json_response['conditions'][0]['receiveAmount'])+' != '+str(condition_receiveAmount))
                        result_list2.append('FAIL')
                
                elif(promo_type == 5):
                    condition_depositAmountMin = json_condition['depositAmountMin']
                    condition_signDays = json_condition['signDays']
                    condition_signReceiveAmount = json_condition['signReceiveAmount']
                    if(str(json_response['conditions']['depositAmountMin']) == str(condition_depositAmountMin)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare depositAmountMin: '+str(condition_depositAmountMin))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare depositAmountMin: '+str(json_response['conditions']['depositAmountMin'])+' != '+str(condition_depositAmountMin))
                        result_list2.append('FAIL')
                    
                    if(str(json_response['conditions']['signDays']) == str(condition_signDays)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare signDays: '+str(condition_signDays))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare signDays: '+str(json_response['conditions']['signDays'])+' != '+str(condition_signDays))
                        result_list2.append('FAIL')
                    
                    if(str(json_response['conditions']['signReceiveAmount']) == str(condition_signReceiveAmount)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare signReceiveAmount: '+str(condition_signReceiveAmount))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare signReceiveAmount: '+str(json_response['conditions']['signReceiveAmount'])+' != '+str(condition_signReceiveAmount))
                        result_list2.append('FAIL')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_type_edit_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminWebPromoTypeEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_type_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_type_edit... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebPromoTypeEditFriend(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_type_edit_friend', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_type_edit_friend... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebPromoStateEdit(res_log, permission, state, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_state_edit', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                if(state == '刪除'):
                    if(CheckPermissionDenied(print_tab, res_log, response_data, 'S01', 'Success')):
                        result_list.append('PASS')
                        res_log = WriteDebugLog(res_log, print_tab+'- Success delete promo')
                    else:
                        result_list.append('FAIL')
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail delete promo')
                else:
                    json_response = json.loads(response_data)
                    if(json_response['state'] == state):
                        result_list.append('PASS')
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get state: '+state)
                    else:
                        result_list.append('FAIL')
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail get state: '+json_response['state']+' != '+state)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_state_edit... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebPromoDelete(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_delete', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_delete... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebPromoEditGet(res_log, permission, promo_type, promoName, promoId, str_condition, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_edit_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_condition = json.loads(str_condition)
                json_response = json.loads(response_data)
                
                if(promo_type != 4):
                    str_reward = IniValue('admin_webPlayer_promo_create', 'API.rewards')
                    if(str(json_response['rewards']) == str(str_reward)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare rewards: '+str(str_reward))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare rewards: '+str(json_response['rewards'])+' != '+str(str_reward))
                        result_list2.append('FAIL')
                
                str_webId = IniValue('admin_webPlayer_promo_create', 'API.webid')
                if(json_response['web_id'] == str_webId):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success compare webId: '+str_webId)
                    result_list2.append('PASS')
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail compare webId: '+json_response['web_id']+' != '+str_webId)
                
                if(json_response['promo_name'] == promoName and str(json_response['promo_id']) == promoId):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success compare (promoName, promoId): ('+promoName+', '+promoId+')')
                    result_list2.append('PASS')
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail compare (promoName, promoId): ('+json_response['promo_name']+', '+str(json_response['promo_id'])+') != ('+promoName+', '+promoId+')')
                
                if(promo_type == 1):
                    condition_reg = json_condition['reg']
                    condition_login = json_condition['login']
                    condition_trunover = json_condition['trunover']
                    if(json_response['conditions']['reg'] == str(condition_reg)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare condition_reg: '+str(condition_reg))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare condition_reg: '+json_response['conditions']['reg']+' != '+str(condition_reg))
                        result_list2.append('FAIL')
                    
                    if(json_response['conditions']['login'] == str(condition_login)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare condition_login: '+str(condition_login))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare condition_login: '+json_response['conditions']['login']+' != '+str(condition_login))
                        result_list2.append('FAIL')
                        
                    if(str(json_response['conditions']['trunover']) == str(condition_trunover)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare condition_trunover: '+str(condition_trunover))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare condition_trunover: '+str(json_response['conditions']['trunover'])+' != '+str(condition_trunover))
                        result_list2.append('FAIL')
                    
                    list_test = []
                    for element in json_response['trunover_list']:
                        if('game_type_name' in element):
                            del element['game_type_name']
                        list_test.append(element)
                    condition_trunover_list = str(json_condition['trunover_list'])
                
                    if(str(list_test) == str(condition_trunover_list)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare trunover_list: '+str(condition_trunover_list))
                        result_list2.append('PASS')
                    else:
                        result_list2.append('FAIL')
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare trunover_list: '+str(list_test)+' != '+str(condition_trunover_list))
                
                elif(promo_type == 2):
                    condition_currentDepositAmount = json_condition['currentDepositAmount']
                    condition_relaxationDays = json_condition['relaxationDays']
                    if(str(json_response['conditions']['currentDepositAmount']) == str(condition_currentDepositAmount)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare currentDepositAmount: '+str(condition_currentDepositAmount))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare currentDepositAmount: '+str(json_response['conditions']['currentDepositAmount'])+' != '+str(condition_currentDepositAmount))
                        result_list2.append('FAIL')
                    
                    if(str(json_response['conditions']['relaxationDays']) == str(condition_relaxationDays)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare relaxationDays: '+str(condition_relaxationDays))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare relaxationDays: '+str(json_response['conditions']['relaxationDays'])+' != '+str(condition_relaxationDays))
                        result_list2.append('FAIL')
                
                elif(promo_type == 3):
                    condition_sendTime = json_condition['sendTime']
                    condition_sendMin = json_condition['sendMin']
                    condition_sendMax = json_condition['sendMax']
                    if(str(json_response['conditions']['sendTime']) == str(condition_sendTime)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare sendTime: '+str(condition_sendTime))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare sendTime: '+str(json_response['conditions']['sendTime'])+' != '+str(condition_sendTime))
                        result_list2.append('FAIL')
                    
                    if(str(json_response['conditions']['sendMin']) == str(condition_sendMin)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare sendMin: '+str(condition_sendMin))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare sendMin: '+str(json_response['conditions']['sendMin'])+' != '+str(condition_sendMin))
                        result_list2.append('FAIL')
                    
                    if(str(json_response['conditions']['sendMax']) == str(condition_sendMax)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare sendMax: '+str(condition_sendMax))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare sendMax: '+str(json_response['conditions']['sendMax'])+' != '+str(condition_sendMax))
                        result_list2.append('FAIL')
                
                elif(promo_type == 4):
                    condition_countNumbers = json_condition[0]['countNumbers']
                    condition_countDepositAmount = json_condition[0]['countDepositAmount']
                    condition_receiveAmount = json_condition[0]['receiveAmount']
                    if(str(json_response['conditions'][0]['countNumbers']) == str(condition_countNumbers)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare countNumbers: '+str(condition_countNumbers))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare countNumbers: '+str(json_response['conditions'][0]['countNumbers'])+' != '+str(condition_countNumbers))
                        result_list2.append('FAIL')
                    
                    if(str(json_response['conditions'][0]['countDepositAmount']) == str(condition_countDepositAmount)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare countDepositAmount: '+str(condition_countDepositAmount))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare countDepositAmount: '+str(json_response['conditions'][0]['countDepositAmount'])+' != '+str(condition_countDepositAmount))
                        result_list2.append('FAIL')
                    
                    if(str(json_response['conditions'][0]['receiveAmount']) == str(condition_receiveAmount)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare receiveAmount: '+str(condition_receiveAmount))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare receiveAmount: '+str(json_response['conditions'][0]['receiveAmount'])+' != '+str(condition_receiveAmount))
                        result_list2.append('FAIL')
                
                elif(promo_type == 5):
                    condition_depositAmountMin = json_condition['depositAmountMin']
                    condition_signDays = json_condition['signDays']
                    condition_signReceiveAmount = json_condition['signReceiveAmount']
                    if(str(json_response['conditions']['depositAmountMin']) == str(condition_depositAmountMin)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare depositAmountMin: '+str(condition_depositAmountMin))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare depositAmountMin: '+str(json_response['conditions']['depositAmountMin'])+' != '+str(condition_depositAmountMin))
                        result_list2.append('FAIL')
                    
                    if(str(json_response['conditions']['signDays']) == str(condition_signDays)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare signDays: '+str(condition_signDays))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare signDays: '+str(json_response['conditions']['signDays'])+' != '+str(condition_signDays))
                        result_list2.append('FAIL')
                    
                    if(str(json_response['conditions']['signReceiveAmount']) == str(condition_signReceiveAmount)):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success compare signReceiveAmount: '+str(condition_signReceiveAmount))
                        result_list2.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail compare signReceiveAmount: '+str(json_response['conditions']['signReceiveAmount'])+' != '+str(condition_signReceiveAmount))
                        result_list2.append('FAIL')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_edit_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminWebPromoEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_edit... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebPromoCommissionTypeCreate(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_commission_type_create', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_commission_type_create... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebPromoCommissionTypeListFrame(res_log, permission, commissionTypeName, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_webPlayer_promo_commission_type_list_frame', 'API.api_path', 'api/webPlayer/promo/commission/type/list/frame')
        else:
            ReplaceIniValue('admin_webPlayer_promo_commission_type_list_frame', 'API.api_path', 'api/webPlayer/promo/commission/type/list/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_commission_type_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                soup = BeautifulSoup(response_data, 'html.parser')
                soup_lis = soup.find_all("li")
                if(web_or_mobile == 'Web'):
                    for soup_li in soup_lis:
                        soup_divs = soup_li.find_all("div", class_=True)
                        for soup_div in soup_divs:
                            if(str(soup_div.string).replace('\n','').replace(' ','') == commissionTypeName):
                                res_log = WriteDebugLog(res_log, print_tab+'Success get commissionTypeName: '+commissionTypeName)
                                commissionTypeId = soup_li.find('a', id=True).get('id')
                                res_log = WriteDebugLog(res_log, print_tab+'Success get commissionTypeId: '+commissionTypeId)
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
                        if('PASS' in result_list2):
                            break
                else:
                    for soup_li in soup_lis:
                        soup_divs = soup_li.find_all("div", class_=True)
                        for soup_div in soup_divs:
                            if(str(soup_div.string).replace('\n','').replace(' ','') == commissionTypeName):
                                res_log = WriteDebugLog(res_log, print_tab+'Success get commissionTypeName: '+commissionTypeName)
                                commissionTypeId = soup_li.find('i', id=True).get('id')
                                res_log = WriteDebugLog(res_log, print_tab+'Success get commissionTypeId: '+commissionTypeId)
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
                        if('PASS' in result_list2):
                            break
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                commissionTypeId = ''
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_commission_type_list_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
            return (res_log, False, '')
    else:
        if('PASS' in result_list):
            return (res_log, True, commissionTypeId)
        else:
            return (res_log, False, '')


def AdminWebPromoCommissionCreateGet(res_log, permission, commissionTypeName, commissionTypeId, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []

        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_commission_create_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                if('commission_type_list' in json_response):
                    type_dict = json_response['commission_type_list'][0]
                    if(str(type_dict['commission_type_id']) == str(commissionTypeId) and str(type_dict['web_commission_name']) == str(commissionTypeName)):
                        result_list2.append('PASS')
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get (commissionTypeName, commissionTypeId): ('+commissionTypeName+', '+commissionTypeId+')')
                elif(CheckPermissionDenied(print_tab, res_log, json_response, 'S02', 'No Data')):
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get (Error_code, Error_message): (S02, No Data)')
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get commissionType')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_commission_create_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminWebPromoCommissionCreateTypeGet(res_log, permission, list_type, web_or_mobile = 'Web'):
    result_list3 = []
    try:
        result_list = []
        result_list2 = []
        if(permission == 'Boss'):
            for gm_type in list_type:
                ReplaceIniValue('admin_webPlayer_promo_commission_create_type_get', 'API.type', gm_type)
                return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_commission_create_type_get', False, False)
                WriteLog(print_tab+'Response data: '+ response_data)
                if(return_value):
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                    res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                    json_response = json.loads(response_data)
                    if(type(json_response) is list):
                        json_dict = {}
                        for each_dict in json_response:
                            provider_id = each_dict['providerid']
                            if(provider_id):
                                type_keys = each_dict['game_type_list']
                                json_dict[provider_id] = {}
                                for type_key in type_keys:
                                    index_value = type_keys.index(type_key)
                                    gameType = type_key.get('gameType')
                                    json_dict[provider_id][gameType] = index_value+1
    #                                 list_key = list(type_key.keys())
    #                                 json_dict[provider_id][list_key[0]] = index_value+1
                                result_list2.append('PASS')
                            else:
                                result_list2.append('FAIL')
                        result_list3.append(str(json_dict))
                        ReplaceIniValue('admin_webPlayer_promo_commission_create', 'API.'+gm_type, str(json_dict).replace("'",'"'))
                    elif(type(json_response) is dict):
                        if(CheckPermissionDenied(print_tab, res_log, response_data, 'S02', 'No Data')):
                            res_log = WriteDebugLog(res_log, print_tab+'- No data')
                            result_list2.append('PASS')
                        else:
                            res_log = WriteDebugLog(res_log, print_tab+'- System error')
                            result_list2.append('FAIL')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- type(json_response) != list and dict')
                        result_list2.append('FAIL')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_commission_create_type_get', False, False)
            WriteLog(print_tab+'Response data: '+ response_data)
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
                result_list3.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                result_list3.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_commission_create_type_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    WriteLog(result_list3)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            if(not result_list3):
                return (res_log, False)
            else:
                return (res_log, True)

def AdminWebPromoCommissionCreate(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_commission_create', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_commission_create... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)

def AdminWebPromoCommissionListFrame(res_log, permission, webCommissionName, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_webPlayer_promo_commission_list_frame', 'API.api_path', 'api/webPlayer/promo/commission/list/frame')
        else:
            ReplaceIniValue('admin_webPlayer_promo_commission_list_frame', 'API.api_path', 'api/webPlayer/promo/commission/list/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_commission_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                soup = BeautifulSoup(response_data, 'html.parser')
                soup_divs = soup.find_all("div", class_=True)
                for soup_div in soup_divs:
                    if(str(soup_div.string).replace('\n','').replace(' ','') == webCommissionName):
                        result_list2.append('PASS')
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get webCommissionName: '+webCommissionName)
                        break
                    else:
                        result_list2.append('FAIL')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_commission_list_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('PASS' in result_list2):
            return (res_log, True)
        else:
            return (res_log, False)


def AdminWebPromoCommissionTypeEditGet(res_log, permission, commissionTypeName, commissionTypeId, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_commission_type_edit_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                if(str(json_response['max_receive_amount']) == '600'):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get max_receive_amount: '+str(json_response['max_receive_amount']))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get max_receive_amount: '+str(json_response['max_receive_amount'])+' != 600')
                    
                if(str(json_response['promotion_limit']) == '500'):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get promotion_limit: '+str(json_response['promotion_limit']))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get promotion_limit: '+str(json_response['promotion_limit'])+' != 500')
                    
                if(str(json_response['total_bet']) == '400'):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get total_bet: '+str(json_response['total_bet']))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get total_bet: '+str(json_response['total_bet'])+' != 400')
                    
                if(str(json_response['commission_times']) == '200'):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get commission_times: '+str(json_response['commission_times']))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get commission_times: '+str(json_response['commission_times'])+' != 200')
                    
                if(str(json_response['single_min_receive_amount']) =='100'):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get single_min_receive_amount: '+str(json_response['single_min_receive_amount']))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get single_min_receive_amount: '+str(json_response['single_min_receive_amount'])+' != 100')
                    
                if(str(json_response['receive_times_daily']) == '5'):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get receive_times_daily: '+str(json_response['receive_times_daily']))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get receive_times_daily: '+str(json_response['receive_times_daily'])+' != 5')
                    
                if(str(json_response['web_commission_name']) == commissionTypeName):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get web_commission_name: '+str(json_response['web_commission_name']))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get web_commission_name: '+str(json_response['web_commission_name'])+' != '+commissionTypeName)
                    
                if(str(json_response['commission_type_id']) == commissionTypeId):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get commission_type_id: '+str(json_response['commission_type_id']))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get commission_type_id: '+str(json_response['commission_type_id'])+' != '+commissionTypeId)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_commission_type_edit_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)

def AdminWebPromoCommissionTypeEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_commission_type_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_commission_type_edit... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)

def AdminWebPromoCommissionEditGet(res_log, permission, commissionName, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_commission_edit_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                if(str(json_response['max_receive_amount']) == '600'):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get max_receive_amount: '+str(json_response['max_receive_amount']))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get max_receive_amount: '+str(json_response['max_receive_amount'])+' != 600')
                    
                if(str(json_response['promotion_limit']) == '500'):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get promotion_limit: '+str(json_response['promotion_limit']))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get promotion_limit: '+str(json_response['promotion_limit'])+' != 500')
                    
                if(str(json_response['total_bet']) == '400'):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get total_bet: '+str(json_response['total_bet']))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get total_bet: '+str(json_response['total_bet'])+' != 400')
                    
                if(str(json_response['commission_times']) == '200'):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get commission_times: '+str(json_response['commission_times']))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get commission_times: '+str(json_response['commission_times'])+' != 200')
                    
                if(str(json_response['single_min_receive_amount']) =='100'):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get single_min_receive_amount: '+str(json_response['single_min_receive_amount']))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get single_min_receive_amount: '+str(json_response['single_min_receive_amount'])+' != 100')
                    
                if(str(json_response['receive_times_daily']) == '5'):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get receive_times_daily: '+str(json_response['receive_times_daily']))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get receive_times_daily: '+str(json_response['receive_times_daily'])+' != 5')
                    
                if(str(json_response['web_commission_name']) == commissionName):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get web_commission_name: '+str(json_response['web_commission_name']))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get web_commission_name: '+str(json_response['web_commission_name'])+' != '+commissionName)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_commission_edit_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)

def AdminWebPromoCommissionEditTypeGet(res_log, permission, list_type, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        result_list3 = []
        if(permission == 'Boss'):
            for gm_type in list_type:
                ReplaceIniValue('admin_webPlayer_promo_commission_edit_type_get', 'API.type', gm_type)
                return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_commission_edit_type_get', False, False)
                WriteLog(print_tab+'Response data: '+ response_data)
                if(return_value):
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                    res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                    json_response = json.loads(response_data)
                    if(type(json_response) is list):
                        json_dict = {}
                        for each_dict in json_response:
                            provider_id = each_dict['providerid']
                            if(provider_id):
                                type_keys = each_dict['game_type_list']
                                json_dict[provider_id] = {}
    #                             print(provider_id)
                                for type_key in type_keys:
                                    index_value = type_keys.index(type_key)
                                    gameType = type_key.get('gameType')
                                    json_dict[provider_id][gameType] = index_value+1
    #                                 index_value = type_keys.index(type_key)
    #                                 list_key = list(type_key.keys())
    #                                 json_dict[provider_id][list_key[0]] = index_value+1
                                result_list2.append('PASS')
                            else:
                                result_list2.append('FAIL')
                        result_list3.append(str(json_dict))
                        ReplaceIniValue('admin_webPlayer_promo_commission_edit', 'API.'+gm_type, str(json_dict).replace("'",'"'))
                    elif(type(json_response) is dict):
                        if(CheckPermissionDenied(print_tab, res_log, response_data, 'S02', 'No Data')):
                            res_log = WriteDebugLog(res_log, print_tab+'- '+gm_type+': no data')
                            result_list2.append('PASS')
                        else:
                            res_log = WriteDebugLog(res_log, print_tab+'- System error')
                            result_list2.append('FAIL')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- type(json_response) != list and dict')
                        result_list2.append('FAIL')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_commission_edit_type_get', False, False)
            WriteLog(print_tab+'Response data: '+ response_data)
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
                result_list3.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                result_list3.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_commission_edit_type_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    WriteLog(result_list3)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            if(not result_list3):
                return (res_log, False)
            else:
                return (res_log, True)


def AdminWebPromoCommissionEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_promo_commission_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_promo_commission_edit... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebRiskCreate(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_risk_create', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_risk_create... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebRiskListFrame(res_log, permission, riskname, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_webPlayer_risk_list_frame', 'API.api_path', 'api/webPlayer/risk/list/frame')
        else:
            ReplaceIniValue('admin_webPlayer_risk_list_frame', 'API.api_path', 'api/webPlayer/risk/list/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_risk_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                
                soup = BeautifulSoup(response_data, 'html.parser')
                # print(soup.prettify())
                soup_lis = soup.find_all("li")
                if(web_or_mobile == 'Web'):
                    for soup_li in soup_lis:
                        soup_divs = soup_li.find_all("div")
                        for soup_div in soup_divs:
                            if(str(soup_div.string).replace('\n','').replace(' ','') == riskname):
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get riskName: '+riskname)
                                riskId = soup_li.find('div', id=True).get('id')
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get riskId: '+riskId)
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
                else:
                    for soup_li in soup_lis:
                        soup_divs = soup_li.find_all("div")
                        for soup_div in soup_divs:
                            if(str(soup_div.string).replace('\n','').replace(' ','') == riskname):
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get riskName: '+riskname)
                                riskId = soup_li.find('a', id=True).get('id')
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get riskId: '+riskId)
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                riskId = ''
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_risk_list_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, '')
    else:
        if('PASS' in result_list2):
            return (res_log, True, riskId)
        else:
            return (res_log, False, '')


def AdminWebRiskRuleFrame(res_log, permission, opt_interval, opt_count, web_or_mobile = 'Web'):
    try:
        result_list = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_webPlayer_risk_rule_frame', 'API.api_path', 'api/webPlayer/risk/rule/frame')
        else:
            ReplaceIniValue('admin_webPlayer_risk_rule_frame', 'API.api_path', 'api/webPlayer/risk/rule/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_risk_rule_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                soup = BeautifulSoup(response_data, 'html.parser')
                risk_interval = soup.find("input", id="interval")
                if(risk_interval.get('value') == opt_interval):
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get interval: '+opt_interval)
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get interval: '+risk_interval.get('value')+' != '+opt_interval)
                
                risk_count = soup.find("input", id="count")
                if(risk_count.get('value') == opt_count):
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get count: '+opt_count)
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get interval: '+risk_count.get('value')+' != '+opt_count)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_risk_rule_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebRiskEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_risk_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_risk_edit... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebRiskWebFrame(res_log, permission, webName, webId, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_webPlayer_risk_web_frame', 'API.api_path', 'api/webPlayer/risk/web/frame')
        else:
            ReplaceIniValue('admin_webPlayer_risk_web_frame', 'API.api_path', 'api/webPlayer/risk/web/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_risk_web_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                soup = BeautifulSoup(response_data, 'html.parser')
                soup_vipCheckItems = soup.find_all("div", class_='ckeck-item')
                if(web_or_mobile == 'Web'):
                    for soup_vipCheckItem in soup_vipCheckItems:
                        if(soup_vipCheckItem.find('span').string.replace('\n','').replace(' ','') == webName):
                            res_log = WriteDebugLog(res_log, print_tab+'- Success get webName: '+webName)
                            if(soup_vipCheckItem.find('input').get('value') == webId):
                                result_list2.append('PASS')
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get webId: '+webId)
                            else:
                                result_list2.append('FAIL')
                                res_log = WriteDebugLog(res_log, print_tab+'- FAIL get webId: '+soup_vipCheckItem.find('input').get('value')+' != '+webId)
                        else:
                            result_list2.append('FAIL')
                else:
                    soup_vipLabelItems = soup.find_all("label", attrs={'class':False})
                    for soup_vipLabelItem in soup_vipLabelItems:
                        if(str(soup_vipLabelItem.find('span').string).replace('\n','').replace(' ','') == webName):
                            res_log = WriteDebugLog(res_log, print_tab+'- Success get webName: '+webName)
                            if(soup_vipLabelItem.find('input').get('value') == webId):
                                result_list2.append('PASS')
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get webId: '+webId)
                            else:
                                result_list2.append('FAIL')
                                res_log = WriteDebugLog(res_log, print_tab+'- FAIL get webId: '+soup_vipLabelItem.find('input').get('value')+' != '+webId)
                        else:
                            result_list2.append('FAIL')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_risk_web_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('PASS' in result_list2):
            return (res_log, True)
        else:
            return (res_log, False)


def AdminWebRiskEditGet(res_log, permission, riskname, riskid, edit_count, edit_interval, edit_time, edit_type, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_risk_edit_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                if(json_response['id'] == riskid):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get riskid: '+riskid)
                    result_list2.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get riskid: '+json_response['id'] +' != '+riskid)
                    result_list2.append('FAIL')
                
                if(json_response['name'] == riskname):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get riskname: '+riskname)
                    result_list2.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get riskname: '+json_response['name'] +' != '+riskname)
                    result_list2.append('FAIL')
                
                if(json_response['opt'][0]['name'] == '单一IP登入'):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get opt_name: 单一IP登入')
                    result_list2.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get opt_name: '+json_response['opt'][0]['name'] +' != 单一IP登入')
                    result_list2.append('FAIL')
                
                if(json_response['opt'][0]['count'] == edit_count):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get opt_count: '+edit_count)
                    result_list2.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get opt_count: '+json_response['opt'][0]['count'] +' != '+edit_count)
                    result_list2.append('FAIL')
                
                if(json_response['opt'][0]['interval'] == edit_interval):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get opt_interval: '+edit_interval)
                    result_list2.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get opt_interval: '+json_response['opt'][0]['interval'] +' != '+edit_interval)
                    result_list2.append('FAIL')
                
                if(json_response['opt'][0]['time'] == edit_time):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get opt_time: '+edit_time)
                    result_list2.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get opt_time: '+json_response['opt'][0]['time'] +' != '+edit_time)
                    result_list2.append('FAIL')
                
                if(json_response['opt'][0]['type'] == edit_type):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get opt_type: '+edit_type)
                    result_list2.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get opt_type: '+json_response['opt'][0]['type'] +' != '+edit_type)
                    result_list2.append('FAIL')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_risk_edit_get... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminWebRiskStateEdit(res_log, permission, state, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_risk_state_edit', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                if(state == '刪除'):
                    if(CheckPermissionDenied(print_tab, res_log, response_data, 'S01', 'Success')):
                        result_list.append('PASS')
                        res_log = WriteDebugLog(res_log, print_tab+'- Success delete risk')
                    else:
                        result_list.append('FAIL')
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail delete risk')
                else:
                    if(json_response['state'] == state):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get state: '+state)
                        result_list.append('PASS')
                    else:
                        res_log = WriteDebugLog(res_log, print_tab+'- Fail get state: '+json_response['state'] +' != '+state)
                        result_list.append('FAIL')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_risk_delete... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebRiskDelete(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_risk_delete', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_risk_delete... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminProviderBankCardCreate(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_bankCard_create', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_bankCard_create... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminProviderBankCardListFrame(res_log, permission, bankName, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_provider_bankCard_list_frame', 'API.api_path', 'api/provider/bankCard/list/frame')
        else:
            ReplaceIniValue('admin_provider_bankCard_list_frame', 'API.api_path', 'api/provider/bankCard/list/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_bankCard_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                
                soup = BeautifulSoup(response_data, 'html.parser')
                soup_lis = soup.find_all('li')
                if(web_or_mobile == 'Web'):
                    for soup_li in soup_lis:
                        soup_divs = soup_li.find_all('div')
                        for soup_div in soup_divs:
                            if(str(soup_div.string).replace('\n','').replace(' ','') == bankName):
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get bankName: '+bankName)
                                cardId = soup_li.find("a", attrs={"href":"provider_card_edit.html"}).get("id")
#                                 ReplaceIniValue('setting', 'API.cardid', cardId)
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get cardId: '+cardId)
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
                        if('PASS' in result_list2):
                            break
                else:
                    for soup_li in soup_lis:
                        soup_divs = soup_li.find_all('div')
                        for soup_div in soup_divs:
                            if(str(soup_div.string).replace('\n','').replace(' ','') == bankName):
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get bankName: '+bankName)
                                cardId = soup_li.find('div', attrs={"class":"crm-edit"}).get("id")
#                                 ReplaceIniValue('setting', 'API.cardid', cardId)
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get cardId: '+cardId)
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
                        if('PASS' in result_list2):
                            break
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                cardId = ''
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                cardId = ''
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_bankCard_list_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, '')
    else:
        if('PASS' in result_list2):
            return (res_log, True, cardId)
        else:
            return (res_log, False, '')


def AdminProviderBankCardEditGet(res_log, permission, amount, maxwithdraw, maxdeposit, mindeposit, bankname, branchname, bankacc, bankaccname, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_bankCard_edit_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                if(json_response['acc_name'] == bankaccname):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get acc_name: '+bankaccname)
                    result_list2.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get acc_name: '+json_response['acc_name'] +' != '+bankaccname)
                    result_list2.append('FAIL')
                
                if(json_response['bank_acc'] == bankacc):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get bank_acc: '+bankacc)
                    result_list2.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get bank_acc: '+json_response['bank_acc'] +' != '+bankacc)
                    result_list2.append('FAIL')
                
                if(json_response['bank_name'] == bankname):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get bank_name: '+bankname)
                    result_list2.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get bank_name: '+json_response['bank_name'] +' != '+bankname)
                    result_list2.append('FAIL')
                
                if(json_response['branch_name'] == branchname):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get branch_name: '+branchname)
                    result_list2.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get branch_name: '+json_response['branch_name'] +' != '+branchname)
                    result_list2.append('FAIL')
                
                if(str(json_response['enable']) == '1'):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get enable: 1')
                    result_list2.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get enable: '+json_response['enable'] +' != 1')
                    result_list2.append('FAIL')
                
                if(str(json_response['amount']) == amount):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get amount: '+amount)
                    result_list2.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get amount: '+str(json_response['amount']) +' != '+amount)
                    result_list2.append('FAIL')
                
                if(str(json_response['maxdeposit']) == maxdeposit):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get maxdeposit: '+maxdeposit)
                    result_list2.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get maxdeposit: '+str(json_response['maxdeposit']) +' != '+maxdeposit)
                    result_list2.append('FAIL')
                
                if(str(json_response['maxwithdraw']) == maxwithdraw):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get maxwithdraw: '+maxwithdraw)
                    result_list2.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get maxwithdraw: '+str(json_response['maxwithdraw']) +' != '+maxwithdraw)
                    result_list2.append('FAIL')
                
                if(str(json_response['mindeposit']) == mindeposit):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get mindeposit: '+mindeposit)
                    result_list2.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get mindeposit: '+str(json_response['mindeposit']) +' != '+mindeposit)
                    result_list2.append('FAIL')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_bankCard_edit_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminProviderBankCardEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_bankCard_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_bankCard_create_edit... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminProviderPaymentSetting(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_payment_setting', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(return_value):
            result_list.append('PASS')
            res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
            res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
        else:
            result_list.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_payment_setting... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminProviderPaymentListFrame(res_log, permission, paymentName, webName, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_provider_payment_list_frame', 'API.api_path', 'api/provider/payment/list/frame')
        else:
            ReplaceIniValue('admin_provider_payment_list_frame', 'API.api_path', 'api/provider/payment/list/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_payment_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                soup = BeautifulSoup(response_data, 'html.parser')
                soup_lis = soup.find_all("li", class_=False)
                if(len(soup_lis) != 0):
                    result_list.append('PASS')
                    if(web_or_mobile == 'Web'):
                        for soup_li in soup_lis:
                            soup_div = soup_li.find('div', class_='box-15')
                            if(str(soup_div.string).replace('\n','').replace(' ','') == paymentName):
                                soup_a = soup_li.find('a', attrs={'href':'provider_cash_edit.html'})
                                paymentId = soup_a.get('id')
#                                 ReplaceIniValue('setting', 'API.paymentId', soup_a.get('id'))
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
                    else:
                        for soup_li in soup_lis:
                            soup_div = soup_li.find('div', class_='crm-name')
                            if(str(soup_div.string).replace('\n','').replace(' ','') == webName+'-'+paymentName):
                                soup_a = soup_li.find('div', class_='crm-edit')
                                paymentId = soup_a.get('id')
#                                 ReplaceIniValue('setting', 'API.paymentId', soup_a.get('id'))
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get paymentName: '+webName+'-'+paymentName)
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+"- There's no paymentId")
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                paymentId = ''
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                paymentId = ''
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_payment_list_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in str(result_list) or not result_list):
        return (res_log, False, '')
    else:
        if('PASS' in result_list2):
            return (res_log, True, paymentId)
        else:
            return (res_log, False, '')


def AdminProviderPaymentEditInfoGet(res_log, permission, paymentName, paymentId, payTypeName, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_payment_edit_info_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                payType = json_response.get('pay_type')[0]
                if(len(list(json_response.get('pay_type')))==0):
                    payType = ''
                else:
                    payType = json_response.get('pay_type')[0]
                if(json_response.get('payment_id') == paymentId and json_response.get('payname') == paymentName and payType.get('pay_type_name') == payTypeName):
                    pay_type_id = str(payType.get('pay_type_id'))
                    payurl = str(json_response.get('payurl'))
                    enable = str(json_response.get('enable'))
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get (payurl, enable): ('+payurl+', '+enable+')')
                    result_list.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get get (payurl, enable)')
                    result_list.append('FAIL')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                pay_type_id = ''
                payurl = ''
                enable = ''
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                pay_type_id = ''
                payurl = ''
                enable = ''
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_payment_edit_info_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, '', '', '')
    else:
        return (res_log, True, pay_type_id, payurl, enable)


def AdminProviderPaymentEditCurrencyGet(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        edit_currency = []
        edit_v_currency = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_payment_edit_currency_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                if(len(json_response['currency']) != 0):
                    result_list2.append('PASS')
                    for node in json_response['currency']:
                        if(str(list(node.values())[0]) == '1'):
                            edit_currency.append(str(list(node.keys())[0]))
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get currency: '+', '.join(edit_currency))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get currency')
                
                if(len(json_response['v_currency']) != 0):
                    result_list2.append('PASS')
                    for node in json_response['v_currency']:
                        if(str(list(node.values())[0]) == '1'):
                            edit_currency.append(str(list(node.keys())[0]))
                            edit_v_currency.append(str(list(node.keys())[0]))
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get v_currency: '+', '.join(edit_v_currency))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get v_currency')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                edit_currency = ''
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                edit_currency = ''
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_payment_edit_currency_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, [])
    else:
        if('PASS' in result_list2):
            return (res_log, True, edit_currency)
        else:
            return (res_log, False, [])


def AdminProviderPaymentPayTypeEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_payment_payType_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_payment_payType_edit... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminProviderPaymentPayTypeGet(res_log, permission, payTypeId, paymentId, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_payment_edit_payType_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                deposit_acc = '888888'
                deposit_payratio = 5
                deposit_secretkey = 'f455ff77fa023376d810a97b68e54e32'
                max_deposit = 88888
                max_withdraw = 6666
                min_deposit = 10
                pay_option = 3
                withdraw_acc = '666666'
                withdraw_payratio = 5
                withdraw_secretkey = 'f455ff77fa023376d810a97b68e54e33'
                json_response = json.loads(response_data)
                if(json_response.get('deposit_acc') == deposit_acc):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get deposit_acc: '+deposit_acc)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get deposit_acc: '+str(json_response.get('deposit_acc'))+' != '+deposit_acc)
                
                if(json_response.get('deposit_payratio') == deposit_payratio):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get deposit_payratio: '+str(deposit_payratio))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get deposit_payratio: '+str(json_response.get('deposit_payratio'))+' != '+str(deposit_payratio))
                
                if(json_response.get('deposit_secretkey') == deposit_secretkey):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get deposit_secretkey: '+deposit_secretkey)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get deposit_secretkey: '+str(json_response.get('deposit_secretkey'))+' != '+deposit_secretkey)
                
                if(json_response.get('max_deposit') == max_deposit):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get max_deposit: '+str(max_deposit))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get max_deposit: '+str(json_response.get('max_deposit'))+' != '+str(max_deposit))
                
                if(json_response.get('max_withdraw') == max_withdraw):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get max_withdraw: '+str(max_withdraw))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get max_withdraw: '+str(json_response.get('max_withdraw'))+' != '+str(max_withdraw))
                
                if(json_response.get('min_deposit') == min_deposit):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get min_deposit: '+str(min_deposit))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get min_deposit: '+str(json_response.get('min_deposit'))+' != '+str(min_deposit))
                
                if(json_response.get('pay_option') == pay_option):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get pay_option: '+str(pay_option))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get pay_option: '+str(json_response.get('pay_option'))+' != '+str(pay_option))
                
                if(str(json_response.get('pay_type_id')) == payTypeId):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get pay_type_id: '+payTypeId)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get pay_type_id: '+str(json_response.get('pay_type_id'))+' != '+payTypeId)
                
                if(json_response.get('payment_id') == paymentId):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get payment_id: '+paymentId)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get payment_id: '+str(json_response.get('payment_id'))+' != '+paymentId)
                
                if(json_response.get('withdraw_acc') == withdraw_acc):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get withdraw_acc: '+withdraw_acc)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get withdraw_acc: '+str(json_response.get('withdraw_acc'))+' != '+withdraw_acc)
                
                if(json_response.get('withdraw_payratio') == withdraw_payratio):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get withdraw_payratio: '+str(withdraw_payratio))
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get withdraw_payratio: '+str(json_response.get('withdraw_payratio'))+' != '+str(withdraw_payratio))
                
                if(json_response.get('withdraw_secretkey') == withdraw_secretkey):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get withdraw_secretkey: '+withdraw_secretkey)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get withdraw_secretkey: '+str(json_response.get('withdraw_secretkey'))+' != '+withdraw_secretkey)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_payment_edit_payType_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)

    
def AdminProviderPaymentEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_payment_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_payment_edit... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)

def AdminProviderPayOptionPaymentGet(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        withdraw_or_deposit_id_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_payOption_payment_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                withdraw_or_deposit_account_list = list(json_response.keys())
                for element in withdraw_or_deposit_account_list:
                    withdraw_or_deposit_id_list.append(json_response.get(element)[0])
                
                if((not withdraw_or_deposit_account_list) or (not withdraw_or_deposit_id_list)):
                    result_list.append('FAIL')
                else:
                    withdraw_or_deposit_account = ', '.join(withdraw_or_deposit_account_list)
                    withdraw_or_deposit_id = ', '.join(withdraw_or_deposit_id_list)
                    res_log = WriteDebugLog(res_log, print_tab+'- Withdraw_or_Deposit AC: '+ withdraw_or_deposit_account)
                    res_log = WriteDebugLog(res_log, print_tab+'- Withdraw_or_Deposit ID: '+ withdraw_or_deposit_id)
                    result_list.append('PASS')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                withdraw_or_deposit_account = ''
                withdraw_or_deposit_id = ''
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                withdraw_or_deposit_account = ''
                withdraw_or_deposit_id = ''
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_payOption_payment_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, '', '')
    else:
        return (res_log, True, withdraw_or_deposit_account, withdraw_or_deposit_id)


def AdminProviderPayOptionCreateGet(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_payOption_create_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                if(json_response.get('currency') != None):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_payOption_create_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminProviderPayOptionCreate(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_payOption_create', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_payOption_create... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminProviderPayOptionListFrame(res_log, permission, payOptionName, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_provider_payOption_list_frame', 'API.api_path', 'api/provider/payOption/list/frame')
        else:
            ReplaceIniValue('admin_provider_payOption_list_frame', 'API.api_path', 'api/provider/payOption/list/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_payOption_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                soup = BeautifulSoup(response_data, 'html.parser')
                soup_lis = soup.find_all("li")
                for soup_li in soup_lis:
                    soup_payOptionIds = soup_li.find_all("div")
                    if(web_or_mobile == 'Web'):
                        for soup_payOptionId in soup_payOptionIds:
                            if(str(soup_payOptionId.string).replace('\n','').replace(' ','') == payOptionName):
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get payOptionName: '+payOptionName)
                                payOptionId = soup_li.find("a", attrs={'href':'provider_pay_edit.html'}).get("id")
#                                 ReplaceIniValue('setting', 'API.payOptionId', payOptionId)
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get payOptionId: '+payOptionId)
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
                    else:
                        for soup_payOptionId in soup_payOptionIds:
                            if(str(soup_payOptionId.string).replace('\n','').replace(' ','') == payOptionName):
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get payOptionName: '+payOptionName)
                                payOptionId = soup_li.find("a", attrs={'alt':'修改'}).get("id")
#                                 ReplaceIniValue('setting', 'API.payOptionId', payOptionId)
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get payOptionId: '+payOptionId)
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                payOptionId = ''
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                payOptionId = ''
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_payOption_list_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, '')
    else:
        if('PASS' in result_list2):
            return (res_log, True, payOptionId)
        else:
            return (res_log, False, '')


def AdminProviderPayOptionEditGetLayerFrame(res_log, permission, payOptionName, payOptionId, vipId, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_provider_payOption_edit_get_layer_frame', 'API.api_path', 'api/provider/payOption/edit/get/layer/frame')
        else:
            ReplaceIniValue('admin_provider_payOption_edit_get_layer_frame', 'API.api_path', 'api/provider/payOption/edit/get/layer/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_payOption_edit_get_layer_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
    
                soup = BeautifulSoup(response_data, 'html.parser')
                select_tag = soup.find("select", id=vipId)
                selected_values = select_tag.find_all("option")
                for selected_value in selected_values:
                    if(str(selected_value.string).replace('\n','').replace(' ','') == payOptionName):
                        if(selected_value.get('value') == payOptionId):
                            res_log = WriteDebugLog(res_log, print_tab+'- Success get payOptionName: '+payOptionName)
                            res_log = WriteDebugLog(res_log, print_tab+'- Success get payOptionId: '+payOptionId)
                            result_list2.append('PASS')
                            break
                        else:
                            res_log = WriteDebugLog(res_log, print_tab+'- Fail get payOptionId: '+selected_value.get('value')+' != '+payOptionId)
                            result_list2.append('FAIL')
                    else:
                        result_list2.append('FAIL')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_payOption_edit_get_layer_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('PASS' in result_list2):
            return (res_log, True)
        else:
            return (res_log, False)


def AdminProviderPayOptionEditLayer(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_payOption_edit_layer', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_payOption_edit_layer... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in str(result_list) or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminProviderPayOptionEditGetWithdraw(res_log, permission, paymentName, withdraw_or_deposit_id, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_payOption_edit_get_withdraw', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
    #             paymentName = IniValue('setting', 'API.paymentname')
    #             paymentId = IniValue('setting', 'API.paymentid')
                list_payment = []
                list_payment.append(withdraw_or_deposit_id)
                list_payment.append('1')
                json_response = json.loads(response_data)
                if(json_response[paymentName] == list_payment):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get list_payment: '+str(list_payment))
                    result_list.append('PASS')
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get list_payment: '+str(json_response[paymentName])+' != '+str(list_payment))
                    result_list.append('FAIL')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_payOption_edit_get_withdraw... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in str(result_list) or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)

def AdminProviderPayOptionEditGet(res_log, permission, payOptionName, payOptionId, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_payOption_edit_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                currency = IniValue('setting', 'API.currency')   
                json_response = json.loads(response_data)
                list_currency = []
                list_currency.append(currency)
                if(json_response['company_amount'] == 100):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['company_amount'])+' != 100')
                    
                if(json_response['company_count'] == 0):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['company_count'])+' != 0')
                    
                if(json_response['company_limit'] == 100):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['company_limit'])+' != 100')
                    
                if(json_response['company_maxdep'] == 5000):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['company_maxdep'])+' != 5000')
                    
                if(json_response['company_mindep'] == 10):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['company_mindep'])+' != 10')
                    
                if(json_response['company_promo'] == 1):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['company_promo'])+' != 1')
                    
                if(json_response['company_ratio'] == 50):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['company_ratio'])+' != 50')
                    
                if(json_response['currency'][currency] == 1):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['currency'][currency])+' != 1')
                    
                if(json_response['deposit'] == list_currency):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['deposit'])+' != '+str(list_currency))
                    
                if(json_response['duplicate_withdraw_hours'] == 2):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['duplicate_withdraw_hours'])+' != 2')
                    
                if(json_response['free_process_fee_times'] == 1):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['free_process_fee_times'])+' != 1')
                    
                if(json_response['normal_audit'] == 0):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['normal_audit'])+' != 0')
                    
                if(json_response['normal_audit_percent'] == 100):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['normal_audit_percent'])+' != 100')
                    
                if(json_response['normal_audit_process_rate'] == 50):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['normal_audit_process_rate'])+' != 50')
                    
                if(json_response['normal_audit_relaxation_amount'] == 10):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['normal_audit_relaxation_amount'])+' != 10')
                
                if(json_response['online_amount'] == 100):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['online_amount'])+' != 100')
                    
                if(json_response['online_count'] == 0):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['online_count'])+' != 0')
                    
                if(json_response['online_limit'] == 1000):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['online_limit'])+' != 1000')
                    
                if(json_response['online_maxdep'] == 5000):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['online_maxdep'])+' != 5000')
                    
                if(json_response['online_mindep'] == 10):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['online_mindep'])+' != 10')
                    
                if(json_response['online_promo'] == 1):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['online_promo'])+' != 1')
                    
                if(json_response['online_ratio'] == 50):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['online_ratio'])+' != 50')
                    
                if(json_response['payoption_id'] == payOptionId):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['payoption_id'])+' != '+str(payOptionId))
                    
                if(json_response['payoption_name'] == payOptionName):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['payoption_name'])+' != '+str(payOptionName))
                    
                if(json_response['review'] == 1):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['review'])+' != 1')
                    
                if(json_response['review_amount'] == 5000):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['review_amount'])+' != 5000')
                    
                if(json_response['review_hour'] == 1):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['review_hour'])+' != 1')
                    
                if(json_response['transfer_preferential_amount'] == 100):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['transfer_preferential_amount'])+' != 100')
                    
                if(json_response['transfer_preferential_maximum'] == 500):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['transfer_preferential_maximum'])+' != 500')
                    
                if(json_response['transfer_preferential_maximum_a_day'] == 500):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['transfer_preferential_maximum_a_day'])+' != 500')
                    
                if(json_response['transfer_preferential_rate'] == 1):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['transfer_preferential_rate'])+' != 1')
                    
#                 if(json_response['v_currency']['V_BTC'] == 0):
#                     result_list.append('PASS')
#                 else:
#                     result_list.append('FAIL')
#                     res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['v_currency']['V_BTC'])+' != 0')
                    
                if(json_response['withdraw'] == list_currency):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['withdraw'])+' != '+ str(list_currency))
                    
                if(json_response['withdraw_maximum'] == 10000):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['withdraw_maximum'])+' != 10000')
                    
                if(json_response['withdraw_minimum'] == 100):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['withdraw_minimum'])+' != 100')
                    
                if(json_response['withdraw_process_maximum'] == 100):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['withdraw_process_maximum'])+' != 100')
                    
                if(json_response['withdraw_process_rate'] == 10):
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'-'+str(json_response['withdraw_process_rate'])+' != 10')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_payOption_edit_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in str(result_list) or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminProviderPayOptionEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_payOption_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_payOption_edit... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in str(result_list) or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminProviderPayOptionBankInfo(res_log, permission, payOptionName, payOptionId, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_payOption_bank_info', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                if(json_response.get('payoption_id') == payOptionId and json_response.get('payoption_name') == payOptionName):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get payoption (name, id): ('+payOptionName+', '+payOptionId+')')
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get payoption (name, id): ('+json_response.get('payoption_name')+', '+json_response.get('payoption_id')+') != ('+payOptionName+', '+payOptionId+')')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_payOption_bank_info... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminProviderPayOptionBankGet(res_log, permission, bankName, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_payOption_bank_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
    #             bankName = IniValue('setting', 'API.bankname')
                json_response = json.loads(response_data)
                if(json_response[bankName].count('0') == 1):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get (bankName, value): ('+bankName+', 0)')
                    result_list2.append('PASS')
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get (bankName, value)')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_payOption_bank_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminProviderPayOptionBankEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_payOption_bank_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_payOption_bank_edit... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebTransferListFrame(res_log, permission, playerAcc, playerId, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_webPlayer_transfer_list_frame', 'API.api_path', 'api/webPlayer/transfer/list/frame')
        else:
            ReplaceIniValue('admin_webPlayer_transfer_list_frame', 'API.api_path', 'api/webPlayer/transfer/list/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_transfer_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
    #             playerAcc = IniValue('setting', 'API.playeracc')
    #             playerId = IniValue('setting', 'API.playerid')
                soup = BeautifulSoup(response_data, 'html.parser')
                soup_lis = soup.find_all("li")
                if(web_or_mobile == 'Web'):
                    for soup_li in soup_lis:
                        soup_divs = soup_li.find_all("div")
                        for soup_div in soup_divs:
                            if(str(soup_div.string).replace('\n','').replace(' ','') == playerAcc):
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get playerAcc: '+playerAcc)
                                player_id = soup_div.get('id')
                                if(player_id == playerId):
                                    res_log = WriteDebugLog(res_log, print_tab+'- Success get playerId: '+player_id)
                                    result_list2.append('PASS')
                                    break
                                else:
                                    result_list2.append('FAIL')
                            else:
                                result_list2.append('FAIL')
                        if('PASS' in result_list2):
                            break
                else:
                    soup_spans = soup.find_all("span")
                    for soup_span in soup_spans:
                        if(str(soup_span.string).replace('\n','').replace(' ','') == playerAcc):
                            res_log = WriteDebugLog(res_log, print_tab+'- Success get playerAcc: '+playerAcc)
                            player_id = soup_span.get('id')
                            if(player_id == playerId):
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get playerId: '+player_id)
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
                        else:
                            result_list2.append('FAIL')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_transfer_list_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('PASS' in result_list2):
            return (res_log, True)
        else:
            return (res_log, False)


def AdminWebTransfer(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_transfer', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_transfer... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebTransferAll(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_transfer_all', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_transfer_all... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminOrgDeptLoadCreate(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        str_permission_final = ''
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_org_dept_load_create', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                if(json_response.get('accCont07').get('bc') == None):
                    result_list.append('FAIL')
                else:
                    str_permission_final = response_data
                    result_list.append(JsonValueCompare(response_data, 'accCont01|ir', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont02|qs', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|orp', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|orpvd', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|orb', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|orw', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|ord', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|orplr', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|prr', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|wr', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|plrr', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|or', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont03|gl', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont04|ee', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont04|dp', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont05|pt', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont05|prt', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont05|ptt', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont05|ptr', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|dm', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|lv', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|wb', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|plr', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|plrt', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|plrd', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|promo', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|cms', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|nt', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|ms', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|ma', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|st', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|risk', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont06|gs', '1'))
    #                 result_list.append(JsonValueCompare(response_data, 'accCont06|pr', '1'))
    #                 result_list.append(JsonValueCompare(response_data, 'accCont07|pvd', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont07|bc', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont07|pm', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont07|po', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont08|md', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont08|mw', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont08|bh', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont08|er', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont08|bt', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont08|rs', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont08|rp', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont08|rfs', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont08|wa', '1'))
                    result_list.append(JsonValueCompare(response_data, 'accCont08|ia', '1'))
                     
#                     ReplaceAllJsonValue(str_permission_final, 'accCont06|dm', 0)
                    
                    ir_ = json_response.get('accCont01').get('ir')
                    qs_ = json_response.get('accCont02').get('qs')
                    orp_ = json_response.get('accCont03').get('orp')
                    orpvd_ = json_response.get('accCont03').get('orpvd')
                    orb_ = json_response.get('accCont03').get('orb')
                    orw_ = json_response.get('accCont03').get('orw')
                    ord_ = json_response.get('accCont03').get('ord')
                    orplr_ = json_response.get('accCont03').get('orplr')
                    prr_ = json_response.get('accCont03').get('prr')
                    wr_ = json_response.get('accCont03').get('wr')
                    plrr_ = json_response.get('accCont03').get('plrr')
                    or_ = json_response.get('accCont03').get('or')
                    gl_ = json_response.get('accCont03').get('gl')
                    ee_ = json_response.get('accCont04').get('ee')
                    dp_ = json_response.get('accCont04').get('dp')
                    pt_ = json_response.get('accCont05').get('pt')
                    prt_ = json_response.get('accCont05').get('prt')
                    ptt_ = json_response.get('accCont05').get('ptt')
                    ptr_ = json_response.get('accCont05').get('ptr')
                    dm_ = json_response.get('accCont06').get('dm')
                    lv_ = json_response.get('accCont06').get('lv')
                    wb_ = json_response.get('accCont06').get('wb')
                    plr_ = json_response.get('accCont06').get('plr')
                    plrt_ = json_response.get('accCont06').get('plrt')
                    plrd_ = json_response.get('accCont06').get('plrd')
                    promo_ = json_response.get('accCont06').get('promo')
                    cms_ = json_response.get('accCont06').get('cms')
                    nt_ = json_response.get('accCont06').get('nt')
                    ms_ = json_response.get('accCont06').get('ms')
                    ma_ = json_response.get('accCont06').get('ma')
                    risk_ = json_response.get('accCont06').get('risk')
                    st_ = json_response.get('accCont06').get('st')
                    gs_ = json_response.get('accCont06').get('gs')
                    bc_ = json_response.get('accCont07').get('bc')
                    pm_ = json_response.get('accCont07').get('pm')
                    po_ = json_response.get('accCont07').get('po')
                    md_ = json_response.get('accCont08').get('md')
                    mw_ = json_response.get('accCont08').get('mw')
                    bh_ = json_response.get('accCont08').get('bh')
                    er_ = json_response.get('accCont08').get('er')
                    bt_ = json_response.get('accCont08').get('bt')
                    rs_ = json_response.get('accCont08').get('rs')
                    rp_ = json_response.get('accCont08').get('rp')
                    rfs_ = json_response.get('accCont08').get('rfs')
                    wa_ = json_response.get('accCont08').get('wa')
                    ia_ = json_response.get('accCont08').get('ia')
    #                 pr_ = json_response.get('accCont06').get('pr')
    #                 pvd_ = json_response.get('accCont07').get('pvd')
                    json_permission_final = {}
                    json_permission_final = ({**ir_, **qs_, **orp_, **orpvd_, **orb_, **orw_, **ord_, **orplr_, **prr_, **wr_, **plrr_, **or_, **gl_, **ee_, **dp_, 
                                              **pt_, **prt_, **ptt_, **dm_, **lv_, **wb_, **plr_, **plrt_, **plrd_, **promo_, **cms_, **nt_, **ms_, **ma_, **risk_, 
                                              **st_, **gs_, **ptr_, **bc_, **pm_, **po_, **md_, **mw_, **bh_, **er_, **bt_, **rs_, **rp_, **rfs_, **wa_, **ia_})
#                     str_permission_final = str(json_permission_final).replace("'",'"').replace(' ','')
                    str_permission_final = ReplaceAllJsonValue(json_permission_final, '', 0)
                    str_permission_final = ReplaceJsonString(str_permission_final, 'ee_c', 1)
                    str_permission_final = ReplaceJsonString(str_permission_final, 'ee_r', 1)
                    str_permission_final = ReplaceJsonString(str_permission_final, 'ee_u', 1)
                    str_permission_final = ReplaceJsonString(str_permission_final, 'ee_d', 1)
                    str_permission_final = ReplaceJsonString(str_permission_final, 'dp_c', 1)
                    str_permission_final = ReplaceJsonString(str_permission_final, 'dp_r', 1)
                    str_permission_final = ReplaceJsonString(str_permission_final, 'dp_u', 1)
                    str_permission_final = ReplaceJsonString(str_permission_final, 'dp_d', 1)
                    result_list2.append('PASS')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_org_dept_load_create... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, str_permission_final)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False, str_permission_final)
        else:
            return (res_log, True, str_permission_final)


def AdminOrgDeptCreate(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_org_dept_create', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        else:
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_org_dept_create... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminOrgDeptListFrame(res_log, permission, depname, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_org_dept_list_frame', 'API.api_path', 'api/organization/department/list/frame')
        else:
            ReplaceIniValue('admin_org_dept_list_frame', 'API.api_path', 'api/organization/department/list/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_org_dept_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
    #             depname = IniValue('setting', 'API.depname')
                soup = BeautifulSoup(response_data, 'html.parser')
                if(web_or_mobile == 'Web'):
                    soup_as = soup.find_all('a', class_='list-group')
                    for soup_a in soup_as:
                        soup_divs = soup_a.find_all('div', class_=True)
                        for soup_div in soup_divs:
                            if(str(soup_div.string).replace('\n','').replace(' ','') == depname):
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get depname: '+depname)
                                depId = soup_a.get('id')
        #                         ReplaceIniValue('setting', 'API.depId', depId)
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get depId: '+depId)
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
                        if('PASS' in result_list2):
                            break
                else:
                    soup_lis = soup.find_all('li')
                    for soup_li in soup_lis:
                        soup_divs = soup_li.find_all('div', class_=True)
                        for soup_div in soup_divs:
                            if(depname in str(soup_div.text).replace('\n','').replace(' ','')): 
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get depname: '+depname)
                                depId = soup_li.find('i', id=True).get('id')
                                ReplaceIniValue('setting', 'API.depId', depId)
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get depId: '+depId)
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
                        if('PASS' in result_list2):
                            break
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                depId = ''
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                depId = ''
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_org_dept_list_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, '')
    else:
        if('PASS' in result_list2):
            return (res_log, True, depId)
        else:
            return (res_log, False, '')


def AdminOrgDeptLoadEdit(res_log, permission, depname, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_org_dept_load_edit', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
    #             depname = IniValue('setting', 'API.depname')
                if(json_response.get('og_name') == depname):
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get depname: '+depname)
                else:
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get depname: '+json_response.get('og_name')+' != '+depname)
                
                result_list2.append(JsonValueCompare(response_data, 'accCont01|ir', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont02|qs', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|orp', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|orpvd', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|orb', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|orw', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|ord', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|orplr', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|prr', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|wr', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|plrr', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|or', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|gl', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont04|ee', '1'))
                result_list2.append(JsonValueCompare(response_data, 'accCont04|dp', '1'))
                result_list2.append(JsonValueCompare(response_data, 'accCont05|pt', '0'))
                if(permission == 'Initial'):
                    result_list2.append(JsonValueCompare(response_data, 'accCont05|prt', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont05|ptt', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont05|ptr', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|dm', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|lv', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|wb', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|plr', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|plrt', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|plrd', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|promo', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|cms', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|nt', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|ms', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|ma', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|st', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|risk', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|gs', '0'))
        #                 result_list2.append(JsonValueCompare(response_data, 'accCont06|pr', '0'))
        #                 result_list2.append(JsonValueCompare(response_data, 'accCont07|pvd', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont07|bc', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont07|pm', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont07|po', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|md', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|mw', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|bh', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|er', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|bt', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|rs', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|rp', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|rfs', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|wa', '0'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|ia', '0'))
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_org_dept_load_edit... %s' % str(e))
    
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminOrgDeptEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_org_dept_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_org_dept_edit... %s' % str(e))
    
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminOrgDeptList(res_log, permission, depName, depId, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_org_dept_list', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
    #             depName = IniValue('setting', 'API.depname')
    #             depId = IniValue('setting', 'API.depid')
                json_response = json.loads(response_data)
                for json_element in json_response:
                    if(json_element.get('og_name') == depName):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get depName: '+depName)
                        result_list2.append('PASS')
                        if(json_element.get('og_sid') == depId):
                            res_log = WriteDebugLog(res_log, print_tab+'- Success get depId: '+depId)
                            result_list2.append('PASS')
                            break
                        else:
                            result_list2.append('FAIL')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_org_dept_list... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
        
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminOrgJobtitlePermission(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        str_permission_final = ''
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_org_jobtitle_permission', False, False)
        res_log = WriteDebugLog(res_log, print_tab+'Response data: '+ response_data)
        
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                result_list2.append(JsonValueCompare(response_data, 'accCont01|ir', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont02|qs', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|orp', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|orpvd', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|orb', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|orw', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|ord', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|orplr', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|prr', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|wr', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|plrr', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|or', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|gl', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont04|ee', '1'))
                result_list2.append(JsonValueCompare(response_data, 'accCont04|dp', '1'))
                result_list2.append(JsonValueCompare(response_data, 'accCont05|pt', '[]'))
                if(permission == 'Initial'):
                    result_list2.append(JsonValueCompare(response_data, 'accCont05|prt', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont05|ptt', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont05|ptr', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|dm', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|lv', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|wb', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|plr', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|plrt', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|plrd', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|promo', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|cms', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|nt', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|ms', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|ma', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|st', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|risk', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|gs', '[]'))
        #                 result_list2.append(JsonValueCompare(response_data, 'accCont06|pr', '[]'))
        #                 result_list2.append(JsonValueCompare(response_data, 'accCont07|pvd', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont07|bc', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont07|pm', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont07|po', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|md', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|mw', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|bh', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|er', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|bt', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|rs', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|rp', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|rfs', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|wa', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|ia', '[]'))
                
#                 ir_ = json_response.get('accCont01').get('ir')
#                 qs_ = json_response.get('accCont02').get('qs')
#                 orp_ = json_response.get('accCont03').get('orp')
#                 orpvd_ = json_response.get('accCont03').get('orpvd')
#                 orb_ = json_response.get('accCont03').get('orb')
#                 orw_ = json_response.get('accCont03').get('orw')
#                 ord_ = json_response.get('accCont03').get('ord')
#                 orplr_ = json_response.get('accCont03').get('orplr')
#                 prr_ = json_response.get('accCont03').get('prr')
#                 wr_ = json_response.get('accCont03').get('wr')
#                 plrr_ = json_response.get('accCont03').get('plrr')
#                 or_ = json_response.get('accCont03').get('or')
#                 gl_ = json_response.get('accCont03').get('gl')
#                 ee_ = json_response.get('accCont04').get('ee')
#                 dp_ = json_response.get('accCont04').get('dp')
#                 pt_ = json_response.get('accCont05').get('pt')
#                 prt_ = json_response.get('accCont05').get('prt')
#                 ptt_ = json_response.get('accCont05').get('ptt')
#                 ptr_ = json_response.get('accCont05').get('ptr')
#                 dm_ = json_response.get('accCont06').get('dm')
#                 lv_ = json_response.get('accCont06').get('lv')
#                 wb_ = json_response.get('accCont06').get('wb')
#                 plr_ = json_response.get('accCont06').get('plr')
#                 plrt_ = json_response.get('accCont06').get('plrt')
#                 plrd_ = json_response.get('accCont06').get('plrd')
#                 promo_ = json_response.get('accCont06').get('promo')
#                 cms_ = json_response.get('accCont06').get('cms')
#                 nt_ = json_response.get('accCont06').get('nt')
#                 ms_ = json_response.get('accCont06').get('ms')
#                 ma_ = json_response.get('accCont06').get('ma')
#                 risk_ = json_response.get('accCont06').get('risk')
#                 st_ = json_response.get('accCont06').get('st')
#                 gs_ = json_response.get('accCont06').get('gs')
#                 bc_ = json_response.get('accCont07').get('bc')
#                 pm_ = json_response.get('accCont07').get('pm')
#                 po_ = json_response.get('accCont07').get('po')
#                 md_ = json_response.get('accCont08').get('md')
#                 mw_ = json_response.get('accCont08').get('mw')
#                 bh_ = json_response.get('accCont08').get('bh')
#                 er_ = json_response.get('accCont08').get('er')
#                 bt_ = json_response.get('accCont08').get('bt')
#                 rs_ = json_response.get('accCont08').get('rs')
#                 rp_ = json_response.get('accCont08').get('rp')
#                 rfs_ = json_response.get('accCont08').get('rfs')
#                 wa_ = json_response.get('accCont08').get('wa')
#                 ia_ = json_response.get('accCont08').get('ia')
# #                 pr_ = json_response.get('accCont06').get('pr')
# #                 pvd_ = json_response.get('accCont07').get('pvd')
#                 json_permission_final = {}
#                 json_permission_final = ({**ir_, **qs_, **orp_, **orpvd_, **orb_, **orw_, **ord_, **orplr_, **prr_, **wr_, **plrr_, **or_, **gl_, **ee_, **dp_, 
#                                           **pt_, **prt_, **ptt_, **dm_, **lv_, **wb_, **plr_, **plrt_, **plrd_, **promo_, **cms_, **nt_, **ms_, **ma_, **risk_, 
#                                           **st_, **gs_, **ptr_, **bc_, **pm_, **po_, **md_, **mw_, **bh_, **er_, **bt_, **rs_, **rp_, **rfs_, **wa_, **ia_})
#                 str_permission_final = str(json_permission_final).replace("'",'"').replace(' ','')
#                 str_permission_final = ReplaceAllJsonValue(json_permission_final, '', 0)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_org_jobtitle_permission... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminOrgJobtitleCreate(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_org_jobtitle_create', True, False)
        res_log = WriteDebugLog(res_log, 'Response data: '+ response_data)
        
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_org_jobtitle_create... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminOrgJobtitleListFrame(res_log, permission, depTitle, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_org_jobtitle_list_frame', 'API.api_path', 'api/organization/department/jobtitle/list/frame')
        else:
            ReplaceIniValue('admin_org_jobtitle_list_frame', 'API.api_path', 'api/organization/department/jobtitle/list/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_org_jobtitle_list_frame', False, False)
        res_log = WriteDebugLog(res_log, print_tab+'Response data: '+ response_data)
        
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                soup = BeautifulSoup(response_data, 'html.parser')
                soup_lis = soup.find_all('li')
                if(web_or_mobile == 'Web'):
                    for soup_li in soup_lis:
                        soup_divs = soup_li.find_all('div', class_=True)
                        for soup_div in soup_divs:
                            if(str(soup_div.string).replace('\n','').replace(' ','') == depTitle):
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get depTitle: '+depTitle)
                                depTitleId = soup_li.find('a', attrs={'href':'organize_office_edit.html'}).get('id')
            #                         ReplaceIniValue('setting', 'API.depTitleId', depTitleId)
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get depTitleId: '+depTitleId)
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
                        if('PASS' in result_list2):
                            break
                else:
                    for soup_li in soup_lis:
                        soup_divs = soup_li.find_all('div', class_=True)
                        for soup_div in soup_divs:
                            if(str(soup_div.string).replace('\n','').replace(' ','') == depTitle):
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get depTitle: '+depTitle)
                                depTitleId = soup_li.find('a', attrs={'alt':'修改'}).get('id')
    #                             ReplaceIniValue('setting', 'API.depTitleId', depTitleId)
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get depTitleId: '+depTitleId)
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
                        if('PASS' in result_list2):
                            break
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                depTitleId = ''
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                depTitleId = ''
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_org_jobtitle_list_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, '')
    else:
        if('PASS' in result_list2):
            return (res_log, True, depTitleId)
        else:
            return (res_log, False, '')


def AdminOrgJobtitleList(res_log, permission, depTitle, depTitleId, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_org_jobtitle_list', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_list = json.loads(response_data)
    #             print(len(list(json_list)))
                for each_element in list(json_list):
                    if(each_element['dp_name'] == depTitle):
                        result_list2.append('PASS')
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get depTitle: '+depTitle)
                        if(each_element['dp_sid'] == depTitleId):
                            result_list2.append('PASS')
                            res_log = WriteDebugLog(res_log, print_tab+'- Success get depTitleId: '+depTitleId)
                        else:
                            result_list2.append('FAIL')
                            res_log = WriteDebugLog(res_log, print_tab+'- Fail get depTitleId: '+each_element['dp_sid']+' != '+depTitleId)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_org_jobtitle_list... %s' % str(e))
    
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminOrgJobtitleGet(res_log, permission, depTitle, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_org_jobtitle_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                if(json_response['dp_name'] == depTitle):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get depTitle: '+depTitle)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get depTitle: '+json_response['dp_name']+' != '+depTitle)
                
                result_list2.append(JsonValueCompare(response_data, 'accCont01|ir', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont02|qs', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|orp', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|orpvd', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|orb', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|orw', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|ord', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|orplr', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|prr', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|wr', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|plrr', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|or', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont03|gl', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont04|ee', '1'))
                result_list2.append(JsonValueCompare(response_data, 'accCont04|dp', '1'))
                result_list2.append(JsonValueCompare(response_data, 'accCont05|pt', '[]'))
                if(permission == 'Initial'):
                    result_list2.append(JsonValueCompare(response_data, 'accCont05|prt', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont05|ptt', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont05|ptr', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|dm', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|lv', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|wb', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|plr', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|plrt', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|plrd', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|promo', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|cms', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|nt', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|ms', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|ma', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|st', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|risk', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont06|gs', '[]'))
        #                 result_list2.append(JsonValueCompare(response_data, 'accCont06|pr', '[]'))
        #                 result_list2.append(JsonValueCompare(response_data, 'accCont07|pvd', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont07|bc', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont07|pm', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont07|po', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|md', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|mw', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|bh', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|er', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|bt', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|rs', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|rp', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|rfs', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|wa', '[]'))
                result_list2.append(JsonValueCompare(response_data, 'accCont08|ia', '[]'))
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_org_jobtitle_get... %s' % str(e))
    
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminOrgJobtitleEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_org_jobtitle_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_org_jobtitle_edit... %s' % str(e))
    
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminOrgEmployeeCreate(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_org_employee_create', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_org_employee_create... %s' % str(e))
    
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminOrgEmployeeListFrame(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile =='Web'):
            ReplaceIniValue('admin_org_employee_list_frame', 'API.api_path', 'api/organization/department/jobtitle/employee/list/frame')
        else:
            ReplaceIniValue('admin_org_employee_list_frame', 'API.api_path', 'api/organization/department/jobtitle/employee/list/frame/m')
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_org_employee_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                soup = BeautifulSoup(response_data, 'html.parser')
                if(web_or_mobile =='Web'):
                    userId = soup.find('a', attrs={'href':'organize_all_mem_edit.html'}).get('id')
                else:
                    userId = soup.find('a', attrs={'alt':'修改'}).get('id')
                
                if(userId):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get userId: '+userId)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get userId')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                userId = ''
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                userId = ''
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_org_employee_list_frame... %s' % str(e))
    
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, '')
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False, '')
        else:
            return (res_log, True, userId)


def AdminOrgEmployeeListSingle(res_log, permission, userAcc, depTitleId, depId, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_org_employee_list_single', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                if(json_response['user_acc'] == userAcc):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get userAcc: '+userAcc)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get userAcc')
                
                if(json_response['dp_sid'] == depTitleId):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get depTitleId: '+depTitleId)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get depTitleId')
                
                if(json_response['og_sid'] == depId):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get depId: '+depId)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get depId')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_org_employee_list_single... %s' % str(e))
    
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminOrgEmployeeListAllFrame(res_log, permission, userAcc, userId, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_org_employee_list_all_frame', 'API.api_path', 'api/organization/department/jobtitle/employee/list/all/frame')
        else:
            ReplaceIniValue('admin_org_employee_list_all_frame', 'API.api_path', 'api/organization/department/jobtitle/employee/list/all/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_org_employee_list_all_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                soup = BeautifulSoup(response_data, 'html.parser')
                soup_lis = soup.find_all('li')
                for soup_li in soup_lis:
                    soup_divs = soup_li.find_all('div', class_=True)
                    for soup_div in soup_divs:
                        if(str(soup_div.string).replace('\n','').replace(' ','') == userAcc):
                            res_log = WriteDebugLog(res_log, print_tab+'- Success get userAcc: '+userAcc)
                            if(web_or_mobile == 'Web'):
                                user_Id = soup_li.find('a', attrs={'href':'organize_all_mem_edit.html'}).get('id')
                            else:
                                user_Id = soup_li.find('a', attrs={'alt':'修改'}).get('id')
                            
                            if(user_Id == userId):
                                result_list2.append('PASS')
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get userId: '+userId)
                            else:
                                result_list2.append('FAIL')
                                res_log = WriteDebugLog(res_log, print_tab+'- Fail get userId')
                            break
                        else:
                            result_list2.append('FAIL')
                    if('PASS' in result_list2):
                        break
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_org_employee_list_all_frame... %s' % str(e))
    
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('PASS' in result_list2):
            return (res_log, True)
        else:
            return (res_log, False)


def AdminOrgEmployeeListDescFrame(res_log, permission, userId, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_org_employee_list_desc_frame', 'API.api_path', 'api/organization/department/jobtitle/employee/list/description/frame')
        else:
            ReplaceIniValue('admin_org_employee_list_desc_frame', 'API.api_path', 'api/organization/department/jobtitle/employee/list/description/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_org_employee_list_desc_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                soup = BeautifulSoup(response_data, 'html.parser')
                if(web_or_mobile == 'Web'):
                    user_Id = soup.find('a', attrs={'href':'organize_mem_edit.html'}).get('id')
                else:
                    user_Id = soup.find('a', attrs={'alt':'修改'}).get('id')
                
                if(user_Id == userId):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get userId: '+userId)
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get userId')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
                result_list2.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_org_employee_list_desc_frame... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminOrgEmployeeEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_org_employee_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_org_employee_edit... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminOrgEmployeeWebsiteList(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_org_employee_websitelist', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        
        if(permission == 'Boss'):
            if(return_value):
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                if(CheckPermissionDenied(print_tab, res_log, response_data, 'S02', 'No Data')):
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- No data')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_org_employee_websitelist... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminOrgEmployeeDelete(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_org_employee_delete', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_org_employee_delete... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminOrgJobtitleDelete(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_org_jobtitle_delete', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
                
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_org_jobtitle_delete... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebPlayerProviderGet(res_log, permission, list_type, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_player_provider_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(return_value):
            result_list.append('PASS')
            res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
            res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            json_response = json.loads(response_data)
            for game_type in list_type:
                if(json_response.get(game_type) == None):
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail key: "'+ game_type+'"')
                else:
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success '+game_type+': '+str(json_response[game_type]))
        else:
            result_list.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_player_provider_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebPlayerTransactionGet(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_player_transaction_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(return_value):
            result_list.append('PASS')
            res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
            res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
#                 json_response = json.loads(response_data)
#                 for game_type in list_type:
#                     if(json_response.get(game_type) == None):
#                         result_list.append('FAIL')
#                         res_log = WriteDebugLog(res_log, print_tab+'- Fail key: "'+ game_type+'"')
#                     else:
#                         result_list.append('PASS')
#                         res_log = WriteDebugLog(res_log, print_tab+'- Success '+game_type+': '+str(json_response[game_type]))
        else:
            result_list.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_player_transaction_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminExport(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_export', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(return_value):
            result_list.append('PASS')
            res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
            res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
#                 json_response = json.loads(response_data)
#                 for game_type in list_type:
#                     if(json_response.get(game_type) == None):
#                         result_list.append('FAIL')
#                         res_log = WriteDebugLog(res_log, print_tab+'- Fail key: "'+ game_type+'"')
#                     else:
#                         result_list.append('PASS')
#                         res_log = WriteDebugLog(res_log, print_tab+'- Success '+game_type+': '+str(json_response[game_type]))
        else:
            result_list.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_export... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebPlayerGameHistoryGet(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_player_game_history_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(return_value):
            result_list.append('PASS')
            res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
            res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
#                 json_response = json.loads(response_data)
#                 for game_type in list_type:
#                     if(json_response.get(game_type) == None):
#                         result_list.append('FAIL')
#                         res_log = WriteDebugLog(res_log, print_tab+'- Fail key: "'+ game_type+'"')
#                     else:
#                         result_list.append('PASS')
#                         res_log = WriteDebugLog(res_log, print_tab+'- Success '+game_type+': '+str(json_response[game_type]))
        else:
            result_list.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_player_game_history_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebPlayerVipList(res_log, permission, vipName, vipId, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_player_vip_list', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
    #             vipId = IniValue('setting', 'API.vipid')
    #             vipName = IniValue('setting', 'API.vipname')
                json_response = json.loads(response_data)
                if(json_response.get(vipId) == vipName):
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get vipName: '+vipName)
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get vipName: '+json_response.get(vipId)+' != '+vipName)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_player_vip_list... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebPlayerCreateGet(res_log, permission, webName, webId, vipName, vipId, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_player_create_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                json_response = json.loads(response_data)
                if(json_response['layerList'][vipId] ==  vipName and json_response['webList'][webId] == webName):
                    result_list2.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get (layerList, webList): ('+vipName+', '+webName+')')
                else:
                    result_list2.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get (layerList, webList): ('+json_response['layerList'][vipId]+', '+json_response['webList'][webId]+')')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_player_create_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        if('FAIL' in result_list2 or not result_list2):
            return (res_log, False)
        else:
            return (res_log, True)


def AdminWebPlayerCreate(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_player_create', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_player_create... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebPlayerListFrame(res_log, permission, playerAcc, web_or_mobile = 'Web'):
    try:
        result_list = []
        result_list2 = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_webPlayer_player_list_frame', 'API.api_path', 'api/webPlayer/player/list/frame')
        else:
            ReplaceIniValue('admin_webPlayer_player_list_frame', 'API.api_path', 'api/webPlayer/player/list/frame/m')
        
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_player_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                soup = BeautifulSoup(response_data, 'html.parser')
                if(web_or_mobile == 'Web'):
                    soup_lis = soup.find_all("li")
                    for soup_li in soup_lis:
                        soup_divs = soup_li.find_all("div")
                        for soup_div in soup_divs:
                            if(str(soup_div.string).replace('\n','').replace(' ','') == playerAcc):
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get playerAcc: '+playerAcc)
                                playerId = soup_li.find("a", attrs={'href':'web_mem_edit.html'}).get('id')
                                res_log = WriteDebugLog(res_log, print_tab+'- Success get playerId: '+playerId)
    #                             ReplaceIniValue('setting', 'API.playerid', playerId)
                                result_list2.append('PASS')
                                break
                            else:
                                result_list2.append('FAIL')
                else:
                    soup_div = soup.find("div", class_='crm-name')
                    if(playerAcc in soup_div.text):
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get playerAcc: '+playerAcc)
                        playerId = soup_div.find("div", class_='vip-type').get('id')
                        res_log = WriteDebugLog(res_log, print_tab+'- Success get playerId: '+playerId)
    #                     ReplaceIniValue('setting', 'API.playerid', playerId)
                        result_list2.append('PASS')
                    else:
                        result_list2.append('FAIL')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
                result_list2.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
                result_list2.append('PASS')
                playerId = ''
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_player_list_frame... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    WriteLog(result_list2)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, '')
    else:
        if('PASS' in result_list2):
            return (res_log, True, playerId)
        else:
            return (res_log, False, '')


def AdminWebPlayerEditGet(res_log, permission, webId, vipId, state, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_player_edit_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                playerAcc = IniValue('setting', 'API.playeracc')
                json_response = json.loads(response_data)
                if(json_response['acc'] == playerAcc):
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get playerAcc: '+playerAcc)
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get playerAcc: '+json_response['acc']+' != '+playerAcc)
                
                if(json_response['vip_id'] == vipId):
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get vipId: '+vipId)
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get vipId: '+json_response['vip_id']+' != '+vipId)
                
                if(json_response['web_id'] == webId):
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get webId: '+webId)
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get webId: '+json_response['web_id']+' != '+webId)
                
                if(json_response['enable'] == state):
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, print_tab+'- Success get enable: '+state)
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, print_tab+'- Fail get enable: '+json_response['enable']+' != '+state)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_player_edit_get... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
        
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminWebPlayerEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_webPlayer_player_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_webPlayer_player_edit... %s' % str(e))
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'- - -'+'\n')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminProviderContentListFrame(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        if(web_or_mobile == 'Web'):
            ReplaceIniValue('admin_provider_content_list_frame', 'API.api_path', 'api/provider/content/list/frame')
        else:
            ReplaceIniValue('admin_provider_content_list_frame', 'API.api_path', 'api/provider/content/list/frame/m')
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_content_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else: # Permission denied.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_content_list_frame... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminProviderContentEditGet(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_content_edit_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else: # Permission denied.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_content_edit_get... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminProviderContentEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_content_edit', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else: # Permission denied.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_content_edit... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminCashDepwithBalanceGet(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_cash_depwith_balance_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_cash_depwith_balance_get... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminCashDepwithDeposit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_cash_depwith_deposit', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_cash_depwith_deposit... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminCashDepwithWithdraw(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_cash_depwith_withdraw', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_cash_depwith_withdraw... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminCashDepwithTransferGet(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_cash_depwith_transfer_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_cash_depwith_transfer_get... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminCashDepwithHistoryListFrame(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_cash_depwith_history_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_cash_depwith_history_list_frame... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminPayOrderBankListFrame(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_pay_order_bank_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_pay_order_bank_list_frame... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminPayOrderThirdListFrame(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_pay_order_third_list_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_pay_order_third_list_frame... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminProviderPaymentListData(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_payment_list_data', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_payment_list_data... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminPayOrderBankOk(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_pay_order_bank_ok', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_pay_order_bank_ok... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminPayOrderBankCancel(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_pay_order_bank_cancel', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_pay_order_bank_cancel... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminPayOrderThirdRepay(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_pay_order_third_repay', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_pay_order_third_repay... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminCashCommisionPeriodCreate(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_cash_commision_period_create', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_cash_commision_period_create... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminCashCommisionPeriodEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_cash_commision_period_edit', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_cash_commision_period_edit... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminCashCommisionPeriodLock(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_cash_commision_period_lock', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_cash_commision_period_lock... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminCashCommisionPeriodList(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_cash_commision_period_list', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_cash_commision_period_list... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminCashCommisionGetList(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_cash_commision_get_list', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_cash_commision_get_list... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminCashCommisionGet(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_cash_commision_get', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_cash_commision_get... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminCashCommisionCreate(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_cash_commision_create', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_cash_commision_create... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminCashCommisionEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_cash_commision_edit', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_cash_commision_edit... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminCashCommisionReportList(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_cash_commision_report_list', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_cash_commision_report_list... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminCashCommisionListChargeFrame(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_cash_commision_listcharge_frame', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_cash_commision_listcharge_frame... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminCashCommisionAddcharge(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_cash_commision_addcharge', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_cash_commision_addcharge... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminCashCommisionEditcharge(res_log, permission, web_or_mobile = 'Web'):
    try:
        result_list = []
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_cash_commision_editcharge', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(permission == 'Boss'):
            if(return_value):
                result_list.append('PASS')
                res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        elif(permission == 'Agent'):
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('PASS')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- System error')
                result_list.append('FAIL')
        
        else: # Permission accept.
            result, res_log = CheckPermissionDenied(print_tab, res_log, response_data)
            if(result):
                res_log = WriteDebugLog(res_log, print_tab+'- No Permission')
                result_list.append('FAIL')
            else:
                res_log = WriteDebugLog(res_log, print_tab+'- It has permission')
                result_list.append('PASS')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_cash_commision_editcharge... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminProviderContentCommList(res_log, permission, list_providerGame, web_or_mobile = 'Web'):
    list_game_category = []
    try:
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_content_comm_list', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(return_value):
            res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
            res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            if(response_data):
                json_response = json.loads(response_data)
                for each_element in list(json_response):
                    list_game_category.append(each_element['providerid'])
                    list_providerGame.append(each_element['providerid'])
#                     ReplaceIniValue('setting', 'TestData.providername_'+each_element['providerid'], each_element['providername'])
                    ReplaceIniValue('setting', 'TestData.providername_'+each_element['providerid'], each_element['providerid'])
                    result_list.append('PASS')
            else:
                result_list.append('FAIL')
        else:
            result_list.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        
#         ReplaceIniValue('setting', 'TestData.providerGames', ', '.join(list_providerGame))
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_content_comm_list... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, list_game_category, list_providerGame)
    else:
        return (res_log, True, list_game_category, list_providerGame)


def AdminProviderContentCommGameList(res_log, permission, providerGame, list_no_data, list_with_data, web_or_mobile = 'Web'):
    try:
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_content_comm_game_list', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(return_value):
            res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
            res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            json_response = json.loads(response_data)
            if(type(json_response) is dict):
                result, res_log = CheckPermissionDenied(print_tab, res_log, response_data, 'S02', 'No Data')
                if(result):
                    res_log = WriteDebugLog(res_log, print_tab+'- No data')
                    list_no_data.append(providerGame)
                else:
                    result_list.append('PASS')
            else:
                if('gameid' in response_data):
                    list_with_data.append(providerGame+'('+(str(len(json_response)))+')')
                    result_list.append('PASS')
                else:
                    result_list.append('FAIL')
        else:
            result_list.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_content_comm_game_list... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, response_data, list_no_data, list_with_data)
    else:
        return (res_log, True, response_data, list_no_data, list_with_data)


def AdminProviderContentSortEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        return_value2, response_time2, response_data2, res_log = ApiResponse(print_tab, res_log, 'admin_provider_content_sort_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data2)
        if(return_value2):
            result_list.append('PASS')
            res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
            res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time2)
        else:
            result_list.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_content_comm_game_list... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
        
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminProviderContentHotEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        return_value2, response_time2, response_data2, res_log = ApiResponse(print_tab, res_log, 'admin_provider_content_hot_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data2)
        if(return_value2):
            result_list.append('PASS')
            res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
            res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time2)
        else:
            result_list.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_content_comm_game_list... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
        
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminProviderContentHotList(res_log, permission, gm_names, web_or_mobile = 'Web'):
    try:
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_content_hot_list', False, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        json_response = json.loads(response_data)
        res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response do not compare).')
        res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
        
        for (each_game, gm_name)in zip(json_response.get('games'), gm_names.split(', ')):
            if(each_game.get('gamename') == gm_name):
                res_log = WriteDebugLog(res_log, print_tab+'- Success verify name: '+gm_name)
                result_list.append('PASS')
            else:
                result_list.append('FAIL')
                res_log = WriteDebugLog(res_log, print_tab+'- Fail verify name: '+each_game.get('gamename')+' != '+gm_name)
        res_log = WriteDebugLog(res_log, print_tab+'---')
    
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_content_hot_list... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminProviderContentGamesortList(res_log, permission, webId, providerId, edit_or_compare, web_or_mobile = 'Web'):
    try:
        games_in_provider = ''
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_content_gamesort_list', False, False)
        if(return_value):
#         WriteLog(print_tab+'Response data: '+ response_data)
            json_response = json.loads(response_data)
            res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response do not compare).')
            res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            if(edit_or_compare == 'edit'):
                dict_all = {}
                dict_data = {}
                dict_hot = {}
                dict_recommend = {}
                dict_newest = {}
                dict_act = {}
                list_hot = []
                list_recommend = []
                list_newest = []
                list_act = []
                list_games = json_response.get('other')
                dict_hot['providerid'] = providerId
                dict_recommend['providerid'] = providerId
                dict_newest['providerid'] = providerId
                dict_act['providerid'] = providerId
                dict_hot['gameid'] = ''
                dict_recommend['gameid'] = ''
                dict_newest['gameid'] = ''
                dict_act['gameid'] = ''
                # compose list of recommend
                # get all games in each provider
                if((len(list_games) >= 4)):
                    list_random = random.sample(list_games, 4)
                    first_key = list_random[0]
                    second_key = list_random[1]
                    third_key = list_random[2]
                    fourth_key = list_random[3]
                    # Get all provider gameid for compose legal format
                    dict_hot['gameid'] = first_key['gameid']
                    dict_recommend['gameid'] = second_key['gameid']
                    dict_newest['gameid'] = third_key['gameid']
                    dict_act['gameid'] = fourth_key['gameid']
                    # compose list of recommend
                    list_hot.append(dict_hot)
                    list_recommend.append(dict_recommend)
                    list_newest.append(dict_newest)
                    list_act.append(dict_act)
                    games_in_provider = first_key['gamename']+', '+second_key['gamename']+', '+third_key['gamename']+', '+fourth_key['gamename']
                    
                elif((len(list_games) == 3)):
                    list_random = random.sample(list_games, 3)
                    first_key = list_random[0]
                    second_key = list_random[1]
                    third_key = list_random[2]
                    dict_hot['providerid'] = providerId
                    dict_hot['gameid'] = first_key['gameid']
                    dict_recommend['providerid'] = providerId
                    dict_recommend['gameid'] = second_key['gameid']
                    dict_newest['providerid'] = providerId
                    dict_newest['gameid'] = third_key['gameid']
                    # compose list of recommend
                    list_hot.append(dict_hot)
                    list_recommend.append(dict_recommend)
                    list_newest.append(dict_newest)
                    games_in_provider = first_key['gamename']+', '+second_key['gamename']+', '+third_key['gamename']
                    
                elif((len(list_games) == 2)):
                    list_random = random.sample(list_games, 2)
                    first_key = list_random[0]
                    second_key = list_random[1]
                    dict_hot['providerid'] = providerId
                    dict_hot['gameid'] = first_key['gameid']
                    dict_recommend['providerid'] = providerId
                    dict_recommend['gameid'] = second_key['gameid']
                    # compose list of recommend
                    list_hot.append(dict_hot)
                    list_recommend.append(dict_recommend)
                    games_in_provider = first_key['gamename']+', '+second_key['gamename']
                    
                elif((len(list_games) == 1)):
                    list_random = random.sample(list_games, 1)
                    first_key = list_random[0]
                    dict_hot['gameid'] = first_key['gameid']
                    # compose list of recommend
                    games_in_provider = first_key['gamename']
                
                # compose input data
                list_hot.append(dict_hot)
                list_recommend.append(dict_recommend)
                list_newest.append(dict_newest)
                list_act.append(dict_act)
                dict_data['hot'] = list_hot
                dict_data['recommend'] = list_recommend
                dict_data['newest'] = list_newest
                dict_data['act'] = list_act
                
                dict_all['webid'] = webId
                dict_all['data'] = dict_data
                
                with open(currentdir+'\\JsonFiles\\Api_Json\\admin_provider_content_gamesort_edit.json', 'w') as outfile:
                    json.dump(dict_all, outfile, indent=4)
                
                result_list.append('PASS')
                
            else:
                games_in_provider = ''
                provider_games= IniValue('setting', 'GameType.suggest_h_r_n_a_'+providerId)
                return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_content_gamesort_list', False, False)
                WriteLog(print_tab+'Response data: '+ response_data)
                list_games = json_response.get('hot')
                
                if(len(list_games) > 0):
                    games_in_provider = games_in_provider + list_games[0].get('gamename')
                else:
                    games_in_provider = games_in_provider + 'NULL'
                
                list_games = json_response.get('recommand')
                if(len(list_games) > 0):
                    games_in_provider = games_in_provider + ', ' + list_games[0].get('gamename')
                else:
                    games_in_provider = games_in_provider + ', NULL'
                
                list_games = json_response.get('newest')
                if(len(list_games) > 0):
                    games_in_provider = games_in_provider + ', ' + list_games[0].get('gamename')
                else:
                    games_in_provider = games_in_provider + ', NULL'
                
                list_games = json_response.get('act')
                if(len(list_games) > 0):
                    games_in_provider = games_in_provider + ', ' + list_games[0].get('gamename')
                else:
                    games_in_provider = games_in_provider + ', NULL'
                
                if(games_in_provider == provider_games):
                    result_list.append('PASS')
                    res_log = WriteDebugLog(res_log, 'API games == INI games (h_r_n_a): '+ provider_games)
                    res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
                    res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
                    
                else:
                    result_list.append('FAIL')
                    res_log = WriteDebugLog(res_log, 'API games != INI games (h_r_n_a): '+ games_in_provider+' != '+provider_games)
                    res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        else:
            result_list.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
        
        res_log = WriteDebugLog(res_log, print_tab+'---')
    
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_content_gamesort_list... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False, games_in_provider)
    else:
        return (res_log, True, games_in_provider)


def AdminProviderContentGamesortEdit(res_log, permission, web_or_mobile = 'Web'):
    try:
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_provider_content_gamesort_edit', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(return_value):
            result_list.append('PASS')
            res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
            res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            res_log = WriteDebugLog(res_log, print_tab+'---')
            
        else:
            result_list.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
            res_log = WriteDebugLog(res_log, print_tab+'---')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_provider_content_gamesort_edit... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)


def AdminLogout(res_log, permission, web_or_mobile = 'Web'):
    try:
        return_value, response_time, response_data, res_log = ApiResponse(print_tab, res_log, 'admin_logout', True, False)
        WriteLog(print_tab+'Response data: '+ response_data)
        if(return_value):
            result_list.append('PASS')
            res_log = WriteDebugLog(res_log, print_tab+'- API success (status and response are correct).')
            res_log = WriteDebugLog(res_log, print_tab+'- Response time: '+ response_time)
            res_log = WriteDebugLog(res_log, print_tab+'---')
            
        else:
            result_list.append('FAIL')
            res_log = WriteDebugLog(res_log, print_tab+'- API fail (status or response is incorrect).')
            res_log = WriteDebugLog(res_log, print_tab+'---')
            
    except Exception as e:
        result_list.append('FAIL')
        res_log = WriteDebugLog(res_log, print_tab+'- Exception: on admin_logout... %s' % str(e))
        
    finally:
        res_log = WriteDebugLog(res_log, print_tab+'---')
    WriteLog(result_list)
    if('FAIL' in result_list or not result_list):
        return (res_log, False)
    else:
        return (res_log, True)