#!/usr/bin/env python
# -*- encoding: utf8 -*-
import csv
import re
import glob
import os
import sys
import xlrd
from bs4 import BeautifulSoup

reg = "[\u4e00-\u9fff\u2E80-\u2FDF\u3400-\u4DBF\uF900-\uFAFF\u31A0-\u31BF]+"
re_words = re.compile(u"[\u4e00-\u9fff\u2E80-\u2FDF\u3400-\u4DBF\uF900-\uFAFF\u31A0-\u31BF]+")
alist = []
mobile_path1 = 'C:\\Users\\tommy\\Documents\\admin_mobile\\'
web_path2 = 'C:\\Users\\tommy\\Documents\\admin_web\\'

excel_admin_path = 'C:\\Users\\tommy\\Documents\\admin.xls'
excel_admin = xlrd.open_workbook(excel_admin_path)

excel_admin_web = excel_admin.sheet_by_index(0)
excel_admin_mobile = excel_admin.sheet_by_index(1)

excel_admin_web_col1 = excel_admin_web.col(1)
excel_admin_web_col0 = excel_admin_web.col(0)

excel_admin_mobile_col1 = excel_admin_mobile.col(1)
excel_admin_mobile_col0 = excel_admin_mobile.col(0)

web_dict = {}
for i,j in zip(excel_admin_web_col1,excel_admin_web_col0):
    web_dict[i.value]= j.value
    
mobile_dict= {}
for i,j in zip(excel_admin_mobile_col1,excel_admin_mobile_col0):
    mobile_dict[i.value]= j.value

# print(web_dict['上层帐号'])
# print(mobile_dict['下线人数'])


# admin_web_comp_dict = dict()
# admin_mobile_comp_dict = dict(zip(excel_admin_mobile_col1, excel_admin_mobile_col0))
# 
# print(admin_web_comp_dict)

# print(admin_mobile_comp_dict["text:'验证码已过期'"])

# for i in excel_admin_web_col1:
#     
# for j in excel_admin_mobile_col1:
    

# text_mobile = open("C:\\Users\\tommy\\Documents\\admin_mobile_1.txt", "w",encoding="utf-8")
# text_web = open("C:\\Users\\tommy\\Documents\\admin_web_1.txt", "w",encoding="utf-8")


# for filename in glob.glob(os.path.join(mobile_path1, '*.html')):
#     alist = []
#     #text_mobile = open(filename.split('.')[0]+".txt", "w", encoding="utf-8")
#     with open(filename, encoding="utf8") as f:
#         html_line = str(f.readlines())
#         #sample = 'I am from 美国。We should be friends. 朋友。'
#         #m =  re_words.search(s,0)
#         for n in re.findall(re_words, html_line):
#             alist.append(n)
#             #print(n)
#         text_mobile.write(str(filename.split('\\')[-1])+'\n')
#         text_mobile.write(str(set(alist)).replace('\'','').replace('{','').replace('}','').replace(', ','\n'))
#     text_mobile.write('\n\n')
#     
#     
# for filename in glob.glob(os.path.join(web_path2, '*.html')):
#     alist = []
#     #text_web = open(filename.split('.')[0]+".txt", "w", encoding="utf-8")
#     with open(filename, encoding="utf8") as f:
#         html_line = str(f.readlines())
#         #sample = 'I am from 美国。We should be friends. 朋友。'
#         #m =  re_words.search(s,0)
#         for n in re.findall(re_words, html_line):
#             alist.append(n)
#             #print(n)
#         text_web.write(str(filename.split('\\')[-1])+'\n')
#         text_web.write(str(set(alist)).replace('\'','').replace('{','').replace('}','').replace(', ','\n'))
#     text_web.write('\n\n')



