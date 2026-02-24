from typing import List
from app.models.diary import DiaryEntry


# バリデーション定数
TITLE_MAX_LENGTH = 100
COMMENT_MAX_LENGTH = 10000


class ValidationError(Exception):
    """入力値バリデーション失敗時に送出する例外。"""


def get_user_diaries(user_id: int) -> List[dict]:
    """ユーザーの日記一覧を辞書のリストで返す（新しい順）。

    JSON レスポンス用に to_dict() で変換している。
    """
    return [entry.to_dict() for entry in DiaryEntry.list_by_user(user_id)]


def create_diary_entry(user_id: int, title: str, comment: str) -> DiaryEntry:
    """日記エントリを作成して返す。

    バリデーション:
    - title・comment が空でないこと
    - 各フィールドが最大長を超えないこと

    Args:
        user_id: 所有者のユーザーID
        title: 日記タイトル（最大 TITLE_MAX_LENGTH 文字）
        comment: 日記本文（最大 COMMENT_MAX_LENGTH 文字）

    Returns:
        作成した DiaryEntry

    Raises:
        ValidationError: バリデーション失敗時
    """
    title = title.strip()
    comment = comment.strip()

    if not title:
        raise ValidationError("タイトルは必須です。")
    if not comment:
        raise ValidationError("本文は必須です。")
    if len(title) > TITLE_MAX_LENGTH:
        raise ValidationError(f"タイトルは {TITLE_MAX_LENGTH} 文字以内で入力してください。")
    if len(comment) > COMMENT_MAX_LENGTH:
        raise ValidationError(f"本文は {COMMENT_MAX_LENGTH} 文字以内で入力してください。")

    return DiaryEntry.create(user_id, title, comment)
