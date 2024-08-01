import os
from flask import session
from sqlalchemy.exc import IntegrityError
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

# ==================================================
# インスタンス生成
# ==================================================
app = Flask(__name__)

# ==================================================
# Flaskに対する設定
# ==================================================
import os
# 乱数を設定
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SECRET_KEY'] = os.urandom(24)
base_dir = os.path.dirname(__file__)
database = 'sqlite:///' + os.path.join(base_dir, 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager()
login_manager.init_app(app)

# ★db変数を使用してSQLAlchemyを操作できる
db = SQLAlchemy(app)
# ★「flask_migrate」を使用できる様にする
Migrate(app, db)

#==================================================
# モデル
#==================================================
# 課題
class Users(UserMixin,db.Model):
    # テーブル名
    __tablename__ = 'users' #user
    
    # ユーザID
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True) #user_id = db.Columu(db.Integer)
    # ユーザ名
    user_name = db.Column(db.String(20), nullable=False, unique=True)
    #パスワード
    password = db.Column(db.String(20), nullable=False)
    #知り合いIDをまとめたlist
    friend_id_list = db.Column(db.JSON)
    # 完了フラグ
    friend_id = db.Column(db.Integer)   
    # ログインフラグ
    is_active = db.Column(db.Boolean, default=False, nullable=False) 

    
class Friends(db.Model):
    # テーブル名
    __tablename__ = 'friends' #user
    
    # ユーザID
    friend_id = db.Column(db.Integer, primary_key=True, autoincrement=True) #user_id = db.Columu(db.Integer)
    # ユーザ名
    friend_name = db.Column(db.String(20), nullable=False)
    #知り合いの時間割
    timetable = db.Column(db.JSON)
    #知り合いと出会った時期
    timing = db.Column(db.DATE)
    # 知り合い連絡先
    contact = db.Column(db.String(255))   
    # その他の備考欄
    other = db.Column(db.String(255)) 
    
# ==================================================
# ルーティング
# ==================================================
# index.htmlを表示する
@app.route('/')
def top():
    return render_template('index.html')

# ログイン後にuser.htmlに情報を渡しながら表示
@app.route('/user')
def index():
    userid = session.get('user_id')
    user = Users.query.filter_by(user_id=userid).first()
    
    return render_template('user.html', user=user)

# ログイン機能
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))
        
# アカウント登録、登録後すぐにuser.htmlに移動できないのでもう一度ログイン必須
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        try:
            username = request.form.get('name')
            password = request.form.get('pass')
            # Userのインスタンスを作成
            users = Users(user_name=username, password=generate_password_hash(password))
            db.session.add(users)
            db.session.commit()
            return render_template('index.html')#login
        except IntegrityError:
            db.session.rollback()
            return "そのユーザ名はすでに使われています。別のユーザ名にしてください。"
    else:
        return render_template('index.html')#signup.html

# ログインの時にユーザ名とパスワードがあっているか確認
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get('name')
        password = request.form.get('pass')
        # Userテーブルからusernameに一致するユーザを取得
        user = Users.query.filter_by(user_name=username).first()
        if user is not None:
            if check_password_hash(user.password, password):
                login_user(user)
                session['user_id'] = user.user_id
                return redirect(url_for('index', user_id=user.user_id))
            else:
                return 'ユーザ名かパスワードが違います', 401
        else:
            return 'ユーザ名かパスワードが違います'
    else:
        return render_template('index.html')#login.html
    
#　ログアウト機能、今のところ使えない
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('login')

#アカウント削除
@app.route('/delete', methods=['POST'])
def delete_user():
    # 対象データ取得
    user_id = request.form.get('user_id')
    user_inf = Users.query.get(user_id)
    db.session.delete(user_inf)
    db.session.commit()
    return render_template('index.html')

#アカウント名の更新、パスワードは変えれない
@app.route('/update', methods=['GET', 'POST'])
def update_username():
    user_id = session.get('user_id')
    user_inf = Users.query.get(user_id)
    # POST
    if request.method == 'POST':
        # 更新するための処理を書くところ
        update_name = request.form['name']
        user_inf.user_name = update_name
        db.session.commit()
        return redirect(url_for('index'))
    # GET
    return render_template('update-user.html', user=user_inf)

# ==================================================
# 実行
# ==================================================
if __name__ == '__main__':
    app.run(port=5656)