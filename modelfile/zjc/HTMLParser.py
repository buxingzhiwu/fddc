#-*- coding: utf-8 -*-
import re
import codecs
import copy
from bs4 import BeautifulSoup
import TextUtils
from collections import defaultdict


class ContantTree(object):
    def __init__(self):
        self.Contant = self.tree()
        self.catalogue = defaultdict()

    def tree(self):
        return defaultdict(self.tree)

    def resolving_tree(self):
        for i in self.Contant:
            print(type(i))


class HTMLParser(object):

    def __init__(self):
        self.contant = ContantTree()
        pass


    def parse_content(self, html_file_path):
        rs = []
        with codecs.open(html_file_path, encoding='utf-8', mode='r') as fp:
            soup = BeautifulSoup(fp.read(), "html.parser")
            [s.extract() for s in soup('table')]
            paragraphs = []
            for div in soup.find_all('div'):
                div_type = div.get('type')
                if div_type is not None and div_type == 'paragraph':
                    paragraphs.append(div)
            for paragraph_div in paragraphs:
                has_sub_paragraph = False
                for div in paragraph_div.find_all('div'):
                    div_type = div.get('type')
                    if div_type is not None and div_type == 'paragraph':
                        has_sub_paragraph = True
                if has_sub_paragraph:
                    continue
                rs.append([])
                for content_div in paragraph_div.find_all('div'):
                    div_type = content_div.get('type')
                    if div_type is not None and div_type == 'content':
                        rs[-1].append(TextUtils.text_processing(content_div.text))
        paragraphs = []
        for content_list in rs:
            if len(content_list) > 0:
                paragraphs.append(''.join(content_list))
        return paragraphs


    def parse_table(self, html_file_path):
        rs_list = []
        with codecs.open(html_file_path, encoding='utf-8', mode='r') as fp:
            soup = BeautifulSoup(fp.read(), "html.parser")
            for table in soup.find_all('table'):
                table_dict, is_head_two_rowspan = self.parse_table_to_2d_dict(table)
                row_length = len(table_dict)
                if table_dict is not None:
                    if is_head_two_rowspan and row_length > 2:
                        try:
                            new_table_dict = {}
                            head_row = {}
                            col_length = len(table_dict[0])
                            for col_idx in range(col_length):
                                head_row[col_idx] = table_dict[0][col_idx] + table_dict[1][col_idx]
                            new_table_dict[0] = head_row
                            for row_idx in range(2, row_length):
                                new_table_dict[row_idx - 1] = table_dict[row_idx]
                            rs_list.append(new_table_dict)
                        except KeyError:
                            rs_list.append(table_dict)
                    else:
                        rs_list.append(table_dict)
        return rs_list


    def parse_inside_table(self, tem):
        rs_list = []
        for table in tem.find_all('table'):
            table_dict, is_head_two_rowspan = self.parse_table_to_2d_dict(table)
            row_length = len(table_dict)
            if table_dict is not None:
                if is_head_two_rowspan and row_length > 2:
                    try:
                        new_table_dict = {}
                        head_row = {}
                        col_length = len(table_dict[0])
                        for col_idx in range(col_length):
                            head_row[col_idx] = table_dict[0][col_idx] + table_dict[1][col_idx]
                        new_table_dict[0] = head_row
                        for row_idx in range(2, row_length):
                            new_table_dict[row_idx - 1] = table_dict[row_idx]
                        rs_list.append(new_table_dict)
                    except KeyError:
                        rs_list.append(table_dict)
                else:
                    rs_list.append(table_dict)
        return rs_list


    def parse_content_zengjianchi(self, html_file_path, flag=False):
        rs = []
        with codecs.open(html_file_path, encoding='utf-8', mode='r') as fp:
            soup = BeautifulSoup(fp.read(), "html.parser")
            [s.extract() for s in soup('table')]
            paragraphs = []
            for div in soup.find_all('div'):
                div_type = div.get('type')
                if div_type is not None and div_type == 'paragraph':
                    paragraphs.append(div)
            for paragraph_div in paragraphs:
                has_sub_paragraph = False
                for div in paragraph_div.find_all('div'):
                    div_type = div.get('type')
                    if div_type is not None and div_type == 'paragraph':
                        has_sub_paragraph = True
                if has_sub_paragraph:
                    continue
                rs.append([])
                for content_div in paragraph_div.find_all('div'):
                    div_type = content_div.get('type')
                    if div_type is not None and div_type == 'content':
                        rs[-1].append(TextUtils.del_space(content_div.text))
        paragraphs = []
        for content_list in rs:
            if len(content_list) > 0:
                paragraphs.append(''.join(content_list))

        article = []
        for sentences in paragraphs:
            for sentence in re.split(r"；|。|？|！|;|\?|!", sentences):
                if len(sentence) != 0:
                    article.append(sentence)

        if flag:
            for i in range(len(article)):
                article[i] = TextUtils.text_processing(article[i])
        return article


    def find_cop(self, sentence):
        cor_name_pattern = r"[\u4e00-\u9fa5,\(\)]*?(有限|股份|有限责任)公司"
        pattern = re.compile(cor_name_pattern)
        cor_names = re.search(pattern, sentence)
        return cor_names


    def parse_content_zengjianchi_v2(self, html_file_path, flag=False):
        rs = []
        with codecs.open(html_file_path, encoding='utf-8', mode='r') as fp:
            soup = BeautifulSoup(fp.read(), "html.parser")
            [s.extract() for s in soup('table')]
            paragraphs = []
            text_temp = ""
            for item in soup.find_all('div', type="content"):
                text = item.get_text(strip=True).replace(" ", "").replace("\n", "").replace("\t", "") \
                    .replace("（", "(").replace("）", ")")
                if len(text) == 0:
                    continue
                    # 纯规则
                elif text.endswith("。") or text.endswith("：") or text.endswith("；"):
                    # print(text_temp)
                    text_temp = text_temp + text
                    paragraphs.append(TextUtils.del_space(text_temp))
                    text_temp = ""
                else:
                    text_temp = text_temp + text
                    continue
            paragraphs.append(TextUtils.del_space(text_temp))


        article = []
        for sentences in paragraphs:
            for sentence in re.split(r"；|。|？|！|;|\?|!", sentences):
                if len(sentence) != 0:
                    article.append(sentence)



        cor_names = self.find_cop(article[-1].replace("特此公告", "？？"))
        if cor_names != None:
            yifang = cor_names.group(0)
        else:
            cor_names = self.find_cop(article[0].replace("号", "??"))
            if cor_names != None:
                yifang = cor_names.group(0)
            else:
                yifang = ""


        for sentence in article:
            if "子公司" in sentence:
                cor_name_pattern = r"(?<=子公司)[\u4e00-\u9fa5,\(\)]*?(有限|股份|有限责任)公司"
                pattern = re.compile(cor_name_pattern)
                cor_names = re.search(pattern, sentence)
                if cor_names != None:
                    if "与" not in cor_names.group(0):
                        yifang = cor_names.group(0)
                        break

                        # if len(data_dict["ORG"][name.split(".")[0]]) != 0 and data_dict["ORG"][name.split(".")[0]][0] in sentence:
                        #     print(data_dict["ORG"][name.split(".")[0]][0])
                        #     print(sentence)

        if flag:
            for i in range(len(article)):
                article[i] = TextUtils.text_processing(article[i])
        return article, yifang


    def parse_content_hetong(self, html_file_path, flag=False):
        rs = []
        with codecs.open(html_file_path, encoding='utf-8', mode='r') as fp:
            soup = BeautifulSoup(fp.read(), "html.parser")
            [s.extract() for s in soup('table')]
            paragraphs = []
            text_temp = ""
            for item in soup.find_all('div', type="content"):
                text = item.get_text(strip=True).replace(" ", "").replace("\n", "").replace("\t", "") \
                    .replace("（", "(").replace("）", ")")
                if len(text) == 0:
                    continue
                elif "误导性陈述或重大遗漏" in text or "误导性陈述或者重大遗漏" in text:
                    text_temp = ""
                    continue
                elif text.endswith("。") or text.endswith("：") or text.endswith("；"):
                    text_temp = text_temp + text
                    paragraphs.append(TextUtils.del_space(text_temp))
                    text_temp = ""
                else:
                    text_temp = text_temp + text
                    continue

        article = []
        for sentences in paragraphs:
            for sentence in re.split(r"；|。|？|！|;|\?|!", sentences):
                if len(sentence) != 0:
                    article.append((sentence.replace(" ", "")).upper())

        return article


    def get_shiyi(self,item, DICT):
        if not DICT:
            DICT = defaultdict(list)
        for tep in item:
            tables = self.parse_inside_table(tep)
            if len(tables) != 0:
                for table in tables:
                    for tem in table.values():
                        try:
                            if str(tem[1]) == "指":
                                DICT[tem[0]] = tem[2]
                            elif tem[1].startswith("指"):
                                DICT[tem[0]] = tem[1][1:]
                        except:
                            pass


            elif tep.get('type') == "content":
                text = tep.get_text(strip=True).replace(" ", "").replace("\n", "").replace("\t", "") \
                    .replace("（", "(").replace("）", ")")
                if "指" in text:
                    DICT[text.split("指")[0]] = text.split("指")[1]

        #print(DICT)
        return DICT


    def parse_content_chongzu(self, html_file_path):
        rs = []
        with codecs.open(html_file_path, encoding='utf-8', mode='r') as fp:
            soup = BeautifulSoup(fp.read(), "html.parser")
            #[s.extract() for s in soup('table')]
            paragraphs = []
            text_temp = ""
            shiyi = None
            for item in soup.find_all('div'):
                if item.get('type') == "paragraph" and item.get('title')is not None:
                    if "释义" in item.get('title').replace(" ", ""):
                        shiyi = (self.get_shiyi(item.find_all('div'), shiyi))
                    if text_temp != "":
                        paragraphs.append(TextUtils.del_space(text_temp))
                    text_temp = ""
                    paragraphs.append(TextUtils.del_space(item.get('title')))


                if item.get('type') == "content":
                    text = item.get_text(strip=True).replace(" ", "").replace("\n", "").replace("\t", "") \
                        .replace("（", "(").replace("）", ")")
                    if len(text) == 0:
                        continue
                        # 纯规则
                    elif text.endswith("。") or text.endswith("：") or text.endswith("；"):
                        # print(text_temp)
                        text_temp = text_temp + text
                        paragraphs.append(TextUtils.del_space(text_temp))
                        text_temp = ""
                    else:
                        text_temp = text_temp + text
                        continue
            paragraphs.append(TextUtils.del_space(text_temp))

        article = []
        for sentences in paragraphs:
            for sentence in re.split(r"；|。|？|！|;|\?|!", sentences):
                if len(sentence) != 0:
                    article.append(TextUtils.dig_processing(sentence))


        return article,shiyi


    @staticmethod
    def parse_table_to_2d_dict(table):
        rs_dict = {}
        row_index = 0
        is_head_two_rowspan, is_head = False, True
        for tr in table.find_all('tr'):
            col_index, cur_col_index = 0, 0
            for td in tr.find_all('td'):
                rowspan = td.get('rowspan')
                rowspan = int(rowspan) if (rowspan is not None and int(rowspan) > 1) else 1
                colspan = td.get('colspan')
                colspan = int(colspan) if (colspan is not None and int(colspan) > 1) else 1
                if is_head:
                    if rowspan > 1 or colspan > 1:
                        is_head_two_rowspan = True
                    is_head = False
                for r in range(rowspan):
                    if (row_index + r) not in rs_dict:
                        rs_dict[row_index + r] = {}
                    for c in range(colspan):
                        cur_col_index = col_index
                        while cur_col_index in rs_dict[row_index + r]:
                            cur_col_index += 1
                        rs_dict[row_index + r][cur_col_index] = TextUtils.del_space(td.text)
                        cur_col_index += 1
                col_index = cur_col_index
            row_index += 1
        return rs_dict, is_head_two_rowspan


if __name__ == "__main__":
    Parser = HTMLParser()
    DICT = Parser.parse_content_new2("../../data/复赛新增类型训练数据-20180712/资产重组/html/1095063.html")
    # print(DICT.Contant.keys())
    # for i in DICT.Contant.keys():
    #     print("#########")
    #     print(DICT.Contant[i])