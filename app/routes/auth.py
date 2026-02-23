from flask import Blueprint, render_template, redirect, request, session, flash

from app.db import init_db
from app.services.auth_service import (
    register_user,
    authenticate_user,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
)

# Blueprint: URL のプレフィックスなし（認証系は / 直下のまま）
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    """トップページ。ログイン状態に応じてナビゲーションを切り替える。"""
    logged_in = "user_id" in session
    return render_template(
        "index.html",
        show_signin_signup=not logged_in,
        show_dashboard_signout=logged_in,
    )


@auth_bp.route("/signin")
def signin():
    """ログインフォームを表示する。既にログイン済みならダッシュボードへ。"""
    if "user_id" in session:
        return redirect("/dashboard")
    return render_template("signin.html")


@auth_bp.route("/signup")
def signup():
    """ユーザー登録フォームを表示する。既にログイン済みならダッシュボードへ。"""
    if "user_id" in session:
        return redirect("/dashboard")
    return render_template("signup.html")


@auth_bp.route("/signout")
def signout():
    """セッションをクリアしてトップページへリダイレクトする。"""
    session.clear()
    return redirect("/")


@auth_bp.route("/auth", methods=["POST"])
def auth():
    """ログイン処理。

    フォームから email・password を受け取り、認証に成功したら
    セッションに user_id のみを保存する（タプル丸ごとは保存しない）。
    """
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email or not password:
        flash("メールアドレスとパスワードは必須です。")
        return redirect("/signin")

    try:
        user = authenticate_user(email, password)
    except InvalidCredentialsError:
        flash("メールアドレスまたはパスワードが正しくありません。")
        return redirect("/signin")

    # セッションには user_id のみ保存する
    # （ユーザー情報が必要な場合は都度 DB から取得する）
    session["user_id"] = user.id
    return redirect("/dashboard")


@auth_bp.route("/register", methods=["POST"])
def register():
    """ユーザー登録処理。

    登録成功後はそのままログイン状態にしてダッシュボードへ遷移する。
    """
    if "user_id" in session:
        return redirect("/dashboard")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    username = request.form.get("username", "").strip()

    if not email or not password or not username:
        flash("すべてのフィールドを入力してください。")
        return redirect("/signup")

    # パスワードの最低長チェック
    if len(password) < 8:
        flash("パスワードは8文字以上で入力してください。")
        return redirect("/signup")

    try:
        # DB が未初期化の場合（初回起動時）に備えて init_db を呼ぶ
        init_db()
        user = register_user(username, email, password)
    except EmailAlreadyExistsError:
        flash("このメールアドレスは既に登録されています。")
        return redirect("/signup")

    session["user_id"] = user.id
    return redirect("/dashboard")
