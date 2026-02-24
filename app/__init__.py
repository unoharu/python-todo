import os
from typing import Optional
from flask import Flask
from dotenv import load_dotenv

from app.config import config
from app.db import db, init_app as db_init_app


def create_app(config_name: Optional[str] = None) -> Flask:
    """アプリケーションファクトリ。

    テスト時は create_app("testing") のように設定名を渡すことで
    インメモリ DB を使った独立した Flask インスタンスを生成できる。

    Args:
        config_name: "development" / "testing" / "production" のいずれか。
                     None の場合は FLASK_ENV 環境変数を参照し、
                     それもなければ "development" を使用する。
    """
    load_dotenv()  # .env ファイルを環境変数に読み込む

    app = Flask(
        __name__,
        # templates と static を app/ の外（プロジェクトルート直下）に置く
        template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"),
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"),
    )

    # 設定の適用
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")
    app.config.from_object(config[config_name])

    # JSON レスポンスで日本語を文字化けさせない
    app.json.ensure_ascii = False

    # SQLAlchemy を Flask アプリに紐づけ、CLI コマンドを登録する
    db_init_app(app)

    # モデルモジュールを import することで db.create_all() がテーブルを認識できる。
    # ローカル変数 app（Flask インスタンス）と名前が衝突しないよう from 形式で書く。
    # _models に束ねることで「副作用目的の import」であることを明示し、
    # IDE の「未参照」ヒントも抑制する。
    from app import models as _models
    _ = _models

    from app.routes.auth import auth_bp
    from app.routes.diary import diary_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(diary_bp)

    return app
