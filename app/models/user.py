from typing import Optional, List
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import db


class User(db.Model):
    """users テーブルの ORM モデル。

    ## ORM とは
    ORM（Object-Relational Mapper）は DB のテーブル行を Python オブジェクトとして
    扱う仕組み。SQL 文字列の代わりに Python のメソッド呼び出しで CRUD を行う。

    ## db.Model 継承
    Flask-SQLAlchemy が提供する基底クラス。継承するだけでテーブルと紐づく。
    クラス名（User）が自動的にテーブル名（users）にスネークケース変換される。

    ## Mapped / mapped_column（SQLAlchemy 2.0 スタイル）
    `Mapped[型]` で型ヒントを付けながらカラムを宣言する新しい書き方。
    `mapped_column()` はカラムの制約（PRIMARY KEY・UNIQUE・nullable など）を指定する。
    """

    __tablename__ = "users"

    # primary_key=True で AUTOINCREMENT な主キーになる。
    # SQLAlchemy が INSERT 後に DB 生成の id を自動でオブジェクトに反映する。
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)

    # server_default: INSERT 時に DB 側でデフォルト値を設定する。
    # Python 側での指定は不要で、commit 後に DB から値が反映される。
    created_at: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="(datetime('now', 'localtime'))",
    )

    # relationship: 外部キーを介した関連オブジェクトへのアクセスを定義する。
    # cascade="all, delete-orphan" = User を削除したら紐づく DiaryEntry も削除する。
    # back_populates で双方向の関連を張り、DiaryEntry.user からも User に辿れる。
    # lazy="select" = relationship に最初にアクセスした時点で SELECT を発行する（遅延ロード）。
    diaries: Mapped[List["DiaryEntry"]] = relationship(  # type: ignore[name-defined]
        "DiaryEntry",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )

    # ---- クラスメソッド（ファクトリ） ----------------------------------------

    @classmethod
    def find_by_email(cls, email: str) -> Optional["User"]:
        """メールアドレスでユーザーを検索する。存在しなければ None を返す。

        ## db.session.scalar()
        クエリを実行して最初の1件を返す。0件なら None。
        SQLAlchemy 2.0 では `db.select(Model).where(...)` で SELECT 文を構築し、
        `db.session.scalar()` / `scalars()` で実行するスタイルが推奨されている。
        """
        return db.session.scalar(
            db.select(cls).where(cls.email == email)
        )

    @classmethod
    def find_by_id(cls, user_id: int) -> Optional["User"]:
        """ID でユーザーを検索する。存在しなければ None を返す。

        ## db.session.get()
        PRIMARY KEY による検索に特化したメソッド。
        同一セッション内でキャッシュ（identity map）が効くため、
        同じ ID を2回 get() しても SQL は1度しか発行されない。
        """
        return db.session.get(cls, user_id)

    @classmethod
    def create(cls, username: str, email: str, password_hash: str) -> "User":
        """新しいユーザーを DB に保存して返す。

        ## db.session の add / commit
        - `db.session.add(obj)`: オブジェクトをセッションに「追跡対象」として登録する。
          この時点では DB にはまだ書き込まれない。
        - `db.session.commit()`: セッション内の変更をまとめて DB に書き込む（トランザクション確定）。
          commit 後、SQLAlchemy は DB が生成した id や server_default 値を自動でオブジェクトに反映する。
        """
        user = cls(username=username, email=email, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def delete(cls, user_id: int) -> None:
        """ユーザーを削除する。cascade により日記も自動削除される。

        ## db.session.delete()
        オブジェクトを「削除予定」としてセッションに登録し、commit でDELETE を発行する。
        relationship に cascade="all, delete-orphan" を設定しているため、
        SQLAlchemy が DiaryEntry の DELETE を自動で先に実行する。
        """
        user = db.session.get(cls, user_id)
        if user is not None:
            db.session.delete(user)
            db.session.commit()
