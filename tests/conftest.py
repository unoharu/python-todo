import pytest
from app import create_app
from app.db import init_db


@pytest.fixture
def app():
    """テスト用の Flask アプリインスタンスを生成する。

    create_app("testing") を呼ぶことで:
    - TESTING = True（例外がハンドラーに吸収されず、そのまま伝播する）
    - DATABASE = ":memory:"（テストごとに独立したインメモリ DB を使用）

    yield を使って fixture を定義すると、yield より前がセットアップ、
    後ろがティアダウン（テスト終了後の後片付け）になる。
    """
    app = create_app("testing")
    with app.app_context():
        init_db()
        yield app
    # app_context を抜けると DB 接続が自動で閉じられる（teardown_appcontext）


@pytest.fixture
def client(app):
    """Flask のテストクライアントを返す。

    test_client() はブラウザを模倣するオブジェクトで、
    HTTP リクエストを実際にサーバーを起動せずに送信できる。
    """
    return app.test_client()


@pytest.fixture
def registered_user(client):
    """テスト用ユーザーを登録してログイン済みのクライアントを返す。

    複数のテストで「ログイン済み状態」が必要な場合に再利用できる。
    """
    client.post("/register", data={
        "email": "test@example.com",
        "password": "testpass123",
        "username": "testuser",
    })
    return client
