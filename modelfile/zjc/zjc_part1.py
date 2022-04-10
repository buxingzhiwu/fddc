#-*- coding: utf-8 -*-
from html_tool_v2 import HTML
import re
from config import *
import pandas as pd
import numpy as np
from collections import defaultdict
import os
import time
from dateutil.parser import parse
import datetime

def normalize_float(s):
    if s==None:return 0
    if re.search('\.0+$',s)!=None:
        s=s.rstrip('0').rstrip('.')
    if re.search('\.\d*[1-9]\d*0+$', s) != None:
        s = s.rstrip('0')
    return s
def table_to_csv(table):

    for i in table:
        cleanedList = [x for x in i if str(x) != 'None']
        #print(cleanedList)
def cut_table(table):
    #表头提取，由于最多3行都是表头，所以用前三行第一列的内容进行判断，
    # 3个都一样则将3行内容拼接作为表头
    if table.shape[0] > 2 and table[0, 0] == table[1, 0] and table[2, 0] == table[1, 0]:
        col_name = [str(table[0, i]) + str(table[1, i])+ str(table[2, i]) for i in range(len(table[0, :]))]
        table=table[3:,:]
    #前两行第一列相同，提取表头
    elif table.shape[0]>1 and table[0, 0] == table[1, 0]:
        col_name=[str(table[0,i])+str(table[1,i]) for i in range(len(table[0,:]))]
        table=table[2:,:]
    #直接提取第一行表头
    else:
        col_name = [str(x) for x in table[0, :]]
        table = np.delete(table, 0, 0)
    df = pd.DataFrame(table,columns=col_name)
    if df.empty:
        return df


    #去掉多余的列（有None）
    feature=[]
    for i in df.columns:
        m=re.search('None',i)
        if m==None:
            feature.append(i)
    df=df[feature]
    #去掉总计，-，\之类的行
    drop_index=[]
    for i in range(df.shape[0]):
        string=','.join(df.iloc[i].astype(str).fillna(''))
        if search_pattern('[总合]计,|,[-/]+,[-/]+,|,,,',string):#[总合]计,|,[-/]?,
            drop_index.append(i)
    df.drop(drop_index,inplace=True)
    df=df.reset_index()
    return df
def ZJC(df,name,state):
    #df:输入需要识别的表
    #name:公告id
    #state：是否连接了两个表
    result= pd.DataFrame(columns=["公告id", "股东全称", "股东简称", "变动截止日期", "变动价格", "变动数量"])
    # 识别表头（验证列名有没有相应模式）
    string=','.join(df.columns)
    if  search_pattern('[增减]持|成交|变动',string) and search_pattern('[时区期]间|日期|月份',string) :
        #print(name)
        # 分别识别相应的列
        for i in df.columns:
            if search_pattern('股东[全名]称|[增减]持主体|姓名|名称|[增减]持股东|[增减]持人',i):
                result["股东全称"]=df[i]
            elif search_pattern('[时区期]间|日期|月份',i)and search_pattern('(均)?价|价格|金额',i)==False:
                result["变动截止日期"]=df[i].apply(lambda x:reverse_time(x))
            elif search_pattern('(均)?价|价格|金额',i) and search_pattern('竞价',i)==False:
                df[i] = df[i].apply(lambda x: search_num(x))
                result["变动价格"]=df[i]
            elif search_pattern('(股)?[数份](量)?',i)and (search_pattern('比例|方式|金额|[前后]',i)!=True):
                if search_pattern('万',i)or search_pattern('万',str(df[i][0])):
                    result["变动数量"]=df[i].apply(lambda x:int(float(search_num(x))*10000)).astype(str)
                else:result["变动数量"]=df[i].apply(lambda x: search_num(x)).astype(str)
        #赋值公告id
        result["公告id"] = name.split(".")[0]
        #对每一行识别是否为表头
        for row in range(df.shape[0]):
            row_string=','.join(df.iloc[row].astype(str).tolist())
            #如果是part_1的表头，则删掉result(保存识别的表)的相应行
            if row_string==string:
                result=result.drop([row])
                result=result.reset_index()
            #如果是part_2的表头，则删掉result之后的所有行，并删除df（被识别的表）之前的所有行，只留第二个表
            if search_pattern('名称|(股东)?性?名', row_string) and search_pattern('[增减]持前.*占?.*总?(股本)?.*(比例)?|[增减]持后.*占?.*总?(股本)?.*(比例)?', row_string) \
           and search_pattern('(股份)?性质', row_string) and (search_pattern('期间', row_string)==False):
                result=result.iloc[:row,:]
                df=df.iloc[row:,:]
                del df['index']
                state=True
                break
        #result规范化
        result['变动截止日期']=result['变动截止日期'].fillna(0)
        result=result.loc[result['变动截止日期']!=0]
        #这句直接将空白的行直接填充最后一个非空白的值（我也不知道为啥，但是减少了工作量）
        result['股东全称']=result['股东全称'].replace('',None)
    return result,state,df
