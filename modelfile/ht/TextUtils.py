#-*- coding: utf-8 -*-
import re

def del_space(text):
    text = text.replace(" ", "").replace("\n", "").replace("\t", "").replace("（", "(").replace("）", ")")
    text = text.replace("html", "")
    return text

def hetong_label_replace(text,dict):
    text = text.replace(" ", "").replace("\n", "").replace("\t", "").replace("（", "(").replace("）", ")")
    text = datechange(text)
    text = percent(text)
    text = replace_YG(text)
    text = text.replace("html", "")
    text=replace_label(text,dict)
    return text


def text_processing(text):
    text = text.replace(" ", "").replace("\n", "").replace("\t", "").replace("（", "(").replace("）", ")")
    text = datechange(text)
    text = percent(text)
    text = replace_yg(text)
    text = text.replace("html", "")
    return text


def dig_processing(text):
    text = re.sub(r'(?P<number>\d+),', _thousands, text)
    text = re.sub(r'(?P<number>(\d+(\.\d+)?))万', _tenthousands, text)
    text = re.sub(r'(?P<number>(\d+(\.\d+)?))亿', _hundredmillion, text)
    text = re.sub(r'(\d+(\.\d+)?)元', _yuan, text)
    return text



##date change
def _datechange(matched):
    if int(matched.group('M')) < 10:
        mounth = "0" + str(int(matched.group('M')))
    else:
        mounth = matched.group('M')
    if int(matched.group('D')) < 10:
        day = "0" + str(int(matched.group('D')))
    else:
        day = matched.group('D')
    date = matched.group('Y')+"-"+ mounth +"-"+day
    return date + "<D>"
def datechange(text):
    text = re.sub(r'\d+年\d+月\d+日[—、-至起)(（）～-]+(?P<Y>\d+)年(?P<M>\d+)月(?P<D>\d+)日', _datechange, text)
    text = re.sub(r'(?P<Y>\d+)年\d+月\d+日[—、-至起)(（）～-]+(?P<M>\d+)月(?P<D>\d+)日', _datechange, text)
    text = re.sub(r'(?P<Y>\d+)年(?P<M>\d+)月\d+日[—、-至起)(（）～-]+(?P<D>\d+)日', _datechange, text)
    text = re.sub(r'(?P<Y>\d+)年(?P<M>\d+)月(?P<D>\d+)日', _datechange, text)
    return(text)

##percent change
def _percent(matched):
    f = matched.group('number')
    if int(float(f)) < 10:
        date = "0.0"
    else:
        date = "0."
    f = f.rstrip("0").split(".")
    for i in f:
        date += i
    return date + "<P>"
def _thousands(matched):
    date = matched.group('number')
    return date
def _tenthousands(matched):
    date = str(int(float(matched.group('number'))*10000))
    return date
def _hundredmillion(matched):
    date = str(int(float(matched.group('number'))*100000000))
    return date
def percent(text):
    text = re.sub(r'(?P<number>(\d+(\.\d+)?))[%％\uf8ff]', _percent, text)
    text = re.sub(r'(?P<number>\d+),', _thousands, text)
    text = re.sub(r'(?P<number>(\d+(\.\d+)?))万', _tenthousands, text)
    text = re.sub(r'(?P<number>(\d+(\.\d+)?))亿', _hundredmillion, text)
    return text

##find yuan and gu
def _yuan(matched):
    date = matched.group()
    return date[:-1] + "<Y>"
def _gu(matched):
    date = matched.group()
    return date[:-1] + "<G>"
def replace_yg(text):
    text = re.sub(r'(\d+(\.\d+)?)元', _yuan, text)
    text = re.sub(r'\d+?股', _gu, text)
    return text
def replace_YG(text):
    text = re.sub(r'(\d+(\.\d+)?)元', _yuan, text)
    text = re.sub(r'\d+?股', _gu, text)
    return text


def _YF(matched):
    return "<YF>"+matched.group(0)+"</YF>"
def _JE(matched):
    return "<JE>"+matched.group(0)+"</JE>"
def _HT(matched):
    return "<HT>"+matched.group(0)+"</HT>"
def _ORG(matched):
    return "<ORG>"+matched.group(0)+"</ORG>"
def _XM(matched):
    return "<XM>"+matched.group(0)+"</XM>"

def replace_label(text,dict):

    text=re.sub(dict["YF"],_YF,text)

    # if dict["JE"]!=[]:
    #     text = re.sub(dict["JE"], _JE, text)
    for i in range(len(dict["HT"])):

        text = re.sub(dict["HT"][i], _HT, text)

    for i in range(len(dict["ORG"])):
        text = re.sub(dict["ORG"][i], _ORG, text)
    for i in range(len(dict["XM"])):
        text = re.sub(dict["XM"][i], _XM, text)
    return text