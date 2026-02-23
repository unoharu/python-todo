from dataclasses import dataclass, asdict
from typing import List
from app.db import get_db


@dataclass
class DiaryEntry:
    """diaries テーブルの1行を表すデータクラス。"""
    id: int
    user_id: int
    title: str
    comment: str
    created_at: str

    @classmethod
    def from_row(cls, row) -> "DiaryEntry":
        """sqlite3.Row から DiaryEntry インスタンスを生成する。"""
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            comment=row["comment"],
            created_at=row["created_at"],
        )

    def to_dict(self) -> dict:
        """JSON シリアライズのために辞書に変換する。

        dataclasses.asdict() を使うと全フィールドを辞書に変換できる。
        """
        return asdict(self)

    @staticmethod
    def list_by_user(user_id: int) -> List["DiaryEntry"]:
        """指定ユーザーの日記を作成日時の降順（新しい順）で返す。

        同一秒内に複数挿入された場合は id DESC を補助キーにして順序を保証する。
        """
        db = get_db()
        rows = db.execute(
            "SELECT * FROM diaries WHERE user_id = ? ORDER BY created_at DESC, id DESC",
            (user_id,)
        ).fetchall()
        return [DiaryEntry.from_row(row) for row in rows]

    @staticmethod
    def create(user_id: int, title: str, comment: str) -> "DiaryEntry":
        """新しい日記エントリを DB に挿入し、作成したエントリを返す。"""
        db = get_db()
        cursor = db.execute(
            "INSERT INTO diaries (user_id, title, comment) VALUES (?, ?, ?)",
            (user_id, title, comment),
        )
        db.commit()
        row = db.execute(
            "SELECT * FROM diaries WHERE id = ?",
            (cursor.lastrowid,)
        ).fetchone()
        if row is None:
            raise RuntimeError("Failed to retrieve created diary entry")
        return DiaryEntry.from_row(row)
