"""認証フロー（登録・ログイン・ログアウト）のテスト。"""
import pytest
from app.services.auth_service import (
    register_user,
    authenticate_user,
    EmailAlreadyExistsError,
    InvalidCredentialsError,
)
from app.models.user import User


class TestRegisterUser:
    def test_register_success(self, app):
        """正常なユーザー登録で User が返る。

        conftest の app fixture が app_context を維持しているため、
        ここでは with app.app_context() は不要（二重コンテキストにしない）。
        """
        user = register_user("alice", "alice@example.com", "password123")
        assert user.id is not None
        assert user.username == "alice"
        assert user.email == "alice@example.com"
        # パスワードは平文で保存されていない
        assert user.password_hash != "password123"
        assert user.password_hash.startswith("pbkdf2:sha256")

    def test_register_duplicate_email_raises(self, app):
        """同じメールアドレスで2回登録すると EmailAlreadyExistsError が発生する。"""
        register_user("alice", "alice@example.com", "password123")
        with pytest.raises(EmailAlreadyExistsError):
            register_user("alice2", "alice@example.com", "password456")


class TestAuthenticateUser:
    def test_authenticate_success(self, app):
        """正しい認証情報で User が返る。"""
        register_user("bob", "bob@example.com", "securepass")
        user = authenticate_user("bob@example.com", "securepass")
        assert user.email == "bob@example.com"

    def test_authenticate_wrong_password_raises(self, app):
        """パスワードが違うと InvalidCredentialsError が発生する。"""
        register_user("carol", "carol@example.com", "correctpass")
        with pytest.raises(InvalidCredentialsError):
            authenticate_user("carol@example.com", "wrongpass")

    def test_authenticate_unknown_email_raises(self, app):
        """存在しないメールアドレスで InvalidCredentialsError が発生する。"""
        with pytest.raises(InvalidCredentialsError):
            authenticate_user("nobody@example.com", "any")


class TestAuthRoutes:
    def test_signup_page(self, client):
        """GET /signup は 200 を返す。"""
        resp = client.get("/signup")
        assert resp.status_code == 200

    def test_signin_page(self, client):
        """GET /signin は 200 を返す。"""
        resp = client.get("/signin")
        assert resp.status_code == 200

    def test_register_redirects_to_dashboard(self, client):
        """POST /register 成功後に /dashboard へリダイレクトされる。"""
        resp = client.post("/register", data={
            "email": "new@example.com",
            "password": "password123",
            "username": "newuser",
        })
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/dashboard")

    def test_register_short_password_returns_error(self, client):
        """パスワードが8文字未満のとき /signup にリダイレクトされる。"""
        resp = client.post("/register", data={
            "email": "short@example.com",
            "password": "short",
            "username": "shortpw",
        })
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/signup")

    def test_register_missing_field_redirects_signup(self, client):
        """必須フィールドが欠けているとき /signup にリダイレクトされる。"""
        resp = client.post("/register", data={
            "email": "missing@example.com",
            "password": "password123",
            # username なし
        })
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/signup")

    def test_login_success_redirects_to_dashboard(self, registered_user):
        """POST /auth 成功後に /dashboard へリダイレクトされる。"""
        client = registered_user
        client.get("/signout")  # 一度ログアウトしてから再ログイン
        resp = client.post("/auth", data={
            "email": "test@example.com",
            "password": "testpass123",
        })
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/dashboard")

    def test_login_wrong_password_redirects_signin(self, registered_user):
        """パスワード違いで /signin にリダイレクトされる。"""
        client = registered_user
        client.get("/signout")
        resp = client.post("/auth", data={
            "email": "test@example.com",
            "password": "wrongpass",
        })
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/signin")

    def test_signout_clears_session(self, registered_user):
        """GET /signout 後はダッシュボードにアクセスできない。"""
        client = registered_user
        client.get("/signout")
        resp = client.get("/dashboard")
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/signin")
