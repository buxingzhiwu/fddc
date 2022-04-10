#-*- coding: utf-8 -*-
import time, os, re
import json
import fool
from config import *
import pandas as pd
from collections import defaultdict
import multiprocessing
import random
import TextUtils
import HTMLParser
import re


def Supplement_fin(row):
    if row["股东全称"] == "" or "《" in row["股东全称"] or "---" in row["股东全称"]:
        row["股东全称"] = "删除"
    elif len(row["股东全称"]) == 4:
        Flag = True
        Parser = HTMLParser.HTMLParser()
        data = Parser.parse_content_zengjianchi(path_test + str(row["公告id"]) + '.html', True)
        _, ners = fool.analysis(data)
        ners = [x[3] for line in ners for x in line if x[2] == "company"]
        try:
            for i in ners:
                if judge_s(i,row["股东全称"]) and i != row["股东全称"]:
                    row["股东简称"] = row["股东全称"]
                    row["股东全称"] = i
                    Flag = False
                    break
            #print(row)
        except:
            pass
        if Flag:
            row["股东全称"] = "删除"

    try:
        row["变动后持股比例"] = str(round(float(row["变动后持股比例"]), 4))
    except:
        pass
    return row
def Supplement(row):
    if int(row["合同金额上限"]) == 0:
        row["合同金额上限"] = ""
        row["合同金额下限"] = ""
    else:
        row["合同金额下限"] = row["合同金额上限"]
    return row
def judge_s(name,name_s):
    if "(" in name_s and ")" in name_s:
        pass
    else:
        name_s = name_s.replace("(", "").replace(")", "")

    cor_name_pattern = r"[\u4e00-\u9fa5\(\)]*".join(name_s)
    cor_name_pattern = r"[\u4e00-\u9fa5\(\)]*".join(name_s)
    pattern = re.compile(cor_name_pattern)
    cor_names = re.search(pattern, name)
    if cor_names != None:
        return True
    else:
        return False
def judge_s2(name,name_s):
    for i in name_s:
        if i not in name:
            return False
    return True
def change_org(row, data_dict):
    DICT = data_dict[row["公告id"]]
    if "ORGS" not in DICT:
        DICT["ORGS"] = []
    if "ORG" not in DICT:
        DICT["ORG"] = []
    if not pd.isnull(row["股东全称"]):
        row["股东全称"] = row["股东全称"].replace("（", "(").replace("）", ")")
        if row["股东全称"] in DICT["ORG"]:
            for i in DICT["ORGS"]:
                if judge_s(row["股东全称"], i):
                    row["股东简称"] = i
                    return row
        elif row["股东全称"] in DICT["ORGS"]:
            for i in DICT["ORG"]:
                if judge_s(i, row["股东全称"]):
                    row["股东简称"] = row["股东全称"]
                    row["股东全称"] = i
                    return row
        else:
            Flag = True
            for orc in DICT["ORG"]:
                if orc.find(row["股东全称"]) != -1:
                    Flag = Flag
                    row["股东全称"] = orc
                    for i in DICT["ORGS"]:
                        if judge_s(row["股东全称"], i) and row["股东全称"] != i:
                            row["股东简称"] = i
                            return row
                    break
                elif judge_s(orc, row["股东全称"]) and orc != row["股东全称"]:
                    Flag = Flag
                    row["股东简称"] = row["股东全称"]
                    row["股东全称"] = orc
            if Flag:
                for orc in DICT["ORG"]:
                    if judge_s2(orc,row["股东全称"]) and orc != row["股东全称"]:
                        row["股东简称"] = row["股东全称"]
                        row["股东全称"] = orc

            return row
        return row
    else:
        if len(DICT["ORG"]) > 0:
            row["股东全称"] = DICT["ORG"][0]
            for i in DICT["ORGS"]:
                if judge_s(row["股东全称"], i):
                    row["股东简称"] = i
                    return row
        elif len(DICT["PRE"]) > 0:
            row["股东全称"] = DICT["PRE"][0]
        return row

def search_pattern(pa,string):
    m=re.search(pa,string)
    if m != None:
        return True
    else:
        return False
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
def check_org(sentence_part,org_list):
    # sentence_part=sentence_part.replace("(","[").replace(")","]")
    for m in org_list:
        m=m.replace("(","\(").replace(")","\)")
        s=re.search(m ,sentence_part)
        if s!=None:
            return s.group(0)
    return None

