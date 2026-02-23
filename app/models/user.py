from dataclasses import dataclass
from typing import Optional
from app.db import get_db


@dataclass
class User:
    """users テーブルの1行を表すデータクラス。

    dataclass を使うと __init__・__repr__ が自動生成される。
    モデルは「データ構造 + DB アクセス」のみを担当する。
    """
    id: int
    username: str
    email: str
    password_hash: str
    created_at: str

    @classmethod
    def from_row(cls, row) -> "User":
        """sqlite3.Row オブジェクトから User インスタンスを生成する。

        sqlite3.Row はカラム名でアクセスできる辞書ライクなオブジェクト。
        """
        return cls(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            password_hash=row["password_hash"],
            created_at=row["created_at"],
        )

    @staticmethod
    def find_by_email(email: str) -> Optional["User"]:
        """メールアドレスでユーザーを検索する。存在しなければ None を返す。"""
        db = get_db()
        row = db.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        return User.from_row(row) if row else None

    @staticmethod
    def find_by_id(user_id: int) -> Optional["User"]:
        """ID でユーザーを検索する。存在しなければ None を返す。"""
        db = get_db()
        row = db.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        return User.from_row(row) if row else None

    @staticmethod
    def create(username: str, email: str, password_hash: str) -> "User":
        """新しいユーザーを DB に挿入し、作成した User を返す。

        INSERT 後に RETURNING 句または lastrowid で生成された ID を取得する。
        """
        db = get_db()
        cursor = db.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash),
        )
        db.commit()
        user = User.find_by_id(cursor.lastrowid)
        if user is None:
            raise RuntimeError("Failed to retrieve created user")
        return user

    @staticmethod
    def delete(user_id: int) -> None:
        """ユーザーを削除する。ON DELETE CASCADE で関連する日記も自動削除される。"""
        db = get_db()
        db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()
