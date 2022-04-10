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
def create_mark(text, mark, data_dict, data_dict_xm, data_dict_ht):
    for i in data_dict:
        if i in text:
            index = -1
            for _ in range(text.count(i)):
                index = text.find(i, index + 1)
                mark = TAG(index, len(i), mark, "ORG")
    for i in data_dict_xm:
        if i in text:
            index = -1
            for _ in range(text.count(i)):
                index = text.find(i, index + 1)
                mark = TAG(index, len(i), mark, "XM")
    for i in data_dict_ht:
        if i in text:
            index = -1
            for _ in range(text.count(i)):
                index = text.find(i, index + 1)
                mark = TAG(index, len(i), mark, "HT")

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
    data_dict_xm = defaultdict(list)
    data_dict_ht = defaultdict(list)
    data = pd.read_table(path_train + "hetong.train", header=None)
    for _, row in data.iterrows():
        if str(row[4]) != "nan" and row[4].upper() not in data_dict_ht[row[0]]:
            data_dict_ht[row[0]].append((row[4].replace(" ", "")).upper())

        if str(row[3]) != "nan" and row[3].upper() not in data_dict_xm[row[0]]:
            data_dict_xm[row[0]].append((row[3].replace(" ", "")).upper())

        if row[1] not in data_dict[row[0]] and str(row[1]) != "nan":
            data_dict[row[0]].append(row[1])

    #loop
    for type in ["train", "dev"]:
        with open(save_crope_path + "ht.data.{0}".format(type), "w", encoding='UTF-8') as f:
            for name in eval('names_{0}'.format(type)):
                #print(name)
                data, yifang = Parser.parse_content_hetong(path_train + "html/" + name)
                for sentences in data:
                    mark = ['O' for _ in sentences]
                    mark = create_mark(sentences, mark, data_dict[int(name.split(".")[0])],
                                       data_dict_xm[int(name.split(".")[0])], data_dict_ht[int(name.split(".")[0])])
                    for i in range(len(sentences)):
                        f.write(sentences[i] + " " + mark[i] + "\n")
                    f.write("\n")


def make_t4t(path_test, save_crope_path):
    names = os.listdir(path_test)
    Parser = HTMLParser.HTMLParser()
    #loop
    print("save_crope_path:",save_crope_path)
    with open(save_crope_path + "ht.TEST", "w", encoding='UTF-8') as f:
        for name in names:
            name = str(name)
            data, yifang = Parser.parse_content_hetong(path_test + name)
            f.write(name + " " + yifang + "\n")
            for sentences in data:
                f.write(sentences)
                f.write("\n")
        # f.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('TRAIN', type=int, default=0)
    parser.add_argument('TEST', type=int, default=0)
    parser.add_argument('random_num', type=int, default=0)
    args = vars(parser.parse_args())


    # if args["TRAIN"]:
        # make_train(path_train, save_crope_path, args["random_num"])
    if args["TEST"]:
        make_t4t(path_test,save_crope_path)


