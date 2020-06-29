from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime,time
"""
初始化数据库，测试用
"""
app = Flask(__name__)
# 数据库地址
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@127.0.0.1/test'
# 跟踪修改，建议False，未来版本会移除
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'linyier'
db = SQLAlchemy(app)


class categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

    # 关联 一对多                    class notes
    the_notes = db.relationship('notes', backref='type_in_notes')


class notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    time = db.Column(db.DateTime)
    content = db.Column(db.Text)
    describe = db.Column(db.String(200))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))  # 外键

    # type_in_notes 的定义在categories中


if __name__ == '__main__':
    db.drop_all()
    db.create_all()  # 创建表
    for i in ['机器学习','算法','编程问题','Linux','Web','网络']:   #可以扩展
        ttt = categories(name=i)
        db.session.add(ttt)
    db.session.commit()
    tpp=categories(id=99,name='tips')
    db.session.add(tpp)
    db.session.commit()
    result1 = categories.query.all()
    print(result1)
    for j in result1:
        for i in range(3):
            notee = notes(name='note'+str(i)+str(j.name),
                          category_id=j.id,
                          content='This is content',
                          describe='small describe',
                          time=datetime.datetime.now())
            time.sleep(1)
            db.session.add(notee)
        db.session.commit()