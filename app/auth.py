from functools import wraps
from flask import session, redirect, jsonify, request


def login_required(f):
    """ログイン済みでなければリダイレクト（または JSON エラー）を返すデコレータ。

    @login_required を付けたルートは、セッションに user_id が存在しない場合に
    ブラウザリクエストは /signin へリダイレクト、AJAX リクエストは JSON エラーを返す。

    使い方:
        @app.route("/dashboard")
        @login_required
        def dashboard():
            ...

    functools.wraps(f) を使う理由:
        デコレータはラッパー関数で元の関数を包む。wraps を付けないと
        Flask がルート名の重複を誤検知してしまう（__name__ が上書きされるため）。
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("user_id") is None:
            # AJAX リクエスト（JSON を期待している場合）は JSON で返す
            if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
                return jsonify({"error": "ログインしていません。"}), 401
            return redirect("/signin")
        return f(*args, **kwargs)
    return wrapper
