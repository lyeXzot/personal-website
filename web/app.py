from flask import Flask, request, flash, url_for, redirect, render_template, make_response
from flask_sqlalchemy import SQLAlchemy
import datetime, time, re
from hashlib import sha1

Pattern = re.compile(r'^[a-zA-Z0-9_-]{4,16}$')

the_secret_key = 'zot'
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
    id = db.Column(db.Integer, primary_key=True)  # 头像使用固定路径+userid的方式获取
    name = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(50))
    passwd = db.Column(db.String(50))
    create_time = db.Column(db.DateTime)
    # 关联一对多
    the_comments = db.relationship('comments', backref='the_user')


class comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    at_note_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 外键
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    create_time = db.Column(db.DateTime)


@app.route('/logic/note_nav/')  # 数据库读取，渲染内容和最新上传
def note_nav():
    all_types = categories.query.order_by('id')
    newest_notes = notes.query.order_by('time')[-10:]
    newest_notes.reverse()

    if identify():
        the_user = users.query.filter(users.id == int(request.cookies.get('data')[0])).first()
        return render_template('note_nav.html', types=all_types, newest=newest_notes, the_user=the_user)

    return render_template('note_nav.html', types=all_types, newest=newest_notes)


@app.route('/logic/note/<int:note_id>')
def note(note_id):
    the_note = notes.query.filter(notes.id == note_id).first()
    newest_notes = notes.query.order_by('time')[-10:]
    the_comments = comments.query.filter(comments.at_note_id == note_id)

    return render_template('note.html', the_note=the_note, newest=newest_notes, comments=the_comments)


@app.route('/logic/search/', methods=['POST'])
def search():
    """应该是有两种实现：
    1：接受搜索表单，后台返回搜过结果       //更消耗服务器资源
    2：返回整个notes，前端js进行search    //更消耗网络
    这里使用第一中
    """
    key = request.form['key'].lower()
    result = []
    query_all = notes.query.all()
    for i in query_all:
        if key in i.name.lower():
            result.append(i)
    news = notes.query.order_by('time')[-10:]
    return render_template('search.html', num=len(result), result=result, search_key=key, newest=news)


@app.route('/logic/signin/', methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        return render_template('signin.html')
    else:
        username = request.form['username']
        password = request.form['password1']
        # 虽然用的sqlaichemy，但底层还是sql语句，避免注入做下正则匹配
        if Pattern.match(username):
            the_user = users.query.filter(users.name == username).first()
            if the_user == None:
                flash('用户名不存在')
                return render_template('signin.html')
            if the_user.passwd == password:
                # 匹配成功,设置cookies登录时间,前端可以设个选项，这里就默认保存1天了
                the_id = str(the_user.id)
                the_time = str(datetime.datetime.now() + datetime.timedelta(days=1))
                _secret_key = my_sha1(the_id + password + the_time + the_secret_key)

                resp = make_response(redirect(url_for('note_nav')))
                resp.set_cookie('data', the_id + the_time + _secret_key)
                return resp
            else:
                # 匹配失败
                flash('密码错误')
                return render_template('signin.html')

        else:
            flash('用户名格式错误')
            return render_template('signin.html')


@app.route('/logic/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        username = request.form['username']
        email = request.form['email']
        passwd1 = request.form['password1']
        passwd2 = request.form['password2']
        print(username, email, passwd1, passwd2)
        for i in users.query.all():
            if i.name == username:
                flash('用户名\'%s\'已被注册' % username)
                return redirect(url_for('register'))
        # 不重名
        add_user = users(name=username, email=email, passwd=passwd1, create_time=datetime.datetime.now())
        db.session.add(add_user)
        db.session.commit()
        flash('注册成功')
        return redirect(url_for('signin'))


@app.route('/logic/add_comment/<int:note_id>', methods=['POST'])
def add_comment(note_id):
    return redirect(url_for('note', note_id=note_id))


"""验证cookies，是否已登录
未登录返回False
已登录返回True"""


def identify():
    cookies = request.cookies.get('data')
    if not cookies or cookies[0]=='0':
        return False
    time = cookies[1:27]
    if str(datetime.datetime.now()) > time:
        return False
    id = int(cookies[0])
    sh = cookies[27:]
    result = users.query.filter(users.id==id).first()
    calc_key = my_sha1(cookies[0]+result.passwd+time+the_secret_key)
    if sh == calc_key:
        return True
    else:
        return False


def my_sha1(str):
    a = sha1()
    a.update(str.encode('utf-8'))
    return a.hexdigest()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=12121, debug=True)
