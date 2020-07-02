# coding:utf-8
"""写得很乱...有空改改"""
import os

work = os.listdir('./temp_data')

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime, time

app = Flask(__name__)
# 数据库地址
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@127.0.0.1/test'
# 跟踪修改，建议False，未来版本会移除
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    time = db.Column(db.DateTime)
    content = db.Column(db.Text)
    describe = db.Column(db.String(200))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))  # 外键
    # type_in_notes 的定义在categories中


class categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    # 关联 一对多                    class notes
    the_notes = db.relationship('notes', backref='type_in_notes')


print(work)

name = ''
content = ''
describe = input("describe:")

cor = categories.query.order_by('id')
print('id\tname')
for i in cor:
    print(i.id, i.name)

category_id = int(input("类别ID:"))

for i in work:
    if (i[-3:] == 'htm'):
        with open('./temp_data/' + i, 'r', encoding='utf-8') as f:
            data = f.read()
            data = data.split("style='text-justify-trim:punctuation'>")[1]  # 不严谨
            content = data.split("</body>")[0]  # 不严谨
        name = i[:-4]

a = len(notes.query.all()) + 1
# 下一篇id: a

content = content.replace(name + '.files', '/static/note_images/' + str(a))

add_note = notes(name=name, category_id=category_id, describe=describe, content=content, time=datetime.datetime.now())
print(name, describe)

db.session.add(add_note)

db.session.commit()

"""移动照片"""
way = './static/note_images/' + str(a)

for i in work:
    if (i[-5:] == 'files'):
        os.mkdir(way)
        need_move_way = './temp_data/'+ name + '.files'
        need_move_list = os.listdir(need_move_way)
        for j in need_move_list:
            with open(need_move_way+'/'+j, 'rb') as f1:
                temp = f1.read()
                with open(way + '/' + j, 'wb') as f2:
                    f2.write(temp)

for i in work:
    if i[-5:] == 'files':
        os.rmdir('./temp_data/'+ i)
    else:
        os.remove('./temp_data/'+ i)

print('success');



