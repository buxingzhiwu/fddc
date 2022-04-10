#-*- coding: utf-8 -*-
import time, os, re
import pickle
import fool
import pandas as pd
from config import *
from collections import defaultdict
import multiprocessing
# from tqdm import tqdm
import random
import HTMLParser
import re
import TextUtils


def get_company(string):
    if string=="":return None
    string=string.split("子公司")[-1]
    string=re.sub("\(以下简称.*\)","",string)
    string=re.split("[。]",string)[-1]
    try:
         p,ners=fool.analysis(string)
         m=ners[-1]
         for i in range(len(m)):
             if(m[-i-1][-2]=='company' ):
                return ners[-1][-i-1][-1]
         for i in range(len(m)):
             if (m[-i - 1][-2] == "org"):
                 return ners[-1][-i - 1][-1]
    except:
        return None
def search_pattern(pa,string):
    m=re.search(pa,string)
    if m != None:
        return True
    else:
        return False
def search_project(sentence):
    if search_pattern("项目名称|工程名称", sentence):
        s = re.split("项目名称|工程名称", sentence)[1]
        p = re.split("[：:，。\"“；;《]", s)
        s1=p[0]
        if p[0] == '':
            s1 = p[1]
        s1 = re.split(".{2}名称|.{2}编号|.{2}地[点址]|.{2}人|.{2}内容$|\(?以下[统简]称|.{2}中标$|详[情见]", s1)[0]
        if search_pattern("[1-9][：.:，。\"“；;《、]|[一二三四五六七八九十][、.：:，。\"“；;《]", s1):
            s1 = re.split("[1-9][.：:，。\"“；;《、]|[一二三四五六七八九十][.：:，。\"“；;《、]", s1)[0]
        if search_pattern("项目.{0,5}$", s1):
            s1 = re.split("项目.{0,5}$", s1)[0] + "项目"
        if len(s1) > 3:
            return s1
    return None
def search_contract(sentence,contract):
    if search_pattern("《.*合同(书)?》", sentence):
        s = re.search("《.*合同(书)?》", sentence)[0]
        s1 = re.split("[，。“《、]|收到", s)[-1]
        contract = s1[:-1]
    elif search_pattern(".*合同书", sentence):
        s = re.split("合同书", sentence)[0] + '合同书'
        s1 = re.split("[，。《、]|收到", s)[-1]
        if contract == None:
            contract = s1
    if contract != None and search_pattern("中小企业|公司.*正式.*签署|公司.*签署.*正式", contract):
        contract = None
    return contract
def search_num(s):
    if s==None:return 0
    if re.search('\.0+$',s)!=None:
        s=s.rstrip('0').rstrip('.')
    s=s.replace(',', '').replace('，', '')
    if re.search('-',s)!=None:
        s=s.split("-")[-1]
    m=re.findall('0\.\d*[1-9]\d*|[1-9]\d*\.?\d*',s)
    if m != []:
        return m[-1]
    return 0
def search_price(sentence,price):
    if not search_pattern("元|￥",sentence):
        return price
    else:
        sentence=TextUtils.percent(sentence)
        sentence = TextUtils.replace_YG(sentence)
    if  price==None and (search_pattern("(总投资|暂定|估[算计]|价格|中标|合同|金额).*<Y>", sentence) or \
            search_pattern("\(￥[0-9]*\.*[0-9]*\)|\(￥[0-9]*\)", sentence)):
        s = sentence.split("<Y>")[0]
        s = re.split("总投资|暂定|估[算计]|价格|中标|合同|金额", s)[-1]
        if (search_pattern("人民币.*[美欧]元", s)):
            s = s.split("人民币")[0]
        p = search_num(s)
        if p!=0:
            if re.search('\.0+$', p) != None:
                p = p.rstrip('0').rstrip('.')
            if float(p)>=10000:
                price=p

    return price

