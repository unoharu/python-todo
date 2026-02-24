# このファイルを import するだけで User・DiaryEntry が SQLAlchemy に登録される。
# db.create_all() はここで import されたモデルクラスを元にテーブルを生成する。
from app.models.user import User
from app.models.diary import DiaryEntry

__all__ = ["User", "DiaryEntry"]