def ZJC_part2(df,result):
    #df:需要识别的表
    #result：part_1识别到的表
    #index方便后面拼接最后一行
    result['index']=result.index
    #识别表头（验证列名有没有相应模式）
    string = ','.join(df.columns)
    df_after=pd.DataFrame(columns=["股东全称",  "变动后持股数", "变动后持股比例"])
    if search_pattern('名称|(股东)?性?名', string) and search_pattern('[增减]持前.*占?.*总?(股本)?.*比(例)?', string)\
            and (search_pattern('[时区期]间|日期|月份', string)==False):
           # and search_pattern('(股份)?性质', string)

        #分别识别相应的列
        for i in df.columns:
            if search_pattern('股东[全名]称|[增减]持主体|姓名|名称|[增减]持股东|[增减]持人',i):
                df[i] = df[i].replace('', None)
                df.drop_duplicates(subset=[i], keep='first', inplace=True)

                df_after['股东全称']=df[i]
            elif search_pattern('[增减]?持?.*后.*股(数)?',i) and (search_pattern('比例',i)==False) :
                #有万的*10000
                if search_pattern('万',i)or search_pattern('万',str(df[i][0])):
                    df_after["变动后持股数"]=df[i].apply(lambda x:int(float(search_num(x))*10000)).astype(str)
                else:df_after["变动后持股数"]=df[i].apply(lambda x: search_num(x))#.astype(int)
            elif search_pattern('[增减]?持?.*后.*股.*比(例)?', i) :
                #有%的*0.01
                if search_pattern('%', i) or search_pattern('%', str(df[i][0])) or float(search_num(str(df[i][0])) )>1:
                    df_after["变动后持股比例"] = df[i].apply(lambda x: percent(str(search_num(x))))
                else:
                    df_after["变动后持股比例"] = df[i].apply(lambda x: search_num(x)).astype(str)
        #只留每个股东第一行，因为第一行一般是合计的，其他无用
        df_after.drop_duplicates(subset=['股东全称'],keep='first',inplace=True)
        ##查看变动后持股比例是否有大于1，如果有则所有都*0.01，原因是由于html的%有可能是image格式的，文本未读到
        tmp = df_after.loc[df_after["变动后持股比例"].astype(float) > 1]
        if tmp.shape[0] > 0:
            df_after["变动后持股比例"] = df_after["变动后持股比例"].apply(lambda x: percent(x))
        #将df_after拼接到result的每个股东的最后一行
        tmp=result.groupby(['股东全称'], as_index=False)['index'].max()
        df_after=pd.merge(df_after,tmp,on=['股东全称'],how='left')
        result=pd.merge(result,df_after,how='left',on=['股东全称',"index"])
        del result['index']
        state=True

    else:state=False
    return result,state
def percent(f):
    # f = matched.group('number')
    if int(float(f)) < 10:
        date = "0.0"
    else:
        date = "0."
    f = f.rstrip("0").split(".")
    for i in f:
        date += i
    return str(date)
def reverse_time(s):
    import calendar
    #1.先看有没有数字，没有则返回0
    if s==None or re.search('[0-9]+',s)==None :return 0
    #2.看是否有连续8位数字，若有则转化为日期返回
    num_str=re.findall('[0-9]{8}',s)
    if num_str!=[]:
        try:
            return parse(num_str[-1]).date()
        except ValueError:
            return 0
    #3.找出4位连续数字，如果有则存为年，没有则设置为2017，保留4位数之后的字符串
    day=''
    m=re.findall('[0-9]{4}', s)
    if m==[]:
        year='1000'
    else:
        year=m[-1]
        s=s.split(year)[-1]
    #3.a.字符串如果剩余有“月”，则可能只有月，存为month，有日期信息则存为day
    if re.search('月',s)!=None:
        p=s.split('月')
        month=re.findall('[0-9]+',p[-2])[-1]
        if re.search('[0-9]+',p[-1])!=None:
            day=re.findall('[0-9]+',p[-1])[-1]
    #3.b.若没有“月”,则直接找字符串最后两个数字，分别存到month,day，若只有一个，存month
    else:
        n=re.findall('[0-9]+', s)
        if len(n)==0:return 0
        elif len(n)==1:month=n[-1]
        else:
            month=n[-2]
            day=n[-1]
    #对没有日期信息的，取当月最后一天
    try:
        if day=='':
            day= str(calendar.monthrange(int(year), int(month))[1])
            s = year + ' ' + month + ' ' + day
            return str(parse(s).date()) + "#"
        else:
            s = year + ' ' + month + ' ' + day
            return parse(s).date()
    except ValueError:
        return 0
