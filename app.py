from flask import Flask, render_template

# ==================================================
# インスタンス生成
# ==================================================
app = Flask(__name__)

# ==================================================
# プロフィール情報
# ==================================================

profiles = [
    {
        'id': '1',
        'name': '琉球 太郎',
        'age': 20,
        'hobby': '野球',
        'image_url': 'https://ie.u-ryukyu.ac.jp/~shiroma/p/1.jpg'
    },
    {
        'id': '2',
        'name': '沖縄 花子',
        'age': 28,
        'hobby': '読書',
        'image_url': 'https://ie.u-ryukyu.ac.jp/~shiroma/p/2.jpg'
    },
    {
        'id': '3',
        'name': '山田 次郎',
        'age': 21,
        'hobby': 'ゲーム',
        'image_url': 'https://ie.u-ryukyu.ac.jp/~shiroma/p/3.jpg'
    },
    {
        'id': '4',
        'name': 'ジョン 三郎',
        'age': 32,
        'hobby': 'スポーツ',
        'image_url': 'https://ie.u-ryukyu.ac.jp/~shiroma/p/4.jpg'
    },
    {
        'id': '5',
        'name': '知能 四郎',
        'age': 25,
        'hobby': '料理',
        'image_url': 'https://ie.u-ryukyu.ac.jp/~shiroma/p/5.jpg'
    },
]


# ==================================================
# ルーティング
# ==================================================
# TOPページ
@app.route('/') 
def show_for_list():
    return render_template('for_list.html', items = profiles)

# 詳細
@app.route('/detail/<int:id>')
def show_detail(id):
    if id < 1 or id > len(profiles):
        return '存在しないIDです'
    return render_template('detail.html', item = profiles[id-1])

# ==================================================
# 実行
# ==================================================
if __name__ == '__main__':
    app.run()