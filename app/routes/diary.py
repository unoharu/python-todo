from flask import Blueprint, render_template, request, session, jsonify

from app.auth import login_required
from app.models.user import User
from app.services.diary_service import (
    get_user_diaries,
    create_diary_entry,
    delete_diary_entry,
    update_diary_entry,
    ValidationError,
    NotFoundOrForbiddenError,
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


@diary_bp.route("/diary/<int:diary_id>/delete", methods=["POST"])
@login_required
def delete_diary(diary_id: int):
    """日記を削除する（AJAX エンドポイント）。

    自分の日記のみ削除可能。他人の日記または存在しない ID は 403 を返す。

    ## なぜ GET ではなく POST か
    GET リクエストはブラウザがキャッシュ・プリフェッチすることがある。
    削除のような副作用を伴う操作は必ず POST（または DELETE）にする。
    """
    try:
        delete_diary_entry(diary_id, session["user_id"])
    except NotFoundOrForbiddenError:
        return jsonify({"error": "削除できませんでした。"}), 403

    return jsonify({"success": "削除しました。"})


@diary_bp.route("/diary/<int:diary_id>/update", methods=["POST"])
@login_required
def update_diary(diary_id: int):
    """日記を更新する（AJAX エンドポイント）。

    自分の日記のみ更新可能。バリデーションエラーは 400、権限エラーは 403 を返す。
    """
    title = request.form.get("title", "")
    comment = request.form.get("comment", "")

    try:
        update_diary_entry(diary_id, session["user_id"], title, comment)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except NotFoundOrForbiddenError:
        return jsonify({"error": "更新できませんでした。"}), 403

    return jsonify({"success": "更新しました。"})
