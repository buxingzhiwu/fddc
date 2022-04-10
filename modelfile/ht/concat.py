#-*- coding: utf-8 -*-
from collections import defaultdict
import json
from config import *
import fool
import pandas as pd
import HTMLParser
import pickle
import re

def Supplement_fin(row):
    if row["甲方"] == row["乙方"]:
        row["甲方"] = "删除"
    return row
def judge_s(name,name_s):
    if "(" in name_s and ")" in name_s:
        pass
    else:
        name_s = name_s.replace("(", "").replace(")", "")

    cor_name_pattern = r"[\u4e00-\u9fa5\(\)A-Z\*\、“”0-9]*".join(name_s)
    pattern = re.compile(cor_name_pattern)
    cor_names = re.search(pattern, name)
    if cor_names != None:
        return True
    else:
        return False
def zengjia(row):
        #names = os.listdir("../data/FDDC_announcements_round1_train_20180518/round1_train_20180518/重大合同/html/")
        Parser = HTMLParser.HTMLParser()
        name = row["公告id"]
        if row["联合体成员"] != "":
            return row

        data = Parser.parse_content_zengjianchi(path_test + str(name) + ".html")
        for sentences in data:
            if "联合体" in sentences:
                for line in sentences.split("，"):
                    if "联合体成员：" in line:
                        line = line.split("联合体成员：")[-1]
                        _, ners = fool.analysis(line)
                        ners = ners[0]
                        ners = [x[3] for x in ners if x[2] == "company" or x[2] == "org"]
                        row["联合体成员"] = "、".join(ners)
                    elif "联合体" in line:
                        line = line.split("联合体")[0]
                        line = re.sub("\(.+?\)", "", line)
                        _, ners = fool.analysis(line)
                        ners = ners[0]
                        ners = [x[3] for x in ners if x[2] == "company" or x[2] == "org"]
                        if len(ners) != 0:
                            if row["乙方"] in ners:
                                ners = [x for x in ners if x != row["乙方"]]
                                row["联合体成员"] = "、".join(ners)

                            elif "本公司" in line or "确定公司" in line or "子公司" in line or "我公司" in line:
                                row["联合体成员"] = "、".join(ners)
        return row


with open(save_path + "zdht_test728.pkl", "rb") as f:
    data_dict2 = pickle.load(f)


data_dict = defaultdict(list)
for i in range(4):
    with open(save_path + "ht{0}.json".format(i + 1), "r", encoding="utf8") as f:
        for line in f:
            if "html" in line:
                if i == 0:
                    name = line.split(" ")[0].strip()
                    data_dict[name] = defaultdict(list)
                    if not line.split(" ")[1] is None:
                        data_dict[name]["YF"] = (line.split(" ")[1]).strip()
            else:
                text = json.loads(line)
                if "XM" in text:
                    data_dict[name]["XM"].extend(text["XM"])
                if "ORG" in text:
                    data_dict[name]["ORG"].extend(text["ORG"])
                if "HT" in text:
                    data_dict[name]["HT"].extend(text["HT"])


for i in data_dict.keys():
    if i in data_dict2:
        if not data_dict2[i]['project_list'] is None:
           data_dict[i]["XM"].extend(data_dict2[i]['project_list'])

        if not data_dict2[i]['contract'] is None:
            data_dict[i]["HT"].extend([data_dict2[i]["contract"]])

    for type in ["HT", "ORG", "XM"]:
        D = []
        for j in data_dict[i][type]:
            j = j.strip()
            if j not in D:
                D.append(j)
        # print("######################")
        # D = sorted(D, key=lambda i: len(i), reverse=False)
        # if len(D) > 2:
            #
            #     D[j] = data_dict[i][type].count(j)

            # if len(D) == 1:
            #     data_dict[i][type] = list(D.keys())
            # else:
            #     tem = []
            #     for j in D.keys():
            #         #if D[j] >= 3:
            #         tem.append(j)
            #     data_dict[i][type] = tem

    # if i=="1240733.html":
    #     print(data_dict[i])
feature = ["公告id", "甲方", "乙方", "项目名称", "合同名称", "合同金额上限", "合同金额下限", "联合体成员"]

data_after = pd.DataFrame(columns=feature)
row=-1
for index, i in enumerate(data_dict.keys()):
    if len(data_dict2[i]["muti_dict"].keys())==0:
        row=row+1
        p_list = []
        p_list.append(i.split(".")[0])



        if len(data_dict[i]["ORG"]) > 0 and data_dict[i]["ORG"][0]!=data_dict[i]["YF"]:
            p_list.append(data_dict[i]["ORG"][0])
        elif data_dict2[i]["jafang"]!=None:
            p_list.append(data_dict2[i]["jafang"])
        else:
            p_list.append("")

        p_list.append(data_dict[i]["YF"])

        if len(data_dict[i]["XM"]) > 0:
            p_list.append(data_dict[i]["XM"][0])
        else:
            p_list.append("")

        if len(data_dict[i]["HT"]) > 0:
            p_list.append(data_dict[i]["HT"][0])
        else:
            p_list.append("")

        if not data_dict2[i]["price"] is None:
            p_list.append(data_dict2[i]["price"])
            p_list.append(data_dict2[i]["price"])
        else:
            p_list.append("")
            p_list.append("")
        p_list.append(data_dict2[i]['combination'])

        data_after.loc[row] = p_list
    else:
        for muti_k in range(len(data_dict2[i]["muti_dict"]["jf_list"])):
            row=row+1
            p_list = []
            p_list.append(i.split(".")[0])
            jf_list=data_dict2[i]["muti_dict"]["jf_list"]
            ht_list=data_dict2[i]["muti_dict"]["ht_list"]
            xm_list=data_dict2[i]["muti_dict"]["xm_list"]
            p_list.append(jf_list[muti_k])
            p_list.append(data_dict[i]["YF"])

            #项目
            if xm_list==[]:
                p_list.append("")

            elif len(xm_list)<len(jf_list):
                if len(data_dict[i]["XM"]) > 0:
                    p_list.append(data_dict[i]["XM"][0])
                else :
                    p_list.append(xm_list[0])
            else:p_list.append(xm_list[muti_k])
            #合同
            if ht_list==[]:
                p_list.append("")
            elif len(ht_list) < len(jf_list):
                if len(data_dict[i]["HT"]) > 0:
                    p_list.append(data_dict[i]["HT"][0])
                else:
                    p_list.append(ht_list[0])
            else:

                p_list.append(ht_list[muti_k])
            ##########
            if not data_dict2[i]["price"] is None:
                p_list.append(data_dict2[i]["price"])
                p_list.append(data_dict2[i]["price"])
            else:
                p_list.append("")
                p_list.append("")
            p_list.append(data_dict2[i]['combination'])

            data_after.loc[row] = p_list
data_after = data_after.drop_duplicates(subset=["公告id", "甲方", "乙方"])

data_after = data_after.apply(Supplement_fin, axis=1)
data_after = data_after[data_after["甲方"] != "删除"]

data_after = data_after.fillna("")
data_after = data_after.apply(zengjia, axis=1)

# print("data_after:",data_after)
data_after.to_csv(save_fin + "hetong.txt", encoding="utf-8", sep="\t", index=False)

