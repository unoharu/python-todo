import pytest
from app import create_app
from app.db import db, init_db


@pytest.fixture
def app():
    """テスト用の Flask アプリインスタンスを生成する。

    create_app("testing") を呼ぶことで:
    - TESTING = True（例外がハンドラーに吸収されず、そのまま伝播する）
    - SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
      （テストごとに独立したインメモリ DB を使用）

    ## ORM でのテスト初期化の流れ
    1. `db.create_all()` でモデルクラスから CREATE TABLE を自動発行
    2. テスト実行（yield）
    3. `db.drop_all()` で全テーブルを削除し、次のテストに影響しないようにする

    drop_all + create_all をテストごとに行うことで、
    各テストが完全に独立したスキーマを持つことを保証する。
    """
    app = create_app("testing")
    with app.app_context():
        init_db()   # db.create_all() を呼ぶ
        yield app
        db.drop_all()  # テスト後にテーブルを削除してクリーンな状態に戻す


@pytest.fixture
def client(app):
    """Flask のテストクライアントを返す。"""
    return app.test_client()


@pytest.fixture
def registered_user(client):
    """テスト用ユーザーを登録してログイン済みのクライアントを返す。"""
    client.post("/register", data={
        "email": "test@example.com",
        "password": "testpass123",
        "username": "testuser",
    })
    return client