def extract_content(data,org_dict):
    forbidden_dict = {"G": "[增减]持[前后]|成交[前后]|变动[前后]", "g": "[增减]持[前]|成交[前]|变动[前]|累计.*前","Y":"收益"}#"P": "[增减]持[前]|成交[前]|变动[前]|累计.*前"
    check_dict = {"G": '[增减]持|成交|变动|出售|买入', "g": "[增减]持[后]|成交[后]|变动[后]|累计.*后"}
    symbol = []
    content = []
    org_list=[]
    if org_dict!={}:

        org_list.extend(org_dict["ORG"])
        org_list.extend(org_dict["ORGS"])
        org_list.extend(org_dict["PRE"])
    for sentence in data:


        m = re.findall('<[DPGY]>', sentence)
        if m == None:
            continue

        cutpart = re.split('<[DPGY]>', sentence)
        #######根据m来cut句子，将不需要的剔除，并保存到相应的pandas表
        for i in range(len(m)):
            if m[i] == '<D>':
                time_str = cutpart[i][-10:]
                content.append(time_str)
                symbol.append(m[i])
            elif m[i] == '<P>':
                content.append(search_num(cutpart[i]))
                symbol.append(m[i])
            elif m[i] == "<G>":

                if search_pattern(forbidden_dict["G"], cutpart[i]) == False and \
                        search_pattern(check_dict["G"], cutpart[i]):
                    content.append(search_num(cutpart[i]))
                    symbol.append(m[i])
                elif search_pattern(forbidden_dict["g"], cutpart[i]) == False and \
                        search_pattern(check_dict["g"], cutpart[i]):
                    content.append(search_num(cutpart[i]))
                    symbol.append("<g>")
            elif m[i] == "<Y>":
                if search_pattern(forbidden_dict["Y"], cutpart[i]) == False :
                    content.append(search_num(cutpart[i]))
                    symbol.append("<Y>")
            if org_dict!={}and check_org(cutpart[i], org_list) != None:
                content.append(check_org(cutpart[i], org_list))
                symbol.append("<O>")
    for i in range(len(content)):
        if symbol[0]=="<D>":
            break
        if symbol[i]=="<D>":
            content_temp = [content[i]]
            content_temp.extend(content[:i] + content[i + 1:])
            symbol_temp = [symbol[i]]
            symbol_temp.extend(symbol[:i] + symbol[i+1:])
            content=content_temp
            symbol=symbol_temp
            break
    return content,symbol

def reconstruct(df_answer, symbol, content, name):
    name = int(name)
    row = len(df_answer)
    for i in range(len(content)):
        if row==0 and symbol[i] != "<D>":
            continue
        if symbol[i] == "<D>":
            if row == 0 or content[i] != df_answer["变动截止日期"][row] or df_answer["公告id"][row] != name or symbol[i - 1] != "<D>":
                row = len(df_answer) + 1
            time_list = df_answer.loc[(df_answer["公告id"] == name) & (df_answer["变动截止日期"] == content[i])].index.tolist()
            if time_list != []:
                row = time_list[0]
            df_answer.loc[row, "公告id"] = name
            df_answer.loc[row, "变动截止日期"] = content[i]
            df_answer = df_answer.where(df_answer.notnull(), None)
        elif symbol[i] == "<G>" and df_answer["变动数量"][row] == None:  # and symbol[i-1]!="<P>":
            df_answer.loc[row, "变动数量"] = content[i]
        elif symbol[i] == "<P>" and df_answer["变动后持股数"][row] != None and (
                df_answer["变动后持股比例"][row] == None or symbol[i - 1] == "<g>"):
            df_answer.loc[row, "变动后持股比例"] = content[i]
        elif symbol[i] == "<Y>" and df_answer["变动价格"][row] == None:
            df_answer.loc[row, "变动价格"] = content[i]
        elif symbol[i] == "<g>" and df_answer["变动后持股数"][row] == None:
            df_answer.loc[row, "变动后持股数"] = content[i]
        elif symbol[i] == "<O>" and df_answer["股东全称"][row] == None:
            df_answer.loc[row, "股东全称"] = content[i]
    return  df_answer

