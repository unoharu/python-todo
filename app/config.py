import os

_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
_DB_PATH = os.path.join(_BASE_DIR, "instance", "diary.db")


class Config:
    """全環境共通の設定基底クラス。"""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-fallback-key-change-in-production")

    # SQLAlchemy が接続先を判断するための URI。
    # SQLite の場合は "sqlite:///絶対パス" の形式になる（スラッシュが3つ）。
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{_DB_PATH}"

    # SQLAlchemy がモデルの変更を追跡する機能（不要なためオフ）。
    # True にするとメモリを余分に使うので、明示的に False を設定しておく。
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """開発環境の設定。デバッグモードを有効にする。"""
    DEBUG = True


class TestingConfig(Config):
    """テスト環境の設定。インメモリ DB を使用する。"""
    TESTING = True
    # テスト用インメモリ DB の URI。
    # "sqlite:///:memory:" は接続を閉じると DB が消える揮発的な SQLite DB。
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    """本番環境の設定。デバッグ無効・SECRET_KEY 必須。"""
    DEBUG = False

    @classmethod
    def init_app(cls, app):
        if cls.SECRET_KEY == "dev-fallback-key-change-in-production":
            raise RuntimeError("SECRET_KEY must be set in production environment")


# 環境名と設定クラスの対応表
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
