from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # よりセキュアなランダムなシークレットキーを生成
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    friends = db.relationship('Friend', backref='user', lazy=True)


class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    contact = db.Column(db.String(120))
    date_met = db.Column(db.String(80))
    note = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('このユーザー名はすでに使用されています。', 'danger')
            return redirect(url_for('signup'))
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('アカウントが作成されました。ログインしてください。', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('ログインしました。', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('ログインに失敗しました。ユーザー名またはパスワードを確認してください。', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('ログアウトしました。', 'success')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    friends = Friend.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', friends=friends)


@app.route('/add_friend', methods=['GET', 'POST'])
@login_required
def add_friend():
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        date_met = request.form['date_met']
        note = request.form['note']
        new_friend = Friend(name=name, contact=contact, date_met=date_met, note=note, user_id=current_user.id)
        db.session.add(new_friend)
        db.session.commit()
        flash('知り合いが追加されました。', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_friend.html')


@app.route('/edit_friend/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_friend(id):
    friend = Friend.query.get_or_404(id)
    if friend.user_id != current_user.id:
        flash('この操作は許可されていません。', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        friend.name = request.form['name']
        friend.contact = request.form['contact']
        friend.date_met = request.form['date_met']
        friend.note = request.form['note']
        db.session.commit()
        flash('知り合い情報が更新されました。', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_friend.html', friend=friend)


@app.route('/delete_friend/<int:id>', methods=['POST'])
@login_required
def delete_friend(id):
    friend = Friend.query.get_or_404(id)
    if friend.user_id != current_user.id:
        flash('この操作は許可されていません。', 'danger')
        return redirect(url_for('dashboard'))
    db.session.delete(friend)
    db.session.commit()
    flash('知り合いが削除されました。', 'success')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # データベースのテーブルを作成
    app.run(debug=True)

