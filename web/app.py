from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime,time,random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'linyier'

# 数据库地址
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@127.0.0.1/test'
# 跟踪修改，建议False，未来版本会移除
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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

class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)    #头像使用固定路径+userid的方式获取
    name = db.Column(db.String(100),unique=True)
    email = db.Column(db.String(50))
    passwd = db.Column(db.String(50))
    create_time = db.Column(db.DateTime)

class comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    at_note_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    create_time = db.Column(db.DateTime)

@app.route('/') #数据库读取，渲染内容和最新上传
def note_nav():
    all_types = categories.query.order_by('id')

    newest_notes = notes.query.order_by('time') #这里应该能优化，不过不清楚SQLAIchemy的查询函数
    newest_notes = newest_notes[-10:]   #不考虑不够10个的情况了

    return render_template('note_nav.html',types=all_types,newest=newest_notes)

@app.route('/login')
def signin():
    pass

@app.route('/register')
def register():
    pass

@app.route('/comment')
def comment():
    pass

@app.route('/go_to_note')
def note():
    pass

if __name__ == '__main__':
    app.run(debug=True)