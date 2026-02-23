import sqlite3
import os
import click
from flask import current_app, g


def get_db():
    """現在のリクエストに紐づいた DB 接続を返す。

    Flask の g オブジェクトに接続をキャッシュすることで、
    1リクエスト内で get_db() を複数回呼んでも接続は1本のみになる。
    """
    if "db" not in g:
        db_path = current_app.config["DATABASE"]

        # テスト用のインメモリ DB でなければ、ディレクトリを作成する
        if db_path != ":memory:":
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

        g.db = sqlite3.connect(db_path)

        # カラム名でアクセスできるように Row ファクトリを設定する
        # 例: row["email"] のようにアクセスできる
        g.db.row_factory = sqlite3.Row

        # 外部キー制約を有効化（SQLite はデフォルトで無効）
        g.db.execute("PRAGMA foreign_keys = ON")

        # WAL モード: 読み取りと書き込みを並行して行えるようにする
        g.db.execute("PRAGMA journal_mode = WAL")

    return g.db


def close_db(e=None):
    """リクエスト終了時に DB 接続を閉じる。

    Flask の teardown_appcontext に登録することで、
    リクエストの完了（正常・エラー問わず）に自動で呼ばれる。
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """データベーススキーマを初期化（テーブルが存在しない場合のみ作成）する。"""
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            username     TEXT    NOT NULL,
            email        TEXT    NOT NULL UNIQUE,
            password_hash TEXT   NOT NULL,
            created_at   TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
        );

        CREATE TABLE IF NOT EXISTS diaries (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            title      TEXT    NOT NULL,
            comment    TEXT    NOT NULL,
            created_at TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_diaries_user_id    ON diaries(user_id);
        CREATE INDEX IF NOT EXISTS idx_diaries_created_at ON diaries(created_at);
    """)
    db.commit()


@click.command("init-db")
def init_db_command():
    """CLI コマンド: flask init-db でスキーマを初期化する。"""
    init_db()
    click.echo("Database initialized.")


def init_app(app):
    """Flask アプリに DB 関連のフックを登録する。

    create_app() から呼ばれることを前提としている。
    """
    # リクエスト終了時に close_db が自動で呼ばれるよう登録
    app.teardown_appcontext(close_db)

    # `flask init-db` コマンドを CLI に追加
    app.cli.add_command(init_db_command)