def search_num(s):
    if s==None:return 0
    if re.search('\.0+$',s)!=None:
        s=s.rstrip('0').rstrip('.')
    s=s.replace(',', '').replace('，', '')
    if re.search('-',s)!=None:
        s=s.split("-")[-1]
    m=re.search('0\.\d*[1-9]\d*|[1-9]\d*\.?\d*',s)
    if m != None:
        return m.group(0)
    return 0
def search_pattern(pa,string):
    m=re.search(pa,string)
    if m != None:
        return True
    return False
def process_table(data,df_answer,name,id_list,time_id,year):
    #增减持第一部分是否有表连接在一起的状态
    p1_state = False
    #防止table里面没有对应表，先建空表
    part_1 = pd.DataFrame(columns=["公告id", "股东全称", "股东简称", "变动截止日期", "变动价格", "变动数量"])
    part_2 = pd.DataFrame(columns=["公告id", "股东全称", "股东简称", "变动截止日期", "变动价格", "变动数量", "变动后持股数", "变动后持股比例"])
    #table数据处理
    for key, table in data.items():
        table1 = np.array(table)
        #将表格的none列、无用的行去掉
        df = cut_table(table1)
        if df.empty: continue
        #第一部分表格识别，将结果保存到s
        #如果是两个表连接，返回的p1_state=true,否则为false
        #如果两个表连接，df只保存后面一个表的内容，方便下一步处理，
        #只有一个表则df还是原来的输入df不变
        s, p1_state, df = ZJC(df, name, p1_state)
        #将识别到的第一部分合并到之前的空表（有可能好几个表都是第一部分的内容）
        part_1 = pd.concat([part_1, s], ignore_index=True)
        #前一步两表连接的情况，需要再cut一下表格，规范化
        if p1_state:
            df = cut_table(np.array(df))
        #p2_state标志是否识别到第二部分，如果识别到则将part_1拼接到最终结果part_2
        part_2, p2_state = ZJC_part2(df, part_1)
        if p2_state:
            break
    #拼接到df_answer
    def compare_time_month(s1,s2):
        try:
            if s1==None:
                return  reverse_time(str(s2))
            if int(re.findall("[0-9]+",s1)[0])<=int(re.findall("[0-9]+",s2)[0]) and int(re.findall("[0-9]+",s1)[1])<=int(re.findall("[0-9]+",s2)[1]):
                return  reverse_time(str(s1))
            else: return  reverse_time(str(s2))
        except:
            return  reverse_time(str(s2))
    if year!=None:
        part_2["变动截止日期"] = part_2["变动截止日期"].apply(lambda x: reverse_time(year+"-"+str(x).split('-')[1]+'-'+str(x).split('-')[2])if search_pattern("-",str(x))and str(x).split('-')[0]=="1000" else x)
    part_2["变动截止日期"]=part_2["变动截止日期"].apply(lambda x: compare_time_month(time_id,x) if (x!=0 and search_pattern("#",str(x)) ) else x)

    if not part_2.empty:
        df_answer = pd.concat([df_answer, part_2], ignore_index=True)
    #elif len(data)!=0:
    else:
        id_list.append(name.split('.')[0])




    return df_answer,id_list

if __name__ == '__main__':
    time_df = pd.read_excel(time_path)
    #print(time_df)
    time_df = pd.DataFrame(columns=["公告日期", "公告号"])

    names = os.listdir(path_test)
    columns_fea = ["公告id", "股东全称", "股东简称", "变动截止日期", "变动价格", "变动数量", "变动后持股数", "变动后持股比例"]
    df_answer = pd.DataFrame(columns=columns_fea)

    ticks = time.time()
    #文件循环
    id_list=[]
    for name in names:
        try:
            path = path_test + name
            data, year = HTML(path)
            #print(name.split(".")[0])
            time_part=time_df.loc[time_df["公告号"].astype(str) == name.split(".")[0]]
            time_id=None
            if not time_part.empty:
                time_id=time_part["公告日期"].values[0]
                time_id=str(time_id).split("T")[0]
            df_answer, id_list = process_table(data, df_answer, name, id_list, time_id,year)
        except:
            pass
    #print(df_answer)
    #"变动价格", "变动数量", "变动后持股数", "变动后持股比例"
    for i in [ "变动价格", "变动数量", "变动后持股数", "变动后持股比例"]:
        df_answer[i]=df_answer[i].apply(lambda x:normalize_float(str(x)))
        df_answer[i] = df_answer[i].replace('nan','').replace('0','')

    df_answer[columns_fea].to_csv(save_path + "ZJC_part1.csv", encoding = "utf-8")
    dataframe = pd.DataFrame({'公告id': id_list})
    dataframe.to_csv(save_path + "ZJC_id_list.csv", encoding = "utf-8")
