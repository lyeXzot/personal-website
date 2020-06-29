from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'linyier'

# 数据库地址
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@127.0.0.1/test'
# 跟踪修改，消耗性能，建议False，未来版本会移除
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
    #关联一对多
    the_comments = db.relationship('comments', backref='the_user')

class comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    at_note_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  #外键
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    create_time = db.Column(db.DateTime)

@app.route('/logic/note_nav/') #数据库读取，渲染内容和最新上传
def note_nav():
    all_types = categories.query.order_by('id')
    newest_notes = notes.query.order_by('time')[-10:]
    newest_notes.reverse()

    return render_template('note_nav.html',types=all_types,newest=newest_notes)

@app.route('/logic/note/<int:note_id>')
def note(note_id):
    the_note = notes.query.filter(notes.id == note_id).first()
    newest_notes = notes.query.order_by('time')[-10:]
    the_comments = comments.query.filter(comments.at_note_id == note_id)
    print(the_note.content)

    return render_template('note.html', the_note=the_note, newest=newest_notes, comments=the_comments)

@app.route('/logic/search/', methods=['POST'])
def search():
    """应该是有两种实现：
    1：接受搜索表单，后台返回搜过结果       //更消耗服务器资源
    2：返回整个notes，前端js进行search    //更消耗网络
    这里使用第一中
    """
    key = request.form['key'].lower()
    result=[]
    query_all = notes.query.all()
    for i in query_all:
        if key in i.name.lower():
            result.append(i)
    news = notes.query.order_by('time')[-10:]
    return render_template('search.html', num=len(result), result=result,search_key=key,newest=news)

@app.route('/logic/signin/')
def signin():
    pass

@app.route('/logic/register/')
def register():
    pass

@app.route('/logic/add_comment/')
def add_comment():
    pass




if __name__ == '__main__':
    app.run(host='127.0.0.1',port=12121,debug=True)