def standardize(df_answer):
    def combine(x):
        if x["变动后持股数"] == "":
            x["变动后持股数"] = x["a"]
        if x["变动后持股比例"] == "":
            x["变动后持股比例"] = x["b"]
        return x

    def max_time(df, x):
        if not df.empty:
            s = df["变动截止日期"].tolist()
            s.sort()
            return s[0]
        return ""
    df_answer = df_answer.fillna("")

    def count_empty(row):
        count = 0
        for i in ["公告id", "股东全称", "股东简称", "变动截止日期", "变动价格", "变动数量", "变动后持股数", "变动后持股比例"]:
            if row[i] == "":
                count = count + 1
        return count
    df_answer["count"] = df_answer.apply(count_empty, axis=1)

    #df_answer["count"] = df_answer.apply(lambda x: (x == "").sum(), axis=1)

    s = df_answer.loc[(df_answer["变动数量"] != "") & (df_answer["count"] == 4)]
    df_answer = df_answer.loc[df_answer['count'] < 4]
    df_answer = df_answer.append(s)
    p = df_answer.loc[(df_answer["变动数量"] == "") & (df_answer["变动价格"] == "")]
    df_answer = df_answer.loc[(df_answer["变动数量"] != "") | (df_answer["变动价格"] != "")]
    if not p.empty:
        p["变动截止日期"] = p.apply(lambda x: max_time(df_answer.loc[(df_answer["公告id"] == x["公告id"]) & (df_answer["股东全称"] == x["股东全称"])], x), axis=1)
        p = p.rename(columns={"变动后持股数": "a", "变动后持股比例": "b"})
        df_answer = pd.merge(df_answer, p[["公告id", "股东全称", "变动截止日期", "a", "b"]], \
                             on=["公告id", "股东全称", "变动截止日期"], how="left")
        df_answer = df_answer.apply(lambda x: combine(x), axis=1)  # lambda x:x["变动后持股数"]=x["a"] if x["变动后持股数"]=="",axis=1
        del  df_answer["a"], df_answer["b"]

    del df_answer["count"],
    # df_answer=df_answer.reset_index()
    df_answer["变动数量"] = df_answer["变动数量"].apply(lambda x: "" if x != "" and search_pattern('\.', x) else x)
    return df_answer