#sheel_1.cell_value(rowx=0,colx=1)
for filename in glob.glob(os.path.join(mobile_path1, '*.html')):
    print('\t'+filename.replace('C:\\Users\\tommy\\Documents\\',''))
    alist = []
    html_mobile = open(filename.split('.')[0]+"_replace.html", "w", encoding="utf-8")
    with open(filename, encoding="utf8") as f:
        html_file = f.read()
        soup = BeautifulSoup(html_file, 'html.parser')
        strhtm = soup.prettify()
        for x in re.findall(re_words, strhtm):
            if(mobile_dict.get(x) != None):
                # 1st Replace string start with single quote ', and end with single quote
                strhtm = re.sub(r"'\b"+x+r"'","lang.set("+mobile_dict.get(x)+")", strhtm) # lang.set(lang636);
                # 2st Replace string start with double quote ", and end with double quote
                strhtm = re.sub(r'"\b'+x+r'"','lang.set('+mobile_dict.get(x)+')', strhtm)
                
                # 3rd Replace string start with ('
                strhtm = re.sub(r"'\(\b"+x+r"\b\)'","'('+lang.set("+mobile_dict.get(x)+")+')'", strhtm)
                strhtm = re.sub(r"\(\b"+x+r"\b\)","+'('+lang.set("+mobile_dict.get(x)+")+')'", strhtm)
                
                # 3rd Replace string start with single quote ', but not end with single quote
                strhtm = re.sub(r"'\b"+x+r"\b","lang.set("+mobile_dict.get(x)+")+'", strhtm)
                # 4th Replace string start with double quote ", but not end with double quote
                strhtm = re.sub(r'"\b'+x+r'\b','lang.set('+mobile_dict.get(x)+')+"', strhtm)
                
                # Replace string without comment (//)
                strhtm = re.sub(r"//\b"+x+r"\b",'//暫定'+x, strhtm)
                strhtm = re.sub(r"<!--\b"+x+r"\b",'+"<!-- "'+x, strhtm)
                strhtm = re.sub(r"=\b"+x+r"\b",'=""+lang.set('+mobile_dict.get(x)+')', strhtm)
                strhtm = re.sub(r"\b"+x+r"\b</option>'","'+lang.set("+mobile_dict.get(x)+")+'</option>'", strhtm)
                strhtm = re.sub(r"！\b"+x+r"\b",'+"！"+lang.set('+mobile_dict.get(x)+')', strhtm)
                strhtm = re.sub(r"\b"+x+r"\b!",'lang.set('+mobile_dict.get(x)+')+"!"', strhtm)
                strhtm = re.sub(r"-\b"+x+r"\b",'+"-"+lang.set('+mobile_dict.get(x)+')', strhtm)
                strhtm = re.sub(r"\b"+x+r"\b",'lang.set('+mobile_dict.get(x)+')', strhtm)
        html_mobile.write(strhtm)
print('Finish replace')


for filename in glob.glob(os.path.join(web_path2, '*.html')):
    print('\t'+filename.replace('C:\\Users\\tommy\\Documents\\',''))
    alist = []
    html_web = open(filename.split('.')[0]+"_replace.html", "w", encoding="utf-8")
    with open(filename, encoding="utf8") as f:
        html_file = f.read()
        soup = BeautifulSoup(html_file, 'html.parser')
        strhtm = soup.prettify()
        for x in re.findall(re_words, strhtm):
            if(web_dict.get(x) != None):
                # 1st Replace string start with single quote ', and end with single quote
                strhtm = re.sub(r"'\b"+x+r"'","lang.set("+web_dict.get(x)+")", strhtm) # lang.set(lang636);
                # 2st Replace string start with double quote ", and end with double quote
                strhtm = re.sub(r'"\b'+x+r'"','lang.set('+web_dict.get(x)+')', strhtm)
                
                # 3rd Replace string start with ('
                strhtm = re.sub(r"'\(\b"+x+r"\b\)'","'('+lang.set("+web_dict.get(x)+")+')'", strhtm)
                strhtm = re.sub(r"\(\b"+x+r"\b\)","+'('+lang.set("+web_dict.get(x)+")+')'", strhtm)
                
                # 3rd Replace string start with single quote ', but not end with single quote
                strhtm = re.sub(r"'\b"+x+r"\b","lang.set("+web_dict.get(x)+")+'", strhtm)
                # 4th Replace string start with double quote ", but not end with double quote
                strhtm = re.sub(r'"\b'+x+r'\b','lang.set('+web_dict.get(x)+')+"', strhtm)
                
                # Replace string without comment (//)
                strhtm = re.sub(r"//\b"+x+r"\b",'//暫定'+x, strhtm)
                strhtm = re.sub(r"<!--\b"+x+r"\b",'+"<!-- "'+x, strhtm)
                strhtm = re.sub(r"=\b"+x+r"\b",'=""+lang.set('+web_dict.get(x)+')', strhtm)
                strhtm = re.sub(r"\b"+x+r"\b</option>'","'+lang.set("+web_dict.get(x)+")+'</option>'", strhtm)
                strhtm = re.sub(r"！\b"+x+r"\b",'+"！"+lang.set('+web_dict.get(x)+')', strhtm)
                strhtm = re.sub(r"\b"+x+r"\b!",'lang.set('+web_dict.get(x)+')+"!"', strhtm)
                strhtm = re.sub(r"-\b"+x+r"\b",'+"-"+lang.set('+web_dict.get(x)+')', strhtm)
                strhtm = re.sub(r"\b"+x+r"\b",'lang.set('+web_dict.get(x)+')', strhtm)
        html_web.write(strhtm)
