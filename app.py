from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import pymysql

pymysql.install_as_MySQLdb()

# 实例化
app = Flask(__name__)

# 设置连接数据库的URL mysql://username:password@server/db
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:112358zyj@127.0.0.1:3306/test1?charset=utf8'
# 设置每次请求结束后会自动提交数据库中的改动
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# 查询时会显示原始SQL语句
# app.config['SQLALCHEMY_ECHO'] = True
# 把flask应用传递给SQLAlchemy作为对象，实例化
db = SQLAlchemy(app)

from sqlalchemy import Table, MetaData


class CalResult(db.Model):
    __table__ = Table('calresult', MetaData(bind=db.engine), autoload=True)

    def find_header_by_id(self,id):
        row=db.session.query(CalResult).filter(CalResult.id==id).all()
        return row

def CalResult_query(id):
    calresult = CalResult()
    row = calresult.find_header_by_id(id)
    return row

@app.route('/')
def indexPage():
    calresult=CalResult_query('108271')
    return render_template('index.html', calresult=calresult)





