from flask import Flask, render_template, redirect, request, session, jsonify, flash
import mysql.connector
import hashlib
import os
import json
from datetime import datetime


app = Flask(__name__)
app.secret_key = "your_secret_key"
app.json.ensure_ascii = False


def database_connection():
    return mysql.connector.connect(
        user='root',
        password='root',
        host='localhost',
        database='py',
        port=8889
    )


@app.route("/")
def index():
    if session.get("login", False):
        return render_template("index.html", show_signin_signup=False, show_dashboard_signout=True)
    return render_template("index.html", show_signin_signup=True, show_dashboard_signout=False)

@app.route("/signin")
def signin():
    if session.get("login", False):
        return redirect("/dashboard")
    return render_template("signin.html")


@app.route("/signup")
def signup():
    if session.get("login", False):
        return redirect("/dashboard")
    return render_template("signup.html")


@app.route("/signout")
def signout():
    session.pop("login", None)
    return redirect("/")

@app.route("/auth", methods=["POST"])
def auth():
    email = request.form.get("email")
    password = request.form.get("password")
 
    if email is None or password is None:
        flash("Emailとパスワードは必須項目です。")
        return redirect("/signin")
 
    password_hash = hashlib.sha256(password.encode()).hexdigest()
 
    try:
        cnx = database_connection()
        if cnx.is_connected:
            cur = cnx.cursor()
            cur.execute(
                "SELECT * FROM users WHERE email = %s",
                (email,)
            )

            user = cur.fetchone()
            if user and user[2] == password_hash:
                session["login"] = True
                session["user"] = user
                cnx.close()
                return redirect("/dashboard")
            else:
                flash("正しいメールアドレスとパスワードを入力してください。")
                return redirect("/signin")
    except Exception as e:
        print(e)
        flash("ログイン時にエラーが発生しました。")
        return redirect("/signin")

    flash("ログイン時に予期せぬエラーが発生しました。")
    return redirect("/signin")

@app.route("/register", methods=["POST"])
def register():
    if not session.get("login", False):
        email = request.form.get("email")
        password = request.form.get("password")
        username = request.form.get("username")

        if not email or not password or not username:
            flash("すべてのフィールドを入力してください。")
            return redirect("/signup")

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        try:
            cnx = database_connection()
            cur = cnx.cursor()
            cur.execute("INSERT INTO users (email, password, username) VALUES (%s, %s, %s)", (email, password_hash, username,))
            cnx.commit()
            cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password_hash))
            user = cur.fetchone()
            cnx.close()

            if user:
                session["login"] = True
                session["user"] = user
                return redirect("/dashboard")
            else:
                flash("ユーザー登録に失敗しました。")
                return redirect("/signup")
        except Exception as e:
            print(e)
            flash("ユーザー登録時にエラーが発生しました。")
            return redirect("/signup")



@app.route("/dashboard")
def dashboard():
    if session.get("login", False):
        return render_template("dashboard.html")
    return redirect("/signin")


def get_user_diary_path(user_id):
    diary_filename = f"user_{user_id}_diary.json"
    diary_folder = "all_users_diaries"
    
    # フォルダが存在しない場合は作成
    if not os.path.exists(diary_folder):
        os.makedirs(diary_folder)

    return os.path.join(diary_folder, diary_filename)

@app.route("/get_json")
def get_json():
    if session.get("login", False):
        try:
            user = session.get("user")
            user_id = user[0] if user else None

            if user_id is not None:
                diary_path = get_user_diary_path(user_id)

                # ユーザーの日記ファイルが存在するか確認
                if os.path.exists(diary_path):
                    with open(diary_path, 'r') as file:
                        diaries = json.load(file)
                else:
                    diaries = []

                return jsonify({"diaries": diaries})

            return jsonify({"error": "ユーザー情報が見つかりません。"})

        except Exception as e:
            print(e)
            return jsonify({"error": "日記の取得に失敗しました。"})

    return jsonify({"error": "ログインしていません。"})

@app.route("/create_diary", methods=["POST"])
def create_diary():
    if session.get("login", False):
        try:
            user = session.get("user")
            user_id = user[0] if user else None

            if user_id is not None:
                diary_path = get_user_diary_path(user_id)

                # リクエストから日記のタイトルとコメントを取得
                title = request.form.get("title")
                comment = request.form.get("comment")

                if title is None or comment is None:
                    return jsonify({"error": "タイトルとコメントは必須です。"})

                # 日記に追記する処理
                diary_entry = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "title": title,
                    "comment": comment
                }

                # ユーザーの日記ファイルが存在するか確認
                if os.path.exists(diary_path):
                    with open(diary_path, 'r') as file:
                        diaries = json.load(file)
                else:
                    diaries = []

                diaries.append(diary_entry)

                # 日記をファイルに保存
                with open(diary_path, 'w') as file:
                    json.dump(diaries, file, indent=2)

                return jsonify({"success": "日記が作成されました。"})

            return jsonify({"error": "ユーザー情報が見つかりません。"})

        except Exception as e:
            print(e)
            return jsonify({"error": "日記の作成に失敗しました。"})

    return jsonify({"error": "ログインしていません。"})


@app.route("/user/delete", methods=["GET"])
def delete_user_page():
    if session.get("login", False):
        return render_template("delete_user.html")
    return redirect("/signin")


@app.route("/user/delete_confirm", methods=["POST"])
def delete_user():
    if session.get("login", False):
        try:
            cnx = database_connection()
            if cnx.is_connected:
                cur = cnx.cursor()

                # セッションからユーザー情報を取得
                user = session.get("user")

                # タプルからuser_idを抽出
                user_id = user[0] if user else None
                
                if user_id is not None:
                    # user_idで指定されたユーザーを削除
                    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
                    cnx.commit()
                    cnx.close()

                    # セッション変数をクリア
                    session.pop("login", None)
                    session.pop("user", None)

                    return redirect("/") 
                else:
                    return render_template("error.html", error_message="ユーザー情報が見つかりません。")
            
        except Exception as e:
            print(e)
            return render_template("error.html", error_message="ユーザーの削除に失敗しました。")
    return redirect("/signin")


if __name__ == "__main__":
    app.run(debug=True, host='localhost', port=8080)
