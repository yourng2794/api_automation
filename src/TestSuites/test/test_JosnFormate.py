#coding=utf8
import json
from O2oUtility import GetJsonValue
from O2oUtility import JsonValueCompare
from O2oUtility import CheckJsonFile
from O2oUtility import ReplaceAllJsonValue

from O2oUtility import ReplaceJsonValue

json_string = '{"type": "poker", "webid": "0e4e80449b7f4492c7725b69c1d8d6de", "settype": "game", "lang": "zh", "data": {"gamerule": [{"gameid": "66002", "providername": "BB_POKER"}, {"gameid": "66001", "providername": "BB_POKER"}, {"gameid": "18004", "providername": "JDB_POKER"}, {"gameid": "18017", "providername": "JDB_POKER"}, {"gameid": "18004", "providername": "JDB_POKER"}, {"gameid": "18017", "providername": "JDB_POKER"}]}}'
json_loads = json.loads(json_string)

##### Sample 3 #####
response_data = json.dumps(json_loads, sort_keys=True, indent=4, ensure_ascii=False)
print(response_data)

# i = 401
# while (i <= 420):
#     i = i+1
#     print('        '+str(i)+',')

# Json replace function
# print(ReplaceAllJsonValue(json_string, '', '1'))

# Json compare function
# print(JsonValueCompare(json_string, 'op', '1'))

##### Sample 1 #####
# json_string2 = GetJsonValue(json_string, 'permission|og')
# for k in json_string2.values():
#     print(k)

##### Sample 2 #####
# for json_value in json_loads.get('boss').values():
#     print(json_value)
#     if(json_value.get('pt_type_name') == 'QAtype30'):
#         if(json_value.get('pt_type_permissionid') == '373051fa3687fc8f1b1d295d513e3b8e'):
#             print(True)


# print(CheckJsonFile('C:\\Users\\tommy\\git\\tommy_autotest\\ApiAutomation\\src\\JsonFiles\\Api_Json\\admin_payment_edit.json', 'payname'))
# from bs4 import BeautifulSoup
# html_data = '''<div class="ckeck-item-unit">
# 
#     <div class="ckeck-item ckeck-all j-c-all">
# 
#         <label for="websiteAll"></label>
# 
#         <input type="checkbox" name="website" id="websiteAll" value="" class="required">
# 
#         <div class="check-box fas"></div>
# 
#         <span>全部网站</span>
# 
#     </div>
# 
#     <div class="check-group j-c-area" id="eventWebsit">
# 
#                     </div>
# 
# </div>
# '''
# soup = BeautifulSoup(html_data, 'html.parser')