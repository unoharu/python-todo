from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash

from app.models.user import User


class EmailAlreadyExistsError(Exception):
    """メールアドレスが既に登録済みの場合に送出する例外。"""


class InvalidCredentialsError(Exception):
    """メールアドレスまたはパスワードが一致しない場合に送出する例外。"""


def register_user(username: str, email: str, password: str) -> User:
    """新規ユーザーを登録してUse返す。

    処理内容:
    1. 入力値の基本バリデーション（空文字チェックはルート層で行う）
    2. メールアドレスの重複チェック
    3. パスワードを Werkzeug でハッシュ化（pbkdf2:sha256 + ソルト自動付与）
    4. DB に保存

    Args:
        username: ユーザー名
        email: メールアドレス（UNIQUE制約）
        password: 平文パスワード

    Returns:
        作成した User オブジェクト

    Raises:
        EmailAlreadyExistsError: メールアドレスが既に存在する場合
    """
    if User.find_by_email(email) is not None:
        raise EmailAlreadyExistsError(f"Email '{email}' is already registered")

    # generate_password_hash は「pbkdf2:sha256$<ソルト>$<ハッシュ>」形式の文字列を返す
    # ソルトは呼び出すたびにランダム生成されるため、同じパスワードでも毎回異なる値になる
    # method を明示: Python 3.9 の macOS システム Python は scrypt を未サポートのため pbkdf2:sha256 を使用
    hashed = generate_password_hash(password, method="pbkdf2:sha256")
    return User.create(username, email, hashed)


def authenticate_user(email: str, password: str) -> User:
    """メールアドレスとパスワードでユーザーを認証し、Userを返す。

    check_password_hash は DB に保存されたハッシュ文字列からソルトを自動で取り出し、
    平文パスワードと照合する。タイミング攻撃を防ぐため比較は定数時間で行われる。

    Raises:
        InvalidCredentialsError: メールアドレスが存在しない、またはパスワードが違う場合
    """
    user: Optional[User] = User.find_by_email(email)

    # ユーザーが存在しない場合でもハッシュ検証を行う
    # （ユーザーの存在有無をレスポンス時間から推測されないようにするため）
    dummy_hash = generate_password_hash("dummy", method="pbkdf2:sha256")
    stored_hash = user.password_hash if user else dummy_hash

    if not check_password_hash(stored_hash, password) or user is None:
        raise InvalidCredentialsError("Invalid email or password")

    return user
