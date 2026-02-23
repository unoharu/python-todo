"""日記 CRUD のテスト。"""
import json
import pytest
from app.services.diary_service import (
    create_diary_entry,
    get_user_diaries,
    ValidationError,
    TITLE_MAX_LENGTH,
    COMMENT_MAX_LENGTH,
)
from app.services.auth_service import register_user


class TestDiaryService:
    def test_create_and_list(self, app):
        """日記を作成して一覧で取得できる。"""
        user = register_user("dave", "dave@example.com", "password123")
        entry = create_diary_entry(user.id, "My Title", "My content")
        assert entry.title == "My Title"
        assert entry.comment == "My content"
        assert entry.user_id == user.id

        diaries = get_user_diaries(user.id)
        assert len(diaries) == 1
        assert diaries[0]["title"] == "My Title"

    def test_list_ordered_newest_first(self, app):
        """一覧は新しい順（降順）で返される。"""
        user = register_user("eve", "eve@example.com", "password123")
        create_diary_entry(user.id, "First", "content")
        create_diary_entry(user.id, "Second", "content")
        diaries = get_user_diaries(user.id)
        assert diaries[0]["title"] == "Second"
        assert diaries[1]["title"] == "First"

    def test_empty_title_raises(self, app):
        """空のタイトルは ValidationError を発生させる。"""
        user = register_user("frank", "frank@example.com", "password123")
        with pytest.raises(ValidationError):
            create_diary_entry(user.id, "", "content")

    def test_empty_comment_raises(self, app):
        """空の本文は ValidationError を発生させる。"""
        user = register_user("grace", "grace@example.com", "password123")
        with pytest.raises(ValidationError):
            create_diary_entry(user.id, "title", "")

    def test_title_too_long_raises(self, app):
        """タイトルが最大長を超えると ValidationError を発生させる。"""
        user = register_user("hank", "hank@example.com", "password123")
        with pytest.raises(ValidationError):
            create_diary_entry(user.id, "a" * (TITLE_MAX_LENGTH + 1), "content")

    def test_whitespace_only_title_raises(self, app):
        """空白のみのタイトルは ValidationError を発生させる。"""
        user = register_user("iris", "iris@example.com", "password123")
        with pytest.raises(ValidationError):
            create_diary_entry(user.id, "   ", "content")

    def test_diaries_isolated_per_user(self, app):
        """ユーザーAの日記はユーザーBからは見えない。"""
        user_a = register_user("jack", "jack@example.com", "password123")
        user_b = register_user("kate", "kate@example.com", "password123")
        create_diary_entry(user_a.id, "Jack's diary", "content")
        diaries_b = get_user_diaries(user_b.id)
        assert len(diaries_b) == 0


class TestDiaryRoutes:
    def test_get_json_returns_empty_list(self, registered_user):
        """ログイン直後は空の日記一覧が返る。"""
        resp = registered_user.get("/get_json")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["diaries"] == []

    def test_create_diary_success(self, registered_user):
        """POST /create_diary で日記が作成される。"""
        resp = registered_user.post("/create_diary", data={
            "title": "Route Test",
            "comment": "Test content",
        })
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "success" in data

    def test_create_diary_empty_title_returns_400(self, registered_user):
        """空タイトルは 400 エラーを返す。"""
        resp = registered_user.post("/create_diary", data={
            "title": "",
            "comment": "content",
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert "error" in data

    def test_get_json_after_create(self, registered_user):
        """日記作成後に /get_json で取得できる。"""
        registered_user.post("/create_diary", data={
            "title": "Test Title",
            "comment": "Test Content",
        })
        resp = registered_user.get("/get_json")
        data = json.loads(resp.data)
        assert len(data["diaries"]) == 1
        assert data["diaries"][0]["title"] == "Test Title"

    def test_get_json_unauthenticated_redirects(self, client):
        """未ログイン時は /signin にリダイレクトされる。"""
        resp = client.get("/get_json")
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/signin")