def make_dict(path_test):
    names = os.listdir(path_test)
    Parser = HTMLParser.HTMLParser()

    data_dict = defaultdict(dict)
    for i in range(1, 5):
        with open(save_path + "zjc_save{0}.json".format(i), "r", encoding="utf8") as f:
            for line in f:
                #tc:此处如果报错是因为zjc的json格式有误，本来应该是xxx.html与字典交替成行的；一切顺利就不会报错
                if i == 1:
                    if "html" in line:
                        name = line.split(".")[0]
                        data_dict[name] = defaultdict(list)
                    else:
                        text = json.loads(line)
                        if "ORGS" in text:
                            for i in text["ORGS"]:
                                if i not in data_dict[name]["ORGS"]:
                                    data_dict[name]["ORGS"].append(i)
                        if "ORG" in text:
                            for i in text["ORG"]:
                                if i not in data_dict[name]["ORG"]:
                                    data_dict[name]["ORG"].append(i)
                        if "PER" in text:
                            for i in text["PER"]:
                                if i not in data_dict[name]["PER"]:
                                    data_dict[name]["PER"].append(i)
                else:
                    if "html" in line:
                        name = line.split(".")[0]
                        if name not in data_dict:
                            data_dict[name] = defaultdict(list)
                    else:
                        text = json.loads(line)
                        if "ORGS" in text:
                            for i in text["ORGS"]:
                                if i not in data_dict[name]["ORGS"]:
                                    data_dict[name]["ORGS"].append(i)
                        if "ORG" in text:
                            for i in text["ORG"]:
                                if i not in data_dict[name]["ORG"]:
                                    data_dict[name]["ORG"].append(i)
                        if "PER" in text:
                            for i in text["PER"]:
                                if i not in data_dict[name]["PER"]:
                                    data_dict[name]["PER"].append(i)

    for name in names:
        data = Parser.parse_content_zengjianchi(path_test + name, True)
        name = name.split(".")[0]
        data_dict1 = []
        for sentences in data:
            words, ners = fool.analysis(sentences)
            for (_, _, k, l) in ners[0]:
                if k == "person":
                    if l not in data_dict[name]["PRE"]:
                        data_dict[name]["PRE"].append(l)
                if k == "company":
                    if l not in data_dict1 and len(l) >= 3:
                        data_dict1.append(l)
        # 筛选简称
        senstence = ""
        for i in data:
            senstence += i
        for i in data_dict[name]["ORGS"]:
            if senstence.count(i) < 3:
                data_dict[name]["ORGS"].remove(i)

        ORG_list = []
        # 添加全称
        for i in data_dict[name]["ORGS"]:
            Flag = True
            for j in data_dict[name]["ORG"]:
                if judge_s(j, i):
                    Flag = False
                    break
            if Flag:
                for j in data_dict1:
                    if judge_s(j, i) and i != j:
                        ORG_list.append(j)

        ORGS_list = []
        # 添加简称
        for i in data_dict[name]["ORG"]:
            Flag = True
            for j in data_dict[name]["ORGS"]:
                if judge_s(i, j):
                    Flag = False
                    break
            if Flag:
                for j in data_dict1:
                    if judge_s(i, j) and i != j:
                        ORGS_list.append(j)

        # 删选重复
        data_dict[name]["ORG"] += ORG_list
        data_dict[name]["ORGS"] += ORGS_list
        for i in data_dict[name]["ORGS"]:
            for j in data_dict[name]["ORGS"]:
                try:
                    if judge_s(j, i) and i != j:
                        data_dict[name]["ORGS"].remove(i)
                except:
                    pass
        for i in data_dict[name]["ORG"]:
            for j in data_dict[name]["ORG"]:
                try:
                    if judge_s(j, i) and i != j:
                        data_dict[name]["ORG"].remove(i)
                except:
                    pass

        for i in data_dict[name]["ORGS"]:
            tem = []
            for j in data_dict[name]["ORG"]:
                try:
                    if judge_s(j, i):
                        tem.append(j)
                except:
                    pass
            if len(tem) == 0:
                data_dict[name]["ORGS"].remove(i)
            if len(tem) > 3:
                tem.sort(key=lambda x: len(x))
                for k in range(len(tem) - 1):
                    data_dict[name]["ORG"].remove(tem[k])

    return data_dict

def zengjia(row):
    def percent(matched):
        f = matched
        if int(float(f)) < 10:
            date = "0.0"
        else:
            date = "0."
        f = f.rstrip("0").split(".")
        for i in f:
            date += i
        return date

    Parser = HTMLParser.HTMLParser()
    name = row["公告id"]
    path = path_test + str(name) + ".html"
    data = Parser.parse_table(path)
    answer_list = ["空", "空"]
    for i in data:
        index_list = []
        for j in i[0]:
            if "减持后" in i[0][j] or "增持后" in i[0][j] or "变动后" in i[0][j]:
                index_list.append(j)
        if len(index_list) == 0:
            continue
        try:
            for k in i:
                for l in i[k]:
                    if "合计" in i[k][l]:
                        i[k][index_list[0]] = re.sub(r'(?P<number>\d+),',
                                                     TextUtils._thousands, i[k][index_list[0]])
                        if "万股" in i[0][index_list[0]]:
                            i[k][index_list[0]] = re.sub(r'(?P<number>(\d+(\.\d+)?))', TextUtils._tenthousands,
                                                         i[k][index_list[0]])
                        if "%" in i[k][index_list[1]]:
                            i[k][index_list[1]] = i[k][index_list[1]][:-1]
                        if i[k][index_list[0]].isdigit() and i[k][index_list[0]].isdigit():
                            answer_list[0] = i[k][index_list[0]]
                            answer_list[1] = i[k][index_list[1]]
                            break
        except:
            pass

    if "空" not in answer_list:
        row["变动后持股数"] = answer_list[0]
        try:
            row["变动后持股比例"] = percent(answer_list[1])
        except:
            pass
    else:
        # print("#####################################################################################################")
        # print(name)
        data = Parser.parse_content_zengjianchi(path)
        the_keys = ["增持计划实施后", "增持后", "减持后", "减持完成后", "减持计划实施后", "增持计划实施完毕后",
                    "增持完成后", "权益变动后", "仍持有", "合计持有", "现持有", "共计持有", "尚持有"]
        Flag = False
        for index in the_keys:
            for text in data:
                if index in text:
                    text = text.split(index)[-1]
                    if "合计" in text:
                        text = text.split("合计")[-1]
                    text = re.sub(r'\(.*?\)', "", text)
                    X = re.findall("[0-9\.,万]+?股", text, flags=0)
                    Y = re.findall("[0-9\.]+?%", text, flags=0)
                    if len(X) != 0 and len(Y) != 0:
                        X = X[0].replace(",", "").replace("\.", "")
                        if "万股" in X:
                            X = re.sub(r'(?P<number>(\d+(\.\d+)?))', TextUtils._tenthousands, X)
                        X = X.replace("万股", "").replace("股", "")
                        Y = Y[0].replace("%", "")
                        row["变动后持股数"] = X
                        try:
                            row["变动后持股比例"] = percent(Y)
                        except:
                            pass
                        Flag = True
                        break
            if Flag:
                break
    return row

