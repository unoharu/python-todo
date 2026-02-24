from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import db

if TYPE_CHECKING:
    from app.models.user import User


class DiaryEntry(db.Model):
    """diaries テーブルの ORM モデル。

    ## ForeignKey（外部キー）
    `ForeignKey("users.id")` は「このカラムは users テーブルの id カラムを参照する」
    という DB レベルの制約。参照先が存在しない値を INSERT しようとするとエラーになる。

    ## relationship の back_populates
    User.diaries と DiaryEntry.user を双方向に紐づける。
    - `entry.user` → その日記を所有する User オブジェクトが取得できる
    - `user.diaries` → そのユーザーの全 DiaryEntry が取得できる
    SQLAlchemy はどちらかを変更したとき、もう一方を自動で同期する。
    """

    __tablename__ = "diaries"

    id: Mapped[int] = mapped_column(primary_key=True)

    # ForeignKey でリレーションの「所有権」を宣言する。
    # ondelete="CASCADE" は DB レベルで User 削除時に DiaryEntry も削除する指示。
    # SQLAlchemy の cascade と組み合わせることで二重に安全になる。
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="(datetime('now', 'localtime'))",
    )

    # User → DiaryEntry の逆方向リレーション
    user: Mapped["User"] = relationship("User", back_populates="diaries")

    # ---- クラスメソッド（ファクトリ） ----------------------------------------

    @classmethod
    def list_by_user(cls, user_id: int) -> List["DiaryEntry"]:
        """指定ユーザーの日記を新しい順で返す。

        ## db.select() + where() + order_by()
        SQLAlchemy の Select 構文。SQL の `SELECT * FROM diaries WHERE user_id=? ORDER BY ...`
        に相当する。文字列ではなく Python の式で書くため IDE の補完・型チェックが効く。

        ## .desc()
        カラムオブジェクトに `.desc()` を呼ぶと降順（DESC）になる。
        `cls.created_at.desc()` = `ORDER BY created_at DESC`

        ## db.session.scalars().all()
        `scalars()` は結果セットをモデルオブジェクトのイテレータに変換する。
        `all()` でリストとして取得する。
        """
        return db.session.scalars(
            db.select(cls)
            .where(cls.user_id == user_id)
            .order_by(cls.created_at.desc(), cls.id.desc())
        ).all()

    @classmethod
    def create(cls, user_id: int, title: str, comment: str) -> "DiaryEntry":
        """新しい日記エントリを保存して返す。

        commit 後、SQLAlchemy は DB が生成した id・created_at を自動でオブジェクトに反映する。
        """
        entry = cls(user_id=user_id, title=title, comment=comment)
        db.session.add(entry)
        db.session.commit()
        return entry

    def to_dict(self) -> dict:
        """JSON シリアライズのために辞書に変換する。

        ORM モデルは dataclass ではないため asdict() は使えない。
        代わりに明示的に辞書を組み立てる。
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "comment": self.comment,
            "created_at": self.created_at,
        }
