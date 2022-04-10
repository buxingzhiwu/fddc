# MySQL笔记

#### 启动和停止服务

```sql
启动服务
net start mysql

停止服务
net stop mysql
```

#### 登录

```sql
登录
#最简单的方式 
>mysql -u root -p112358zyj
#稍安全的方式
>mysql -u root -p
>112358zyj

#登录别的端口
>mysql -u root -P3306 -p密码

#登录别的ip
>mysql -u root -P 3306 -h 127.0.0.1 -p密码

退出
quit


```

# Flask笔记

## 模板

#### 继承母版页面

```jinja
主页面
# 要填充的位置
{% block content %}
{% endblock%}

块页面
# 开头处 base.html指主页面
{% extend 'base.html'%}
{% block content %}
# 页面内容
# 结尾处
{% endblock %}
```

#### 按需要引入页面块

```jinja
# 按需要引入side.html（写在主页面）
{% include 'side.html' %}

# 继承母版的块页面，如果需要按需引入的页面
{% include 'side.html' %}

```



## I/O类操作

#### pymysql

```python
# 所有的I/O类操作有三个基本步骤：

import pymysql
from pymysql.cursor import DictCursor
# 第一步：链接到数据库
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', 
						charset='utf8', database='test1')
print(conn.get_server_info())

# 第二步：执行SQL语句
# 1.实例化一个游标对象
# cursor = conn.cursor()
cursor = conn.cursor(DictCursor)

# 2.定义SQL语句
sql = "select * from users"
# 3.通过游标执行
cursor.execute(sql)
# 4.处理执行结果
result = cursor.fetchall()
# result是一个二维元组，可以通过下标操作输出，但是一般不建议使用下标获取
#建议使用key-value

# 更新操作
sql = "update users set qq='123' where userid=4"
cursor.execute(sql)
# 提交修改 update insert delete，或者conn的autocommite设置为true
conn.commite()

# 第三步：关闭数据库链接
cursor.close()
conn.close()
```

#### 自定义ORM

a)    Object-Relational Mapping：对象-关系映射。把数据转换成Python对象。进而实现数据库的操作对象化，减少或完全不用编写SQL原生语句。

b)   数据库中的表 –> Python的类。

c)    表里面的列 -> 类的属性。

d)   表里面的行 à 类的实例，字典对象表述

e)    字典对象的Key对应列，Value对应值。

f)    对增删改查进行封装。