def search_combination(sentence,combination):
    if search_pattern("与.*联合体", sentence)==False or combination!=None:
        return combination
    sentence = sentence.split("联合体")[0].split("与")[-1]
    if search_pattern("的$", sentence):
        sentence = sentence.strip('的')[:-2]
    m = re.split("[、，,“]", sentence)
    res=[]
    for i in range(len(m)):
        m[i] = m[i].split("(以下简称")[0].split("组成")[0].split("(曾用名")[0]
        if search_pattern("确定",sentence):
            res=[]
        if search_pattern("^.{1,2}[人方]", m[i]):
            m[i] = re.split("^.{1,2}[人方]", m[i])[1]
        p, ners = fool.analysis(m[i])
        for i in range(len(ners[-1])):
            if (ners[-1][-i - 1][-2] == 'company'):
                m[i] = ners[-1][-i - 1][-1]
                res.append(m[i])
                break
    return "、".join([i for i in res if i is not ""])
def search_JF(sentence,JF):
    if JF!=None:
        return JF
    if search_pattern("[收接]到.*(发来)?的.*中标通知书", sentence):
        sentence=re.split("[收接]到.*(发来)?的.*中标通知书",sentence)[0]
        return get_company(sentence)
    elif  search_pattern("确定.*为.*中标单位|确定.*公司为.*中标|确定.*为.*中标人",sentence):
          return get_company( sentence.split("为")[0])
    elif search_pattern("[与和].*签[署订].*合同|[与和].*签[署订].*协议",sentence):
        return get_company(re.search("[与和].*签[署订].*合同|[与和].*签[署订].*协议", sentence).group(0))
    return JF
def get_multi_s(sentence,muti_dict):
    if len(muti_dict.keys())!=0:
        return muti_dict
    if search_pattern("分别与.*签订|与.*分别签订", sentence):

        ht_list=[]
        xm_list = []
        cpn_list = re.search("分别与.*签订|与.*分别签订", sentence).group(0).split("、")
        ht_str=re.split("分别与.*签订|与.*分别签订", sentence)[-1].split('，')[0]
        if search_pattern("的.+合同|的.+协议(书)?",ht_str):
            ht_list.append(re.search("的.+合同|的.+协议(书)?",ht_str).group(0).split("的")[-1])
            ht_str=re.split("的.+合同|的.+协议(书)?",ht_str)[0]
        str_list = ht_str.split("、")
        for k in range(len(cpn_list)):
            cpn_list[k]=get_company(cpn_list[k])
            if len(cpn_list) == len(str_list):
                if search_pattern(".*合同|.*协议(书)?", str_list[k]):
                   ht_list.append(re.search(".*合同|.*协议(书)?",str_list[k]).group(0))
                else:
                   xm_list.append(str_list[k])
        if len(cpn_list)!= len(str_list) :
            if search_pattern(".*合同|.*协议(书)?", str_list[0]):
                ht_list.append(re.search(".*合同|.*协议(书)?", str_list[0]).group(0))
            else:
                xm_list.append(str_list[0])

        muti_dict={"jf_list":cpn_list,"ht_list":ht_list,"xm_list":xm_list}
    return muti_dict
def find_contract(path):
    Parser = HTMLParser.HTMLParser()
    names = os.listdir(path)
    id_dict={}

    for name in names:
        try:
            price,contract,combination,JF=None,None,None,None
            muti_dict=defaultdict(list)
            project_list=[]
           # print(name)
            data = Parser.parse_content_hetong_v2(path + name , True)
            for sentence in data:
                pro=search_project(sentence)
                if pro!=None:
                    project_list.append(pro)
                contract=search_contract(sentence,contract)
                price=search_price(sentence,price)
                combination=search_combination(sentence,combination)
                JF=search_JF(sentence,JF)

                muti_dict=get_multi_s(sentence,muti_dict)
            id_dict[name]={"jafang":JF,"contract":contract,"price":price,"project_list":project_list,"combination":combination,"muti_dict":muti_dict}
        except:
            pass
    with open(save_path + 'zdht_test728.pkl', 'wb') as f:
        pickle.dump(id_dict, f)







if __name__ == "__main__":
    ticks = time.time()
    find_contract(path_test)