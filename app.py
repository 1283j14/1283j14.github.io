from flask import Flask, jsonify, render_template, request
from aozora import AozoraLoader  # aozora.pyからAozoraLoaderクラスをインポート
import random

# Flaskアプリケーションを初期化
# templatesフォルダとstaticフォルダを自動的に認識する設定
app = Flask(__name__, static_folder="static", template_folder="templates")

# 青空文庫ローダーのインスタンスを作成
# このインスタンスがテキストのダウンロードと整形を担当する
loader = AozoraLoader()

# ゲームで利用する作品のURLリストを辞書として定義
# キーはAPIで指定するための短い名前、値は実際のURL
BOOKS = {
    "wagahai": "https://www.aozora.gr.jp/cards/000148/files/789_ruby_5639.zip",
    "rashomon": "https://www.aozora.gr.jp/cards/000879/files/127_ruby_150.zip",
    "kokoro": "https://www.aozora.gr.jp/cards/000148/files/773_ruby_5968.zip",
    "botchan": "https://www.aozora.gr.jp/cards/000148/files/752_ruby_2438.zip",
    "run_melos": "https://www.aozora.gr.jp/cards/000035/files/1567_ruby_4948.zip",
}

# --- ページのルーティング ---


@app.route("/")
def index():
    """
    トップページ（http://127.0.0.1:5000/）にアクセスされたときに
    templates/index.html をブラウザに返す
    """
    return render_template("index.html")


@app.route("/game")
def game():
    """
    ゲームページ（http://127.0.0.1:5000/game）にアクセスされたときに
    templates/game.html をブラウザに返す
    """
    return render_template("game.html")


# --- APIのルーティング ---


@app.route("/api/text")
def get_text():
    """
    ゲーム用のテキストデータをJSON形式で返すAPIエンドポイント
    例: /api/text?book=wagahai
    """
    # クエリパラメータからどの本かを取得（指定がなければ'random'）
    book_key = request.args.get("book", "random")

    # 'random'が指定された場合は、BOOKSリストからランダムにキーを選ぶ
    if book_key == "random":
        book_key = random.choice(list(BOOKS.keys()))

    # 指定されたキーに対応するURLを取得
    url = BOOKS.get(book_key)

    # もし辞書にキーが存在しなければエラーを返す
    if not url:
        return jsonify({"error": f"Book with key '{book_key}' not found"}), 404

    # AozoraLoaderを使ってテキストをダウンロード＆整形
    text = loader.load(url)

    # テキストが取得できなかったり、短すぎたりした場合の保険
    if not text or len(text) < 100:
        text = "吾輩は猫である。名前はまだ無い。どこで生れたかとんと見当がつかぬ。何でも薄暗いじめじめした所でニャーニャー泣いていた事だけは記憶している。"

    # タイピングに適した長さに文章を切り出す (約100〜150文字)
    # まず「。」で文章を区切る
    sentences = text.split("。")
    result_text = ""
    for s in sentences:
        # 空の文は無視
        if s.strip():
            # 文を連結していき、目標の長さに達したら終了
            result_text += s + "。"
            if len(result_text) > 100:
                break

    # 最終的なテキストをJSONとして返す
    return jsonify({"text": result_text.strip()})


# --- サーバーの起動 ---

if __name__ == "__main__":
    # Flaskの開発用サーバーを起動
    # debug=Trueにすると、コードを変更した際に自動でサーバーが再起動する
    app.run(debug=True, port=5000)
