#-*- coding: utf-8 -*-
from collections import defaultdict
from bs4 import BeautifulSoup
import re
import lxml.html


def table_to_2d(table_tag):
    #给每个表建立空列表
    rows = table_tag("tr")
    if "代码" in str(rows):
        return None
    table_3y = []
    m, len_t, head_num = 0, 0, 0
    #把原始html表格转变成三元组
    for row_i, row in enumerate(rows):
        table_row = []
        n = 100
        for col in row(["td", "th"]):
            x, y = 1, 1
            if col.has_attr('rowspan'):
                y = int(col['rowspan'])
            if col.has_attr('colspan'):
                x = int(col['colspan'])
            n = min(n, y)
            if row_i == 0:
                head_num = max(head_num, y)
            table_row.append([''.join(col.get_text().split()), x, y])
        for r in table_row:
            r[2] = r[2] - n + 1
            if row_i == 0:
                head_num = head_num - n + 1
        #处理一行只有一条元素的行
        if len(table_row) == 1:
            if len_t > 0:
                for col_i, col in enumerate(table_3y[len_t -1]):
                    if col[2] > 1:
                        table_3y[len_t - 1][col_i][2] -= 1
            continue

        m = max(m, sum([i[1] for i in table_row]))
        table_3y.append(table_row)
        len_t += 1

    #建立完全表格
    table = [[None] * m for _ in range(len(table_3y))]
    for row_i, row in enumerate(table_3y):
        for col_i, col in enumerate(row):
                insert_V2(table, row_i, col_i, col,)

    #处理表头问题
    # if head_num > 1:
    #     for i in range(1, head_num):
    #         for j in range(m):
    #             if table[0][j] != table[i][j]:
    #                 table[0][j] = table[0][j] + table[i][j]

        # if table[head_num][0] == None:
        #     for j in range(len_cols_n):
        #         if table[0][j] != table[head_num][j]:
        #             if table[head_num][j] == None:
        #                 table[0][j] = table[0][j]
        #             else :
        #                 table[0][j] = table[0][j] + table[head_num][j]
        #     head_num += 1
        #
        # if table[0][0] == None:
        #     for j in range(len_cols_n):
        #         if table[0][j] != table[head_num][j]:
        #             if table[0][j] == None:
        #                 table[0][j] = table[head_num][j]
        #             else :
        #                 table[0][j] = table[0][j] + table[head_num][j]
        #     head_num += 1

        # table = [table[0][:]] + table[head_num:][:]

    return table


def insert_V2(table, row, col, element):
    if table[row][col] is None:
        table[row][col] = element[0]
        if element[1] > 1:
            for i in range(1, element[1]):
                table[row][col+i] = element[0]
        if element[2] > 1:
            for i in range(1, element[2]):
                table[row+i][col] = element[0]
        if element[1] > 1 and element[2] > 1:
            for i in range(1, element[2]):
                for j in range(1, element[1]):
                    table[row + i][col + j] = element[0]
    else:
        insert_V2(table, row, col + 1, element)

def add_year(path):
    htmlfile = open(path, 'r', encoding='utf-8')
    htmlhandle = htmlfile.read()
    soup = BeautifulSoup(htmlhandle, "lxml")
    #去除table的内容
    [s.extract() for s in soup('table')]
    text_temp = ""
    for item in soup.find_all('div', type="content"):
        text = item.get_text(strip=True).replace(" ", "").replace("\n", "").replace("\t", "")\
                                        .replace("（", "(").replace("）", ")")
def HTML(path):
    with open(path, encoding='utf-8') as r:
        txt = ''.join(r.readlines())
    txt1 = re.sub(r'</tbody>[\S][^\u4e00-\u9fa5]*?<tbody>', "", txt)
    soup = BeautifulSoup(txt1, "lxml")
    tables = soup.findAll('table')
    # for table in tables:
    #     data = table_to_2d(table)
    #     yield data

    tables_list = defaultdict(list)
    num = 0
    for table in tables:
        data = table_to_2d(table)
        if data != None:
            tables_list[num] = data
            num += 1




    ####提取文本中的年
    [s.extract() for s in soup('table')]
    year=None
    year_list=[]
    for item in soup.find_all('div', type="content"):
        text = item.get_text(strip=True).replace(" ", "").replace("\n", "").replace("\t", "") \
            .replace("（", "(").replace("）", ")")
        m=re.findall('[0-9]{4}年',text)
        if m!=None:
            for m1 in m:
                year_list.append(m1.split("年")[0])
    if year_list!=[]:
        year=max(map(lambda x: (year_list.count(x), x), year_list))[1]








    return tables_list,year


if __name__ == '__main__':
    data = HTML("../train/html/1667722.html")#tc:不改了好麻烦
    #data = HTML("../增减持/100829_change.html")
