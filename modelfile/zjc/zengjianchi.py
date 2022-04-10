#-*- coding: utf-8 -*-
import time, os, re
import pickle
from config import *
import argparse
import pandas as pd
from collections import defaultdict
import multiprocessing
import random
import HTMLParser


#annotation
def TAG(index, len_i, mark, tag):
    mark[index] = "B-" +tag
    for i in range(1, len_i):
        mark[i + index] = "I-" + tag
    return mark
def create_mark(text, mark, data_dict, data_dict_s):
    for i in data_dict_s:  # 缩写
        if i in text:
            index = -1
            for _ in range(text.count(i)):
                index = text.find(i, index + 1)
                mark = TAG(index, len(i), mark, "ORGS")
    for i in data_dict:#判断公司名还是人名
        if len(i) <= 3:
            tag = "PER"
        else:
            tag = "ORG"
        if i in text:
            index = -1
            for _ in range(text.count(i)):
                index = text.find(i, index + 1)
                mark = TAG(index, len(i), mark, tag)
    return mark


def make_train(path_train, save_crope_path, random_number):
    names = os.listdir(path_train + "html")
    Parser = HTMLParser.HTMLParser()

    # shuffle
    random.seed(random_number)
    random.shuffle(names)
    names_train = names[:-200]
    names_dev = names[-200:]

    # dict
    data_dict = defaultdict(list)
    data_dict_s = defaultdict(list)

    # tc:open一次file并且加上sep和encoding解决读不了bug；原：data = pd.read_table(路径, header=None)
    filename = open(path_train + "zengjianchi.train", encoding='utf-8')
    data = pd.read_table(filename, header=None,sep="\t", encoding="utf-8")

    for _, row in data.iterrows():
        if row[2] not in data_dict_s[row[0]] and str(row[2]) != "nan":
            data_dict_s[row[0]].append(row[2])
        if row[1] not in data_dict[row[0]] and str(row[1]) != "nan":
            data_dict[row[0]].append(row[1])

    #loop
    for type in ["train", "dev"]:
        with open(save_crope_path + "zjc.data.{0}".format(type), "w", encoding='UTF-8') as f:
            for name in eval('names_{0}'.format(type)):
                #print(name)
                data = Parser.parse_content_zengjianchi(path_train + "html/" + name)
                for sentences in data:
                    mark = ['O' for _ in sentences]
                    mark = create_mark(sentences, mark, data_dict[int(name.split(".")[0])], #tc:重要！mark训练数据产生的地方！
                                       data_dict_s[int(name.split(".")[0])])
                    for i in range(len(sentences)):
                        f.write(sentences[i] + " " + mark[i] + "\n")
                    f.write("\n")


def make_t4t(path_test, save_crope_path):
    names = os.listdir(path_test)
    Parser = HTMLParser.HTMLParser()
    #loop
    with open(save_crope_path + "zjc.TEST", "w", encoding='UTF-8') as f:
        for name in names:
           # print(name)
            f.write(name + "\n")
            data = Parser.parse_content_zengjianchi(path_test + name)
            for sentences in data:
                f.write(sentences)
                f.write("\n")


def find_others(path, miss_list, save_others_path):

    names = pd.read_csv(miss_list, encoding="GBK")
    names = names["公告id"]
    Parser = HTMLParser.HTMLParser()


    with open(save_others_path + "zjc.others", "w", encoding='UTF-8') as f:
        for name in names:
            name = str(name) + ".html"
            print(name)
            data = Parser.parse_content_zengjianchi(path + "html/" + name, True)
            print(data)
            list_type1 = []
            list_type2 = []
            for sentence in data:
                if "<D>" in sentence and "<P>" in sentence and "<G>" in sentence:
                    list_type1.append(sentence)
                elif "<G>" in sentence and "<P>" in sentence:
                    list_type2.append(sentence)
            print(list_type1)
            print(list_type2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('TRAIN', type=int, default=0)
    parser.add_argument('TEST', type=int, default=0)
    parser.add_argument('FindOthers', type=int, default=0)
    parser.add_argument('random_num', type=int, default=0)
    args = vars(parser.parse_args())

    if args["TRAIN"]:
        make_train(path_train, save_crope_path, args["random_num"])
    if args["TEST"]:
        make_t4t(path_test, save_crope_path)
    if args["FindOthers"]:
        find_others(path_test, miss_list, save_path)

