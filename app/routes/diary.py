from flask import Blueprint, render_template, redirect, request, session, jsonify

from app.auth import login_required
from app.models.user import User
from app.services.diary_service import (
    get_user_diaries,
    create_diary_entry,
    ValidationError,
)

diary_bp = Blueprint("diary", __name__)


@diary_bp.route("/dashboard")
@login_required
def dashboard():
    """ダッシュボード画面を表示する。

    @login_required デコレータにより、未ログインの場合は /signin にリダイレクトされる。
    ユーザー名をテンプレートに渡すために DB からユーザー情報を取得する。
    """
    user = User.find_by_id(session["user_id"])
    username = user.username if user else "ゲスト"
    return render_template("dashboard.html", username=username)


@diary_bp.route("/get_json")
@login_required
def get_json():
    """ユーザーの日記一覧を JSON で返す（AJAX エンドポイント）。

    フロントエンドの JavaScript から fetch/$.ajax で呼ばれる。
    """
    user_id = session["user_id"]
    diaries = get_user_diaries(user_id)
    return jsonify({"diaries": diaries})


@diary_bp.route("/create_diary", methods=["POST"])
@login_required
def create_diary():
    """日記エントリを作成する（AJAX エンドポイント）。

    バリデーションエラーは JSON でクライアントに返す。
    """
    user_id = session["user_id"]
    title = request.form.get("title", "")
    comment = request.form.get("comment", "")

    try:
        create_diary_entry(user_id, title, comment)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"success": "日記が作成されました。"})


@diary_bp.route("/user/delete")
@login_required
def delete_user_page():
    """アカウント削除確認ページを表示する。"""
    return render_template("delete_user.html")


@diary_bp.route("/user/delete_confirm", methods=["POST"])
@login_required
def delete_user():
    """アカウントを削除する。

    ON DELETE CASCADE により diaries テーブルの関連データも自動削除される。
    削除後はセッションをクリアしてトップページへリダイレクトする。
    """
    user_id = session["user_id"]
    User.delete(user_id)
    session.clear()
    return redirect("/")