print('Finish replace')

for filename in glob.glob(os.path.join(web_path2, '*.1.html')):
    print('\t'+filename.replace('C:\\Users\\tommy\\Documents\\',''))
    alist = []
    html_web = open(filename.split('.')[0]+"_replace.1.html", "w", encoding="utf-8")
    with open(filename, encoding="utf8") as f:
        html_file = f.read()
        soup = BeautifulSoup(html_file, 'html.parser')
        strhtm = soup.prettify()
        for x in re.findall(re_words, strhtm):
            if(web_dict.get(x) != None):
                # 1st Replace string start with single quote ', and end with single quote
                strhtm = re.sub(r"'\b"+x+r"'","lang.set("+web_dict.get(x)+")", strhtm) # lang.set(lang636);
                # 2st Replace string start with double quote ", and end with double quote
                strhtm = re.sub(r'"\b'+x+r'"','lang.set('+web_dict.get(x)+')', strhtm)
                
                # 3rd Replace string start with ('
                strhtm = re.sub(r"'\(\b"+x+r"\b\)'","'('+lang.set("+web_dict.get(x)+")+')'", strhtm)
                strhtm = re.sub(r"\(\b"+x+r"\b\)","+'('+lang.set("+web_dict.get(x)+")+')'", strhtm)
                
                # 3rd Replace string start with single quote ', but not end with single quote
                strhtm = re.sub(r"'\b"+x+r"\b","lang.set("+web_dict.get(x)+")+'", strhtm)
                # 4th Replace string start with double quote ", but not end with double quote
                strhtm = re.sub(r'"\b'+x+r'\b','lang.set('+web_dict.get(x)+')+"', strhtm)
                
                # Replace string without comment (//)
                strhtm = re.sub(r"//\b"+x+r"\b",'//暫定'+x, strhtm)
                strhtm = re.sub(r"<!--\b"+x+r"\b",'+"<!-- "'+x, strhtm)
                strhtm = re.sub(r"=\b"+x+r"\b",'=""+lang.set('+web_dict.get(x)+')', strhtm)
                strhtm = re.sub(r"\b"+x+r"\b</option>'","'+lang.set("+web_dict.get(x)+")+'</option>'", strhtm)
                strhtm = re.sub(r"！\b"+x+r"\b",'+"！"+lang.set('+web_dict.get(x)+')', strhtm)
                strhtm = re.sub(r"\b"+x+r"\b!",'lang.set('+web_dict.get(x)+')+"!"', strhtm)
                strhtm = re.sub(r"-\b"+x+r"\b",'+"-"+lang.set('+web_dict.get(x)+')', strhtm)
                strhtm = re.sub(r"\b"+x+r"\b",'lang.set('+web_dict.get(x)+')', strhtm)
        html_web.write(strhtm)
print('Finish replace')
        