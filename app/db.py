import click
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy のシングルトンインスタンス。
# このオブジェクトを models/ でインポートして db.Model を継承する。
# create_app() で db.init_app(app) を呼ぶことで Flask アプリに紐づく。
db = SQLAlchemy()


def init_db():
    """テーブルが存在しない場合のみ全テーブルを作成する。

    SQLAlchemy は db.Model を継承したクラスの Column 定義から
    CREATE TABLE 文を自動生成する（スキーマを Python コードで宣言的に管理できる）。
    """
    db.create_all()


@click.command("init-db")
def init_db_command():
    """CLI コマンド: flask init-db でスキーマを初期化する。"""
    init_db()
    click.echo("Database initialized.")


def init_app(app):
    """Flask アプリに SQLAlchemy を紐づけ、CLI コマンドを登録する。

    db.init_app(app) は「このアプリを使うときは app.config の
    SQLALCHEMY_DATABASE_URI に接続せよ」と SQLAlchemy に伝える処理。
    接続のライフサイクル管理（リクエスト終了時のクローズ等）は
    Flask-SQLAlchemy が自動で行うため、teardown_appcontext の手動登録は不要になる。
    """
    db.init_app(app)
    app.cli.add_command(init_db_command)