def fin(data_dict, save_fin):
    data_zjc = pd.read_csv(save_path +"ZJC_part1.csv",sep = ',(?!")', dtype=object, encoding="UTF-8") #tc:补了,sep = ',(?!")'后解决文件解析不了的bug
    data_zjc2 = pd.read_csv(save_path +"ZJC_part2.csv",sep = ',(?!")', dtype=object, encoding="UTF-8") #tc:补了,sep = ',(?!")'后解决文件解析不了的bug

    data_zjc = data_zjc.apply(change_org, axis=1, data_dict=data_dict)
    data_zjc2 = data_zjc2.apply(change_org, axis=1, data_dict=data_dict)
    data_zjc = pd.concat([data_zjc, data_zjc2])


    data = data_zjc.reset_index()
    data["Index"] = data.index
    data = data.fillna("")
    data1 = data.drop_duplicates("公告id", keep='last')
    data1 = data1[(data1["变动后持股数"] == "") & (data1["变动后持股比例"] == "")]
    data1 = data1.apply(zengjia, axis=1)

    data1 = data1.rename(columns={"变动后持股数": "a", "变动后持股比例": "b"})
    data = pd.merge(data, data1[["Index", "a", "b"]], on="Index", how="left")
    data = data.fillna("")
    data["变动后持股数"] = data.apply(lambda x: x["a"] if x["a"] != "" else x["变动后持股数"], axis=1)
    data["变动后持股比例"] = data.apply(lambda x: x["b"] if x["b"] != "" else x["变动后持股比例"], axis=1)

    data_zjc = data[["公告id", "股东全称", "股东简称", "变动截止日期", "变动价格", "变动数量", "变动后持股数", "变动后持股比例"]]
    data_zjc = data_zjc.fillna("")
    data_zjc = data_zjc.apply(Supplement_fin, axis=1)
    data_zjc = data_zjc[data_zjc["股东全称"] != "删除"]

    data_zjc.to_csv(save_fin + "zengjianchi.txt", encoding="utf-8", sep="\t", index=False)


def find_others(path_test, save_path, save_fin):
    names = pd.read_csv(save_path + "ZJC_id_list.csv",sep = ',(?!")', encoding="utf-8") #tc:补了,sep = ',(?!")'后解决文件解析不了的bug
    names = names["公告id"].tolist()
    Parser = HTMLParser.HTMLParser()
    columns_fea = ["公告id", "股东全称", "股东简称", "变动截止日期", "变动价格", "变动数量", "变动后持股数", "变动后持股比例"]
    df_answer = pd.DataFrame(columns=columns_fea)

    data_dict = make_dict(path_test) # 构建过程比较慢

    for name in names:
        try:
            name = str(name)
            data = Parser.parse_content_zengjianchi(path_test + str(name) + '.html', True)

            content, symbol = extract_content(data, data_dict[name])

            df_answer = reconstruct(df_answer, symbol, content, name)
        except:
            pass

    df_answer = standardize(df_answer)
    df_answer.to_csv(save_path + "ZJC_part2.csv", encoding="utf-8")
    fin(data_dict, save_fin)


if __name__ == "__main__":
    find_others(path_test, save_path, save_fin)

